import os


class Initializer:
    def __init__(self, config):
        self.repoName = config.gitRepoName
        self.clonedRepoName = config.clonedGitRepoName

    def createIgnore(self):
        newLine = "\n"
        with open(".gitIgnore", "w") as ignore:
            ignore.write(".jazz" + newLine)
            ignore.write(".metadata" + newLine)

    def initalize(self):
        os.system("git init --bare " + self.repoName)
        print("Repository was created in " + os.getcwd())
        os.system("git clone " + self.repoName)
        os.chdir(self.clonedRepoName)
        self.createIgnore()

    def initialCommitAndPush(self):
        os.system("git add .")
        os.system("git commit -m Initial Commit")
        os.system("git push origin")


class Commiter:
    def addAndcommit(self, changeEntry):
        os.system("git config --global user.name " + changeEntry.author)
        os.system("git add .")
        os.system("git commit -m " + changeEntry.comment)

    def branch(self, branchName):
        os.system("git checkout -b " + branchName)

    def pushBranch(self, branchName):
        os.system("git push origin " + branchName)
