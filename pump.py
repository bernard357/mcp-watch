# Licensed to the Apache Software Foundation (ASF) under one or more
# contributor license agreements.  See the NOTICE file distributed with
# this work for additional information regarding copyright ownership.
# The ASF licenses this file to You under the Apache License, Version 2.0
# (the "License"); you may not use this file except in compliance with
# the License.  You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import colorlog
from datetime import date, datetime, timedelta
import logging
from multiprocessing import Process, Queue
import os
import re
import requests
from six import string_types
import socket
import string
import sys
import time

from libcloud.compute.providers import get_driver as get_compute_driver
from libcloud.compute.types import Provider as ComputeProvider

import config


class Pump(object):
    """
    Pumps logs from the Managed Cloud Platform (MCP) of Dimension Data

    Under Linux, you may want to edit ``~/.bash_profile`` like this::

        # credentials to access cloud resources from Dimension Data
        export MCP_USER='foo.bar'
        export MCP_PASSWORD='WhatsUpDoc'

    """

    def __init__(self, settings={}):
        """
        Ignites the plumbing engine

        :param settings: the parameters for this pump instance
        :type settings: ``dict``

        :param parameters: the external parameters
        :type plan: ``str`` or ``file`` or ``dict``

        """

        self.settings = settings
        if self.settings.get('debug', False):
            logging.basicConfig(format='%(levelname)s:%(message)s', level=logging.DEBUG)
        else:
            logging.basicConfig(format='%(message)s', level=logging.INFO)

        self._userName = None
        self._userPassword = None

        self.engines = {}
        self.dqueues = []
        self.mqueues = []

        self.updaters = []

        self.context = {}

    def get_user_name(self):
        """
        Retrieves user name to authenticate to the API

        :return: the user name to be used with the driver
        :rtype: ``str``

        :raises: :class:`Exception`
            - if no user name can be found

        The user name is normally taken
        from the environment variable ``MCP_USER``.

        Under Linux, you may want to edit ``~/.bash_profile`` like this::

            # credentials to access cloud resources from Dimension Data
            export MCP_USER='foo.bar'
            export MCP_PASSWORD='WhatsUpDoc'

        In addition, you can put the value in the configuration file,
        like this::

            mcp:
              MCP_USER: 'foo.bar'

        """

        if self._userName is None:
            self._userName = self.settings.get('MCP_USER')

        if self._userName is None:
            self._userName = os.getenv('MCP_USER')
            if self._userName is None or len(self._userName) < 3:
                raise Exception(
                    "Missing credentials in environment MCP_USER")

        return self._userName

    def get_user_password(self):
        """
        Retrieves user password to authenticate to the API

        :return: the user password to be used with the driver
        :rtype: ``str``

        :raises: :class:`plumbery.Exception`
            - if no user password can be found

        The user password is normally
        taken from the environment variable ``MCP_PASSWORD``.

        Under Linux, you may want to edit ``~/.bash_profile`` like this::

            # credentials to access cloud resources from Dimension Data
            export MCP_USER='foo.bar'
            export MCP_PASSWORD='WhatsUpDoc'

        In addition, you can put the value in the configuration file,
        like this::

            mcp:
              MCP_PASSWORD: 'WhatsUpDoc'

        """

        if self._userPassword is None:
            self._userPassword = self.settings.get('MCP_PASSWORD')

        if self._userPassword is None:
            self._userPassword = os.getenv('MCP_PASSWORD')
            if self._userPassword is None or len(self._userPassword) < 3:
                raise Exception(
                    "Missing credentials in environment MCP_PASSWORD")

        return self._userPassword

    def get_regions(self):
        """
        Retrieves regions to be analysed

        :return: the list of regions
        :rtype: ``list`` of ``str``

        Regions should normally be listed in main configuration::

            mcp:
              regions: ['dd-af', 'dd-ap', 'dd-au', 'dd-eu', 'dd-na']

        """

        return self.settings.get('regions',
                                 ('dd-af', 'dd-ap', 'dd-au', 'dd-eu', 'dd-na'))

    def set_drivers(self):
        """
        Sets compute drivers from Apache Libcloud

        """

        driver = get_compute_driver(ComputeProvider.DIMENSIONDATA)

        self.engines = {}

        for region in self.get_regions():

            self.engines[ region ] = driver(
                key=self.get_user_name(),
                secret=self.get_user_password(),
                region=region,
                host=None)

        return self.engines

    def set_workers(self):
        """
        Sets processing workers

        """

        self.dqueues = []
        self.mqueues = []

        for region in self.get_regions():

            self.context[ region ] = {}

            q = Queue()
            w = Process(target=self.work_every_day, args=(q, region))
            w.daemon = True
            w.start()
            self.dqueues.append(q)

            q = Queue()
            w = Process(target=self.work_every_minute, args=(q, region))
            w.daemon = True
            w.start()
            self.mqueues.append(q)

    def get_date(self, horizon='90d', since=None):
        """
        Computes target date

        :param horizon: amount of time in the past, e.g., '90d', '3m', '1y'
        :type horizon: ``str`` or `None`

        :param since: staring date for computation
        :type since: ``date`` or `None`

        :return: the related date, e.g., date(2016, 11, 30)
        :rtype: ``date``

        """

        if since is None:
            since = date.today()

        if horizon.endswith('y'):
            years = int(horizon.strip('y'))
            target = date(since.year - years, 1, 1)

        elif horizon.endswith('m'):
            months = int(horizon.strip('m'))
            year = since.year - int(months/12)
            month = since.month - months%12
            while month < 1:
                year -= 1
                month += 12
            target = date(year, month, 1)

        elif horizon.endswith('d'):
            days = int(horizon.strip('d'))
            target = (since - timedelta(days=days))

        else:
            raise ValueError('Incorrect horizon value')

        return target


    def pump(self, since=None, forever=True):
        """
        Pumps data continuously

        :param since: the beginning date, e.g., date(2016, 09, 01)
        :type since: ``date`` or `None`

        :param forever: loop until Ctrl-C or not
        :type forever: `True` or `False`

        """

        head = since if since else date.today()

        tail = date.today()

        try:

            while head < tail:
                logging.info("Pumping data for {}".format(head))
                for queue in self.dqueues:
                    queue.put(head)
                head += timedelta(days=1)

            while forever:

                if head < tail:
                    logging.info("Pumping data for {}".format(head))
                    for queue in self.dqueues:
                        queue.put(head)
                    head += timedelta(days=1)

                else:
                    logging.info("Pumping data for one minute")
                    for queue in self.mqueues:
                        queue.put(head)
                    time.sleep(60)
                    tail = date.today()

        except KeyboardInterrupt:
            pass
        except:
            raise

    def work_every_day(self, queue, region):
        """
        Handles data for one day and for one region

        :param queue: the list of days to consider
        :type queue: `Queue`

        :param region: the region to consider
        :type region: `str`

        This is ran as an independant process, so it works asynchronously
        from the rest.
        """

        try:

            for cursor in iter(queue.get, 'STOP'):
                self.pull(cursor, region)
                time.sleep(0.5)

        except KeyboardInterrupt:
            pass
        except:
            raise

    def work_every_minute(self, queue, region):
        """
        Handles data for one minute and for one region

        :param queue: the minute ticks for a given day
        :type queue: `Queue`

        :param region: the region to consider
        :type region: `str`

        This is ran as an independant process, so it works asynchronously
        from the rest.
        """

        try:

            for cursor in iter(queue.get, 'STOP'):
                self.tick(cursor, region)
                time.sleep(0.5)

        except KeyboardInterrupt:
            pass
        except:
            raise

    def pull(self, on, region='dd-eu'):
        """
        Pulls data for a given region on a given date

        :param on: the target day, e.g., date(2016, 11, 30)
        :type on: ``date``

        :param region: the target region, e.g., 'dd-eu'
        :type region: ``str``

        """

        try:
            items = self.fetch_summary_usage(on, region)
            self.update_summary_usage(items, region)

            items = self.fetch_detailed_usage(on, region)
            self.update_detailed_usage(items, region)

            items = self.fetch_audit_log(on, region)
            self.update_audit_log(items, region)

        except socket.error as feedback:
            logging.warning('Cannot access API endpoint for {}'.format(region))
            logging.warning('- {}'.format(str(feedback)))

        except Exception as feedback:
            logging.warning('Unable to pull for {}'.format(region))
            logging.exception('- {}'.format(feedback))

    def tick(self, on, region='dd-eu'):
        """
        Detects active servers over the past minute for a given region

        :param on: the current day, e.g., date(2016, 11, 30)
        :type on: ``date``

        :param region: the target region, e.g., 'dd-eu'
        :type region: ``str``

        """

        try:
            today = (on + timedelta(days=1))
            raw = self.fetch_audit_log(today, region)
            items = self.tail_audit_log(today, raw, region)
            servers = self.list_active_servers(items, region)
            self.on_active_servers(servers, region)

        except socket.error as feedback:
            logging.warning('Cannot access API endpoint for {}'.format(region))
            logging.warning('- {}'.format(str(feedback)))

        except Exception as feedback:
            logging.warning('Unable to tick for {}'.format(region))
            logging.exception(feedback)


    def fetch_summary_usage(self, on, region='dd-eu'):
        """
        Fetches and returns summary usage

        :param on: the target day, e.g., date(2016, 11, 30)
        :type on: ``date``

        :param region: the target region, e.g., 'dd-eu'
        :type region: ``str``

        """

        logging.info("Fetching summary usage for {} on {}".format(
            region, on.strftime("%Y-%m-%d")))

        start_date = (on - timedelta(days=1)).strftime("%Y-%m-%d")
        end_date = on.strftime("%Y-%m-%d")

        items = self.engines[region].ex_summary_usage_report(
            start_date,
            end_date)

        if len(items) > 0:

            first = ','.join(items[0])

            if len(first) < 1 or first.startswith(('<!DOCTYPE', '<?xml')):
                logging.debug('Data could not be fetched')
                logging.debug(items)
                items = []
                logging.warning("- no item could be found for {} on {}".format(
                    region, end_date))

            else:
                items.pop(-1)
                logging.debug("- found {} items for {} on {}".format(
                    len(items), region, end_date))

        return items

    def fetch_detailed_usage(self, on, region='dd-eu'):
        """
        Fetches and returns detailed usage

        :param on: the target day, e.g., date(2016, 11, 30)
        :type on: ``date``

        :param region: the target region, e.g., 'dd-eu'
        :type region: ``str``

        """

        logging.info("Fetching detailed usage for {} on {}".format(
            region, on.strftime("%Y-%m-%d")))

        start_date = (on - timedelta(days=1)).strftime("%Y-%m-%d")
        end_date = on.strftime("%Y-%m-%d")

        items = self.engines[region].ex_detailed_usage_report(
            start_date,
            end_date)

        if len(items) > 0:

            first = ','.join(items[0])

            if len(first) < 1 or first.startswith(('<!DOCTYPE', '<?xml')):
                logging.debug('Data could not be fetched')
                logging.debug(items)
                items = []
                logging.warning("- no item could be found for {} on {}".format(
                    region, end_date))

            else:
                items.pop(-1)
                logging.debug("- found {} items for {} on {}".format(
                    len(items), region, end_date))

        return items

    def fetch_audit_log(self, on, region='dd-eu'):
        """
        Fetches and returns audit log records

        :param on: the target day, e.g., date(2016, 11, 30)
        :type on: ``date``

        :param region: the target region, e.g., 'dd-eu'
        :type region: ``str``

        """

        logging.info("Fetching audit log for {} on {}".format(
            region, on.strftime("%Y-%m-%d")))

        start_date = (on - timedelta(days=1)).strftime("%Y-%m-%d")
        end_date = on.strftime("%Y-%m-%d")

        items = self.engines[region].ex_audit_log_report(
            start_date,
            end_date)

        if len(items) > 0:

            first = ','.join(items[0])

            if len(first) < 1 or first.startswith(('<!DOCTYPE', '<?xml')):
                logging.debug('Data could not be fetched')
                logging.debug(items)
                items = []
                logging.warning("- no item could be found for {} on {}".format(
                    region, end_date))

            else:
                logging.debug("- found {} items for {} on {}".format(
                    len(items), region, end_date))

        return items

    def tail_audit_log(self, on, raw=[], region='dd-eu'):
        """
        Considers only new records from the audit log

        :param on: the target day, e.g., date(2016, 11, 30)
        :type on: ``date``

        :param raw: raw records from the audit log
        :type raw: `list` of `list`

        :param region: the target region, e.g., 'dd-eu'
        :type region: ``str``

        """

        if raw in ([], None):
            return []

        cursor = self.context[region].get('cursor')
        uid = self.context[region].get('uid')

        raw.pop(0)    # remove headers

        if cursor == on and uid is not None:

            index = 0
            while index < len(raw):
                if raw[index][0] == uid:
                    break
                index += 1

            if index > 0 and index < len(raw):
                del raw[:index+1]
            elif len(raw) > 0 and raw[0][0] == uid:
                del raw[0]

        if len(raw) > 0:
            self.context[region]['cursor'] = on
            self.context[region]['uid'] = raw[-1][0]
            logging.debug("- tail to {} for {}".format(raw[-1][0], region))
            logging.debug("- {} new items have been found".format(len(raw)))

        else:
            logging.debug("- nothing new at {}".format(region))

        return raw

    def list_active_servers(self, raw=[], region='dd-eu'):
        """
        Detects active servers from the audit log

        :param raw: raw records from the audit log
        :type raw: `list` of `dict`

        :param region: the target region, e.g., 'dd-eu'
        :type region: ``str``

        """

        servers = []

        name_and_id = r'(.*)\[(.*)_(.*)\]'

        nodes = {}

        # process every record from the audit log
        #
        for item in raw:

            # we are interested only into completed actions on servers
            #
            if item[6] != 'SERVER' or item[10] != 'OK':
                continue

            # we are looking for server activations
            #
            if item[8].lower() not in ('deploy server',
                                       'start server',
                                       'reboot server'):
                continue

            # extract name and unique id of the activated server
            #
            matches = re.match(name_and_id, item[7])
            name = matches.group(1)
            id = matches.group(3)

            # catch any real-time problem
            #
            try:

                # cache in memory the information retrieved from the API
                #
                if id not in nodes:
                    node = self.engines[region].ex_get_node_by_id(id=id)

                    # hack - the driver does not report public ipv4 accurately
                    if len(node.public_ips) < 1:
                        domain = self.engines[region].ex_get_network_domain(
                            node.extra['networkDomainId'])
                        for rule in self.engines[region].ex_list_nat_rules(domain):
                            if rule.internal_ip == node.private_ips[0]:
                                node.public_ips.append(rule.external_ip)
                                break

                    nodes[id] = node

                # retrieve node information
                #
                node = nodes[id]
                if node is None:
                    continue

                # build a record for the updaters
                #
                server = {
                    'name': name,
                    'id': id,
                    'action': item[8],
                    'stamp': item[1],
                    'private_ip': node.private_ips[0],
                    'public_ip': node.public_ips[0] \
                        if len(node.public_ips) > 0 else None,
                    'description': node.extra['description'],
                    'region': region,
                    'sourceImageId': node.extra['sourceImageId'],
                    'networkDomainId': node.extra['networkDomainId'],
                    'datacenterId': node.extra['datacenterId'],
                    'deployedTime': node.extra['deployedTime'],
                    'cpu': node.extra['cpu'].cpu_count,
                    'memoryMb': node.extra['memoryMb'],
                    'OS_id': node.extra['OS_id'],
                    'OS_type': node.extra['OS_type'],
                    'OS_displayName': node.extra['OS_displayName'],
                    'disks': [x.size_gb for x in node.extra['disks']],
                    }

                # extend the raw list of activated servers
                #
                servers.insert(0,server)

            # recover safely from any error
            #
            except Exception as feedback:
                logging.debug('Cannot locate {}'.format(name))
                logging.debug('- {}'.format(str(feedback)))
                nodes[id] = None

        # keep only the most recent record for each server
        #
        if len(servers) > 0:
            logging.debug('Found active servers for {}'.format(region))
        uniques = []
        processed = []
        for server in servers:
            if server['id'] in processed:
                continue
            processed.append(server['id'])
            uniques.append(server)
            logging.debug("- {}".format(server))

        if len(uniques) < 1:
            logging.debug("- no new active server at {}".format(region))

        # list of activated servers
        #
        return uniques

    def add_updater(self, updater):
        """
        Adds a new database updater

        :param updater: check directory `updaters`
        :type updater: ``object``

        """

        self.updaters.append(updater)

    def update_summary_usage(self, items, region='dd-eu'):
        """
        Saves records of summary usage

        :param items: to be recorded in database
        :type items: ``list`` of ``dict``

        :param region: the target region, e.g., 'dd-eu'
        :type region: ``str``

        """

        avoided = 0
        for updater in self.updaters:

            if not updater.get('active', False):
                avoided += 1
                continue

            try:
                updater.update_summary_usage(list(items), region)

            except IndexError:
                logging.error('Invalid index in provided data')
                logging.error(items)

        if avoided == len(self.updaters) and len(items) > 0:
            logging.warning('No updater has been activated')

    def update_detailed_usage(self, items, region='dd-eu'):
        """
        Saves records of detailed usage

        :param items: to be recorded in database
        :type items: ``list`` of ``dict``

        :param region: the target region, e.g., 'dd-eu'
        :type region: ``str``

        """

        avoided = 0
        for updater in self.updaters:

            if not updater.get('active', False):
                avoided += 1
                continue

            try:
                updater.update_detailed_usage(list(items), region)

            except IndexError:
                logging.error('Invalid index in provided data')
                logging.error(items)

        if avoided == len(self.updaters) and len(items) > 0:
            logging.warning('No updater has been activated')

    def update_audit_log(self, items, region='dd-eu'):
        """
        Saves records of audit log

        :param items: to be recorded in database
        :type items: ``list`` of ``dict``

        :param region: the target region, e.g., 'dd-eu'
        :type region: ``str``

        """

        avoided = 0
        for updater in self.updaters:

            if not updater.get('active', False):
                avoided += 1
                continue

            try:
                updater.update_audit_log(list(items), region)

            except IndexError:
                logging.error('Invalid index in provided data')
                logging.error(items)

        if avoided == len(self.updaters) and len(items) > 0:
            logging.warning('No updater has been activated')

    def on_active_servers(self, items, region='dd-eu'):
        """
        Signals that active servers have been detected

        :param items: to be recorded in database
        :type items: ``list`` of ``dict``

        :param region: the target region, e.g., 'dd-eu'
        :type region: ``str``

        """

        avoided = 0
        for updater in self.updaters:

            if not updater.get('active', False):
                avoided += 1
                continue

            try:
                updater.on_active_servers(list(items), region)

            except Exception as feedback:
                logging.warning('Unable to update on active servers')
                logging.exception(feedback)

        if avoided == len(self.updaters) and len(items) > 0:
            logging.warning('No updater has been activated')

