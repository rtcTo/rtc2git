import unittest

class IgnoreTestCase(unittest.TestCase):

    def setUp(self):
        pass

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
            for repositoryfile in repositoryfiles:
                print(repositoryfile)
