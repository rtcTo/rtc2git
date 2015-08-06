import os
import configparser
import shutil

import shell
import shouter
import shlex

config = None


def read(configname="config.ini"):
    parsedconfig = configparser.ConfigParser()
    parsedconfig.read(configname)
    generalsection = parsedconfig['General']
    migrationsection = parsedconfig['Migration']

    user = generalsection['User']
    password = generalsection['Password']
    repositoryurl = generalsection['Repo']
    scmcommand = generalsection['ScmCommand']
    shell.logcommands = parsedconfig['Miscellaneous']['LogShellCommands'] == "True"
    shell.setencoding(generalsection['encoding'])

    workspace = shlex.quote(generalsection['WorkspaceName'])
    gitreponame = generalsection['GIT-Reponame']

    useexistingworkspace = generalsection['useExistingWorkspace']
    useprovidedhistory = migrationsection['UseProvidedHistory']
    useautomaticconflictresolution = migrationsection['UseAutomaticConflictResolution']

    workdirectory = getworkdirectory(generalsection['Directory'])
    streamname = shlex.quote(migrationsection['StreamToMigrate'].strip())
    previousstreamname = migrationsection['PreviousStream'].strip()
    baselines = getinitialcomponentbaselines(migrationsection['InitialBaseLines'])

    configbuilder = Builder().setuser(user).setpassword(password).setrepourl(repositoryurl).setscmcommand(scmcommand)
    configbuilder.setworkspace(workspace).setgitreponame(gitreponame).setrootfolder(os.getcwd())
    configbuilder.setuseexistingworkspace(useexistingworkspace).setuseprovidedhistory(useprovidedhistory)
    configbuilder.setuseautomaticconflictresolution(useautomaticconflictresolution)
    configbuilder.setworkdirectory(workdirectory).setstreamname(streamname).setinitialcomponentbaselines(baselines)
    configbuilder.setpreviousstreamname(previousstreamname)
    global config
    config = configbuilder.build()
    return config


def get():
    if not config:
        read()
    return config


def getworkdirectory(workdirectory):
    if not workdirectory:
        workdirectory = "."
    return workdirectory


def getinitialcomponentbaselines(definedbaselines):
    initialcomponentbaselines = []
    if definedbaselines:
        componentbaselines = definedbaselines.split(",")
        for entry in componentbaselines:
            componentbaseline = entry.split("=")
            component = componentbaseline[0].strip()
            baseline = componentbaseline[1].strip()
            initialcomponentbaselines.append(ComponentBaseLineEntry(component, baseline, component, baseline))
    return initialcomponentbaselines


class Builder:
    def __init__(self):
        self.user = ""
        self.password = ""
        self.repourl = ""
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
        self.gitreponame = ""
        self.clonedgitreponame = ""
        self.previousstreamname = ""
        self.ignorefileextensions = ""

    def setuser(self, user):
        self.user = user
        return self

    def setpassword(self, password):
        self.password = password
        return self

    def setrepourl(self, repourl):
        self.repourl = repourl
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

    def setinitialcomponentbaselines(self, initialcomponentbaselines):
        self.initialcomponentbaselines = initialcomponentbaselines
        return self

    def setstreamname(self, streamname):
        self.streamname = streamname
        return self

    def setgitreponame(self, reponame):
        self.gitreponame = reponame
        self.clonedgitreponame = reponame[:-4]  # cut .git
        return self

    def setuseexistingworkspace(self, useexistingworkspace):
        self.useexistingworkspace = self.isenabled(useexistingworkspace)
        return self

    def setuseprovidedhistory(self, useprovidedhistory):
        self.useprovidedhistory = self.isenabled(useprovidedhistory)
        return self

    def setuseautomaticconflictresolution(self, useautomaticconflictresolution):
        self.useautomaticconflictresolution = self.isenabled(useautomaticconflictresolution)
        return self

    def setpreviousstreamname(self, previousstreamname):
        self.previousstreamname = previousstreamname
        return self

    def setignorefileextensions(self, ignorefileextensions):
        self.ignorefileextensions = ignorefileextensions
        return self

    @staticmethod
    def isenabled(stringwithbooleanexpression):
        return stringwithbooleanexpression == "True"

    def build(self):
        return ConfigObject(self.user, self.password, self.repourl, self.scmcommand, self.workspace,
                            self.useexistingworkspace, self.workdirectory, self.initialcomponentbaselines,
                            self.streamname, self.gitreponame, self.useprovidedhistory,
                            self.useautomaticconflictresolution, self.clonedgitreponame, self.rootFolder,
                            self.previousstreamname, self.ignorefileextensions)


class ConfigObject:
    def __init__(self, user, password, repourl, scmcommand, workspace, useexistingworkspace, workdirectory,
                 initialcomponentbaselines, streamname, gitreponame, useprovidedhistory,
                 useautomaticconflictresolution, clonedgitreponame, rootfolder, previousstreamname,
                 ignorefileextensionsproperty):
        self.user = user
        self.password = password
        self.repo = repourl
        self.scmcommand = scmcommand
        self.workspace = workspace
        self.useexistingworkspace = useexistingworkspace
        self.useprovidedhistory = useprovidedhistory
        self.useautomaticconflictresolution = useautomaticconflictresolution
        self.workDirectory = workdirectory
        self.initialcomponentbaselines = initialcomponentbaselines
        self.streamname = streamname
        self.gitRepoName = gitreponame
        self.clonedGitRepoName = clonedgitreponame
        self.rootFolder = rootfolder
        self.logFolder = rootfolder + os.sep + "Logs"
        self.hasCreatedLogFolder = os.path.exists(self.logFolder)
        self.streamuuid = ""
        self.previousstreamname = previousstreamname
        self.previousstreamuuid = ""
        self.ignorefileextensions = ConfigObject.parseignorefileextensionsproperty(ignorefileextensionsproperty)

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

    def collectstreamuuid(self, streamname):
        if not streamname:
            return
        shouter.shout("Get UUID of configured stream " + streamname)
        showuuidcommand = "%s --show-alias n --show-uuid y show attributes -r %s -w %s" % (
            self.scmcommand, self.repo, streamname)
        output = shell.getoutput(showuuidcommand)
        splittedfirstline = output[0].split(" ")
        streamuuid = splittedfirstline[0].strip()[1:-1]
        return streamuuid

    def collectstreamuuids(self):
        self.streamuuid = self.collectstreamuuid(self.streamname)
        self.previousstreamuuid = self.collectstreamuuid(self.previousstreamname)

    @staticmethod
    def parseignorefileextensionsproperty(ignorefileextensionsproperty):
        """
        :param ignorefileextensionsproperty
        :return: a list of file extensions to be ignored, possibly empty
        """
        splittedextensions = []
        if ignorefileextensionsproperty and len(ignorefileextensionsproperty) > 0:
            splittedextensions = ignorefileextensionsproperty.split(',')
        ignorefileextensions = []
        for splittedextension in splittedextensions:
            ignorefileextensions.append(splittedextension.strip())
        return ignorefileextensions


class ComponentBaseLineEntry:
    def __init__(self, component, baseline, componentname, baselinename):
        self.component = component
        self.baseline = baseline
        self.componentname = componentname
        self.baselinename = baselinename
