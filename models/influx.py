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
from influxdb import InfluxDBClient


class InfluxdbUpdater(Updater):
    """
    Updates a database
    """

    def use_database(self):
        """
        Opens a database to save data
        """

        self.db = InfluxDBClient(
            self.settings.get('host', 'localhost'),
            self.settings.get('port', 8086),
            self.settings.get('user', 'root'),
            self.settings.get('password', 'root'),
            self.settings.get('database', 'mcp'),
            )
        return self.db

    def reset_database(self):
        """
        Opens a database for points
        """

        self.db = InfluxDBClient(
            self.settings.get('host', 'localhost'),
            self.settings.get('port', 8086),
            self.settings.get('user', 'root'),
            self.settings.get('password', 'root'),
            self.settings.get('database', 'mcp'),
            )
        self.db.drop_database(self.settings.get('database', 'mcp'))
        self.db.create_database(self.settings.get('database', 'mcp'))
        return self.db

    def update_summary_usage(self, items=[], region='dd-eu'):
        """
        Updates summary usage records

        :param items: new items to push to the database
        :type items: ``list`` of ``list``

        :param region: source of the information, e.g., 'dd-eu' or other region
        :type region: ``str``

        """

        measurements = []

        if len(items) > 0:
            headers = items.pop(0)
            logging.debug("- headers: {}".format(headers))

        for item in items:

            if len(item[1]) < 1:
                continue

            measurement = {
                    "measurement": 'Summary usage',
                    "tags": {
                        "region": region,
                        "location": item[1],
                    },
                    "time": item[0],
                    "fields": {
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
                }

#            print measurement

            measurements.append(measurement)

        self.db.write_points(measurements)

        logging.info("- stored {} measurements for {} in influxdb".format(
            len(measurements), region))

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

        measurements = []

        if len(items) > 0:
            headers = items.pop(0)
            logging.debug("- headers: {}".format(headers))

# ['Name', 'UUID', 'Type', 'Location', 'Private IP Address', 'Status', '"user: EUITAAS_Tag"', '"user: Platform Owner"', '"user: Test_Agenda"', 'Start Time', 'End Time', 'Duration (Hours)', 'CPU Type', 'CPU Count', 'RAM (GB)', 'Storage (GB)', 'High Performance Storage (GB)', 'Economy Storage (GB)', 'CPU Hours', 'High Performance CPU Hours', 'RAM Hours', 'Storage Hours', 'High Performance Storage Hours', 'Economy Storage Hours', 'Bandwidth-In (GB)', 'Bandwidth-Out (GB)', 'Subadmin Hours', 'Network Hours', 'Essentials Network Domain Hours', 'Advanced Network Domain Hours', 'VLAN Hours', 'Public IP Hours', 'Cloud Files Account Hours', 'Cloud Storage (GB)']

        for item in items:

            if len(item[2]) < 1:  # no type (e.g., total line)
                continue

            if item[ headers.index('CPU Count') ] > '0':  # with CPU
                measurement = {
                        "measurement": item[2],
                        "tags": {
                            "name": item[0],
                            "UUID": item[1],
                            "region": region,
                            "location": item[3],
                            "private_ip": item[4],
                            "status": item[5],
                        },
                        "time": item[ headers.index('End Time') ],
                        "fields": {
                            "duration": float(item[ headers.index('Duration (Hours)') ]),
                            "CPU": int(item[ headers.index('CPU Count') ]),
                            "RAM": int(item[ headers.index('RAM (GB)') ]),
                            "Storage": int(item[ headers.index('Storage (GB)') ]),
                            "HP Storage": int(item[ headers.index('High Performance Storage (GB)') ]),
                            "Eco Storage": int(item[ headers.index('Economy Storage (GB)') ]),
                        }
                    }

            elif len(item[3]) > 0: # at some location
                measurement = {
                        "measurement": item[2],
                        "tags": {
                            "name": item[0],
                            "UUID": item[1],
                            "region": region,
                            "location": item[3],
                        },
                        "time": item[ headers.index('End Time') ],
                        "fields": {
                            "duration": float(item[ headers.index('Duration (Hours)') ]),
                        }
                    }

            else: # global
                measurement = {
                        "measurement": item[2],
                        "tags": {
                            "name": item[0],
                            "UUID": item[1],
                        },
                        "time": item[ headers.index('End Time') ],
                        "fields": {
                            "duration": float(item[ headers.index('Duration (Hours)') ]),
                        }
                    }

#            print measurement

            measurements.append(measurement)

        self.db.write_points(measurements)

        logging.info("- stored {} measurements for {} in influxdb".format(
            len(measurements), region))

    def update_audit_log(self, items=[], region='dd-eu'):
        """
        Updates audit log records

        :param items: new items to push to the database
        :type items: ``list`` of ``list``

        :param region: source of the information, e.g., 'dd-eu' or other region
        :type region: ``str``

        """

        measurements = []

        if len(items) > 0:
            headers = items.pop(0)
            logging.debug("- headers: {}".format(headers))

        for item in items:

            measurement = {
                    "measurement": 'Audit log',
                    "tags": {
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
                    },
                    "time": item[1],
                    "fields": {
                        "API Call": 1,
                    }
                }

#            print measurement

            measurements.append(measurement)

        self.db.write_points(measurements)

        logging.info("- stored {} measurements for {} in influxdb".format(
            len(measurements), region))
