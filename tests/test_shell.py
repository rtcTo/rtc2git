import unittest
from unittest.mock import patch

import shell


class ShellTest(unittest.TestCase):
    def setUp(self):
        shell.encoding = None

    @patch('shell.shouter')
    @patch('shell.call')
    def testWhenLoggingShellComandsIsDisabled_ExpectNoOutput(self, subprocess_call_mock, shouter_mock):
        shell.logcommands = False
        shell.execute("doSomething")
        assert not shouter_mock.shout.called

    @patch('shell.shouter')
    @patch('shell.call')
    def testWhenLoggingShellComandsIsEnabled_ExpectCommandIsLoggedToOutput(self, subprocess_call_mock, shouter_mock):
        shell.logcommands = True
        shell.execute("doSomething")
        assert shouter_mock.shout.called

    def testSetEncodingUTF8_ShouldBeUTF8(self):
        encoding = "UTF-8"
        shell.setencoding(encoding)
        self.assertEqual(encoding, shell.encoding)

    def testSetNoEncoding_ShouldBeNone(self):
        shell.setencoding("")
        self.assertIsNone(shell.encoding)

    def testEscapeShellVariableExpansion(self):
        self.assertEqual('my simple comment', shell.escapeShellVariableExpansion('my simple comment'))
        self.assertEqual('my simple "\$"variable comment', shell.escapeShellVariableExpansion('my simple $variable comment'))
