import unittest
import os
from unittest.mock import patch

import migration
from configuration import Builder


class MigrationTestCase(unittest.TestCase):
    def setUp(self):
        self.rootfolder = os.path.dirname(os.path.realpath(__file__))

    @patch('migration.Initializer')
    @patch('migration.RTCInitializer')
    @patch('migration.os')
    @patch('configuration.shutil')
    def testDeletionOfLogFolderOnInitalization(self, shutil_mock, os_mock, rtc_initializer_mock, git_initializer_mock):
        config = Builder().setrootfolder(self.rootfolder).build()
        anylogpath = config.getlogpath("testDeletionOfLogFolderOnInitalization")
        os_mock.path.exists.return_value = False

        migration.initialize(config)

        expectedlogfolder = self.rootfolder + os.sep + "Logs"
        shutil_mock.rmtree.assert_called_once_with(expectedlogfolder)
