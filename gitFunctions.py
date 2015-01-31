import os
import shouter


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
        os.system("git init --bare " + self.repoName)
        shouter.shout("Repository was created in " + os.getcwd())
        os.system("git clone " + self.repoName)
        os.chdir(self.clonedRepoName)
        self.createignore()

    @staticmethod
    def initialcommitandpush():
        shouter.shout("Initial git add")
        os.system("git add -A")
        shouter.shout("Finished initial git add, starting commit")
        os.system("git commit -m \"Initial Commit\" -q")
        shouter.shout("Finished commit")
        os.system("git push origin master")
        shouter.shout("Finished push")


class Commiter:
    @staticmethod
    def addandcommit(changeentry):
        os.system("git config --global --replace-all user.name \"" + changeentry.author + "\"")
        os.system("git add -A")
        os.system("git commit -m \"%s\" --date %s" % (changeentry.comment, changeentry.date))

    @staticmethod
    def branch(branchname):
        branchexist = os.system("git show-ref --verify --quiet refs/heads/" + branchname)
        if branchexist is 0:
            os.system("git checkout " + branchname)
        else:
            os.system("git checkout -b " + branchname)

    @staticmethod
    def pushbranch(branchname):
        os.system("git push origin " + branchname)
