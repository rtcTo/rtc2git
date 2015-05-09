import unittest
from unittest.mock import patch

import shell


class ShellTest(unittest.TestCase):
    @patch('shell.shouter')
    @patch('shell.call')
    def testWhenLoggingShellComandsIsDisabled_ExpectNoOutput(self, subprocess_call_mock, shouter_mock):
        shell.logcommands = False
        shell.execute("doSomething")
        assert not shouter_mock.called

    @patch('shell.shouter')
    @patch('shell.call')
    def testWhenLoggingShellComandsIsEnabled_ExpectCommandIsLoggedToOutput(self, subprocess_call_mock, shouter_mock):
        shell.logcommands = True
        shell.execute("doSomething")
        assert not shouter_mock.called
