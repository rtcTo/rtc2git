from contextlib import contextmanager
import os
import unittest

import shell
from gitFunctions import Commiter


@contextmanager
def cd(newdir):
    """
    Change directory to newdir and return to the previous upon completion
    :param newdir: directory to change to
    """
    previousdir = os.getcwd()
    os.chdir(os.path.expanduser(newdir))
    try:
        yield
    finally:
        os.chdir(previousdir)


class IgnoreTestCase(unittest.TestCase):

    def setUp(self):
        pass

    def test_splitstatusz(self):
        with open('./resources/test_ignore_git_status_z.txt', 'r') as file:
            repositoryfiles = Commiter.splitoutputofgitstatusz(file.readline())
            self.assertEqual(12, len(repositoryfiles))

    def __test_gitstatus(self):
        # TODO first replace this with Committer.filterIgnore(config)
        # TODO write this with git init and all the stuff with a context manager of a temp dir?
        with cd('/Users/oti/stuff/gitrepo/bigbinaries'):
            strippedlines = shell.getoutput('git status -z')
            self.assertEqual(1, len(strippedlines))
            repositoryfiles = Commiter.splitoutputofgitstatusz(strippedlines[0])
            repositoryfilestoignore = BinaryFileFilter.match(repositoryfiles)
            for repositoryfiletoignore in repositoryfilestoignore:
                print(repositoryfiletoignore)
            Commiter.ignore(repositoryfilestoignore)


