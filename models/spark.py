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

#from shellbot import ShellBot


UPDATE_TEMPLATE = """{region } {action} {name}:
* {OS}
* CPU: {cpu}
* RAM: {memoryMb} (MB)
* disks: {disks} (GB)
* private IPv4: {private_ip} (GB)
{extensions}"""


class dummy(object):
    def configure(self, *args, **kwargs):
        logging.debug('configured')

    def say(self, *args, **kwargs):
        logging.debug('say something')

my_bot = dummy()

#ShellBot()


class SparkUpdater(Updater):
    """
    Interacts with Cisco Spark service

    Token is expected in ``CHAT_TOKEN``.

    """

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

    def on_active_servers(self, items=[], region='dd-eu'):
        """
        Signals the deployment, start or reboot of cloud servers

        :param items: description of new servers
        :type items: ``list`` of ``dict``

        :param region: source of the information, e.g., 'dd-eu' or other region
        :type region: ``str``

        """

        # activate a bot on first update
        #
        try:
            assert my_bot.has_been_configured == True
        except:
            my_bot.has_been_configured = True
            os.environ['CHAT_ROOM_TITLE'] = self.get('room')
            os.environ['CHAT_ROOM_MODERATORS'] = self.get('moderators')
            my_bot.configure()

        # look at every server that have been activated
        #
        count = 0
        for item in items:
            count += 1

            if item['public_ip'] is None:
                extension = ''
            else:
                extension = u"* public IPv4: {}\n".format(item['public_ip'])

            update = UPDATE_TEMPLATE.format(
                action=item['action'],
                cpu=item['cpu'],
                disks=item['disks'],
                extension=extension,
                memoryMb=item['memoryMb'],
                name=item['name'],
                OS=item['OS_displayName'],
                private_ip=item['private_ip'],
                region=item['region'],
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


