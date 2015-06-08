import os
import configparser
import shutil

from rtcFunctions import ComponentBaseLineEntry
import shell
import shouter


def read():
    config = configparser.ConfigParser()
    config.read("config.ini")
    generalsection = config['General']
    user = generalsection['User']
    password = generalsection['Password']
    workspace = generalsection['WorkspaceName']
    useexistingworkspace = bool(generalsection['useExistingWorkspace'])
    repositoryurl = generalsection['Repo']
    scmcommand = generalsection['ScmCommand']
    workdirectory = generalsection['Directory']
    if not workdirectory:
        workdirectory = "."
    migrationsection = config['Migration']
    streamname = migrationsection['StreamToMigrate'].strip()
    initialcomponentbaselines = []
    definedbaselines = migrationsection['InitialBaseLines']
    if definedbaselines:
        componentbaselines = definedbaselines.split(",")
        for entry in componentbaselines:
            componentbaseline = entry.split("=")
            component = componentbaseline[0].strip()
            baseline = componentbaseline[1].strip()
            initialcomponentbaselines.append(ComponentBaseLineEntry(component, baseline, component, baseline))
    gitreponame = generalsection['GIT-Reponame']
    useprovidedhistory = bool(migrationsection['UseProvidedHistory'])
    useautomaticconflictresolution = bool(migrationsection['UseAutomaticConflictResolution'])
    shell.logcommands = bool(config['Miscellaneous']['LogShellCommands'])
    return ConfigObject(user, password, repositoryurl, scmcommand, workspace, useexistingworkspace, workdirectory,
                        initialcomponentbaselines, streamname,
                        gitreponame, useprovidedhistory, useautomaticconflictresolution)


class ConfigObject:
    def __init__(self, user, password, repo, scmcommand, workspace, useexistingworkspace, workdirectory,
                 initialcomponentbaselines, streamname, gitreponame, useprovidedhistory,
                 useautomaticconflictresolution):
        self.user = user
        self.password = password
        self.repo = repo
        self.scmcommand = scmcommand
        self.workspace = workspace
        self.useexistingworkspace = useexistingworkspace == "True"
        self.useprovidedhistory = useprovidedhistory == "True"
        self.useautomaticconflictresolution = useautomaticconflictresolution == "True"
        self.workDirectory = workdirectory
        self.initialcomponentbaselines = initialcomponentbaselines
        self.streamname = streamname
        self.gitRepoName = gitreponame
        self.clonedGitRepoName = gitreponame[:-4]  # cut .git
        self.rootFolder = os.getcwd()
        self.logFolder = self.rootFolder + os.sep + "Logs"
        self.hasCreatedLogFolder = os.path.exists(self.logFolder)
        self.streamuuid = ""

    def getlogpath(self, filename):
        if not self.hasCreatedLogFolder:
            os.makedirs(self.logFolder)
            self.hasCreatedLogFolder = True
        return self.logFolder + os.sep + filename

    def deletelogfolder(self):
        if self.hasCreatedLogFolder:
            shutil.rmtree(self.logFolder)
            self.hasCreatedLogFolder = False

    def gethistorypath(self, filename):
        historypath = self.rootFolder + os.sep + "History"
        return historypath + os.sep + filename

    def collectstreamuuid(self):
        shouter.shout("Get UUID of configured stream")
        showuuidcommand = "%s --show-alias n --show-uuid y show attributes -r %s -w %s" % (
            self.scmcommand, self.repo, self.streamname)
        output = shell.getoutput(showuuidcommand)
        splittedfirstline = output[0].split(" ")
        self.streamuuid = splittedfirstline[0].strip()[1:-1]


class Builder:
    def __init__(self):
        self.user = ""
        self.password = ""
        self.repo = ""
        self.scmcommand = "lscm"
        self.workspace = ""
        self.useexistingworkspace = ""
        self.useprovidedhistory = ""
        self.useautomaticconflictresolution = ""
        self.workdirectory = os.path.dirname(os.path.realpath(__file__))
        self.rootFolder = self.workdirectory
        self.logFolder = self.rootFolder + os.sep + "Logs"
        self.hasCreatedLogFolder = os.path.exists(self.logFolder)
        self.initialcomponentbaselines = ""
        self.streamname = ""
        self.streamuuid = ""
        self.gitreponame = ""
        self.clonedgitreponame = ""

    def setuser(self, user):
        self.user = user
        return self

    def setpassword(self, password):
        self.password = password
        return self

    def setrepo(self, repo):
        self.repo = repo
        return self

    def setscmcommand(self, scmcommand):
        self.scmcommand = scmcommand
        return self

    def setworkspace(self, workspace):
        self.workspace = workspace
        return self

    def setworkdirectory(self, workdirectory):
        self.workdirectory = workdirectory
        return self

    def setrootfolder(self, rootfolder):
        self.rootFolder = rootfolder
        return self

    def setlogfolder(self, logfolder):
        self.logFolder = logfolder
        return self

    def sethascreatedlogfolder(self, hascreatedlogfolder):
        self.hasCreatedLogFolder = bool(hascreatedlogfolder)
        return self

    def setinitialcomponentbaselines(self, initialcomponentbaselines):
        self.initialcomponentbaselines = initialcomponentbaselines
        return self

    def setstreamname(self, streamname):
        self.streamname = streamname
        return self

    def setstreamuuid(self, streamuuid):
        self.streamuuid = streamuuid
        return self

    def setgitreponame(self, reponame):
        self.gitreponame = reponame
        return self

    def build(self):
        return ConfigObject(self.user, self.password, self.repo, self.scmcommand, self.workspace,
                            self.useexistingworkspace, self.workdirectory, self.initialcomponentbaselines,
                            self.streamname, self.gitreponame, self.useprovidedhistory,
                            self.useautomaticconflictresolution)
