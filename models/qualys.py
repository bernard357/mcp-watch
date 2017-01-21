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
import requests
from base import Updater


class QualysUpdater(Updater):
    """
    Interacts with Qualys service

    Qualys credentials should normally be set
    in environment variables  ``QUALYS_LOGIN`` and ``QUALYS_PASSWORD``.

    Under Linux, you may want to edit ``~/.bash_profile`` like this::

        # credentials to access Qualys service
        export QUALYS_LOGIN='foo.bar'
        export QUALYS_PASSWORD='WhatsUpDoc'

    """

    def update_summary_usage(self, items=[], region='dd-eu'):
        """
        Not applicable to the Qualys updater
        """

        pass

    def update_detailed_usage(self, items=[], region='dd-eu'):
        """
        Not applicable to the Qualys updater
        """

        pass

    def update_audit_log(self, items=[], region='dd-eu'):
        """
        Not applicable to the Qualys updater
        """

        pass

    def on_active_servers(self, items=[], region='dd-eu'):
        """
        Signals the deployment, start or reboot of cloud servers

        :param items: description of new servers
        :type items: ``list`` of ``dict``

        :param region: source of the information, e.g., 'dd-eu' or other region
        :type region: ``str``

        """

        # access the qualys API directly
        #
        add_url = self.get('url', '$QUALYS_URL')+'api/2.0/fo/asset/ip/'
        launch_url = self.get('url', '$QUALYS_URL')+'api/2.0/fo/scan/'
        auth = (self.get('login', '$QUALYS_LOGIN'),
                self.get('password', '$QUALYS_PASSWORD'))
        headers = {'X-Requested-With': 'MCP Watch'}

        # number of scans that are triggered
        #
        count = 0

        # look at every server that have been activated
        #
        for item in items:

            # we need a public IP address to do the scan
            #
            if item['public_ip'] is None:
                continue

            # trigger a scan
            #
            logging.info("- scanning {} at {} for {}".format(
                item['name'], item['public_ip'], region))
            count += 1

            # catch any real-time problem
            #
            try:

                # add the public IP to the inventory handled by Qualys
                #
                payload = {
                    'action': 'add',
                    'ips': item['public_ip'],
                    'enable_vm': 1,
                    }

                response = requests.post(url=add_url,
                                         auth=auth,
                                         headers=headers,
                                         params=payload)

                if response.status_code != 200:
                    logging.info(response.json())
                    raise Exception("Received error code {}".format(
                        response.status_code))

                # launch an actual scan by Qualys
                #
                payload = {
                    'action': 'launch',
                    'ip': item['public_ip'],
                    'scan_title': "Scan of {} at {} for {}".format(
                        item['name'], item['public_ip'], region),
                    'option_title': self.get('option', 'MCP Watch'),
                    }

                response = requests.post(url=launch_url,
                                         auth=auth,
                                         headers=headers,
                                         params=payload)

                if response.status_code != 200:
                    logging.info(response.json())
                    raise Exception("Received error code {}".format(
                        response.status_code))

            # recover safely from any error
            #
            except Exception as feedback:
                logging.warning('- unable to use Qualys service')
                logging.warning(str(feedback))

        # report on this batch
        #
        if count > 0:
            logging.info("- triggered {} scans from Qualys for {}".format(
                count, region))
        else:
            logging.info("- nothing to scan from Qualys for {}".format(
                region))


