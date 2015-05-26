__author__ = 'Manuel'

import unittest
from unittest.mock import patch
import os

from rtcFunctions import Changes, ChangeEntry, ImportHandler


class RtcFunctionsTestCase(unittest.TestCase):
    def setUp(self):
        self.workspace = "anyWorkspace"
        self.apath = "aLogPath"

    @patch('rtcFunctions.shell')
    def test_Accept_AssertThatCorrectParamaterGetPassedToShell(self, shell_mock):
        revision1 = "anyRevision"
        revision2 = "anyOtherRevision"
        Changes.accept(self.workspace, self.apath, self.createChangeEntry(revision1), self.createChangeEntry(revision2))
        expected_accept_command = "lscm accept -v --overwrite-uncommitted -t %s --changes %s %s" % (self.workspace,
                                                                                                    revision1,
                                                                                                    revision2)
        appendlogfileshortcut = "a"
        shell_mock.execute.assert_called_once_with(expected_accept_command, self.apath, appendlogfileshortcut)

    @patch('rtcFunctions.shell')
    def test_Discard_AssertThatCorrectParamaterGetPassedToShell(self, shell_mock):
        revision1 = "anyRevision"
        revision2 = "anyOtherRevision"
        Changes.discard(self.workspace, self.createChangeEntry(revision1), self.createChangeEntry(revision2))
        expected_discard_command = "lscm discard -w %s --overwrite-uncommitted %s %s" % (self.workspace,
                                                                                         revision1, revision2)
        shell_mock.execute.assert_called_once_with(expected_discard_command)

    def createChangeEntry(self, revision):
        return ChangeEntry(revision, "anyAuthor", "anyEmail", "anyDate", "anyComment")

    def test_ReadChangesetInformationFromFile_WithoutLineBreakInComment_ShouldBeSuccessful(self):
        samplefilepath = os.path.realpath(__file__) + "_SampleCompareOutputWithoutLineBreaks.txt"
        changeentries = ImportHandler.getchangeentriesfromfile(samplefilepath)
        self.assertEqual(2, len(changeentries))
        self.assert_Change_Entry(changeentries[0], "Jon Doe", "Jon.Doe@rtc2git.rocks", "My first commit in rtc! :D",
                                 "2015-05-26 10:40:00")
        self.assert_Change_Entry(changeentries[1],"Jon Doe", "Jon.Doe@rtc2git.rocks", "I want to commit on my flight to Riga :(",
                                 "2015-05-26 10:42:00")

    def test_ReadChangesetInformationFromFile_WithLineBreakInComment_ShouldBeSuccesful(self):
        samplefilepath = os.path.realpath(__file__) + "_SampleCompareOutputWithLineBreaks.txt"
        changeentries = ImportHandler.getchangeentriesfromfile(samplefilepath)
        self.assertEqual(2, len(changeentries))


    def assert_Change_Entry(self, change, author, email, comment, date):
        self.assertIsNotNone(change)
        self.assertEqual(author, change.author)
        self.assertEqual(email, change.email)
        self.assertEqual(comment, change.comment)
        self.assertEqual(date, change.date)