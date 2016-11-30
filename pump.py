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

import hashlib
import logging
import os
import random
import requests
from six import string_types
import string
import sys
import time
import uuid
import yaml

from libcloud.compute.providers import get_driver as get_compute_driver
from libcloud.compute.types import Provider as ComputeProvider


class Pump(object):
    """
    Pumps logs from the Managed Cloud Platform (MCP) of Dimension Data

    Under Linux, you may want to edit ``~/.bash_profile`` like this::

        # credentials to access cloud resources from Dimension Data
        export MCP_USERNAME='foo.bar'
        export MCP_PASSWORD='WhatsUpDoc'

    """

    def __init__(self, settings={}):
        """
        Ignites the plumbing engine

        :param settings: the parameters for this pump instance
        :type settings: ``str`` or ``file`` or ``dict`` or ``list`` of ``dict``

        :param parameters: the external parameters
        :type plan: ``str`` or ``file`` or ``dict``

        """

        self.settings = settings

        self._userName = None
        self._userPassword = None
        self._engine = None


    def set_user_name(self, name):
        """
        Changes the name used to authenticate to the API

        :param name: the user name to be used with the driver
        :type name: ``str``

        This function can be used to supplement the normal provision of
        a user name via the environment variable ``MCP_USERNAME``.

        """

        self._userName = name

    def get_user_name(self):
        """
        Retrieves user name to authenticate to the API

        :return: the user name to be used with the driver
        :rtype: ``str``

        :raises: :class:`Exception`
            - if no user name can be found

        The user name is normally taken
        from the environment variable ``MCP_USERNAME``.

        Under Linux, you may want to edit ``~/.bash_profile`` like this::

            # credentials to access cloud resources from Dimension Data
            export MCP_USERNAME='foo.bar'
            export MCP_PASSWORD='WhatsUpDoc'

        """

        if self._userName is None:
            self._userName = os.getenv('MCP_USERNAME')
            if self._userName is None or len(self._userName) < 3:
                raise Exception(
                    "Error: missing credentials in environment MCP_USERNAME")

        return self._userName

    def set_user_password(self, password):
        """
        Changes the password used to authenticate to the API

        :param password: the user password to be used with the driver
        :type password: ``str``

        This function can be used to supplement the normal provision of
        a user password via the environment variable ``MCP_PASSWORD``.

        """

        self._userPassword = password

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
            export MCP_USERNAME='foo.bar'
            export MCP_PASSWORD='WhatsUpDoc'

        """

        if self._userPassword is None:
            self._userPassword = os.getenv('MCP_PASSWORD')
            if self._userPassword is None or len(self._userPassword) < 3:
                raise Exception(
                    "Error: missing credentials in environment MCP_PASSWORD")

        return self._userPassword

    def set_driver(self, region='dd-eu', host=None):
        """
        Sets a compute driver from Apache Libcloud

        """

        driver = get_compute_driver(ComputeProvider.DIMENSIONDATA)

        self._engine = driver(
            key=self.get_user_name(),
            secret=self.get_user_password(),
            region=region,
            host=host)

        return self._engine

    def pump(self):
        """
        Pumps data continuously
        """

        while True:

            self.pull()

            time.sleep(30)


    def pull(self):
        """
        Pulls some data
        """

        start_date = '2016-11-20'
        end_date = '2016-11-30'

        try:
            data = self._engine.ex_detailed_usage_report(
                start_date,
                end_date)

            print(data)

        except Exception as feedback:

            if 'RESOURCE_BUSY' in str(feedback):
                pass

            else:
                raise


pump = Pump()
pump.set_driver()
pump.pull()
