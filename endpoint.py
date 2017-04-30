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

import colorlog
from datetime import date, datetime, timedelta
import logging
import os
import re
import requests
from six import string_types
import socket
import string
import sys
import time
import xmltodict


class Endpoint(object):
    """
    Implements an API endpoint for the MCP
    """

    HOSTS = {
        'dd-af': 'https://api-mea.dimensiondata.com',
        'dd-ap': 'https://api-ap.dimensiondata.com',
        'dd-au': 'https://api-au.dimensiondata.com',
        'dd-eu': 'https://api-eu.dimensiondata.com',
        'dd-na': 'https://api-na.dimensiondata.com',
    }

    def __init__(self, key, secret, region, endpoint=None, orgId=None):

        assert key not in (None, '')
        self.key = key

        assert secret not in (None, '')
        self.secret = secret

        assert region not in (None, '')
        self.region = region

        if endpoint is None:   # allow for endpoint injection
            endpoint = self.HOSTS[region]

        if orgId is None:  # allow for orgId injection
            r = requests.get(endpoint+'/oec/0.9/myaccount',
                             auth=(self.key, self.secret))
            orgId_re = r":orgId>([a-f0-9\-]+)</"
            match = re.search(orgId_re, r.text)
            orgId = match.group(1)

        self.url_v1 = endpoint+'/oec/0.9/'+orgId
        self.url_v2 = endpoint+'/caas/2.5/'+orgId

    def summary_usage_report(self, start_date, end_date):
        """
        Fetches smmary usage data from the API

        :param start_date: first day of the report
        :type start_date: str

        :param end_date: days after last day of the report
        :type end_date: str

        :return: report records
        :rtype: list of list
        """

        url_template = self.url_v1+'/report/usage?startDate={}&endDate={}'
        url = url_template.format(start_date, end_date)
        r = requests.get(url, auth=(self.key, self.secret))
        lines = str.splitlines(str(r.text))
        return [line.split(',') for line in lines]

    def detailed_usage_report(self, start_date, end_date):
        """
        Fetches detailed usage data from the API

        :param start_date: first day of the report
        :type start_date: str

        :param end_date: days after last day of the report
        :type end_date: str

        :return: report records
        :rtype: list of list
        """


        url_template = self.url_v1+'/report/usageDetailed?startDate={}&endDate={}'
        url = url_template.format(start_date, end_date)
        r = requests.get(url, auth=(self.key, self.secret))
        lines = str.splitlines(str(r.text))
        return [line.split(',') for line in lines]

    def audit_log_report(self, start_date, end_date):
        """
        Fetches audit data from the API

        :param start_date: first day of the report
        :type start_date: str

        :param end_date: days after last day of the report
        :type end_date: str

        :return: report records
        :rtype: list of list
        """


        url_template = self.url_v1+'/auditlog?startDate={}&endDate={}'
        url = url_template.format(start_date, end_date)
        r = requests.get(url, auth=(self.key, self.secret))
        lines = str.splitlines(str(r.text))
        #print(lines)
        return [line.split(',') for line in lines]

    def get_node_by_id(self, id=None, body=None):
        """
        Retrieves node details from the API

        :param id: unique id of the target node
        :type id: str

        :param body: for test by data injection
        :type body: str

        :return: attributes of the node
        :rtype: dict or None

        """
        assert id is None or body is None
        assert id is not None or body is not None

        if body:  # allow for test injection
            text = body

        else:
            url = self.url_v2+'/server/server/'+id
            r = requests.get(url, auth=(self.key, self.secret))

            if r.status_code != 200:
                logging.error(u"Status: {}".format(r.status_code))
                return None

            text = r.text

        try:
            #print(text)
            item = xmltodict.parse(text)['server']
        except:
            logging.error(u"Response: {}".format(text))
            raise RuntimeError("Unable to get node from API")

        #print(item.keys())

        node = {}
        node['id'] = item['@id']
        node['name'] = item['name']
        node['description'] = item.get('description', '')
        node['private_ips'] = [ item['networkInfo']['primaryNic']['@privateIpv4'] ]
        node['datacenterId'] = item['@datacenterId']
        node['cpu'] = item['cpu']['@count']
        node['memoryMb'] = int(item['memoryGb'])*1024
        node['networkDomainId'] = item['networkInfo']['@networkDomainId']
        node['ipv6'] = item['networkInfo']['primaryNic']['@ipv6']
        node['vlanId'] = item['networkInfo']['primaryNic']['@vlanId']
        node['vlanName'] = item['networkInfo']['primaryNic']['@vlanName']
        node['networkAdapter'] = item['networkInfo']['primaryNic']['@networkAdapter']
        try:
            node['macAddress'] = item['networkInfo']['primaryNic']['@macAddress']
        except:
            pass
        node['sourceImageId'] = item['sourceImageId']
        node['deployed'] = item['deployed']
        node['deployedTime'] = item.get('createTime')
        node['started'] = item['started']
        node['state'] = item['state']
        node['OS_id'] = item['guest']['operatingSystem']['@id']
        node['OS_displayName'] = item['guest']['operatingSystem']['@displayName']
        node['OS_type'] = item['guest']['operatingSystem']['@family']
        node['virtualHardware'] = item['virtualHardware']['@version']
        node['disks'] = []

        if not isinstance(item['scsiController']['disk'], list):
            item['scsiController']['disk'] = [item['scsiController']['disk']]

        for disk in item['scsiController']['disk']:
            node['disks'].append(disk['@sizeGb'])

        # hack - the API does not report public ipv4 accurately
        # so we look at the NAT rules to find public IP address

        try:
            assert body is None

            url_template = self.url_v2+'/network/natRule?networkDomainId={}&internalIp={}'
            url = url_template.format(node['networkDomainId'], node['private_ips'][0])
            r = requests.get(url, auth=(self.key, self.secret))
            #print(r.text)
            node['public_ip'] = xmltodict.parse(r.text)['natRules']['natRule']['externalIp']

        except:
            node['public_ip'] = None

        return node
