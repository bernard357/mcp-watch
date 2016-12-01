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

    def update_summary_usage(self, items, region='dd-eu'):
        """
        Updates summary usage records

        :param items: new items to push to the database
        :type items: ``list`` of ``list``

        :param region: source of the information, e.g., 'dd-eu' or other region
        :type region: ``str``

        """

        measurements = []

        for item in items:

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

        logging.info("Found {} measurements for {}".format(
            len(measurements), region))

        self.db.write_points(measurements)

    def update_detailed_usage(self, items, region='dd-eu'):
        """
        Updates detailed usage records

        :param items: new items to push to the database
        :type items: ``list`` of ``list``

        :param region: source of the information, e.g., 'dd-eu' or other region
        :type region: ``str``

        """

        measurements = []

        for item in items:

            if len(item[2]) < 1:  # no type (e.g., total line)
                continue

            if item[13] > '0':  # with CPU
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
                        "time": item[10],
                        "fields": {
                            "duration": float(item[11]),
                            "CPU": int(item[13]),
                            "RAM": int(item[14]),
                            "Storage": int(item[15]),
                            "HP Storage": int(item[16]),
                            "Eco Storage": int(item[17]),
                        }
                    }

            elif len(item[3]) > 0:
                measurement = {
                        "measurement": item[2],
                        "tags": {
                            "name": item[0],
                            "UUID": item[1],
                            "region": region,
                            "location": item[3],
                        },
                        "time": item[10],
                        "fields": {
                            "duration": float(item[11]),
                        }
                    }

            else:
                measurement = {
                        "measurement": item[2],
                        "tags": {
                            "name": item[0],
                            "UUID": item[1],
                        },
                        "time": item[10],
                        "fields": {
                            "duration": float(item[11]),
                        }
                    }

#            print measurement

            measurements.append(measurement)

        logging.info("Found {} measurements for {}".format(
            len(measurements), region))

        self.db.write_points(measurements)

