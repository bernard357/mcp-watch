#!/usr/bin/env python

from datetime import date, datetime, timedelta
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

from pump import Pump
from models.base import Updater
from models.influx import InfluxdbUpdater

class PumpTests(unittest.TestCase):

    def test_config(self):

        print('***** Test config ***')

        import config

        try:
            settings = config.pump
        except:
            settings = {}

        pump = Pump(settings)


    def test_settings(self):

        print('***** Test settings ***')

        pump = Pump()
        self.assertEqual(pump.settings.get('unknown'), None)
        self.assertEqual(pump.settings.get('unknown', 'expected'), 'expected')

        self.assertEqual(pump.get_regions(),
                         ('dd-af', 'dd-ap', 'dd-au', 'dd-eu', 'dd-na'))

        settings = {
            'MCP_USER': 'foo.bar',
            'MCP_PASSWORD': 'WhatsUpDoc',
            'regions': ['dd-eu', 'dd-na'],
            }
        pump = Pump(settings)
        self.assertEqual(pump.settings.get('MCP_USER'), 'foo.bar')
        self.assertEqual(pump.settings.get('MCP_PASSWORD'), 'WhatsUpDoc')
        self.assertEqual(pump.get_regions(),
                         ['dd-eu', 'dd-na'])
        self.assertEqual(pump.settings.get('unknown'), None)


    @vcr.use_cassette(
        os.path.abspath(os.path.dirname(__file__))+'/fixtures/mcp.yaml')
    def test_mcp(self):

        pump = Pump()
        pump.set_drivers()

        someday = date(2016, 11, 30)

        print('***** Test fetch summary usage ***')

        items = pump.fetch_summary_usage(on=someday)
        items.pop(0)

        name = 'fixtures/summary-usage-dd-eu.yaml'
        lname = os.path.abspath(os.path.dirname(__file__))+'/'+name
        if os.path.isfile(lname):
            with open(lname, 'r') as handle:
                expected = yaml.load(handle)
                expected.pop()
                self.assertEqual(items, expected)

        else:
            with open(lname, 'w') as handle:
                yaml.dump(items, handle)

        print('***** Test fetch detailed usage ***')

        items = pump.fetch_detailed_usage(on=someday)
        items.pop(0)

        name = 'fixtures/detailed-usage-dd-eu.yaml'
        lname = os.path.abspath(os.path.dirname(__file__))+'/'+name
        if os.path.isfile(lname):
            with open(lname, 'r') as handle:
                expected = yaml.load(handle)
                self.assertEqual(items[100:200], expected)

        else:
            with open(lname, 'w') as handle:
                yaml.dump(items[100:200], handle)

        print('***** Test pull ***')

        pump.pull(on=someday)

    def test_update(self):

        pump = Pump()
        pump.set_drivers()

        influx = InfluxdbUpdater()
        pump.add_updater(influx)

        print('***** Test update summary usage ***')

        with mock.patch.object(influx,
                               'update_summary_usage',
                               return_value=None) as mocked:

            name = 'fixtures/summary-usage-dd-eu.yaml'
            lname = os.path.abspath(os.path.dirname(__file__))+'/'+name
            if os.path.isfile(lname):
                with open(lname, 'r') as handle:
                    items = yaml.load(handle)
                    pump.update_summary_usage(items)

                    mocked.assert_called_once_with(items, 'dd-eu')

        print('***** Test update detailed usage ***')

        with mock.patch.object(influx,
                               'update_detailed_usage',
                               return_value=None) as mocked:

            name = 'fixtures/detailed-usage-dd-eu.yaml'
            lname = os.path.abspath(os.path.dirname(__file__))+'/'+name
            if os.path.isfile(lname):
                with open(lname, 'r') as handle:
                    items = yaml.load(handle)
                    pump.update_detailed_usage(items)

                    mocked.assert_called_once_with(items, 'dd-eu')

if __name__ == '__main__':
    logging.getLogger('').setLevel(logging.DEBUG)
    sys.exit(unittest.main())
