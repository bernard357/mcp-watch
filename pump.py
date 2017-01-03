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

from datetime import date, datetime, timedelta
import logging
from multiprocessing import Process, Queue
import os
import requests
from six import string_types
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

        self._userName = None
        self._userPassword = None

        self.engines = {}
        self.queues = []

        self.updaters = []

    def lookup(self, key, default=None):
        """
        Finds a value from settings

        :param key: the parameter to lookup
        :type key: ``str``

        :param default: the default value
        :type default: ``str`` or ``list`` or ``dict``

        """

        settings = self.settings
        tokens = key.split('.')
        label = tokens.pop(-1)
        for token in tokens:

            if token in settings:
                settings = settings[ token ]
            else:
                raise KeyError(
                    "Missing configuration '{}'".format(token))

        return settings.get(label, default)

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
            self._userName = self.lookup('MCP_USER')

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
            self._userPassword = self.lookup('MCP_PASSWORD')

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

        return self.lookup('regions',
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

        self.queues = []

        for region in self.get_regions():

            q = Queue()

            w = Process(target=self.work, args=(q, region))
            w.daemon = True
            w.start()

            self.queues.append(q)

        return self.queues

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
            years = int(months/12)
            months = months%12
            target = date(since.year - years, since.month - months, 1)

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

        while head < tail:
            logging.info("Pumping data for {}".format(head))
            for queue in self.queues:
                queue.put(head)
            head += timedelta(days=1)

        while forever:

            if head < tail:
                logging.info("Pumping data for {}".format(head))
                for queue in self.queues:
                    queue.put(head)
                head += timedelta(days=1)

            else:
                logging.debug("Waiting for next day")
                time.sleep(60)
                tail = date.today()

    def pull_all(self, on):
        """
        Pulls data for one day, across all regions

        :param on: the target day, e.g., date(2016, 11, 30)
        :type on: ``date``

        """


    def work(self, queue, region):

        for cursor in iter(queue.get, 'STOP'):
            self.pull(cursor, region)

    def pull(self, on, region='dd-eu'):
        """
        Pulls data for a given region on a given date

        :param on: the target day, e.g., date(2016, 11, 30)
        :type on: ``date``

        :param region: the target region, e.g., 'dd-eu'
        :type region: ``str``

        """

        items = self.fetch_summary_usage(on, region)
        self.update_summary_usage(items, region)

        items = self.fetch_detailed_usage(on, region)
        self.update_detailed_usage(items, region)

        items = self.fetch_audit_log(on, region)
        self.update_audit_log(items, region)

    def fetch_summary_usage(self, on, region='dd-eu'):
        """
        Fetches and returns summary usage

        :param on: the target day, e.g., date(2016, 11, 30)
        :type on: ``date``

        :param region: the target region, e.g., 'dd-eu'
        :type region: ``str``

        """

        logging.info("Fetching summary usage for {} on {}".format(region, on.strftime("%Y-%m-%d")))

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

        logging.info("Fetching detailed usage for {} on {}".format(region, on.strftime("%Y-%m-%d")))

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

        logging.info("Fetching audit log for {} on {}".format(region, on.strftime("%Y-%m-%d")))

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

        for updater in self.updaters:

            try:
                updater.update_summary_usage(list(items), region)

            except IndexError:
                logging.error('Invalid index in provided data')
                logging.error(items)

    def update_detailed_usage(self, items, region='dd-eu'):
        """
        Saves records of detailed usage

        :param items: to be recorded in database
        :type items: ``list`` of ``dict``

        :param region: the target region, e.g., 'dd-eu'
        :type region: ``str``

        """

        for updater in self.updaters:

            try:
                updater.update_detailed_usage(list(items), region)

            except IndexError:
                logging.error('Invalid index in provided data')
                logging.error(items)

    def update_audit_log(self, items, region='dd-eu'):
        """
        Saves records of audit log

        :param items: to be recorded in database
        :type items: ``list`` of ``dict``

        :param region: the target region, e.g., 'dd-eu'
        :type region: ``str``

        """

        for updater in self.updaters:

            try:
                updater.update_audit_log(list(items), region)

            except IndexError:
                logging.error('Invalid index in provided data')
                logging.error(items)

# the program launched from the command line
#
if __name__ == "__main__":

    # uncomment only one
    #
    logging.basicConfig(format='%(message)s', level=logging.INFO)
    #logging.basicConfig(format='%(levelname)s:%(message)s', level=logging.DEBUG)

    # create the pump itself
    #
    try:
        settings = config.pump
    except:
        settings = {}

    pump = Pump(settings)

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
        if horizon:
            updater.reset_store()
        else:
            updater.use_store()
        pump.add_updater(updater)

    except AttributeError:
        logging.debug("No configuration for file storage")


    # add an influxdb updater as per configuration
    #
    try:
        settings = config.influxdb

        logging.debug("Storing data in InfluxDB")
        from models.influx import InfluxdbUpdater
        updater = InfluxdbUpdater(settings)
        if horizon:
            updater.reset_store()
        else:
            updater.use_store()
        pump.add_updater(updater)

    except AttributeError:
        logging.debug("No configuration for InfluxDB")

    if len(pump.updaters) < 1:
        logger.warning('No updater has been configured, check config.py')
        time.sleep(5)

    # fetch and dispatch data
    #
    pump.set_drivers()
    pump.set_workers()
    pump.pump(since=horizon)
