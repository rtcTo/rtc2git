import os

from rtc2git import shouter


class Initializer:
    def __init__(self, config):
        self.repoName = config.gitRepoName
        self.clonedRepoName = config.clonedGitRepoName

    def createIgnore(self):
        newLine = "\n"
        with open(".gitignore", "w") as ignore:
            ignore.write(".jazz5" + newLine)
            ignore.write(".metadata" + newLine)

    def initalize(self):
        os.system("git init --bare " + self.repoName)
        shouter.shout("Repository was created in " + os.getcwd())
        os.system("git clone " + self.repoName)
        os.chdir(self.clonedRepoName)
        self.createIgnore()

    def initialCommitAndPush(self):
        shouter.shout("Initial git add")
        os.system("git add -A")
        shouter.shout("Finished initial git add, starting commit")
        os.system("git commit -m \"Initial Commit\"")
        shouter.shout("Finished commit")
        os.system("git push origin master")
        shouter.shout("Finished push")


class Commiter:
    def addAndcommit(self, changeEntry):
        os.system("git config --global --replace-all user.name \"" + changeEntry.author + "\"")
        os.system("git add -A")
        os.system("git commit -m \"%s\" --date %s" % (changeEntry.comment, changeEntry.date))

    def branch(self, branchName):
        branchExist = os.system("git show-ref --verify --quiet refs/heads/" + branchName)
        if branchExist is 0:
            os.system("git checkout " + branchName)
        else:
            os.system("git checkout -b " + branchName)

    def pushBranch(self, branchName):
        os.system("git push origin " + branchName)
