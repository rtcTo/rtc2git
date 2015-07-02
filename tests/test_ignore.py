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

# TODO replace with class from gitFunctions
class BinaryFileFilter:

    @staticmethod
    def match(repositoryfiles):
        """
        Determine the repository files to ignore.
        These filenames are returned as a list of newline terminated lines, ready to be added to .gitignore with writelines()

        :param repositoryfiles: a list of (changed) files
        :return: a list of newline terminated file names, possibly empty
        """
        extensions = ['.zip', '.jar', '.exe', '.docx']                  # TODO make configurable
        repositoryfilestoignore = []
        for repositoryfile in repositoryfiles:
            for extension in extensions:
                if len(repositoryfile) >= len(extension):
                    if repositoryfile[-len(extension):] == extension:
                        # escape a backslash with a backslash, and append a newline
                        repositoryfilestoignore.append(repositoryfile.replace('\\', '\\\\') + '\n')
        return repositoryfilestoignore


class IgnoreTestCase(unittest.TestCase):

    def setUp(self):
        pass

    # TODO replace with method from Commiter
    def splitoutputofgitstatusz(self, line):
        """
        Split the output of  'git status -z' into single files

        :param line: the output line from the command
        :return: a list of all repository files with status changes

        [ to add to .gitignore, each backslash has to be escaped with a backslash ]
        """
        repositoryfiles = []
        entries = line.split(sep='\x00')         # ascii 0 is the delimiter
        for entry in entries:
            entry = entry.strip()
            if len(entry) > 0:
                start = entry.find(' ')
                if 1 <= start <= 2:
                    repositoryfile = entry[3:]   # output is formatted
                else:
                    repositoryfile = entry       # file on a single line (e.g. rename continuation)
                repositoryfiles.append(repositoryfile)
        return repositoryfiles

    def test_splitstatusz(self):
        with open('./resources/test_ignore_git_status_z.txt', 'r') as file:
            repositoryfiles = self.splitoutputofgitstatusz(file.readline())
            self.assertEqual(12, len(repositoryfiles))
            #for repositoryfile in repositoryfiles:
            #    print(repositoryfile)

    def test_gitstatus(self):
        # TODO first replace this with Committer.filterIgnore(config)
        # TODO write this with git init and all the stuff with a context manager of a temp dir?
        with cd('/Users/oti/stuff/gitrepo/bigbinaries'):
            strippedlines = shell.getoutput('git status -z')
            self.assertEqual(1, len(strippedlines))
            repositoryfiles = self.splitoutputofgitstatusz(strippedlines[0])
            repositoryfilestoignore = BinaryFileFilter.match(repositoryfiles)
            for repositoryfiletoignore in repositoryfilestoignore:
                print(repositoryfiletoignore)
            Commiter.ignore(repositoryfilestoignore)


