import unittest
import os

from configuration import ConfigObject


class ConfigurationTestCase(unittest.TestCase):
    def setUp(self):
        testpath = os.path.realpath(__file__)
        self.workdirectory = os.path.dirname(testpath)

    def test_DeletionOfFolder(self):
        config = ConfigObject("", "", "", "", "", "", self.workdirectory, "", "", "", "", "")
        self.assertTrue(os.path.exists(config.logFolder))
        config.deletelogfolder()
        self.assertFalse(os.path.exists(config.logFolder))
