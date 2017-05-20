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

import logging
import os


class Updater(object):
    """
    Updates a database
    """

    def __init__(self, settings={}):
        """
        Sets updater settings

        :param settings: the parameters for this updater
        :type settings: ``dict``

        """

        self.settings = settings

    def get(self, label, default=None):
        """
        Gets some settings

        :param label: name of the settings
        :type label: ``str``

        :param default: default value
        :type default: ``str``

        If the value starts with `$` then a lookup is done from the environment.
        For example:

            value = updater.get('login', '$QUALYS_LOGIN')

        In that case, if no value can be found for `login`, then the value
        of the environment variable `QUALYS_LOGIN` is provided instead.

        """
        value = self.settings.get(label, default)

        if value is not None and str(value)[0] == '$':
            value = os.environ.get(str(value)[1:])

        return value

    def use_store(self):
        """
        Opens an existing store before updating it
        """
        logging.debug(u"- no code to use store")

    def reset_store(self):
        """
        Creates or resets a store before updating it
        """
        logging.debug(u"- no code to reset store")

    def close_store(self):
        """
        Closes a store when the pump is stopped
        """
        logging.debug(u"- no code to close store")

    def update_summary_usage(self, items=[], region='dd-eu'):
        """
        Updates detailed usage records

        :param items: new items to push to the database
        :type items: ``list`` of ``list``

        :param region: source of the information, e.g., 'dd-eu' or other region
        :type region: ``str``

        Items provided have the following structure:
        - DAY
        - Location
        - CPU Hours
        - High Performance CPU Hours
        - RAM Hours
        - Storage Hours
        - High Performance Storage Hours
        - Economy Storage Hours
        - Bandwidth In
        - Bandwidth Out
        - Sub-Admin Hours
        - Network Hours
        - Essentials Network Domain Hours
        - Advanced Network Domain Hours
        - VLAN Hours
        - Public IP Hours
        - Cloud Files Account Hours
        - Cloud Files (GB Days)
        - Software Units
        - Essentials Client Days
        - Advanced Client Days
        - Enterprise Client Days
        - Essentials Backups (GB)
        - Advanced Backups (GB)
        - Enterprise Backups (GB)
        - Essentials Monitoring Hours
        - Advanced Monitoring Hours

        """
        logging.debug(u"- no code to update summary usage")

    def update_detailed_usage(self, items=[], region='dd-eu'):
        """
        Updates detailed usage records

        :param items: new items to push to the database
        :type items: ``list`` of ``list``

        :param region: source of the information, e.g., 'dd-eu' or other region
        :type region: ``str``

        Items provided have more or less the following structure:
        - Name
        - UUID
        - Type
        - Location
        - Private IP Address
        - Status
        - Start Time
        - End Time
        - Duration (Hours)
        - CPU Type
        - CPU Count
        - RAM (GB)
        - Storage (GB)
        - High Performance Storage (GB)
        - Economy Storage (GB)
        - CPU Hours
        - High Performance CPU Hours
        - RAM Hours
        - Storage Hours
        - High Performance Storage Hours
        - Economy Storage Hours
        - Bandwidth-In (GB)
        - Bandwidth-Out (GB)
        - Subadmin Hours
        - Network Hours
        - Essentials Network Domain Hours
        - Advanced Network Domain Hours
        - VLAN Hours
        - Public IP Hours
        - Cloud Files Account Hours
        - Cloud Storage (GB)

        """
        logging.debug(u"- no code to update detailed usage")

    def update_audit_log(self, items=[], region='dd-eu'):
        """
        Updates audit log records

        :param items: new items to push to the database
        :type items: ``list`` of ``list``

        :param region: source of the information, e.g., 'dd-eu' or other region
        :type region: ``str``

        Items provided have the following structure:
        - UUID
        - Time
        - Create User
        - Department
        - Customer Defined 1
        - Customer Defined 2
        - Type
        - Name
        - Action
        - Details
        - Response Code

        """
        logging.debug(u"- no code to update audit log")

    def on_servers(self, updates=[], region='dd-eu'):
        """
        Signals the deployment, start or reboot of cloud servers

        :param updates: description of new servers
        :type updates: ``list`` of ``dict``

        :param region: source of the information, e.g., 'dd-eu' or other region
        :type region: ``str``

        Items provided have following named attributes:
        - 'name' - node name
        - 'id' - node unique id
        - 'action' - type of activation
        - 'stamp' - date of record in the audit log
        - 'private_ip' - node primary private ip address
        - 'public_ip' - node public ip address, or None
        - 'description' - node description, or None
        - 'region' - region where the node belongs
        - 'sourceImageId' - unique id of the image used for this node
        - 'networkDomainId' - unique id of the network domain of this node
        - 'datacenterId' - unique id of the data centre of this node
        - 'deployedTime' - date of deployment
        - 'cpu' - quantity of cpu
        - 'memoryMb' - quantity of memory
        - 'OS_id' - name and version of the operating system
        - 'OS_type' - family of the operating system
        - 'OS_displayName' - for human beings
        - 'disks' - list of disk sizes in GB

        This is a sample CentOS server deployed privately:

            {'sourceImageId': 'bdc67f9b-df9a-4d0c-8889-2c9f9bbda610',
             'networkDomainId': '315d1a1f-8644-427d-bcf7-2ad98c401c67',
             'name': 'BE-CloudCenter-CCM',
             'memoryMb': 4096,
             'stamp': '2017-01-21 08:47:30',
             'disks': [55],
             'deployedTime': '2017-01-21T08:36:21.000Z',
             'cpu': 2,
             'public_ip': None,
             'OS_displayName': 'CENTOS7/64',
             'datacenterId': 'EU8',
             'private_ip': '10.1.1.100',
             'region': 'dd-eu',
             'action': 'Start Server',
             'OS_id': 'CENTOS764',
             'OS_type': 'UNIX',
             'id': 'adb0125b-e10c-4776-ac19-608169c7546c',
             'description': None}

        This is a sample Ubuntu machine exposed to the Internet:

            {'sourceImageId': '07a1d8b9-9a63-4b79-b630-9b6a734695da',
             'networkDomainId': '3e0ade0e-65cd-4c78-8494-6260218b4e7a',
             'name': 'slave-03',
             'memoryMb': 12288,
             'stamp': '2017-01-21 12:51:02',
             'disks': [10, 200],
             'deployedTime': '2017-01-21T08:20:47.000Z',
             'cpu': 4,
             'public_ip': '168.128.13.201',
             'OS_displayName': 'UBUNTU14/64',
             'datacenterId': 'EU6',
             'private_ip': '10.60.0.9',
             'region': 'dd-eu',
             'action': 'Start Server',
             'OS_id': 'UBUNTU1464',
             'OS_type': 'UNIX',
             'id': '12c6a79f-1555-44b1-811b-d05ab0f1bf46',
             'description': 'Hadoop slave node #plumbery'}

        """
        logging.debug(u"- no code to update server information")
