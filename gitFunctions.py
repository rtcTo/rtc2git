import os
import shouter
import shell


class Initializer:
    def __init__(self, config):
        self.repoName = config.gitRepoName
        self.clonedRepoName = config.clonedGitRepoName

    @staticmethod
    def createignore():
        newline = "\n"
        with open(".gitignore", "w") as ignore:
            ignore.write(".jazz5" + newline)
            ignore.write(".metadata" + newline)

    def initalize(self):
        shell.execute("git init --bare " + self.repoName)
        shouter.shout("Repository was created in " + os.getcwd())
        shell.execute("git clone " + self.repoName)
        os.chdir(self.clonedRepoName)
        self.createignore()

    @staticmethod
    def initialcommitandpush():
        shouter.shout("Initial git add")
        shell.execute("git add -A", os.devnull)
        shouter.shout("Finished initial git add, starting commit")
        shell.execute("git commit -m \"Initial%sCommit\" -q" % shell.spaceSeparator)
        shouter.shout("Finished commit")
        shell.execute("git push origin master")
        shouter.shout("Finished push")


class Commiter:

    @staticmethod
    def addandcommit(changeentry):
        message = Commiter.replacespaces(changeentry.comment)
        date = Commiter.replacespaces(changeentry.date)
        shell.execute("git config --global --replace-all user.name \"" + changeentry.author + "\"")
        shell.execute("git add -A")
        shell.execute("git commit -m \"%s\" --date %s" % (message, date))

    @staticmethod
    def replacespaces(comment):
        if comment.__contains__(' '):
            comment = comment.replace(' ', shell.spaceSeparator)
        return comment


    @staticmethod
    def branch(branchname):
        branchexist = shell.execute("git show-ref --verify --quiet refs/heads/" + branchname)
        if branchexist is 0:
            shell.execute("git checkout " + branchname)
        else:
            shell.execute("git checkout -b " + branchname)

    @staticmethod
    def pushbranch(branchname):
        shell.execute("git push origin " + branchname)
