import os
from datetime import datetime

import shouter
import shell
import configuration


class Initializer:
    def __init__(self):
        config = configuration.get()
        self.repoName = config.gitRepoName
        self.clonedRepoName = config.clonedGitRepoName
        self.author = config.user

    @staticmethod
    def createignore():
        newline = "\n"
        git_ignore = ".gitignore"

        if not os.path.exists(git_ignore):
            with open(git_ignore, "w") as ignore:
                ignore.write(".jazz5" + newline)
                ignore.write(".metadata" + newline)
                ignore.write(".jazzShed" + newline)
            shell.execute("git add " + git_ignore)
            shell.execute("git commit -m %s -q" % shell.quote("Add .gitignore"))

    def initalize(self):
        self.createrepo()
        self.preparerepo()

    @staticmethod
    def preparerepo():
        Initializer.setgitconfigs()
        Initializer.createignore()

    def createrepo(self):
        shell.execute("git init --bare " + self.repoName)
        shouter.shout("Repository was created in " + os.getcwd())
        shell.execute("git clone " + self.repoName)
        os.chdir(self.clonedRepoName)

    @staticmethod
    def setgitconfigs():
        shell.execute("git config push.default current")
        shell.execute("git config core.ignorecase false")
        shouter.shout("Set core.ignorecase to false")

    @staticmethod
    def initialcommit():
        shouter.shout("Initial git add")
        shell.execute("git add -A", os.devnull)
        shouter.shout("Finished initial git add, starting commit")
        shell.execute("git commit -m %s -q" % shell.quote("Initial Commit"))
        shouter.shout("Finished initial commit")


class Commiter:
    commitcounter = 0

    @staticmethod
    def addandcommit(changeentry):
        Commiter.replaceauthor(changeentry.author, changeentry.email)
        shell.execute("git add -A")

        Commiter.handle_captitalization_filename_changes()

        shell.execute(Commiter.getcommitcommand(changeentry))
        Commiter.commitcounter += 1
        if Commiter.commitcounter is 30:
            shouter.shout("30 Commits happend, push current branch to avoid out of memory")
            Commiter.pushbranch("")
            Commiter.commitcounter = 0
        shouter.shout("Commited change in local git repository")

    @staticmethod
    def handle_captitalization_filename_changes():
        sandbox = os.path.join(configuration.get().workDirectory, configuration.get().clonedGitRepoName)
        lines = shell.getoutput("git status -z")
        for line in lines:
            for entry in line.split(sep='\x00'):  # ascii 0 is the delimiter
                entry = entry.strip()
                if entry.startswith("A "):
                    newfilerelativepath = entry[3:]  # cut A and following space and NUL at the end
                    directoryofnewfile = os.path.dirname(os.path.join(sandbox, newfilerelativepath))
                    newfilename = os.path.basename(newfilerelativepath)
                    cwd = os.getcwd()
                    os.chdir(directoryofnewfile)
                    files = shell.getoutput("git ls-files")
                    for previousFileName in files:
                        was_same_file_name = newfilename.lower() == previousFileName.lower()
                        file_was_renamed = newfilename != previousFileName

                        if was_same_file_name and file_was_renamed:
                            shell.execute("git rm --cached %s" % previousFileName)
                    os.chdir(cwd)

    @staticmethod
    def getcommitcommand(changeentry):
        comment = Commiter.replacegitcreatingfilesymbol(changeentry.comment)
        return "git commit -m %s --date %s --author=%s" \
               % (shell.quote(comment), shell.quote(changeentry.date), changeentry.getgitauthor())

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
    def replaceauthor(author, email):
        shell.execute("git config --replace-all user.name " + shell.quote(author))
        shell.execute("git config --replace-all user.email " + email)

    @staticmethod
    def branch(branchname):
        branchexist = shell.execute("git show-ref --verify --quiet refs/heads/" + branchname)
        if branchexist is 0:
            Commiter.checkout(branchname)
        else:
            shell.execute("git checkout -b " + branchname)

    @staticmethod
    def pushbranch(branchname, force=False):
        if branchname:
            shouter.shout("Push of branch " + branchname)
        if force:
            return shell.execute("git push -f origin " + branchname)
        else:
            return shell.execute("git push origin " + branchname)

    @staticmethod
    def pushmaster():
        Commiter.pushbranch("master")

    @staticmethod
    def checkout(branchname):
        shell.execute("git checkout " + branchname)

    @staticmethod
    def renamebranch(oldname, newname):
        return shell.execute("git branch -m %s %s" % (oldname, newname))

    @staticmethod
    def promotebranchtomaster(branchname):
        masterename = Commiter.renamebranch("master", "masterRenamedAt_" + datetime.now().strftime('%H_%M_%S'))
        migratedstreamrename = Commiter.renamebranch(branchname, "master")
        if masterename is 0 and migratedstreamrename is 0:
            return Commiter.pushbranch("master", True)
        return 1  # branch couldnt get renamed


class Differ:
    @staticmethod
    def has_diff():
        return shell.execute("git diff --quiet") is 1
