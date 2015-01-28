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
        shouter.shout("Finished initial git add")
        os.system("git commit -m \"Initial Commit\"")
        os.system("git push origin master")


class Commiter:
    def addAndcommit(self, changeEntry):
        os.system("git config --global --replace-all user.name \"" + changeEntry.author + "\"")
        os.system("git add -A")
        os.system("git commit -m \"" + changeEntry.comment + "\"")

    def branch(self, branchName):
        os.system("git checkout -b " + branchName)

    def pushBranch(self, branchName):
        os.system("git push origin " + branchName)
