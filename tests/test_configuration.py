import unittest
import os

from configuration import Builder
import configuration
import shell


class ConfigurationTestCase(unittest.TestCase):

    def setUp(self):
        self.workdirectory = os.path.dirname(os.path.realpath(__file__))
        # reset global shell variables
        shell.logcommands = False
        shell.encoding = None

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
        config = Builder().setignorefileextensions(configuration.parseignorefileextensionsproperty(None)).build()
        self.assertEqual(0, len(config.ignorefileextensions))

    def test_fileExtensionsToBeIgnored_ShouldBeEmpty_FromEmpty(self):
        config = Builder().setignorefileextensions("").build()
        self.assertEqual(0, len(config.ignorefileextensions))

    def test_fileExtensionsToBeIgnored_SingleExtensions(self):
        config = Builder().setignorefileextensions(configuration.parseignorefileextensionsproperty(" .zip  ")).build()
        self.assertEqual(1, len(config.ignorefileextensions))
        self.assertEqual(['.zip'], config.ignorefileextensions)

    def test_fileExtensionsToBeIgnored_MultipleExtensions(self):
        config = Builder().setignorefileextensions(configuration.parseignorefileextensionsproperty(".zip; .jar;  .exe")) \
            .build()
        self.assertEqual(3, len(config.ignorefileextensions))
        self.assertEqual(['.zip', '.jar', '.exe'], config.ignorefileextensions)

    def test_read_passedin_configfile(self):
        self._assertTestConfig(configuration.read('resources/test_config.ini'))

    def test_read_configfile_from_configuration(self):
        configuration.setconfigfile('resources/test_config.ini')
        self._assertTestConfig(configuration.read())

    def test_read_minimumconfigfile_shouldrelyonfallbackvalues(self):
        configuration.setconfigfile('resources/test_minimum_config.ini')
        self._assertDefaultConfig(configuration.read())

    def _assertTestConfig(self, config):
        # [General]
        self.assertEqual('https://rtc.supercompany.com/ccm/', config.repo)
        self.assertEqual('superuser', config.user)
        self.assertEqual('supersecret', config.password)
        self.assertEqual('super.git', config.gitRepoName)
        self.assertEqual('Superworkspace', config.workspace)
        self.assertEqual('/tmp/migration', config.workDirectory)
        self.assertTrue(config.useexistingworkspace)
        self.assertEqual('scm', config.scmcommand)
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
        self.assertEqual("UP-", config.commitmessageprefix)
        # [Miscellaneous]
        self.assertTrue(shell.logcommands)  # directly deviated to shell
        ignorefileextensions = config.ignorefileextensions
        self.assertEqual(2, len(ignorefileextensions))
        self.assertEqual('.zip', ignorefileextensions[0])
        self.assertEqual('.jar', ignorefileextensions[1])
        self.assertTrue(config.includecomponentroots)

    def _assertDefaultConfig(self, config):
        # [General]
        self.assertEqual('https://rtc.minicompany.com/ccm/', config.repo)
        self.assertEqual('miniuser', config.user)
        self.assertEqual('minisecret', config.password)
        self.assertEqual('mini.git', config.gitRepoName)
        self.assertEqual('Miniworkspace', config.workspace)
        self.assertEqual(os.getcwd(), config.workDirectory)
        self.assertFalse(config.useexistingworkspace)
        self.assertEqual('lscm', config.scmcommand)
        self.assertEqual(None, shell.encoding)  # directly deviated to shell
        # [Migration]
        self.assertEqual('Ministream', config.streamname)
        self.assertEqual('', config.previousstreamname)
        self.assertEqual(0, len(config.initialcomponentbaselines))
        self.assertFalse(config.useprovidedhistory)
        self.assertFalse(config.useautomaticconflictresolution)
        self.assertEqual("", config.commitmessageprefix)
        # [Miscellaneous]
        self.assertFalse(shell.logcommands)  # directly deviated to shell
        self.assertEqual(0, len(config.ignorefileextensions))
        self.assertFalse(config.includecomponentroots)
