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

    def test_ReadChangesetInformationFromFile_WithoutLineBreak_ShouldBeSuccessful(self):
        samplefilepath = os.path.realpath(__file__) + "_SampleCompareOutputWithoutLineBreaks.txt"
        for change in ImportHandler.getchangeentriesfromfile(samplefilepath):
            self.assertIsNotNone(change)
