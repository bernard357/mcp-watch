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

    def get_summary_usage_file(self):
        return self.settings.get('summary_usage', './logs/summary_usage.log')

    def get_detailed_usage_file(self):
        return self.settings.get('detailed_usage', './logs/detailed_usage.log')

    def get_audit_log_file(self):
        return self.settings.get('audit_log', './logs/audit_log.log')

    def use_database(self):
        """
        Opens a database to save data
        """

        pass

    def reset_database(self):
        """
        Opens a database for points
        """

        file = self.get_summary_usage_file()
        try:
            if os.path.exists(file):
                mode = 'a'
            else:
                mode = 'w'

            with open(file, mode) as handle:
                handle.truncate()

        except:
            logging.warning("could not truncate {}".format(file))

        file = self.get_detailed_usage_file()
        try:
            if os.path.exists(file):
                mode = 'a'
            else:
                mode = 'w'

            with open(file, mode) as handle:
                handle.truncate()

        except:
            logging.warning("could not truncate {}".format(file))

        file = self.get_audit_log_file()
        try:
            if os.path.exists(file):
                mode = 'a'
            else:
                mode = 'w'

            with open(file, mode) as handle:
                handle.truncate()

        except:
            logging.warning("could not truncate {}".format(file))


    def update_summary_usage(self, items=[], region='dd-eu'):
        """
        Updates summary usage records

        :param items: new items to push to the database
        :type items: ``list`` of ``list``

        :param region: source of the information, e.g., 'dd-eu' or other region
        :type region: ``str``

        """

        file = self.get_summary_usage_file()
        try:
            logging.debug("- logging into {}".format(file))

            path = os.path.dirname(file)
            if not os.path.exists(path):
                try:
                    os.makedirs(path)
                except OSError as feedback: # prevent race condition
                    if feedback.errno != errno.EEXIST:
                        raise

            if os.path.exists(file):
                mode = 'a'
            else:
                mode = 'w'

            with open(file, mode) as handle:

                if len(items) > 0:
                    headers = items.pop(0)
                    logging.debug("- headers: {}".format(headers))

                for item in items:
                    handle.write(str(item)+'\n')

            logging.info("- logged {} measurements for {}".format(
                len(items), region))

        except:
            logging.warning("- could not update {}".format(file))


    def update_detailed_usage(self, items=[], region='dd-eu'):
        """
        Updates detailed usage records

        :param items: new items to push to the database
        :type items: ``list`` of ``list``

        :param region: source of the information, e.g., 'dd-eu' or other region
        :type region: ``str``

        """

        file = self.get_detailed_usage_file()
        try:
            logging.debug("- logging into {}".format(file))

            path = os.path.dirname(file)
            if not os.path.exists(path):
                try:
                    os.makedirs(path)
                except OSError as feedback: # prevent race condition
                    if feedback.errno != errno.EEXIST:
                        raise

            if os.path.exists(file):
                mode = 'a'
            else:
                mode = 'w'

            with open(file, mode) as handle:

                if len(items) > 0:
                    headers = items.pop(0)
                    logging.debug("- headers: {}".format(headers))

                for item in items:
                    handle.write(str(item)+'\n')

            logging.info("- logged {} measurements for {}".format(
                len(items), region))

        except:
            logging.warning("- could not update {}".format(file))

    def update_audit_log(self, items=[], region='dd-eu'):
        """
        Updates audit log records

        :param items: new items to push to the database
        :type items: ``list`` of ``list``

        :param region: source of the information, e.g., 'dd-eu' or other region
        :type region: ``str``

        """

        file = self.get_audit_log_file()
        try:
            logging.debug("- logging into {}".format(file))

            path = os.path.dirname(file)
            if not os.path.exists(path):
                try:
                    os.makedirs(path)
                except OSError as feedback: # prevent race condition
                    if feedback.errno != errno.EEXIST:
                        raise

            if os.path.exists(file):
                mode = 'a'
            else:
                mode = 'w'

            with open(file, mode) as handle:

                if len(items) > 0:
                    headers = items.pop(0)
                    logging.debug("- headers: {}".format(headers))

                for item in items:
                    handle.write(str(item)+'\n')

            logging.info("- logged {} measurements for {}".format(
                len(items), region))

        except:
            logging.warning("- could not update {}".format(file))
