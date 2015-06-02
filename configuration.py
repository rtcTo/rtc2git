import os
import configparser

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
    useexistingworkspace = generalsection['useExistingWorkspace']
    repositoryurl = generalsection['Repo']
    scmcommand = generalsection['ScmCommand']
    workdirectory = generalsection['Directory']
    if not workdirectory:
        workdirectory = "."
    migrationsection = config['Migration']
    oldeststream = migrationsection['OldestStream']
    streamsfromconfig = migrationsection['StreamsToMigrate']
    streamnames = getstreamnames(streamsfromconfig)
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
    useprovidedhistory = migrationsection['UseProvidedHistory']
    useautomaticconflictresolution = migrationsection['UseAutomaticConflictResolution']
    shell.logcommands = config['Miscellaneous']['LogShellCommands'] == "True"
    return ConfigObject(user, password, repositoryurl, scmcommand, workspace, useexistingworkspace, workdirectory,
                        initialcomponentbaselines, streamnames,
                        gitreponame, oldeststream, useprovidedhistory, useautomaticconflictresolution)


def getstreamnames(streamsfromconfig):
    streamnames = []
    for streamname in streamsfromconfig.split(","):
        streamname = streamname.strip()
        streamnames.append(streamname)
    return streamnames


class ConfigObject:
    def __init__(self, user, password, repo, scmcommand, workspace, useexistingworkspace, workdirectory, initialcomponentbaselines,
                 streamnames,
                 gitreponame, oldeststream, useprovidedhistory, useautomaticconflictresolution):
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
        self.streamnames = streamnames
        self.earlieststreamname = oldeststream
        self.gitRepoName = gitreponame
        self.clonedGitRepoName = gitreponame[:-4]  # cut .git
        self.rootFolder = os.getcwd()
        self.logFolder = os.getcwd() + os.sep + "Logs"
        self.streamuuids = []

    def getlogpath(self, filename):
        if not os.path.exists(self.logFolder):
            os.makedirs(self.logFolder)
        return self.logFolder + os.sep + filename

    def gethistorypath(self, filename):
        historypath = self.rootFolder + os.sep + "History"
        return historypath + os.sep + filename

    def collectstreamuuids(self):
        shouter.shout("Get UUID's of configured streamnames")
        for streamname in self.streamnames:
            streamname = streamname.strip()
            showuuidcommand = "%s --show-alias n --show-uuid y show attributes -r %s -w %s" % (self.scmcommand, self.repo, streamname)
            output = shell.getoutput(showuuidcommand)
            splittedfirstline = output[0].split(" ")
            streamuuid = splittedfirstline[0].strip()[1:-1]
            self.streamuuids.append(streamuuid)












