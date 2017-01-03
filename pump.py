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
                    "Error: missing configuration '{}'".format(token))

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
                    "Error: missing credentials in environment MCP_USER")

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
                    "Error: missing credentials in environment MCP_PASSWORD")

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

    def set_driver(self):
        """
        Sets a compute driver from Apache Libcloud

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

    def pump(self, begin=None, end=None, continuously=False):
        """
        Pumps data continuously

        :param begin: the beginning date, e.g., date(2016, 09, 01)
        :type begin: ``date`` or `None`

        :param end: the ending day, e.g., date(2016, 11, 30)
        :type end: ``date`` or `None`

        :param continuously: loop until Ctrl-C
        :type continuusly: `True` or `False`

        """

        if end is None:
            end = date.today()

        if begin:

            cursor = begin
            while cursor < end:
                logging.info("Pulling data for {}".format(cursor))
                self.pull_all(on=cursor)
                cursor += timedelta(days=1)

        while continuously:

            if cursor < end:
                logging.info("Pulling data for {}".format(cursor))
                self.pull_all(on=cursor)
                cursor += timedelta(days=1)

            else:
                time.sleep(60)
                end = date.today()

    def pull_all(self, on):
        """
        Pulls data for one day, across all regions

        :param on: the target day, e.g., date(2016, 11, 30)
        :type on: ``date``

        """
        logging.info("Considering {}".format(', '.join(self.engines.keys())))

        for region in self.engines.keys():
            self.pull(on=on, region=region)

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

        logging.info("Fetching summary usage for {}".format(region))

        start_date = (on - timedelta(days=1)).strftime("%Y-%m-%d")
        end_date = on.strftime("%Y-%m-%d")

        items = self.engines[region].ex_summary_usage_report(
            start_date,
            end_date)

        if len(items) > 0:
            items.pop(-1)

        logging.info("- found {} items for {} on {}".format(
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

        logging.info("Fetching detailed usage for {}".format(region))

        start_date = (on - timedelta(days=1)).strftime("%Y-%m-%d")
        end_date = on.strftime("%Y-%m-%d")

        items = self.engines[region].ex_detailed_usage_report(
            start_date,
            end_date)

        if len(items) > 0:
            items.pop(-1)

        logging.info("- found {} items for {} on {}".format(
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

        logging.info("Fetching audit log for {}".format(region))

        start_date = (on - timedelta(days=1)).strftime("%Y-%m-%d")
        end_date = on.strftime("%Y-%m-%d")

        items = self.engines[region].ex_audit_log_report(
            start_date,
            end_date)

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
            updater.update_summary_usage(list(items), region)

    def update_detailed_usage(self, items, region='dd-eu'):
        """
        Saves records of detailed usage

        :param items: to be recorded in database
        :type items: ``list`` of ``dict``

        :param region: the target region, e.g., 'dd-eu'
        :type region: ``str``

        """

        for updater in self.updaters:
            updater.update_detailed_usage(list(items), region)

    def update_audit_log(self, items, region='dd-eu'):
        """
        Saves records of audit log

        :param items: to be recorded in database
        :type items: ``list`` of ``dict``

        :param region: the target region, e.g., 'dd-eu'
        :type region: ``str``

        """

        for updater in self.updaters:
            updater.update_audit_log(list(items), region)

# the program launched from the command line
#
if __name__ == "__main__":

    # uncomment only one
    #
    #logging.basicConfig(format='%(message)s', level=logging.INFO)
    logging.basicConfig(format='%(levelname)s:%(message)s', level=logging.DEBUG)

    # create the pump itself
    #
    try:
        settings = config.pump
    except:
        settings = {}

    pump = Pump(settings)
    pump.set_driver()

    # log data in files
    #
    try:
        settings = config.files

        logging.debug("storing data in files")
        from models.files import FilesUpdater
        updater = FilesUpdater(settings)
        updater.reset_database()
        pump.add_updater(updater)

    except AttributeError:
        logging.debug("no configuration for file storage")


    # add an influxdb updater if one has been defined
    #
    try:
        settings = config.influxdb

        logging.debug("storing data in InfluxDB")
        from models.influx import InfluxdbUpdater
        updater = InfluxdbUpdater(settings)
        updater.reset_database()
        pump.add_updater(updater)

    except AttributeError:
        logging.debug("no configuration for InfluxDB")


    # fetch and dispatch data
    #
    today = date.today()
    cursor = (today - timedelta(days=90)).replace(day=1)

    pump.pump(begin=cursor, end=today)
