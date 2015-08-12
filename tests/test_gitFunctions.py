__author__ = 'Manuel'

import unittest
import os
import tempfile

from gitFunctions import Commiter, Initializer
from configuration import Builder
import shell
import configuration


class GitFunctionsTestCase(unittest.TestCase):
    def setUp(self):
        self.cwd = os.getcwd()
        self.createRepo()

    def tearDown(self):
        configuration.config = None
        os.chdir(self.cwd)

    def createRepo(self):
        self.repodir = tempfile.mkdtemp(prefix="gitfunctionstestcase_")
        configuration.config = Builder().setworkdirectory(self.repodir).setgitreponame("test.git").build()
        self.initializer = Initializer()
        os.chdir(self.repodir)
        self.initializer.initalize()

    def test_ExistingFileStartsWithLowerCase_RenameToUpperCase_ExpectGitRename(self):
        originalfilename = "aFileWithLowerStart"
        newfilename = "AFileWithLowerStart"

        self.simulateCreationAndRenameInGitRepo(originalfilename, newfilename)
        self.assertGitStatusShowsIsRenamed()

    def assertGitStatusShowsIsRenamed(self):
        statusoutput = shell.getoutput("git status -z")
        modifier = statusoutput[0][0]
        self.assertEquals("R", modifier)

    def test_ExistingFileStartsWithUpperCase_RenameToLowerCase_ExpectGitRename(self):
        originalfilename = "AFileWithLowerStart"
        newfilename = "aFileWithLowerStart"

        self.simulateCreationAndRenameInGitRepo(originalfilename, newfilename)
        self.assertGitStatusShowsIsRenamed()

    def test_ExistingFileStartsWithUpperCaseInSubFolder_RenameToLowerCase_ExpectGitRename(self):
        originalfilename = "AFileWithLowerStart"
        newfilename = "aFileWithLowerStart"
        subfolder = "test"
        os.mkdir(subfolder)
        os.chdir(subfolder)

        self.simulateCreationAndRenameInGitRepo(originalfilename, newfilename)
        self.assertGitStatusShowsIsRenamed()

    # test for issue #39
    def test_ExistingDirStartsWithUpperCaseA_RenameChildFile_ExpectGitRename(self):
        originalfilename = "AFileWithLowerStart"
        newfilename = "aFileWithLowerStart"
        subfolder = "Afolder" # this is key to reproduce #39
        os.mkdir(subfolder)
        os.chdir(subfolder)

        self.simulateCreationAndRenameInGitRepo(originalfilename, newfilename)
        self.assertGitStatusShowsIsRenamed()

    def simulateCreationAndRenameInGitRepo(self, originalfilename, newfilename):
        open(originalfilename, 'a').close()  # create file
        self.initializer.initialcommitandpush()
        os.rename(originalfilename, newfilename)  # change capitalization
        shell.execute("git add -A")
        Commiter.handle_captitalization_filename_changes()


if __name__ == '__main__':
    unittest.main()
