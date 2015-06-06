import unittest
import os
from unittest.mock import patch

import migration
from configuration import ConfigObject


class MigrationTestCase(unittest.TestCase):
    workdirectory = ""

    def setUp(self):
        testpath = os.path.realpath(__file__)
        self.workdirectory = os.path.dirname(testpath)

    @patch('migration.Initializer')
    @patch('migration.RTCInitializer')
    @patch('migration.os')
    @patch('migration.shutil')
    def testDeletionOfLogFolderOnInitalization(self, shutil_mock, os_mock, rtc_initializer_mock, git_initializer_mock):
        config = ConfigObject("", "", "", "", "", "", self.workdirectory, "", "", "", "", "")
        os_mock.path.exists.return_value = False

        migration.initialize(config)

        expectedlogfolder = self.workdirectory + os.sep + "Logs" + os.sep
        shutil_mock.rmtree.assert_called_once_with(expectedlogfolder)
