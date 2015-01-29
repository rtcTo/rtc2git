import os
import configparser

from rtc2git import shell


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
    streams = collectstreams(migrationsection['Streams'], repositoryurl)
    initialcomponentbaselines = []
    definedbaselines = migrationsection['InitialBaseLine']
    if definedbaselines:
        componentbaselines = definedbaselines.split(",")
        for entry in componentbaselines:
            componentbaseline = entry.split("=")
            component = componentbaseline[0].strip()
            baseline = componentbaseline[1].strip()
            if " " in baseline:
                baseline = baseline.replace(" ", shell.spaceSeparator)
    gitreponame = generalsection['GIT-Reponame']
    return ConfigObject(user, password, repositoryurl, workspace, workdirectory, mainstream, streams, gitreponame)


def collectstreams(streamsfromconfig, repo):
    streams = []
    for streamname in streamsfromconfig.split(","):
        streamname = streamname.strip()
        output = shell.getoutput("lscm --show-alias n --show-uuid y show attributes -r %s -w %s" % (repo, streamname))
        splittedfirstline = output[0].split(" ")
        streamuuid = splittedfirstline[0].strip()[1:-1]
        streams.append(streamuuid)
    return streams


class ConfigObject:
    def __init__(self, user, password, repo, workspace, workDirectory, mainStream, streams, gitRepoName):
        self.user = user
        self.password = password
        self.repo = repo
        self.workspace = workspace
        self.workDirectory = workDirectory
        self.mainStream = mainStream
        self.streams = streams
        self.gitRepoName = gitRepoName
        self.clonedGitRepoName = gitRepoName[:-4]  # cut .git
        self.logFolder = os.getcwd()

    def getlogpath(self, filename):
        return "%s\%s" % (self.logFolder, filename)


