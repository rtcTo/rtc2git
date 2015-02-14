import os

import shouter
import shell


class Initializer:
    def __init__(self, config):
        self.repoName = config.gitRepoName
        self.clonedRepoName = config.clonedGitRepoName
        self.author = config.user

    @staticmethod
    def createignore():
        newline = "\n"
        with open(".gitignore", "w") as ignore:
            ignore.write(".jazz5" + newline)
            ignore.write(".metadata" + newline)
            ignore.write(".jazzShed" + newline)

    def initalize(self):
        shell.execute("git init --bare " + self.repoName)
        shouter.shout("Repository was created in " + os.getcwd())
        shell.execute("git clone " + self.repoName)
        os.chdir(self.clonedRepoName)
        Commiter.replaceauthor(self.author)
        shell.execute("git config push.default current")
        self.createignore()

    @staticmethod
    def initialcommitandpush():
        shouter.shout("Initial git add")
        shell.execute("git add -A", os.devnull)
        shouter.shout("Finished initial git add, starting commit")
        shell.execute("git commit -m %s -q" % shell.quote("Initial Commit"))
        shouter.shout("Finished commit")
        shell.execute("git push origin master")
        shouter.shout("Finished push")


class Commiter:
    commitcounter = 0

    @staticmethod
    def addandcommit(changeentry):
        comment = Commiter.replacegitcreatingfilesymbol(changeentry.comment)
        Commiter.replaceauthor(changeentry.author)
        shell.execute("git add -A")
        shell.execute("git commit -m %s --date %s" % (shell.quote(comment), shell.quote(changeentry.date)))
        Commiter.commitcounter += 1
        if Commiter.commitcounter % 100 is 0:
            Commiter.pushbranch("")


    @staticmethod
    def replacegitcreatingfilesymbol(comment):
        return Commiter.replacewords(" to ", comment, "-->", "->", ">")

    @staticmethod
    def replacewords(replacedwith, word, *replacingstrings):
        for replacingstring in replacingstrings:
            if replacingstring in word:
                word = word.replace(replacingstring, replacedwith)
        return word

    @staticmethod
    def replaceauthor(author):
        shell.execute("git config --replace-all user.name " + shell.quote(author))

    @staticmethod
    def branch(branchname):
        branchexist = shell.execute("git show-ref --verify --quiet refs/heads/" + branchname)
        if branchexist is 0:
            shell.execute("git checkout " + branchname)
        else:
            shell.execute("git checkout -b " + branchname)

    @staticmethod
    def pushbranch(branchname):
        shouter.shout("Push branch " + branchname)
        shell.execute("git push origin " + branchname)
