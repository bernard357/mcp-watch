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
from models.files import FilesUpdater
from models.influx import InfluxdbUpdater

import config

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
            updater.update_summary_usage()

        with self.assertRaises(NotImplementedError):
            updater.update_detailed_usage()

        with self.assertRaises(NotImplementedError):
            updater.update_audit_log()

    def test_files(self):

        print('***** Test files ***')

        updater = FilesUpdater({'a': 'b'})
        self.assertEqual(updater.settings['a'], 'b')

        try:
            settings = config.files
        except:
            settings = {}

        updater = FilesUpdater(settings)

        updater.use_database()

        updater.reset_database()

        updater.update_summary_usage()

        updater.update_detailed_usage()

        updater.update_audit_log()

    def test_influxdb(self):

        print('***** Test influxdb ***')

        updater = InfluxdbUpdater({'a': 'b'})
        self.assertEqual(updater.settings['a'], 'b')

        try:
            settings = config.influxdb
        except:
            settings = {}

        updater = InfluxdbUpdater(settings)

if __name__ == '__main__':
    logging.getLogger('').setLevel(logging.DEBUG)
    sys.exit(unittest.main())
