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

from models.base import Updater
from models.influx import InfluxdbUpdater

class ModelsTests(unittest.TestCase):

    def test_updater(self):

        print('***** Test updater ***')

        updater = Updater({'a': 'b'})
        self.assertEqual(updater.settings['a'], 'b')

        with self.assertRaises(NotImplementedError):
            updater.use_database()

        with self.assertRaises(NotImplementedError):
            updater.reset_database()

        with self.assertRaises(NotImplementedError):
            updater.update_detailed_usage()

    def test_influxdb(self):

        print('***** Test influxdb ***')

        updater = InfluxdbUpdater({'a': 'b'})
        self.assertEqual(updater.settings['a'], 'b')

if __name__ == '__main__':
    logging.getLogger('').setLevel(logging.DEBUG)
    sys.exit(unittest.main())
