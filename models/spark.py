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

from shellbot import ShellBot


UPDATE_TEMPLATE = """{action} at {dc} ({region}):
* name: {name}
* type: {OS}
* CPU: {cpu}
* RAM: {memoryMb} (MB)
* disks: {disks} (GB)
* private IPv4: {private_ip}
{extensions}"""

my_bot = ShellBot()


class SparkUpdater(Updater):
    """
    Interacts with Cisco Spark service

    Token is expected in ``CHAT_TOKEN``.

    """

    def use_store(self):
        """
        Opens an existing store before updating it
        """
        self.reset_store()

    def reset_store(self):
        """
        Creates or resets a store before updating it
        """
        logging.debug("Connecting to Cisco Spark")

        try:
            os.environ['CHAT_ROOM_TITLE'] = self.get('room', '$CHAT_ROOM_TITLE')
            os.environ['CHAT_ROOM_MODERATORS'] = self.get('moderators', '$CHAT_ROOM_MODERATORS')
            os.environ['CHAT_TOKEN'] = self.get('token', '$CHAT_TOKEN')
            my_bot.configure()
            my_bot.bond()

        except Exception as feedback:
            logging.error(u"Unable to connect to Cisco Spark")
            logging.exception(feedback)

    def close_store(self):
        """
        Closes a store when the pump is stopped
        """
        logging.debug("Closing Cisco Spark")

        try:
            my_bot.dispose()

        except Exception as feedback:
            logging.error(u"Unable to close Cisco Spark")
            logging.exception(feedback)

    def update_summary_usage(self, items=[], region='dd-eu'):
        """
        Not applicable to the Cisco Spark updater
        """
        pass

    def update_detailed_usage(self, items=[], region='dd-eu'):
        """
        Not applicable to the Cisco Spark updater
        """
        pass

    def update_audit_log(self, items=[], region='dd-eu'):
        """
        Not applicable to the Cisco Spark updater
        """
        pass

    def on_servers(self, updates=[], region='dd-eu'):
        """
        Signals the deployment, start or reboot of cloud servers

        :param updates: description of new servers
        :type updates: ``list`` of ``dict``

        :param region: source of the information, e.g., 'dd-eu' or other region
        :type region: ``str``

        """

        count = 0
        for item in updates:
            count += 1

            if item['public_ip'] is None:
                extensions = ''
            else:
                extensions = u"* public IPv4: {}\n".format(item['public_ip'])

            extensions += u"* date: {} UTC\n".format(item['stamp'])
            extensions += u"* actor: {}\n".format(item['actor'])

            update = UPDATE_TEMPLATE.format(
                action=item['action'],
                cpu=item['cpu'],
                disks=', '.join([str(int(x)) for x in item['disks']]),
                extensions=extensions,
                memoryMb=item['memoryMb'],
                name=item['name'],
                OS=item['OS_displayName'],
                private_ip=', '.join(item['private_ips']),
                region=item['region'],
                dc=item['datacenterId'],
            )

            my_bot.say(message=update, markdown=update)

        # report on this batch
        #
        if count > 0:
            logging.info("- triggered {} updates to Cisco Spark for {}".format(
                count, region))
        else:
            logging.info("- nothing to report to Cisco Spark for {}".format(
                region))


