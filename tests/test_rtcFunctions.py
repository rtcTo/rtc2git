__author__ = 'Manuel'

import unittest
from unittest.mock import patch
import os

from rtcFunctions import Changes, ChangeEntry, ImportHandler
from configuration import Builder
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
        Changes.accept(config, self.apath, self.createChangeEntry(revision1),
                       self.createChangeEntry(revision2))
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
        Changes.discard(config, self.createChangeEntry(revision1), self.createChangeEntry(revision2))
        expected_discard_command = "lscm discard -w %s -r %s -o %s %s" % (self.workspace, anyurl, revision1, revision2)
        shell_mock.execute.assert_called_once_with(expected_discard_command)

    def createChangeEntry(self, revision = "anyRevisionId", author = "anyAuthor", email = "anyEmail", comment = "anyComment", date = "anyDate"):
        return ChangeEntry(revision, author, email, date, comment)

    def test_ReadChangesetInformationFromFile_WithoutLineBreakInComment_ShouldBeSuccessful(self):
        sample_file_path = self.get_Sample_File_Path("SampleCompareOutputWithoutLineBreaks.txt")
        changeentries = ImportHandler.getchangeentriesfromfile(sample_file_path)
        self.assertEqual(2, len(changeentries))
        author = "Jon Doe"
        mail = "Jon.Doe@rtc2git.rocks"
        self.assert_Change_Entry(changeentries[0], author, mail, "My first commit in rtc! :D", "2015-05-26 10:40:00")
        self.assert_Change_Entry(changeentries[1], author, mail, "I want to commit on my flight to Riga :(",
                                 "2015-05-26 10:42:00")

    def test_ReadChangesetInformationFromFile_WithLineBreakInComment_ShouldBeSuccesful(self):
        sample_file_path = self.get_Sample_File_Path("SampleCompareOutputWithLineBreaks.txt")
        changeentries = ImportHandler.getchangeentriesfromfile(sample_file_path)
        self.assertEqual(2, len(changeentries))
        author = "Jon Doe"
        mail = "Jon.Doe@rtc2git.rocks"
        self.assert_Change_Entry(changeentries[0], author, mail, "My first commit in rtc! :D", "2015-05-26 10:40:00")
        expectedcomment = "I want to commit on my flight to Riga :(" + os.linesep + "This is a new line"
        self.assert_Change_Entry(changeentries[1], author, mail, expectedcomment, "2015-05-26 10:42:00")

    def test_ReadChangesetInformationFromFile_InUtf8_ShouldBeSuccesful(self):
        shell.setencoding("UTF-8")
        sample_file_path = self.get_Sample_File_Path("SampleCompareOutputInUtf8.txt")
        changeentries = ImportHandler.getchangeentriesfromfile(sample_file_path)
        self.assertEqual(1, len(changeentries))
        author = "John ÆØÅ"
        mail = "Jon.Doe@rtc2git.rocks"
        self.assert_Change_Entry(changeentries[0], author, mail, "Comment", "2015-05-26 10:40:00")
        
    @patch('rtcFunctions.Changes')
    @patch('builtins.input', return_value='')
    def test_RetryAccept_AssertThatTwoChangesGetAcceptedTogether(self, inputmock, changesmock):
        changeentry1 = self.createChangeEntry("anyRevId")
        changeentry2 = self.createChangeEntry("anyOtherRevId")
        changeentries = [changeentry1, changeentry2]
        changesmock.accept.return_value = 0

        config = self.configBuilder.build()
        handler = ImportHandler(config)
        handler.retryacceptincludingnextchangeset(changeentry1, changeentries)

        changesmock.accept.assert_called_with(config, handler.acceptlogpath, changeentry1, changeentry2)

    def test_collectChangeSetsToAcceptToAvoidMergeConflict_ShouldCollectThreeChangesets(self):
        mychange1 = self.createChangeEntry("doSomethingOnOldRev")
        mychange2 = self.createChangeEntry("doSomethingElseOnOldRev")
        mymergechange = self.createChangeEntry("anyRev", comment="merge change")
        changefromsomeoneelse = self.createChangeEntry(author="anyOtherAuthor", revision="2", comment="anotherCommit")

        changeentries = [mychange1, mychange2, mymergechange, changefromsomeoneelse]

        handler = ImportHandler(self.configBuilder.build())
        collectedchanges = handler.collect_changes_to_accept_to_avoid_conflicts(mychange1, changeentries)
        self.assertTrue(mychange1 in collectedchanges)
        self.assertTrue(mychange2 in collectedchanges)
        self.assertTrue(mymergechange in collectedchanges)
        self.assertFalse(changefromsomeoneelse in collectedchanges)
        self.assertEqual(3, len(collectedchanges))



    def get_Sample_File_Path(self, filename):
        testpath = os.path.realpath(__file__)
        testdirectory = os.path.dirname(testpath)
        testfilename = os.path.splitext(os.path.basename(testpath))[0]
        sample_file_path = testdirectory + os.sep + "resources" + os.sep + testfilename + "_" + filename
        return sample_file_path

    def assert_Change_Entry(self, change, author, email, comment, date):
        self.assertIsNotNone(change)
        self.assertEqual(author, change.author)
        self.assertEqual(email, change.email)
        self.assertEqual(comment, change.comment)
        self.assertEqual(date, change.date)
