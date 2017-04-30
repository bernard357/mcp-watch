#!/usr/bin/env python

import unittest
import logging
import os
import random
import sys
import time
import mock
from requests import ConnectionError
import base64
import yaml
import vcr

sys.path.insert(0, os.path.abspath('..'))

from endpoint import Endpoint

import config

node_1_body = """<?xml version="1.0" encoding="UTF-8"?><server xmlns="urn:didata.com:api:cloud:types" id="88c42718-727f-4d9f-aa1f-6eb3be9fd9d1" datacenterId="EU6"><name>Web2</name><cpu count="1" speed="STANDARD" coresPerSocket="1"/><memoryGb>1</memoryGb><scsiController state="NORMAL" id="3e01c1b0-e45a-42c2-bdd9-775910e255a4" adapterType="VMWARE_PARAVIRTUAL" key="1000" busNumber="0"><disk state="NORMAL" id="149be0a7-0673-430d-824a-c2dfd3f09b9f" sizeGb="20" speed="STANDARD" scsiId="0"/></scsiController><networkInfo networkDomainId="88fc5170-8ca8-421a-abc5-1c9758f76288"><primaryNic id="abbd2fe7-15c9-4c70-b039-d4cd2fd5a181" privateIpv4="10.0.0.8" ipv6="2a00:47c0:111:1379:5a73:d8b5:7440:ad47" vlanId="6939aeb0-3b14-4854-be6a-9b7691c001b8" vlanName="Web" networkAdapter="VMXNET3" macAddress="00:50:56:bb:00:1b" key="4000" state="NORMAL"/></networkInfo><sourceImageId>56eb0b7c-15a7-4b63-b373-05b962e37554</sourceImageId><createTime>2017-04-28T20:00:44.000Z</createTime><deployed>true</deployed><started>false</started><state>NORMAL</state><guest osCustomization="true"><operatingSystem id="REDHAT764" displayName="REDHAT7/64" family="UNIX"/><vmTools type="VMWARE_TOOLS" versionStatus="CURRENT" runningStatus="NOT_RUNNING" apiVersion="9356"/></guest><virtualHardware version="vmx-10" upToDate="true"/></server>"""

node_1_dict = {
    'macAddress': u'00:50:56:bb:00:1b',
    'public_ip': None,
    'id': u'88c42718-727f-4d9f-aa1f-6eb3be9fd9d1',
    'datacenterId': u'EU6',
    'deployedTime': u'2017-04-28T20:00:44.000Z',
    'memoryMb': 1024,
    'state': u'NORMAL',
    'OS_id': u'REDHAT764',
    'ipv6': u'2a00:47c0:111:1379:5a73:d8b5:7440:ad47',
    'networkAdapter': u'VMXNET3',
    'networkDomainId': u'88fc5170-8ca8-421a-abc5-1c9758f76288',
    'description': '',
    'started': u'false',
    'vlanId': u'6939aeb0-3b14-4854-be6a-9b7691c001b8',
    'sourceImageId': u'56eb0b7c-15a7-4b63-b373-05b962e37554',
    'deployed': u'true',
    'private_ips': [u'10.0.0.8'],
    'OS_displayName': u'REDHAT7/64',
    'name': u'Web2',
    'disks': [u'20'],
    'vlanName': u'Web',
    'OS_type': u'UNIX',
    'cpu': u'1',
    'virtualHardware': u'vmx-10'
}

node_2_body = """<?xml version="1.0" encoding="UTF-8"?><server xmlns="urn:didata.com:api:cloud:types" id="c206db43-4ba1-4ad7-ba6e-f79523c2d103" datacenterId="EU6"><name>master-01</name><description>Hadoop master node #plumbery</description><cpu count="4" speed="STANDARD" coresPerSocket="1"/><memoryGb>12</memoryGb><scsiController state="NORMAL" id="7730ea3a-db47-4b84-a9e3-2d894786f1ba" adapterType="LSI_LOGIC_PARALLEL" key="1000" busNumber="0"><disk state="NORMAL" id="3a504906-8e6b-4a8e-bb3e-c81a6f7141bf" sizeGb="10" speed="STANDARD" scsiId="0"/><disk state="NORMAL" id="7785465a-bbc9-4c01-aa68-b9e2fd120a02" sizeGb="200" speed="STANDARD" scsiId="1"/></scsiController><networkInfo networkDomainId="b31814c7-2787-4799-b285-40c2f8384077"><primaryNic id="d99c2092-5f3e-4176-8485-32406333d864" privateIpv4="10.60.0.6" ipv6="2a00:47c0:111:1108:20c6:f4eb:2527:2326" vlanId="73e0c787-11a3-49c2-b2c1-1d82cd1e0291" vlanName="HadoopClusterNetwork" networkAdapter="VMXNET3" macAddress="00:50:56:bb:17:68" key="4000" state="NORMAL"/></networkInfo><monitoring monitoringId="38995" servicePlan="ESSENTIALS" state="NORMAL"/><sourceImageId>6b2c51ec-cc9e-42b7-985b-b6ec9148c16d</sourceImageId><createTime>2017-04-28T09:57:06.000Z</createTime><deployed>true</deployed><started>true</started><state>NORMAL</state><guest osCustomization="true"><operatingSystem id="UBUNTU1464" displayName="UBUNTU14/64" family="UNIX"/><vmTools type="VMWARE_TOOLS" versionStatus="CURRENT" runningStatus="RUNNING" apiVersion="9356"/></guest><virtualHardware version="vmx-10" upToDate="true"/></server>"""


node_2_dict = {
    'macAddress': u'00:50:56:bb:17:68',
    'public_ip': None,
    'id': u'c206db43-4ba1-4ad7-ba6e-f79523c2d103',
    'datacenterId': u'EU6',
    'deployedTime': u'2017-04-28T09:57:06.000Z',
    'memoryMb': 12288,
    'state': u'NORMAL',
    'OS_id': u'UBUNTU1464',
    'ipv6': u'2a00:47c0:111:1108:20c6:f4eb:2527:2326',
    'networkAdapter': u'VMXNET3',
    'networkDomainId': u'b31814c7-2787-4799-b285-40c2f8384077',
    'description': u'Hadoop master node #plumbery',
    'started': u'true',
    'vlanId': u'73e0c787-11a3-49c2-b2c1-1d82cd1e0291',
    'sourceImageId': u'6b2c51ec-cc9e-42b7-985b-b6ec9148c16d',
    'deployed': u'true',
    'private_ips': [u'10.60.0.6'],
    'OS_displayName': u'UBUNTU14/64',
    'name': u'master-01',
    'disks': [u'10', u'200'],
    'vlanName': u'HadoopClusterNetwork',
    'OS_type': u'UNIX',
    'cpu': u'4',
    'virtualHardware': u'vmx-10'
}

class EndpointTests(unittest.TestCase):

    def test_node(self):

        print('***** Test get_node_by_id ***')

        handle = Endpoint(key='k', secret='s', region='dd-eu', orgId='*org')

        node = handle.get_node_by_id(body=node_1_body)
        self.assertEqual(node, node_1_dict)

        node = handle.get_node_by_id(body=node_2_body)
        self.assertEqual(node, node_2_dict)

if __name__ == '__main__':
    logging.getLogger('').setLevel(logging.DEBUG)
    sys.exit(unittest.main())
