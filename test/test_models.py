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
from models.elastic import ElasticUpdater
from models.influx import InfluxdbUpdater
from models.qualys import QualysUpdater
from models.spark import SparkUpdater

import config

class ModelsTests(unittest.TestCase):

    def test_updater(self):

        print('***** Test updater ***')

        updater = Updater({'a': 'b'})
        self.assertEqual(updater.settings['a'], 'b')

        updater.use_store()
        updater.reset_store()
        updater.update_summary_usage()
        updater.update_detailed_usage()
        updater.update_audit_log()
        updater.on_servers()
        updater.close_store()

    def test_files(self):

        print('***** Test files ***')

        updater = FilesUpdater({'a': 'b'})
        self.assertEqual(updater.settings['a'], 'b')

        self.assertEqual(updater.get_summary_usage_file(),
                         './logs/summary_usage.log')

        self.assertEqual(updater.get_detailed_usage_file(),
                         './logs/detailed_usage.log')

        self.assertEqual(updater.get_audit_log_file(),
                         './logs/audit_log.log')

        try:
            settings = config.files
        except:
            settings = {}

        updater = FilesUpdater(settings)

        updater.use_store()

        updater.reset_store()

        updater.update_summary_usage()

        updater.update_detailed_usage()

        updater.update_audit_log()

    def test_elastic(self):

        print('***** Test elastic ***')

        updater = ElasticUpdater({'a': 'b'})
        self.assertEqual(updater.settings['a'], 'b')

        try:
            settings = config.elastic
        except:
            settings = {}

        updater = ElasticUpdater(settings)

    def test_influxdb(self):

        print('***** Test influxdb ***')

        updater = InfluxdbUpdater({'a': 'b'})
        self.assertEqual(updater.settings['a'], 'b')

        try:
            settings = config.influxdb
        except:
            settings = {}

        updater = InfluxdbUpdater(settings)

    def test_qualys(self):

        print('***** Test qualys ***')

        updater = QualysUpdater({'a': 'b'})
        self.assertEqual(updater.settings['a'], 'b')

        try:
            settings = config.qualys
        except:
            settings = {}

        updater = QualysUpdater(settings)

    def test_spark(self):

        print('***** Test spark ***')

        updater = SparkUpdater({'a': 'b'})
        self.assertEqual(updater.settings['a'], 'b')

        try:
            settings = config.spark
        except:
            settings = {}

        updater = SparkUpdater(settings)

if __name__ == '__main__':
    logging.getLogger('').setLevel(logging.DEBUG)
    sys.exit(unittest.main())
