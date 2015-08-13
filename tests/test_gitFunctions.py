__author__ = 'Manuel'

import unittest
import os
import tempfile
from contextlib import contextmanager
import shutil
import time

from gitFunctions import Commiter, Initializer
from configuration import Builder
import shell
import configuration


class GitFunctionsTestCase(unittest.TestCase):

    def setUp(self):
        self.cwd = os.getcwd()

    def tearDown(self):
        configuration.config = None
        os.chdir(self.cwd)

    @contextmanager
    def createRepo(self):
        self.repodir = tempfile.mkdtemp(prefix="gitfunctionstestcase_")
        configuration.config = Builder().setworkdirectory(self.repodir).setgitreponame("test.git").build()
        self.initializer = Initializer()
        os.chdir(self.repodir)
        self.initializer.initalize()
        try:
            yield
        finally:
            shutil.rmtree(self.repodir, ignore_errors=True)  # on windows folder remains in temp, git process locks it

    def test_ExistingFileStartsWithLowerCase_RenameToUpperCase_ExpectGitRename(self):
        with self.createRepo():
            originalfilename = "aFileWithLowerStart"
            newfilename = "AFileWithLowerStart"

            self.simulateCreationAndRenameInGitRepo(originalfilename, newfilename)
            self.assertGitStatusShowsIsRenamed()

    def assertGitStatusShowsIsRenamed(self):
        statusoutput = shell.getoutput("git status -z")
        modifier = statusoutput[0][0]
        self.assertEquals("R", modifier)

    def test_ExistingFileStartsWithUpperCase_RenameToLowerCase_ExpectGitRename(self):
        with self.createRepo():
            originalfilename = "AFileWithLowerStart"
            newfilename = "aFileWithLowerStart"

            self.simulateCreationAndRenameInGitRepo(originalfilename, newfilename)
            self.assertGitStatusShowsIsRenamed()

    def test_ExistingFileStartsWithUpperCaseInSubFolder_RenameToLowerCase_ExpectGitRename(self):
        with self.createRepo():
            originalfilename = "AFileWithLowerStart"
            newfilename = "aFileWithLowerStart"
            subfolder = "test"
            create_and_change_directory(subfolder)

            self.simulateCreationAndRenameInGitRepo(originalfilename, newfilename)
            self.assertGitStatusShowsIsRenamed()

    # test for issue #39
    def test_ExistingDirStartsWithUpperCaseA_RenameChildFile_ExpectGitRename(self):
        with self.createRepo():
            originalfilename = "AFileWithLowerStart"
            newfilename = "aFileWithLowerStart"
            subfolder = "Afolder"  # this is key to reproduce #39
            create_and_change_directory(subfolder)

            self.simulateCreationAndRenameInGitRepo(originalfilename, newfilename)
            self.assertGitStatusShowsIsRenamed()

    def test_CreationOfGitIgnore_ExistAlready_ShouldntGetCreated(self):
        with mkchdir("aFolder") as folder:
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
        with mkchdir("aFolder") as folder:
            configuration.config = Builder().setworkdirectory(folder).setgitreponame("test.git").build()
            ignore = '.gitignore'
            Initializer().createrepo()
            Initializer.createignore()
            gitignorepath = os.path.join(os.getcwd(), ignore)
            self.assertTrue(os.path.exists(gitignorepath))

    def test_BranchRenaming_TargetBranchDoesntExist(self):
        with self.createRepo():
            branchname = "hello"
            Commiter.branch(branchname)
            self.assertEqual(0, Commiter.promotebranchtomaster(branchname))

    def test_BranchRenaming_TargetBranchExist_ShouldntFail(self):
        with self.createRepo():
            branchname = "hello"
            Commiter.branch(branchname)
            self.assertEqual(0, Commiter.promotebranchtomaster(branchname))
            time.sleep(1)
            self.assertEqual(1, Commiter.promotebranchtomaster(branchname))

    def simulateCreationAndRenameInGitRepo(self, originalfilename, newfilename):
        open(originalfilename, 'a').close()  # create file
        self.initializer.initialcommit()
        Commiter.pushmaster()
        os.rename(originalfilename, newfilename)  # change capitalization
        shell.execute("git add -A")
        Commiter.handle_captitalization_filename_changes()


def create_and_change_directory(subfolder):
    os.mkdir(subfolder)
    os.chdir(subfolder)


@contextmanager
def mkchdir(subfolder):
    tempfolder = tempfile.mkdtemp(prefix="gitfunctionstestcase_" + subfolder)
    os.chdir(tempfolder)
    try:
        yield tempfolder
    finally:
        shutil.rmtree(tempfolder, ignore_errors=True)  # on windows folder remains in temp, git process locks it


if __name__ == '__main__':
    unittest.main()
