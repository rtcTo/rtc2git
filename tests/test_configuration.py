import unittest
import os

from configuration import Builder
import configuration
import shell


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

    def test_getSampleConfig_ExpectInitializedConfigWithDefaultValues(self):
        config = configuration.read("../config.ini.sample")
        self.assertEqual("lscm", config.scmcommand)
        self.assertEqual(config, configuration.get())

    def test_fileExtensionsToBeIgnored_ShouldBeEmpty_FromNone(self):
        config = Builder().setignorefileextensions(None).build()
        self.assertTrue(len(config.ignorefileextensions) == 0)

    def test_fileExtensionsToBeIgnored_ShouldBeEmpty_FromEmpty(self):
        config = Builder().setignorefileextensions("").build()
        self.assertTrue(len(config.ignorefileextensions) == 0)

    def test_fileExtensionsToBeIgnored_SingleExtensions(self):
        config = Builder().setignorefileextensions(" .zip  ").build()
        self.assertTrue(len(config.ignorefileextensions) == 1)
        self.assertEqual(['.zip'], config.ignorefileextensions)

    def test_fileExtensionsToBeIgnored_MultipleExtensions(self):
        config = Builder().setignorefileextensions(".zip; .jar;  .exe").build()
        self.assertTrue(len(config.ignorefileextensions) == 3)
        self.assertEqual(['.zip', '.jar', '.exe'], config.ignorefileextensions)

    def test_read(self):
        # [General]
        config = configuration.read('resources/test_config.ini')
        self.assertEqual('https://rtc.supercompany.com/ccm/', config.repo)
        self.assertEqual('superuser', config.user)
        self.assertEqual('supersecret', config.password)
        self.assertEqual('super.git', config.gitRepoName)
        self.assertEqual('Superworkspace', config.workspace)
        self.assertEqual('/tmp/migration', config.workDirectory)
        self.assertTrue(config.useexistingworkspace)
        self.assertEqual('lscm', config.scmcommand)
        self.assertEqual('UTF-8', shell.encoding)  # directly deviated to shell
        # [Migration]
        self.assertEqual('Superstream', config.streamname)
        self.assertEqual('Previousstream', config.previousstreamname)
        initialcomponentbaselines = config.initialcomponentbaselines
        self.assertEqual(2, len(initialcomponentbaselines))
        initialcomponentbaseline = initialcomponentbaselines[0]
        self.assertEqual('Component1', initialcomponentbaseline.componentname)
        self.assertEqual('Baseline1', initialcomponentbaseline.baselinename)
        initialcomponentbaseline = initialcomponentbaselines[1]
        self.assertEqual('Component2', initialcomponentbaseline.componentname)
        self.assertEqual('Baseline2', initialcomponentbaseline.baselinename)
        self.assertTrue(config.useprovidedhistory)
        self.assertTrue(config.useautomaticconflictresolution)
        # [Miscellaneous]
        self.assertTrue(shell.logcommands)  # directly deviated to shell
        ignorefileextensions = config.ignorefileextensions
        self.assertEqual(2, len(ignorefileextensions))
        self.assertEqual('.zip', ignorefileextensions[0])
        self.assertEqual('.jar', ignorefileextensions[1])


