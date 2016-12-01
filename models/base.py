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

    def use_database(self):
        """
        Opens an existing database to update it
        """

        raise NotImplementedError

    def reset_database(self):
        """
        Creates or resets a database to receive updates
        """

        raise NotImplementedError

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

        Items provided have the following structure:
        - Name
        - UUID
        - Type
        - Location
        - Private IP Address
        - Status
        - "user: Country"
        - "user: EUITAAS_Tag"
        - "user: Test_Agenda"
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
