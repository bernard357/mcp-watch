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
from base import Updater


class FilesUpdater(Updater):
    """
    Updates files
    """

    def use_database(self):
        """
        Opens a database to save data
        """

        pass

    def reset_database(self):
        """
        Opens a database for points
        """

        file = self.settings.get('summary_usage', './summary_usage.log')
        try:
            if os.path.exists(file):
                mode = 'a'
            else:
                mode = 'w'

            with open(file, mode) as handle:
                handle.truncate()

        except:
            logging.debug("could not truncate {}".format(file))

        file = self.settings.get('detailed_usage', './detailed_usage.log')
        try:
            if os.path.exists(file):
                mode = 'a'
            else:
                mode = 'w'

            with open(file, mode) as handle:
                handle.truncate()

        except:
            logging.debug("could not truncate {}".format(file))

        file = self.settings.get('audit_log', './audit_log.log')
        try:
            if os.path.exists(file):
                mode = 'a'
            else:
                mode = 'w'

            with open(file, mode) as handle:
                handle.truncate()

        except:
            logging.debug("could not truncate {}".format(file))


    def update_summary_usage(self, items=[], region='dd-eu'):
        """
        Updates summary usage records

        :param items: new items to push to the database
        :type items: ``list`` of ``list``

        :param region: source of the information, e.g., 'dd-eu' or other region
        :type region: ``str``

        """

        file = self.settings.get('summary_usage', './summary_usage.log')
        try:
            logging.debug("logging into {}".format(file))

            if os.path.exists(file):
                mode = 'a'
            else:
                mode = 'w'

            with open(file, mode) as handle:

                for item in items:
                    handle.write(str(item)+'\n')

            logging.info("Found {} measurements for {}".format(
                len(items), region))

        except:
            logging.debug("could not update {}".format(file))


    def update_detailed_usage(self, items=[], region='dd-eu'):
        """
        Updates detailed usage records

        :param items: new items to push to the database
        :type items: ``list`` of ``list``

        :param region: source of the information, e.g., 'dd-eu' or other region
        :type region: ``str``

        """

        file = self.settings.get('detailed_usage', './detailed_usage.log')
        try:
            logging.debug("logging into {}".format(file))

            if os.path.exists(file):
                mode = 'a'
            else:
                mode = 'w'

            with open(file, mode) as handle:

                for item in items:
                    handle.write(str(item)+'\n')

            logging.info("Found {} measurements for {}".format(
                len(items), region))

        except:
            logging.debug("could not update {}".format(file))

    def update_audit_log(self, items=[], region='dd-eu'):
        """
        Updates audit log records

        :param items: new items to push to the database
        :type items: ``list`` of ``list``

        :param region: source of the information, e.g., 'dd-eu' or other region
        :type region: ``str``

        """

        file = self.settings.get('audit_log', './audit_log.log')
        try:
            logging.debug("logging into {}".format(file))

            if os.path.exists(file):
                mode = 'a'
            else:
                mode = 'w'

            with open(file, mode) as handle:

                for item in items:
                    handle.write(str(item)+'\n')

            logging.info("Found {} measurements for {}".format(
                len(items), region))

        except:
            logging.debug("could not update {}".format(file))

