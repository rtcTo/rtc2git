__author__ = 'Manuel'

import unittest
import os
import time

from gitFunctions import Commiter, Initializer
from configuration import Builder
import shell
import configuration
from tests import testhelper


class GitFunctionsTestCase(unittest.TestCase):

    def setUp(self):
        self.cwd = os.getcwd()

    def tearDown(self):
        configuration.config = None
        os.chdir(self.cwd)

    def test_ExistingFileStartsWithLowerCase_RenameToUpperCase_ExpectGitRename(self):
        with testhelper.createrepo(folderprefix="gitfunctionstestcase_"):
            originalfilename = "aFileWithLowerStart"
            newfilename = "AFileWithLowerStart"

            self.simulateCreationAndRenameInGitRepo(originalfilename, newfilename)
            self.assertGitStatusShowsIsRenamed()

    def assertGitStatusShowsIsRenamed(self):
        statusoutput = shell.getoutput("git status -z")
        modifier = statusoutput[0][0]
        self.assertEquals("R", modifier)

    def test_ExistingFileStartsWithUpperCase_RenameToLowerCase_ExpectGitRename(self):
        with testhelper.createrepo(folderprefix="gitfunctionstestcase_"):
            originalfilename = "AFileWithLowerStart"
            newfilename = "aFileWithLowerStart"

            self.simulateCreationAndRenameInGitRepo(originalfilename, newfilename)
            self.assertGitStatusShowsIsRenamed()

    def test_ExistingFileStartsWithUpperCaseInSubFolder_RenameToLowerCase_ExpectGitRename(self):
        with testhelper.createrepo(folderprefix="gitfunctionstestcase_"):
            originalfilename = "AFileWithLowerStart"
            newfilename = "aFileWithLowerStart"
            subfolder = "test"
            create_and_change_directory(subfolder)

            self.simulateCreationAndRenameInGitRepo(originalfilename, newfilename)
            self.assertGitStatusShowsIsRenamed()

    # test for issue #39
    def test_ExistingDirStartsWithUpperCaseA_RenameChildFile_ExpectGitRename(self):
        with testhelper.createrepo(folderprefix="gitfunctionstestcase_"):
            originalfilename = "AFileWithLowerStart"
            newfilename = "aFileWithLowerStart"
            subfolder = "Afolder"  # this is key to reproduce #39
            create_and_change_directory(subfolder)

            self.simulateCreationAndRenameInGitRepo(originalfilename, newfilename)
            self.assertGitStatusShowsIsRenamed()

    def test_CreationOfGitIgnore_ExistAlready_ShouldntGetCreated(self):
        with testhelper.mkchdir("aFolder") as folder:
            configuration.config = Builder().setworkdirectory(folder).setgitreponame("test.git").build()
            ignore = '.gitignore'
            existing_git_ignore_entry = "test"
            Initializer().createrepo()
            with open(ignore, 'w') as gitIgnore:
                gitIgnore.write(existing_git_ignore_entry)
            Initializer.createignore()
            with open(ignore, 'r') as gitIgnore:
                for line in gitIgnore.readlines():
                    self.assertEqual(existing_git_ignore_entry, line)

    def test_CreationOfGitIgnore_DoesntExist_ShouldGetCreated(self):
        with testhelper.mkchdir("aFolder") as folder:
            configuration.config = Builder().setworkdirectory(folder).setgitreponame("test.git").build()
            ignore = '.gitignore'
            Initializer().createrepo()
            Initializer.createignore()
            gitignorepath = os.path.join(os.getcwd(), ignore)
            self.assertTrue(os.path.exists(gitignorepath))

    def test_BranchRenaming_TargetBranchDoesntExist(self):
        with testhelper.createrepo(folderprefix="gitfunctionstestcase_"):
            branchname = "hello"
            Commiter.branch(branchname)
            self.assertEqual(0, Commiter.promotecurrentbranchtomaster())

    def test_BranchRenaming_TargetBranchExist_ShouldntFail(self):
        with testhelper.createrepo(folderprefix="gitfunctionstestcase_"):
            branchname = "hello"
            Commiter.branch(branchname)
            self.assertEqual(0, Commiter.promotecurrentbranchtomaster())
            time.sleep(1)
            self.assertEqual(0, Commiter.promotecurrentbranchtomaster())

    def simulateCreationAndRenameInGitRepo(self, originalfilename, newfilename):
        open(originalfilename, 'a').close()  # create file
        Initializer.initialcommit()
        Commiter.pushmaster()
        os.rename(originalfilename, newfilename)  # change capitalization
        shell.execute("git add -A")
        Commiter.handle_captitalization_filename_changes()


def create_and_change_directory(subfolder):
    os.mkdir(subfolder)
    os.chdir(subfolder)



if __name__ == '__main__':
    unittest.main()
