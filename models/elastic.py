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
from elasticsearch import Elasticsearch, ConnectionError


class ElasticUpdater(Updater):
    """
    Updates a database
    """

    def use_store(self):
        """
        Opens a database to save data
        """

        logging.info('Using Elasticsearch database')

        self.db = Elasticsearch(
            [self.settings.get('host', 'localhost:9200')],
            )

        try:
            self.db.indices.create(index='mcp-watch', ignore=400) # may exist
        except ConnectionError as feedback:
            logging.error('- unable to connect')
            raise

        return self.db

    def reset_store(self):
        """
        Opens a database for points
        """

        logging.info('Resetting Elasticsearch database')

        self.db = Elasticsearch(
            [self.settings.get('host', 'localhost:9200')],
            )

        try:
            self.db.indices.create(index='mcp-watch', ignore=400) # may exist
        except ConnectionError as feedback:
            logging.error('- unable to connect')
            raise

        return self.db

    def update_summary_usage(self, items=[], region='dd-eu'):
        """
        Updates summary usage records

        :param items: new items to push to the database
        :type items: ``list`` of ``list``

        :param region: source of the information, e.g., 'dd-eu' or other region
        :type region: ``str``

        """

        if len(items) > 0:
            headers = items.pop(0)
            logging.debug("- headers: {}".format(headers))

        updated = 0
        for item in items:

            if len(item[1]) < 1:
                continue

            measurement = {
                    "measurement": 'Summary usage',
                    "region": region,
                    "location": item[1],
                    "stamp": item[0],
                    "CPU Hours": int(item[2]),
                    "High Performance CPU Hours": int(item[3]),
                    "RAM Hours": int(item[4]),
                    "Storage Hours": int(item[5]),
                    "High Performance Storage Hours": int(item[6]),
                    "Economy Storage Hours": int(item[7]),
                    "Bandwidth In": int(item[8]),
                    "Bandwidth Out": int(item[9]),
                    "Sub-Admin Hours": float(item[10]),
                    "Network Hours": float(item[11]),
                    "Essentials Network Domain Hours": int(item[12]),
                    "Advanced Network Domain Hours": int(item[13]),
                    "VLAN Hours": int(item[14]),
                    "Public IP Hours": int(item[15]),
                    "Cloud Files Account Hours": float(item[16]),
                    "Cloud Files (GB Days)": int(item[17]),
                    "Software Units": int(item[18]),
                    "Essentials Client Days": int(item[19]),
                    "Advanced Client Days": int(item[20]),
                    "Enterprise Client Days": int(item[21]),
                    "Essentials Backups (GB)": int(item[22]),
                    "Advanced Backups (GB)": int(item[23]),
                    "Enterprise Backups (GB)": int(item[24]),
                    "Essentials Monitoring Hours": int(item[25]),
                    "Advanced Monitoring Hours": int(item[26]),
                }

            try:
                result = self.db.index(index="mcp-watch",
                                       doc_type='summary',
                                       body=measurement)
                updated += 1

            except Exception as feedback:
                logging.error('- unable to update elasticsearch')
                logging.debug(feedback)
                return

        if updated:
            logging.info(
                "- stored {} measurements for {} in elasticsearch".format(
                    updated, region))

    def update_detailed_usage(self, items=[], region='dd-eu'):
        """
        Updates detailed usage records

        :param items: new items to push to the database
        :type items: ``list`` of ``list``

        :param region: source of the information, e.g., 'dd-eu' or other region
        :type region: ``str``

        Note that headers can change dynamically, so it is important to map
        them appropriately.

        """

        if len(items) > 0:
            headers = items.pop(0)
            logging.debug("- headers: {}".format(headers))

        updated = 0
        for item in items:

            if len(item[2]) < 1:  # no type (e.g., total line)
                continue

            if item[ headers.index('CPU Count') ] > '0':  # with CPU
                measurement = {
                        "measurement": item[2],
                        "name": item[0],
                        "UUID": item[1],
                        "region": region,
                        "location": item[3],
                        "private_ip": item[4],
                        "status": item[5],
                        "stamp": item[ headers.index('End Time') ],
                        "duration": float(item[ headers.index('Duration (Hours)') ]),
                        "CPU": int(item[ headers.index('CPU Count') ]),
                        "RAM": int(item[ headers.index('RAM (GB)') ]),
                        "Storage": int(item[ headers.index('Storage (GB)') ]),
                        "HP Storage": int(item[ headers.index('High Performance Storage (GB)') ]),
                        "Eco Storage": int(item[ headers.index('Economy Storage (GB)') ]),
                    }
                doc_type = 'detailed'

            elif len(item[3]) > 0: # at some location
                measurement = {
                        "measurement": item[2],
                        "name": item[0],
                        "UUID": item[1],
                        "region": region,
                        "location": item[3],
                        "stamp": item[ headers.index('End Time') ],
                        "duration": float(item[ headers.index('Duration (Hours)') ]),
                    }
                doc_type = 'detailed-location'

            else: # global
                measurement = {
                        "measurement": item[2],
                        "name": item[0],
                        "UUID": item[1],
                        "stamp": item[ headers.index('End Time') ],
                        "duration": float(item[ headers.index('Duration (Hours)') ]),
                    }
                doc_type = 'detailed-global'

            try:
                result = self.db.index(index="mcp-watch",
                                       doc_type=doc_type,
                                       body=measurement)
                updated += 1

            except Exception as feedback:
                logging.error('- unable to update elasticsearch')
                logging.debug(feedback)
                return

        if updated:
            logging.info(
                "- stored {} measurements for {} in elasticsearch".format(
                    updated, region))

    def update_audit_log(self, items=[], region='dd-eu'):
        """
        Updates audit log records

        :param items: new items to push to the database
        :type items: ``list`` of ``list``

        :param region: source of the information, e.g., 'dd-eu' or other region
        :type region: ``str``

        """

        if len(items) > 0:
            headers = items.pop(0)
            logging.debug("- headers: {}".format(headers))

        updated = 0
        for item in items:

            measurement = {
                    "measurement": 'Audit log',
                    "region": region,
                    "caller": item[2].lower().replace('.', ' '),
                    "department": item[3],
                    "custom-1": item[4],
                    "custom-2": item[5],
                    "type": item[6],
                    "name": item[7],
                    "action": item[8],
                    "details": item[9],
                    "status": item[10],
                    "stamp": item[1],
                }

            try:
                result = self.db.index(index="mcp-watch",
                                       doc_type='audit',
                                       body=measurement)
                updated += 1

            except Exception as feedback:
                logging.error('- unable to update elasticsearch')
                logging.debug(feedback)
                return

        if updated:
            logging.info(
                "- stored {} measurements for {} in elasticsearch".format(
                    updated, region))

    def on_servers(self, updates=[], region='dd-eu'):
        """
        Signals the deployment, start or reboot of cloud servers

        :param updates: description of new servers
        :type updates: ``list`` of ``dict``

        :param region: source of the information, e.g., 'dd-eu' or other region
        :type region: ``str``

        """

        updated = 0
        for item in updates:
            updated += 1

            try:
                result = self.db.index(index="mcp-watch",
                                       doc_type='server',
                                       body=item)

            except Exception as feedback:
                logging.error('- unable to update elasticsearch')
                logging.debug(feedback)
                return

        if updated:
            logging.info(
                "- triggered {} updated to elasticsearch for {}".format(
                    updated, region))

        else:
            logging.info("- nothing to report to elasticsearch for {}".format(
                region))

