import unittest
import os

from configuration import Builder
import configuration


class ConfigurationTestCase(unittest.TestCase):

    def setUp(self):
        self.workdirectory = os.path.dirname(os.path.realpath(__file__))

    def test_DeletionOfFolder(self):
        config = Builder().setworkdirectory(self.workdirectory).build()
        samplepath = os.path.dirname(config.getlogpath("anyPath"))
        self.assertTrue(os.path.exists(samplepath))
        config.deletelogfolder()
        self.assertFalse(os.path.exists(samplepath))

    def test_ReaddingLogFolderAfterDeletion(self):
        config = Builder().setworkdirectory(self.workdirectory).build()
        samplepath = os.path.dirname(config.getlogpath("anyPath"))
        self.assertTrue(os.path.exists(samplepath))
        config.deletelogfolder()
        self.assertFalse(os.path.exists(samplepath))
        samplepath = os.path.dirname(config.getlogpath("anyPath"))
        self.assertTrue(os.path.exists(samplepath))

    def test_sampleBoolConfigEntrySetToFalse_ShouldBeFalse(self):
        config = Builder().setuseautomaticconflictresolution("False").build()
        self.assertFalse(config.useautomaticconflictresolution)

    def test_sampleBoolConfigEntrySetToTrue_ShouldBeTrue(self):
        config = Builder().setuseautomaticconflictresolution("True").build()
        self.assertTrue(config.useautomaticconflictresolution)

    def test_getSampleConfig_WhenNotYetRead_ExpectError(self):
        try:
            config = configuration.get()
            self.fail("Should have thrown an exception, that config is not yet initalized")
        except SystemExit as e:
            self.assertEqual("Config has not been initalized yet", e.code)

    def test_getSampleConfig_WhenRead_ExpectInitializedConfigWithDefaultValues(self):
        config = configuration.read("../config.ini.sample")
        self.assertEqual("lscm", config.scmcommand)
        self.assertEqual(config, configuration.get())
