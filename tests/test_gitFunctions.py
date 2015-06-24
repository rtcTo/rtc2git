import unittest
import os

from gitFunctions import Differ


class GitFunctionsTestCase(unittest.TestCase):
    afilepath = None

    def setUp(self):
        with open("somechange", 'a') as file:
            self.afilepath = file.name

    def tearDown(self):
        if os.path.exists(self.afilepath):
            os.remove(self.afilepath)

    def test_WhenUncommitedFile_HasDiffShouldReturnTrue(self):
        self.assertTrue(Differ.has_diff())

    """
    Test fails in case not every change in this git repo is commited
    """

    def test_WhenUncommitedFile_HasDiffShouldReturnFalse(self):
        os.remove(self.afilepath)
        self.assertFalse(Differ.has_diff())


if __name__ == '__main__':
    unittest.main()