# when the program is launched from the command line
#
if __name__ == "__main__":

    # create the pump itself
    #
    try:
        settings = config.pump
    except:
        settings = {}

    pump = Pump(settings)

    # logging to console
    #
    handler = colorlog.StreamHandler()
    formatter = colorlog.ColoredFormatter(
        "%(asctime)-2s %(log_color)s%(message)s",
        datefmt='%H:%M:%S',
        reset=True,
        log_colors={
            'DEBUG':    'cyan',
            'INFO':     'green',
            'WARNING':  'yellow',
            'ERROR':    'red',
            'CRITICAL': 'red,bg_white',
        },
        secondary_log_colors={},
        style='%'
    )
    handler.setFormatter(formatter)

    logging.getLogger('').handlers = []
    logging.getLogger('').addHandler(handler)


    # get args
    #
    horizon = None
    if len(sys.argv) > 1:
        horizon = sys.argv[1]

        if horizon[-1] not in ('d', 'm', 'y'):
            print('usage: pump [<horizon>]')
            print('examples:')
            print('pump')
            print('pump 90d')
            print('pump 3m')
            print('pump 12m')
            print('pump 1y')
            sys.exit(1)

        horizon = pump.get_date(horizon)
        logging.info('Pumping since {}'.format(horizon))

    # log data in files as per configuration
    #
    try:
        settings = config.files

        logging.debug("Storing data in files")
        from models.files import FilesUpdater
        updater = FilesUpdater(settings)
        if updater.get('active', False):
            if horizon:
                updater.reset_store()
            else:
                updater.use_store()
            pump.add_updater(updater)
        else:
            logging.debug("- module is not active")

    except AttributeError:
        logging.debug("No configuration for file storage")

    # add an influxdb updater as per configuration
    #
    try:
        settings = config.influxdb

        logging.debug("Storing data in InfluxDB")
        from models.influx import InfluxdbUpdater
        updater = InfluxdbUpdater(settings)
        if updater.get('active', False):
            if horizon:
                updater.reset_store()
            else:
                updater.use_store()
            pump.add_updater(updater)
        else:
            logging.debug("- module is not active")

    except AttributeError:
        logging.debug("No configuration for InfluxDB")

    # add a qualys updater as per configuration
    #
    try:
        settings = config.qualys

        logging.debug("Using Qualys service")
        from models.qualys import QualysUpdater
        updater = QualysUpdater(settings)
        if updater.get('active', False):
            if horizon:
                updater.reset_store()
            else:
                updater.use_store()
            pump.add_updater(updater)
        else:
            logging.debug("- module is not active")

    except AttributeError:
        logging.debug("No configuration for Qualys")

    # add a Cisco Spark updater as per configuration
    #
    try:
        settings = config.spark

        logging.debug("Using Cisco Spark service")
        from models.spark import SparkUpdater
        updater = SparkUpdater(settings)
        if updater.get('active', False):
            if horizon:
                updater.reset_store()
            else:
                updater.use_store()
            pump.add_updater(updater)
        else:
            logging.debug("- module is not active")

    except AttributeError:
        logging.debug("No configuration for Cisco Spark")

    # sanity check
    #
    if len(pump.updaters) < 1:
        logging.warning('No updater has been configured, check config.py')
        time.sleep(5)

    # fetch and dispatch data
    #
    pump.set_drivers()
    pump.set_workers()
    pump.pump(since=horizon)
