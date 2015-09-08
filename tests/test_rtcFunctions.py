__author__ = 'Manuel'

import unittest
from unittest.mock import patch
import os

from rtcFunctions import Changes, ChangeEntry, ImportHandler, WorkspaceHandler, CompareType
from configuration import Builder
import configuration
import shell


class RtcFunctionsTestCase(unittest.TestCase):
    def setUp(self):
        self.workspace = "anyWorkspace"
        self.apath = "aLogPath"
        self.configBuilder = Builder()

    @patch('rtcFunctions.shell')
    def test_Accept_AssertThatCorrectParamaterGetPassedToShell(self, shell_mock):
        revision1 = "anyRevision"
        revision2 = "anyOtherRevision"
        anyurl = "anyUrl"
        config = self.configBuilder.setrepourl(anyurl).setworkspace(self.workspace).build()
        configuration.config = config
        Changes.accept(self.apath, self.createChangeEntry(revision1), self.createChangeEntry(revision2))
        expected_accept_command = "lscm accept -v -o -r %s -t %s --changes %s %s" % (anyurl, self.workspace, revision1,
                                                                                     revision2)
        appendlogfileshortcut = "a"
        shell_mock.execute.assert_called_once_with(expected_accept_command, self.apath, appendlogfileshortcut)
        self.assertEqual(expected_accept_command, Changes.latest_accept_command)

    @patch('rtcFunctions.shell')
    def test_Discard_AssertThatCorrectParamaterGetPassedToShell(self, shell_mock):
        revision1 = "anyRevision"
        revision2 = "anyOtherRevision"
        anyurl = "anyUrl"
        config = self.configBuilder.setrepourl(anyurl).setworkspace(self.workspace).build()
        configuration.config = config
        Changes.discard(self.createChangeEntry(revision1), self.createChangeEntry(revision2))
        expected_discard_command = "lscm discard -w %s -r %s -o %s %s" % (self.workspace, anyurl, revision1, revision2)
        shell_mock.execute.assert_called_once_with(expected_discard_command)

    def test_ReadChangesetInformationFromFile_WithoutLineBreakInComment_ShouldBeSuccessful(self):
        sample_file_path = self.get_Sample_File_Path("SampleCompareOutputWithoutLineBreaks.txt")
        changeentries = ImportHandler.getchangeentriesfromfile(sample_file_path)
        self.assertEqual(2, len(changeentries))
        author = "Jon Doe"
        mail = "Jon.Doe@rtc2git.rocks"
        self.assert_Change_Entry(changeentries[0], author, mail, "My first commit in rtc! :D", "2015-05-26 10:40:00", "_2mytestcomponent2-UUID")
        self.assert_Change_Entry(changeentries[1], author, mail, "I want to commit on my flight to Riga :(",
                                 "2015-05-26 10:42:00", "_2mytestcomponent2-UUID")

    def test_ReadChangesetInformationFromFile_WithMultipleComponents(self):
        sample_file_path = self.get_Sample_File_Path("SampleCompareOutputWithComponents.txt")
        changeentries = ImportHandler.getchangeentriesfromfile(sample_file_path)
        self.assertEqual(4, len(changeentries))
        author = "Bubba Gump"
        mail = "bubba.gump@shrimps.com"
        self.assert_Change_Entry(changeentries[0], author, mail, "1234: work item - commit 1", "2015-06-07 16:34:22", "_2mytestcomponent2-UUID")
        self.assert_Change_Entry(changeentries[1], author, mail, "1234: work item - commit 3", "2015-08-25 16:15:50", "_2mytestcomponent2-UUID")
        self.assert_Change_Entry(changeentries[2], author, mail, "1234: work item - commit 2", "2015-06-08 16:34:22", "_3mytestcomponent3-UUID")
        self.assert_Change_Entry(changeentries[3], author, mail, "1234: work item - commit 4", "2015-08-26 16:15:50", "_3mytestcomponent3-UUID")

    def test_ReadChangesetInformationFromFile_WithLineBreakInComment_ShouldBeSuccesful(self):
        sample_file_path = self.get_Sample_File_Path("SampleCompareOutputWithLineBreaks.txt")
        changeentries = ImportHandler.getchangeentriesfromfile(sample_file_path)
        self.assertEqual(2, len(changeentries))
        author = "Jon Doe"
        mail = "Jon.Doe@rtc2git.rocks"
        self.assert_Change_Entry(changeentries[0], author, mail, "My first commit in rtc! :D", "2015-05-26 10:40:00", "_2mytestcomponent2-UUID")
        expectedcomment = "I want to commit on my flight to Riga :(" + os.linesep + "This is a new line"
        self.assert_Change_Entry(changeentries[1], author, mail, expectedcomment, "2015-05-26 10:42:00", "_3mytestcomponent3-UUID")

    def test_ReadChangesetInformationFromFile_InUtf8_ShouldBeSuccesful(self):
        shell.setencoding("UTF-8")
        sample_file_path = self.get_Sample_File_Path("SampleCompareOutputInUtf8.txt")
        changeentries = ImportHandler.getchangeentriesfromfile(sample_file_path)
        self.assertEqual(1, len(changeentries))
        author = "John ÆØÅ"
        mail = "Jon.Doe@rtc2git.rocks"
        self.assert_Change_Entry(changeentries[0], author, mail, "Comment", "2015-05-26 10:40:00", "_2mytestcomponent2-UUID")

    @patch('rtcFunctions.shell')
    @patch('builtins.input', return_value='')
    def test_RetryAccept_AssertThatTwoChangesGetAcceptedTogether(self, inputmock, shellmock):
        changeentry1 = self.createChangeEntry("anyRevId")
        changeentry2 = self.createChangeEntry("anyOtherRevId")
        changeentries = [changeentry1, changeentry2]

        shellmock.execute.return_value = 0
        self.configBuilder.setrepourl("anyurl").setuseautomaticconflictresolution("True").setworkspace("anyWs")
        config = self.configBuilder.build()
        configuration.config = config

        handler = ImportHandler()
        handler.retryacceptincludingnextchangesets(changeentry1, changeentries)

        expectedshellcommand = 'lscm accept -v -o -r anyurl -t anyWs --changes anyRevId anyOtherRevId'
        shellmock.execute.assert_called_once_with(expectedshellcommand, handler.config.getlogpath("accept.txt"), "a")

    def test_collectChangeSetsToAcceptToAvoidMergeConflict_ShouldCollectThreeChangesets(self):
        mychange1 = self.createChangeEntry("doSomethingOnOldRev")
        mychange2 = self.createChangeEntry("doSomethingElseOnOldRev")
        mymergechange = self.createChangeEntry("anyRev", comment="merge change")
        changefromsomeoneelse = self.createChangeEntry(author="anyOtherAuthor", revision="2", comment="anotherCommit")

        changeentries = [mychange1, mychange2, mymergechange, changefromsomeoneelse]

        configuration.config = self.configBuilder.build()
        collectedchanges = ImportHandler().collect_changes_to_accept_to_avoid_conflicts(mychange1, changeentries)
        self.assertTrue(mychange1 in collectedchanges)
        self.assertTrue(mychange2 in collectedchanges)
        self.assertTrue(mymergechange in collectedchanges)
        self.assertFalse(changefromsomeoneelse in collectedchanges)
        self.assertEqual(3, len(collectedchanges))

    @patch('builtins.input', return_value='Y')
    def test_useragreeing_answeris_y_expecttrue(self, inputmock):
        configuration.config = self.configBuilder.build()
        self.assertTrue(ImportHandler().is_user_agreeing_to_accept_next_change(self.createChangeEntry()))

    @patch('builtins.input', return_value='n')
    def test_useragreeing_answeris_n_expectfalseandexception(self, inputmock):
        configuration.config = self.configBuilder.build()
        try:
            ImportHandler().is_user_agreeing_to_accept_next_change(self.createChangeEntry())
            self.fail("Should have exit the program")
        except SystemExit as e:
            self.assertEqual("Please check the output/log and rerun program with resume", e.code)

    @patch('rtcFunctions.shell')
    def test_load(self, shellmock):
        anyurl = "anyUrl"
        config = self.configBuilder.setrepourl(anyurl).setworkspace(self.workspace).build()
        configuration.config = config
        WorkspaceHandler().load()
        expected_load_command = "lscm load -r %s %s --force" % (anyurl, self.workspace)
        shellmock.execute.assert_called_once_with(expected_load_command)

    @patch('rtcFunctions.shell')
    def test_load_includecomponentroots(self, shellmock):
        anyurl = "anyUrl"
        config = self.configBuilder.setrepourl(anyurl).setworkspace(self.workspace).setincludecomponentroots("True").build()
        configuration.config = config
        WorkspaceHandler().load()
        expected_load_command = "lscm load -r %s %s --force --include-root" % (anyurl, self.workspace)
        shellmock.execute.assert_called_once_with(expected_load_command)

    def test_CreateChangeEntry_minimal(self):
        revision="anyRevisionId"
        author="anyAuthor"
        email="anyEmail"
        date="anyDate"
        comment="anyComment"
        change = ChangeEntry(revision, author, email, date, comment)
        self.assertEqual(revision, change.revision)
        self.assertEqual(author, change.author)
        self.assertEqual(email, change.email)
        self.assertEqual(date, change.date)
        self.assertEqual(comment, change.comment)
        self.assertEqual("unknown", change.component)
        self.assertEqual(False, change.accepted)

    def test_CreateChangeEntry_component(self):
        revision="anyRevisionId"
        author="anyAuthor"
        email="anyEmail"
        date="anyDate"
        comment="anyComment"
        component = "anyComponent"
        change = ChangeEntry(revision, author, email, date, comment, component)
        self.assertEqual(revision, change.revision)
        self.assertEqual(author, change.author)
        self.assertEqual(email, change.email)
        self.assertEqual(date, change.date)
        self.assertEqual(comment, change.comment)
        self.assertEqual(component, change.component)
        self.assertEqual(False, change.accepted)

    def test_ChangeEntry_flip_accepted(self):
        change = self.createChangeEntry()
        self.assertEqual(False, change.accepted)
        change.setAccepted()
        self.assertEqual(True, change.accepted)
        change.setUnaccepted()
        self.assertEqual(False, change.accepted)

    def test_ChangeEntry_tostring(self):
        change = self.createChangeEntry(revision="anyRev", component="anyCmp")
        self.assertEqual("anyComment (Date: anyDate, Author: anyAuthor, Revision: anyRev, Component: anyCmp, Accepted: False)",
                         change.tostring())

    @patch('rtcFunctions.shell')
    def test_getchangeentriesbytypeandvalue_type_stream(self, shellmock):
        anyurl = "anyUrl"
        config = self.configBuilder.setrepourl(anyurl).setworkspace(self.workspace).build()
        configuration.config = config
        stream = "myStreamUUID"
        comparetype = CompareType.stream
        comparetypename = comparetype.name
        filename = "Compare_%s_%s.txt" % (comparetypename, stream)
        outputfilename = config.getlogpath(filename)
        try:
            shellmock.encoding = 'UTF-8'
            ImportHandler().getchangeentriesbytypeandvalue(comparetype, stream)
        except FileNotFoundError:
            pass # do not bother creating the output file here
        expected_compare_command = "lscm --show-alias n --show-uuid y compare ws %s %s %s -r %s -I swc -C @@{name}@@{email}@@ --flow-directions i -D @@\"yyyy-MM-dd HH:mm:ss\"@@" \
                                   % (self.workspace, comparetypename, stream, anyurl)
        shellmock.execute.assert_called_once_with(expected_compare_command, outputfilename)

    @patch('rtcFunctions.shell')
    def test_getchangeentriesbytypeandvalue_type_baseline(self, shellmock):
        anyurl = "anyUrl"
        config = self.configBuilder.setrepourl(anyurl).setworkspace(self.workspace).build()
        configuration.config = config
        baseline = "myBaselineUUID"
        comparetype = CompareType.baseline
        comparetypename = comparetype.name
        filename = "Compare_%s_%s.txt" % (comparetypename, baseline)
        outputfilename = config.getlogpath(filename)
        try:
            shellmock.encoding = 'UTF-8'
            ImportHandler().getchangeentriesbytypeandvalue(comparetype, baseline)
        except FileNotFoundError:
            pass # do not bother creating the output file here
        expected_compare_command = "lscm --show-alias n --show-uuid y compare ws %s %s %s -r %s -I swc -C @@{name}@@{email}@@ --flow-directions i -D @@\"yyyy-MM-dd HH:mm:ss\"@@" \
                                   % (self.workspace, comparetypename, baseline, anyurl)
        shellmock.execute.assert_called_once_with(expected_compare_command, outputfilename)


    def get_Sample_File_Path(self, filename):
        testpath = os.path.realpath(__file__)
        testdirectory = os.path.dirname(testpath)
        testfilename = os.path.splitext(os.path.basename(testpath))[0]
        sample_file_path = testdirectory + os.sep + "resources" + os.sep + testfilename + "_" + filename
        return sample_file_path

    def createChangeEntry(self, revision="anyRevisionId", author="anyAuthor", email="anyEmail", comment="anyComment",
                          date="anyDate", component="anyComponentUUID"):
        return ChangeEntry(revision, author, email, date, comment, component)

    def assert_Change_Entry(self, change, author, email, comment, date, component, accepted=False):
        self.assertIsNotNone(change)
        self.assertEqual(author, change.author)
        self.assertEqual(email, change.email)
        self.assertEqual(comment, change.comment)
        self.assertEqual(date, change.date)
        self.assertEqual(component, change.component)
        self.assertEqual(accepted, change.accepted)
