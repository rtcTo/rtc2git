import os
import configparser

import shell
import shouter


def readconfig():
    config = configparser.ConfigParser()
    config.read("config.ini")
    generalsection = config['General']
    user = generalsection['User']
    password = generalsection['Password']
    workspace = generalsection['WorkspaceName']
    repositoryurl = generalsection['Repo']
    mainstream = generalsection['Stream']
    workdirectory = generalsection['Directory']
    if not workdirectory:
        workdirectory = "."
    migrationsection = config['Migration']
    streamsfromconfig = migrationsection['Streams']
    streamnames = getstreamnames(streamsfromconfig)
    initialcomponentbaselines = []
    definedbaselines = ""  # migrationsection['InitialBaseLine']
    if definedbaselines:
        componentbaselines = definedbaselines.split(",")
        for entry in componentbaselines:
            componentbaseline = entry.split("=")
            component = componentbaseline[0].strip()
            baseline = componentbaseline[1].strip()
            if " " in baseline:
                baseline = baseline.replace(" ", shell.spaceSeparator)
    gitreponame = generalsection['GIT-Reponame']
    return ConfigObject(user, password, repositoryurl, workspace, workdirectory, mainstream, streamnames, gitreponame)


def getstreamnames(streamsfromconfig):
    streamnames = []
    for streamname in streamsfromconfig.split(","):
        streamname = streamname.strip()
        streamnames.append(streamname)
    return streamnames


class ConfigObject:
    def __init__(self, user, password, repo, workspace, workdirectory, mainstream, streamnames, gitreponame):
        self.user = user
        self.password = password
        self.repo = repo
        self.workspace = workspace
        self.workDirectory = workdirectory
        self.mainStream = mainstream
        self.streamnames = streamnames
        self.gitRepoName = gitreponame
        self.clonedGitRepoName = gitreponame[:-4]  # cut .git
        self.logFolder = os.getcwd()
        self.streamuuids = []

    def getlogpath(self, filename):
        return "%s\%s" % (self.logFolder, filename)

    def collectstreamuuids(self):
        shouter.shout("Get UUID's of configured streamnames")
        for streamname in self.streamnames:
            streamname = streamname.strip()
            showuuidcommand = "lscm --show-alias n --show-uuid y show attributes -r %s -w %s" % (self.repo, streamname)
            output = shell.getoutput(showuuidcommand)
            splittedfirstline = output[0].split(" ")
            streamuuid = splittedfirstline[0].strip()[1:-1]
            self.streamuuids.append(streamuuid)












