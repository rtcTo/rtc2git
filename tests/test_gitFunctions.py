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
        self.createRepo()

    def createRepo(self):
        self.repodir = tempfile.mkdtemp(prefix="gitfunctionstestcase_")
        configuration.config = Builder().setworkdirectory(self.repodir).setgitreponame("test.git").build()
        self.initializer = Initializer()
        os.chdir(self.repodir)
        self.initializer.initalize()

    def test_ExistingFileStartsWithLowerCase_RenameToUpperCase_ExpectGitRename(self):
        originalfilename = "aFileWithLowerStart"
        newfilename = "AFileWithLowerStart"

        self.simulateRenameInGitRepo(originalfilename, newfilename)
        self.assertGitStatusShowsIsRenamed()

    def assertGitStatusShowsIsRenamed(self):
        statusoutput = shell.getoutput("git status -z")
        modifier = statusoutput[0][0]
        self.assertEquals("R", modifier)

    def test_ExistingFileStartsWithUpperCase_RenameToLowerCase_ExpectGitRename(self):
        originalfilename = "AFileWithLowerStart"
        newfilename = "aFileWithLowerStart"

        self.simulateRenameInGitRepo(originalfilename, newfilename)
        self.assertGitStatusShowsIsRenamed()

    def simulateRenameInGitRepo(self, originalfilename, newfilename):
        open(originalfilename, 'a').close()  # create file
        self.initializer.initialcommitandpush()
        os.rename(originalfilename, newfilename)  # change capitalization
        shell.execute("git add -A")
        Commiter.handle_captitalization_filename_changes()


if __name__ == '__main__':
    unittest.main()
