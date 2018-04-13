import os
import unittest

import configuration
import shell
from configuration import Builder
from tests import testhelper


class ConfigurationTestCase(unittest.TestCase):

    def setUp(self):
        self.workdirectory = os.path.dirname(os.path.realpath(__file__))
        # reset global shell variables
        shell.logcommands = False
        shell.encoding = None
        configuration.setconfigfile(None)
        configuration.setUser(None)
        configuration.setPassword(None)

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
        config = configuration.read(testhelper.getrelativefilename("../config.ini.sample"))
        self.assertEqual("lscm", config.scmcommand)
        self.assertEqual(config, configuration.get())

    def test_fileExtensionsToBeIgnored_ShouldBeEmpty_FromNone(self):
        config = Builder().setignorefileextensions(configuration.parsesplittedproperty(None)).build()
        self.assertEqual(0, len(config.ignorefileextensions))

    def test_fileExtensionsToBeIgnored_ShouldBeEmpty_FromEmpty(self):
        config = Builder().setignorefileextensions("").build()
        self.assertEqual(0, len(config.ignorefileextensions))

    def test_fileExtensionsToBeIgnored_SingleExtension(self):
        config = Builder().setignorefileextensions(configuration.parsesplittedproperty(" .zip  ")).build()
        self.assertEqual(1, len(config.ignorefileextensions))
        self.assertEqual(['.zip'], config.ignorefileextensions)

    def test_fileExtensionsToBeIgnored_MultipleExtensions(self):
        config = Builder().setignorefileextensions(configuration.parsesplittedproperty(".zip; .jar;  .exe")) \
            .build()
        self.assertEqual(3, len(config.ignorefileextensions))
        self.assertEqual(['.zip', '.jar', '.exe'], config.ignorefileextensions)

    def test_directoriesToBeIgnored_ShouldBeEmpty_FromNone(self):
        config = Builder().setignoredirectories(configuration.parsesplittedproperty(None)).build()
        self.assertEqual(0, len(config.ignoredirectories))

    def test_directoriesToBeIgnored_ShouldBeEmpty_FromEmpty(self):
        config = Builder().setignoredirectories("").build()
        self.assertEqual(0, len(config.ignoredirectories))

    def test_directoriesToBeIgnored_SingleExtension(self):
        config = Builder().setignoredirectories(configuration.parsesplittedproperty(" project/dist  ")).build()
        self.assertEqual(1, len(config.ignoredirectories))
        self.assertEqual(['project/dist'], config.ignoredirectories)

    def test_directoriesToBeIgnored_MultipleExtensions(self):
        config = Builder().setignoredirectories(configuration.parsesplittedproperty(" project/dist ; project/lib ;  out ")) \
            .build()
        self.assertEqual(3, len(config.ignoredirectories))
        self.assertEqual(['project/dist', 'project/lib', 'out'], config.ignoredirectories)

    def test_gitattributes_ShouldBeEmpty_FromNone(self):
        config = Builder().setgitattributes(configuration.parsesplittedproperty(None)).build()
        self.assertEqual(0, len(config.gitattributes))

    def test_gitattributes_ShouldBeEmpty_FromEmpty(self):
        config = Builder().setgitattributes(configuration.parsesplittedproperty("")).build()
        self.assertEqual(0, len(config.gitattributes))

    def test_gitattributes__SingleProperty(self):
        config = Builder().setgitattributes(configuration.parsesplittedproperty("  * text=auto  ")).build()
        self.assertEqual(1, len(config.gitattributes))
        self.assertEqual(['* text=auto'], config.gitattributes)

    def test_gitattributes__MultipleProperties(self):
        config = Builder().setgitattributes(configuration.parsesplittedproperty(" # some comment ;   * text=auto  ; *.sql text ")).build()
        self.assertEqual(3, len(config.gitattributes))
        self.assertEqual(['# some comment', '* text=auto', '*.sql text'], config.gitattributes)

    def test_read_passedin_configfile(self):
        self._assertTestConfig(configuration.read(testhelper.getrelativefilename('resources/test_config.ini')))

    def test_read_passedin_configfile_expect_override_user_password(self):
        configuration.setUser('newUser')
        configuration.setPassword('newPassword')
        self._assertTestConfig(configuration.read(testhelper.getrelativefilename('resources/test_config.ini')),
                               user='newUser', password='newPassword')

    def test_read_configfile_from_configuration(self):
        configuration.setconfigfile(testhelper.getrelativefilename('resources/test_config.ini'))
        self._assertTestConfig(configuration.read())

    def test_read_minimumconfigfile_shouldrelyonfallbackvalues(self):
        configuration.setconfigfile(testhelper.getrelativefilename('resources/test_minimum_config.ini'))
        self._assertDefaultConfig(configuration.read())

    def _assertTestConfig(self, config, user=None, password=None):
        # [General]
        self.assertEqual('https://rtc.supercompany.com/ccm/', config.repo)
        if not user:
            self.assertEqual('superuser', config.user)
        else:
            self.assertEqual(user, config.user)
        if not password:
            self.assertEqual('supersecret', config.password)
        else:
            self.assertEqual(password, config.password)
        self.assertEqual('super.git', config.gitRepoName)
        self.assertEqual('Superworkspace', config.workspace)
        self.assertEqual('/tmp/migration', config.workDirectory)
        self.assertTrue(config.useexistingworkspace)
        self.assertEqual('scm', config.scmcommand)
        self.assertEqual('UTF-8', shell.encoding)  # directly deviated to shell
        self.assertEqual(6, config.rtcversion)
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
        self.assertEqual(100, config.maxchangesetstoaccepttogether)
        self.assertEqual("UP-", config.commitmessageprefix)
        gitattributes = config.gitattributes
        self.assertEqual(4, len(gitattributes))
        self.assertEqual('# Handle line endings automatically for text files', gitattributes[0])
        self.assertEqual('# and leave binary files untouched', gitattributes[1])
        self.assertEqual('* text=auto', gitattributes[2])
        self.assertEqual('*.sql text', gitattributes[3])
        # [Miscellaneous]
        self.assertTrue(shell.logcommands)  # directly deviated to shell
        ignorefileextensions = config.ignorefileextensions
        self.assertEqual(2, len(ignorefileextensions))
        self.assertEqual('.zip', ignorefileextensions[0])
        self.assertEqual('.jar', ignorefileextensions[1])
        self.assertTrue(config.includecomponentroots)
        ignoredirectories = config.ignoredirectories
        self.assertEqual(2, len(ignoredirectories))
        self.assertEqual('projectX/WebContent/node_modules', ignoredirectories[0])
        self.assertEqual('projectY/distribution', ignoredirectories[1])

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
        self.assertEqual(5, config.rtcversion)
        # [Migration]
        self.assertEqual('Ministream', config.streamname)
        self.assertEqual('', config.previousstreamname)
        self.assertEqual(0, len(config.initialcomponentbaselines))
        self.assertFalse(config.useprovidedhistory)
        self.assertFalse(config.useautomaticconflictresolution)
        self.assertEqual(10, config.maxchangesetstoaccepttogether)
        self.assertEqual("", config.commitmessageprefix)
        self.assertEqual(0, len(config.gitattributes))
        # [Miscellaneous]
        self.assertFalse(shell.logcommands)  # directly deviated to shell
        self.assertEqual(0, len(config.ignorefileextensions))
        self.assertFalse(config.includecomponentroots)
