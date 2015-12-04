import unittest
import os
from unittest.mock import patch, call

import configuration
import shell
from rtcFunctions import Changes, ChangeEntry, ImportHandler, WorkspaceHandler, CompareType
from configuration import Builder
from tests import testhelper

__author__ = 'Manuel'


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
        Changes.accept(self.apath, testhelper.createchangeentry(revision1), testhelper.createchangeentry(revision2))
        commandtemplate = u"lscm accept --verbose --overwrite-uncommitted --accept-missing-changesets --no-merge --repository-uri {0:s} --target {1:s} --changes {2:s} {3:s}"
        expected_accept_command = commandtemplate.format(anyurl, self.workspace, revision1, revision2)
        appendlogfileshortcut = "a"
        shell_mock.execute.assert_called_once_with(expected_accept_command, self.apath, appendlogfileshortcut)
        self.assertEqual(expected_accept_command, Changes.latest_accept_command)

    def test_Accept_AssertThatChangeEntriesGetAccepted(self):
        with patch.object(shell, 'execute', return_value=0) as shell_mock:
            revision1 = "anyRevision"
            revision2 = "anyOtherRevision"
            anyurl = "anyUrl"
            config = self.configBuilder.setrepourl(anyurl).setworkspace(self.workspace).build()
            configuration.config = config
            changeentry1 = testhelper.createchangeentry(revision1)
            changeentry2 = testhelper.createchangeentry(revision2)
            Changes.accept(self.apath, changeentry1, changeentry2)
            self.assertTrue(changeentry1.isAccepted())
            self.assertTrue(changeentry1.isAccepted())

    @patch('rtcFunctions.shell')
    def test_Discard_AssertThatCorrectParamaterGetPassedToShell(self, shell_mock):
        revision1 = "anyRevision"
        revision2 = "anyOtherRevision"
        anyurl = "anyUrl"
        config = self.configBuilder.setrepourl(anyurl).setworkspace(self.workspace).build()
        configuration.config = config
        Changes.discard(testhelper.createchangeentry(revision1), testhelper.createchangeentry(revision2))
        expected_discard_command = "lscm discard -w %s -r %s -o %s %s" % (self.workspace, anyurl, revision1, revision2)
        shell_mock.execute.assert_called_once_with(expected_discard_command)

    def test_Discard_AssertThatChangeEntriesGetUnAccepted(self):
        with patch.object(shell, 'execute', return_value=0) as shell_mock:
            revision1 = "anyRevision"
            revision2 = "anyOtherRevision"
            anyurl = "anyUrl"
            config = self.configBuilder.setrepourl(anyurl).setworkspace(self.workspace).build()
            configuration.config = config
            changeentry1 = testhelper.createchangeentry(revision1)
            changeentry1.setAccepted()
            changeentry2 = testhelper.createchangeentry(revision2)
            changeentry2.setAccepted()
            Changes.discard(changeentry1, changeentry2)
            self.assertFalse(changeentry1.isAccepted())
            self.assertFalse(changeentry2.isAccepted())

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
        changeentry1 = testhelper.createchangeentry("anyRevId")
        changeentry2 = testhelper.createchangeentry("anyOtherRevId")
        changeentries = [changeentry1, changeentry2]

        shellmock.execute.return_value = 0
        self.configBuilder.setrepourl("anyurl").setuseautomaticconflictresolution("True").setmaxchangesetstoaccepttogether(10).setworkspace("anyWs")
        config = self.configBuilder.build()
        configuration.config = config

        handler = ImportHandler()
        handler.retryacceptincludingnextchangesets(changeentry1, changeentries)

        expectedshellcommand = 'lscm accept --verbose --overwrite-uncommitted --accept-missing-changesets --no-merge --repository-uri anyurl --target anyWs --changes anyRevId anyOtherRevId'
        shellmock.execute.assert_called_once_with(expectedshellcommand, handler.config.getlogpath("accept.txt"), "a")

    @patch('rtcFunctions.shell')
    @patch('builtins.input', return_value='')
    def test_RetryAccept_AssertThatOnlyChangesFromSameComponentGetAcceptedTogether(self, inputmock, shellmock):
        component1 = "uuid1"
        component2 = "uuid2"
        changeentry1 = testhelper.createchangeentry(revision="anyRevId", component=component1)
        changeentry2 = testhelper.createchangeentry(revision="component2RevId", component=component2)
        changeentry3 = testhelper.createchangeentry(revision="anyOtherRevId", component=component1)
        changeentries = [changeentry1, changeentry2, changeentry3]

        shellmock.execute.return_value = 0
        self.configBuilder.setrepourl("anyurl").setuseautomaticconflictresolution("True").setmaxchangesetstoaccepttogether(10).setworkspace("anyWs")
        config = self.configBuilder.build()
        configuration.config = config

        handler = ImportHandler()
        handler.retryacceptincludingnextchangesets(changeentry1, changeentries)

        expectedshellcommand = 'lscm accept --verbose --overwrite-uncommitted --accept-missing-changesets --no-merge --repository-uri anyurl --target anyWs --changes anyRevId anyOtherRevId'
        shellmock.execute.assert_called_once_with(expectedshellcommand, handler.config.getlogpath("accept.txt"), "a")

    @patch('rtcFunctions.shell')
    @patch('builtins.input', return_value='N')
    @patch('sys.exit')
    def test_RetryAccept_NotSuccessful_AndExit(self, exitmock, inputmock, shellmock):
        component1 = "uuid1"
        component2 = "uuid2"
        changeentry1 = testhelper.createchangeentry(revision="anyRevId", component=component1)
        changeentry2 = testhelper.createchangeentry(revision="component2RevId", component=component2)
        changeentry3 = testhelper.createchangeentry(revision="anyOtherRevId", component=component1)
        changeentry3.setAccepted()
        changeentries = [changeentry1, changeentry2, changeentry3]

        self.configBuilder.setrepourl("anyurl").setuseautomaticconflictresolution("True").setmaxchangesetstoaccepttogether(10).setworkspace("anyWs")
        config = self.configBuilder.build()
        configuration.config = config

        handler = ImportHandler()
        handler.retryacceptincludingnextchangesets(changeentry1, changeentries)
        inputmock.assert_called_once_with('Do you want to continue? Y for continue, any key for abort')
        exitmock.assert_called_once_with("Please check the output/log and rerun program with resume")

    def test_collectChangeSetsToAcceptToAvoidMergeConflict_ShouldCollectThreeChangesets(self):
        change1 = testhelper.createchangeentry("1")
        change2 = testhelper.createchangeentry("2")
        change3 = testhelper.createchangeentry("3")

        changeentries = [change1, change2, change3]

        configuration.config = self.configBuilder.build()
        collectedchanges = ImportHandler().collect_changes_to_accept_to_avoid_conflicts(change1, changeentries, 10)
        self.assertTrue(change1 in collectedchanges)
        self.assertTrue(change2 in collectedchanges)
        self.assertTrue(change3 in collectedchanges)
        self.assertEqual(3, len(collectedchanges))

    def test_collectChangeSetsToAcceptToAvoidMergeConflict_ShouldCollectOnlyUnacceptedChangesets(self):
        change1 = testhelper.createchangeentry(revision="1")
        change2 = testhelper.createchangeentry(revision="2")
        change2.setAccepted()
        change3 = testhelper.createchangeentry(revision="3")

        changeentries = [change1, change2, change3]

        configuration.config = self.configBuilder.build()
        collectedchanges = ImportHandler().collect_changes_to_accept_to_avoid_conflicts(change1, changeentries, 10)
        self.assertTrue(change1 in collectedchanges)
        self.assertFalse(change2 in collectedchanges)
        self.assertTrue(change3 in collectedchanges)
        self.assertEqual(2, len(collectedchanges))

    def test_collectChangeSetsToAcceptToAvoidMergeConflict_ShouldAdhereToMaxChangeSetCount(self):
        change1 = testhelper.createchangeentry("1")
        change2 = testhelper.createchangeentry("2")
        change3 = testhelper.createchangeentry("3")

        changeentries = [change1, change2, change3]

        configuration.config = self.configBuilder.build()
        collectedchanges = ImportHandler().collect_changes_to_accept_to_avoid_conflicts(change1, changeentries, 2)
        self.assertTrue(change1 in collectedchanges)
        self.assertTrue(change2 in collectedchanges)
        self.assertFalse(change3 in collectedchanges)
        self.assertEqual(2, len(collectedchanges))

    def test_collectChangeSetsToAcceptToAvoidMergeConflict_ShouldAcceptLargeAmountOfChangeSets(self):
        changeentries = [testhelper.createchangeentry(str(i)) for i in range(1, 500)]
        change1 = changeentries[0]

        configuration.config = self.configBuilder.build()
        collectedchanges = ImportHandler().collect_changes_to_accept_to_avoid_conflicts(change1, changeentries, 500)
        self.assertEqual(499, len(collectedchanges))

    @patch('builtins.input', return_value='Y')
    def test_useragreeing_answeris_y_expecttrue(self, inputmock):
        configuration.config = self.configBuilder.build()
        self.assertTrue(ImportHandler().is_user_agreeing_to_accept_next_change(testhelper.createchangeentry()))

    @patch('builtins.input', return_value='n')
    def test_useragreeing_answeris_n_expectfalseandexception(self, inputmock):
        configuration.config = self.configBuilder.build()
        try:
            ImportHandler().is_user_agreeing_to_accept_next_change(testhelper.createchangeentry())
            self.fail("Should have exit the program")
        except SystemExit as e:
            self.assertEqual("Please check the output/log and rerun program with resume", e.code)

    @patch('rtcFunctions.shell')
    @patch('rtcFunctions.Commiter')
    def test_load(self, commitermock, shellmock):
        anyurl = "anyUrl"
        config = self.configBuilder.setrepourl(anyurl).setworkspace(self.workspace).build()
        configuration.config = config
        WorkspaceHandler().load()
        expected_load_command = "lscm load -r %s %s --force" % (anyurl, self.workspace)
        shellmock.execute.assert_called_once_with(expected_load_command)
        calls = [call.get_untracked_statuszlines(), call.restore_shed_gitignore(commitermock.get_untracked_statuszlines())]
        commitermock.assert_has_calls(calls)

    @patch('rtcFunctions.shell')
    @patch('rtcFunctions.Commiter')
    def test_load_includecomponentroots(self, commitermock, shellmock):
        anyurl = "anyUrl"
        config = self.configBuilder.setrepourl(anyurl).setworkspace(self.workspace).setincludecomponentroots("True").build()
        configuration.config = config
        WorkspaceHandler().load()
        expected_load_command = "lscm load -r %s %s --force --include-root" % (anyurl, self.workspace)
        shellmock.execute.assert_called_once_with(expected_load_command)
        shellmock.execute.assert_called_once_with(expected_load_command)
        calls = [call.get_untracked_statuszlines(), call.restore_shed_gitignore(commitermock.get_untracked_statuszlines())]
        commitermock.assert_has_calls(calls)

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
        change = testhelper.createchangeentry()
        self.assertEqual(False, change.accepted)
        change.setAccepted()
        self.assertEqual(True, change.accepted)
        change.setUnaccepted()
        self.assertEqual(False, change.accepted)

    def test_ChangeEntry_tostring(self):
        change = testhelper.createchangeentry(revision="anyRev", component="anyCmp")
        self.assertEqual("anyComment (Date: 2015-01-22, Author: anyAuthor, Revision: anyRev, Component: anyCmp, Accepted: False)",
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

    def test_getnextchangeset_fromsamecomponent_expectsamecomponent(self):
        component1 = "uuid_1"
        component2 = "uuid_2"
        # entries for component 1 (2nd entry being already accepted)
        entry1_1 = testhelper.createchangeentry(revision="1.1", component=component1)
        entry1_2 = testhelper.createchangeentry(revision="1.2", component=component1)
        entry1_2.setAccepted()
        entry1_3 = testhelper.createchangeentry(revision="1.3", component=component1)
        # entries for component 2 (2nd entry being already accepted)
        entry2_1 = testhelper.createchangeentry(revision="2.1", component=component2)
        entry2_2 = testhelper.createchangeentry(revision="2.2", component=component2)
        entry2_2.setAccepted()
        entry2_3 = testhelper.createchangeentry(revision="2.3", component=component2)
        changeentries = []
        changeentries.append(entry1_1)
        changeentries.append(entry2_1)
        changeentries.append(entry1_2)
        changeentries.append(entry2_2)
        changeentries.append(entry1_3)
        changeentries.append(entry2_3)

        nextentry = ImportHandler.getnextchangeset_fromsamecomponent(currentchangeentry=entry2_1, changeentries=changeentries)
        self.assertIsNotNone(nextentry)
        self.assertFalse(nextentry.isAccepted())
        self.assertEqual(component2, nextentry.component)
        self.assertEqual("2.3", nextentry.revision)

    def test_getnextchangeset_fromsamecomponent_expectnonefound(self):
        component1 = "uuid_1"
        component2 = "uuid_2"
        # entries for component 1
        entry1_1 = testhelper.createchangeentry(revision="1.1", component=component1)
        entry1_1.setAccepted()
        entry1_2 = testhelper.createchangeentry(revision="1.2", component=component1)
        entry1_2.setAccepted()
        # entries for component 2 (2nd entry being already accepted)
        entry2_1 = testhelper.createchangeentry(revision="2.1", component=component2)
        entry2_1.setAccepted()
        entry2_2 = testhelper.createchangeentry(revision="2.2", component=component2)
        entry2_2.setAccepted()
        changeentries = []
        changeentries.append(entry1_1)
        changeentries.append(entry2_1)
        changeentries.append(entry1_2)
        changeentries.append(entry2_2)

        nextentry = ImportHandler.getnextchangeset_fromsamecomponent(currentchangeentry=entry2_1, changeentries=changeentries)
        self.assertIsNone(nextentry)

    def get_Sample_File_Path(self, filename):
        testpath = os.path.realpath(__file__)
        testdirectory = os.path.dirname(testpath)
        testfilename = os.path.splitext(os.path.basename(testpath))[0]
        sample_file_path = testdirectory + os.sep + "resources" + os.sep + testfilename + "_" + filename
        return sample_file_path

    def assert_Change_Entry(self, change, author, email, comment, date, component, accepted=False):
        self.assertIsNotNone(change)
        self.assertEqual(author, change.author)
        self.assertEqual(email, change.email)
        self.assertEqual(comment, change.comment)
        self.assertEqual(date, change.date)
        self.assertEqual(component, change.component)
        self.assertEqual(accepted, change.accepted)
