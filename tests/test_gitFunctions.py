import unittest
import os
import time

import shell
import configuration
from gitFunctions import Commiter, Initializer
from configuration import Builder
from tests import testhelper


class GitFunctionsTestCase(unittest.TestCase):

    def setUp(self):
        self.cwd = os.getcwd()
        configuration.config = Builder().build()

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
        self.assertEqual("R", modifier)

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
            self.assertEqual(0, Commiter.promotebranchtomaster(branchname))

    def test_BranchRenaming_TargetBranchExist_ShouldBeSuccessful(self):
        with testhelper.createrepo(folderprefix="gitfunctionstestcase_"):
            branchname = "hello"
            Commiter.branch(branchname)
            self.assertEqual(0, Commiter.promotebranchtomaster(branchname))
            time.sleep(1)
            self.assertEqual(0, Commiter.promotebranchtomaster(branchname))

    def test_BranchRenaming_TwoCallsAtTheSameTime_ShouldFail(self):
        with testhelper.createrepo(folderprefix="gitfunctionstestcase_"):
            branchname = "hello"
            Commiter.branch(branchname)
            self.assertEqual(0, Commiter.promotebranchtomaster(branchname))
            self.assertEqual(1, Commiter.promotebranchtomaster(branchname))

    def test_CopyBranch_TargetDoesntExist_ShouldBeSucessful(self):
        with testhelper.createrepo(folderprefix="gitfunctionstestcase_"):
            branchname = "hello"
            self.assertEqual(0, Commiter.copybranch("master", branchname))

    def test_CopyBranch_TargetAlreadyExist_ShouldFail(self):
        with testhelper.createrepo(folderprefix="gitfunctionstestcase_"):
            branchname = "hello"
            Commiter.branch(branchname)
            self.assertFalse(Commiter.copybranch("master", branchname) is 0)

    def test_splitoutputofgitstatusz(self):
        with open(testhelper.getrelativefilename('./resources/test_ignore_git_status_z.txt'), 'r') as file:
            repositoryfiles = Commiter.splitoutputofgitstatusz(file.readlines())
            self.assertEqual(12, len(repositoryfiles))
            self.assertEqual('project1/src/tobedeleted.txt', repositoryfiles[0])
            self.assertEqual('project2/src/taka.txt', repositoryfiles[1])
            self.assertEqual('project1/src/taka.txt', repositoryfiles[2]) # rename continuation would bite here
            self.assertEqual('project2/src/takatuka.txt', repositoryfiles[3])
            self.assertEqual('project2/src/tuka.txt', repositoryfiles[4])
            self.assertEqual('project1/src/sub/kling -- klong.zip', repositoryfiles[5])
            self.assertEqual('project1/src/sub/kling :and: klong.zip', repositoryfiles[6])
            self.assertEqual('project1/src/sub/kling ;and; klong.zip', repositoryfiles[7])
            self.assertEqual('project1/src/sub/kling >and< klong.zip', repositoryfiles[8])
            self.assertEqual('project1/src/sub/kling \\and\\ klong.zip', repositoryfiles[9])
            self.assertEqual('project1/src/sub/kling |and| klong.zip', repositoryfiles[10])
            self.assertEqual('project1/src/sub/klingklong.zip', repositoryfiles[11])

    def test_splitoutputofgitstatusz_filterprefix_A(self):
        with open(testhelper.getrelativefilename('./resources/test_ignore_git_status_z.txt'), 'r') as file:
            repositoryfiles = Commiter.splitoutputofgitstatusz(file.readlines(), 'A  ')
            self.assertEqual(1, len(repositoryfiles))
            self.assertEqual('project1/src/tobedeleted.txt', repositoryfiles[0])

    def test_splitoutputofgitstatusz_filterprefix_double_question(self):
        with open(testhelper.getrelativefilename('./resources/test_ignore_git_status_z.txt'), 'r') as file:
            repositoryfiles = Commiter.splitoutputofgitstatusz(file.readlines(), '?? ')
            self.assertEqual(7, len(repositoryfiles))
            self.assertEqual('project1/src/sub/kling -- klong.zip', repositoryfiles[0])
            self.assertEqual('project1/src/sub/kling :and: klong.zip', repositoryfiles[1])
            self.assertEqual('project1/src/sub/kling ;and; klong.zip', repositoryfiles[2])
            self.assertEqual('project1/src/sub/kling >and< klong.zip', repositoryfiles[3])
            self.assertEqual('project1/src/sub/kling \\and\\ klong.zip', repositoryfiles[4])
            self.assertEqual('project1/src/sub/kling |and| klong.zip', repositoryfiles[5])
            self.assertEqual('project1/src/sub/klingklong.zip', repositoryfiles[6])

    def test_filterignore(self):
        with testhelper.mkchdir("aFolder") as folder:
            # create test repo
            configuration.config = Builder().setworkdirectory(folder).setgitreponame("test.git").setignorefileextensions('.zip; .jar').build()
            ignore = '.gitignore'
            Initializer().createrepo()
            # simulate addition of .zip and .jar files
            zip = 'test.zip'
            with open(zip, 'w') as testzip:
                testzip.write('test zip content')
            jar = 'test.jar'
            with open(jar, 'w') as testjar:
                testjar.write('test jar content')
            # do the filtering
            Commiter.filterignore()
            # check output of .gitignore
            with open(ignore, 'r') as gitIgnore:
                lines = gitIgnore.readlines()
                self.assertEqual(2, len(lines))
                lines.sort()
                self.assertEqual(jar, lines[0].strip())
                self.assertEqual(zip, lines[1].strip())

    def test_checkbranchname_expect_valid(self):
        with testhelper.createrepo(folderprefix="gitfunctionstestcase_"):
            self.assertEqual(True, Commiter.checkbranchname("master"), "master should be a valid branch name")

    def test_checkbranchname_quoted_expect_invalid(self):
        with testhelper.createrepo(folderprefix="gitfunctionstestcase_"):
            self.assertEqual(False, Commiter.checkbranchname("'master pflaster'"),
                             "'master pflaster' should not be a valid branch name")

    def test_checkbranchname_unquoted_expect_invalid(self):
        with testhelper.createrepo(folderprefix="gitfunctionstestcase_"):
            self.assertEqual(False, Commiter.checkbranchname("master pflaster"),
                             "master pflaster should not be a valid branch name")

    def test_getcommentwithprefix_enabled_commitisattached_shouldreturnwithprefix(self):
        prefix = "APREFIX-"
        configuration.config = Builder().setcommitmessageprefix(prefix)
        comment = "1337: Upgrade to Wildfly - A comment"
        expectedcomment = prefix + comment
        self.assertEqual(expectedcomment, Commiter.getcommentwithprefix(comment))

    def test_getcommentwithprefix_enabled_commitisattached_containsspecialchars_shouldreturnwithprefix(self):
        prefix = "PR-"
        configuration.config = Builder().setcommitmessageprefix(prefix)
        comment = "1338: VAT: VAT-Conditions defined with 0 % and 0 amount - reverse"
        expectedcomment = prefix + comment
        self.assertEqual(expectedcomment, Commiter.getcommentwithprefix(comment))

    def test_getcommentwithprefix_disabled_commitisattached_shouldreturncommentwithoutprefix(self):
        configuration.config = Builder().setcommitmessageprefix("")
        comment = "1337: Upgrade to Wildfly - A comment"
        self.assertEqual(comment, Commiter.getcommentwithprefix(comment))

    def test_getcommentwithprefix_enabled_commitisnotattachedtoanworkitem_shouldreturncommentwithoutprefix(self):
        configuration.config = Builder().setcommitmessageprefix("PR-")
        comment = "US1337: Fix some problems"
        self.assertEqual(comment, Commiter.getcommentwithprefix(comment))

    def test_IllegalGitCharsShouldntCreateFile_Arrow(self):
        with testhelper.createrepo(folderprefix="gitfunctionstestcase_"):
            Commiter.addandcommit(testhelper.createchangeentry(comment="Some commit -> Bad"))
            self.assertEqual(0, len(shell.getoutput("git status -z")), "No file should be created by commit message")

    def test_IllegalGitCharsShouldntCreateFile_LongArrow(self):
        with testhelper.createrepo(folderprefix="gitfunctionstestcase_"):
            Commiter.addandcommit(testhelper.createchangeentry(comment="Some commit --> Worse"))
            self.assertEqual(0, len(shell.getoutput("git status -z")), "No file should be created by commit message")

    def test_IllegalGitCharsShouldntCreateFile_NoCommentCase(self):
        with testhelper.createrepo(folderprefix="gitfunctionstestcase_"):
            Commiter.addandcommit(testhelper.createchangeentry(comment="<No Comment>"))
            self.assertEqual(0, len(shell.getoutput("git status -z")), "No file should be created by commit message")

    def test_IllegalGitCharsShouldntCreateFile_SpecialCaseAlreadyQuoted(self):
        with testhelper.createrepo(folderprefix="gitfunctionstestcase_"):
            Commiter.addandcommit(testhelper.createchangeentry(comment="Check out \"" + ">" + "\"US3333\""))
            self.assertEqual(0, len(shell.getoutput("git status -z")), "No file should be created by commit message")

    def test_translatejazzignore(self):
        with open(testhelper.getrelativefilename('./resources/test_.jazzignore'), 'r') as jazzignore:
            inputlines = jazzignore.readlines()
        with open(testhelper.getrelativefilename('./resources/test_.gitignore'), 'r') as gitignore:
            expectedlines = gitignore.readlines()
        self.assertEqual(expectedlines, Commiter.translatejazzignore(inputlines))


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
