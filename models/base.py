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
        :type label: `str`

        :param default: default value
        :type default: `str`

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

        pass

    def reset_store(self):
        """
        Creates or resets a store before updating it
        """

        pass

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

        raise NotImplementedError

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

        raise NotImplementedError

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

        raise NotImplementedError

    def on_active_servers(self, items=[], region='dd-eu'):
        """
        Signals the deployment, start or reboot of cloud servers

        :param items: description of new servers
        :type items: ``list`` of ``dict``

        :param region: source of the information, e.g., 'dd-eu' or other region
        :type region: ``str``

        """

        pass
