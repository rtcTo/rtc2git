import unittest
import os

from configuration import ConfigObject


class ConfigurationTestCase(unittest.TestCase):
    def setUp(self):
        testpath = os.path.realpath(__file__)
        self.workdirectory = os.path.dirname(testpath)

    def test_DeletionOfFolder(self):
        config = ConfigObject("", "", "", "", "", "", self.workdirectory, "", "", "", "", "")
        samplepath = os.path.dirname(config.getlogpath("anyPath"))
        self.assertTrue(os.path.exists(samplepath))
        config.deletelogfolder()
        self.assertFalse(os.path.exists(samplepath))

    def test_ReaddingLogFolderAfterDeletion(self):
        config = ConfigObject("", "", "", "", "", "", self.workdirectory, "", "", "", "", "")
        samplepath = os.path.dirname(config.getlogpath("anyPath"))
        self.assertTrue(os.path.exists(samplepath))
        config.deletelogfolder()
        self.assertFalse(os.path.exists(samplepath))
        samplepath = os.path.dirname(config.getlogpath("anyPath"))
        self.assertTrue(os.path.exists(samplepath))
