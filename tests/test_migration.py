import unittest
import os
from unittest.mock import patch

import migration
from configuration import Builder
import configuration
from tests import testhelper


class MigrationTestCase(unittest.TestCase):
    def setUp(self):
        self.rootfolder = os.path.dirname(os.path.realpath(__file__))

    @patch('migration.Commiter')
    @patch('migration.Initializer')
    @patch('migration.RTCInitializer')
    @patch('migration.os')
    @patch('configuration.shutil')
    def testDeletionOfLogFolderOnInitalization(self, shutil_mock, os_mock, rtc_initializer_mock, git_initializer_mock,
                                               git_comitter_mock):
        config = Builder().setrootfolder(self.rootfolder).build()
        anylogpath = config.getlogpath("testDeletionOfLogFolderOnInitalization")
        os_mock.path.exists.return_value = False
        configuration.config = config

        migration.initialize()

        expectedlogfolder = self.rootfolder + os.sep + "Logs"
        shutil_mock.rmtree.assert_called_once_with(expectedlogfolder)

    def testExistRepo_Exists_ShouldReturnTrue(self):
        with testhelper.createrepo(folderprefix="test_migration"):
            self.assertTrue(migration.existsrepo())

    def testExistRepo_DoesntExist_ShouldReturnFalse(self):
        configuration.config = Builder().setworkdirectory(self.rootfolder).setgitreponame("test.git").build()
        self.assertFalse(migration.existsrepo())
