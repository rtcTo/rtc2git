import os
import configparser

from rtc2git import shell


def readConfig():
    config = configparser.ConfigParser()
    config.read("config.ini")
    generalSection = config['General']
    user = generalSection['User']
    password = generalSection['Password']
    workspace = generalSection['WorkspaceName']
    repositoryURL = generalSection['Repo']
    mainStream = generalSection['Stream']
    workDirectory = generalSection['Directory']
    if not workDirectory:
        workDirectory = "."
    migrationSection = config['Migration']
    streams = collectstreams(migrationSection['Streams'], repositoryURL)
    initialComponentBaseLines = []
    definedBaseLines = migrationSection['InitialBaseLine']
    if definedBaseLines:
        componentBaseLines = definedBaseLines.split(",")
        for entry in componentBaseLines:
            componentBaseLine = entry.split("=")
            component = componentBaseLine[0].strip()
            baseline = componentBaseLine[1].strip()
            if " " in baseline:
                baseLine = baseline.replace(" ", shell.spaceSeparator)
    gitRepoName = generalSection['GIT-Reponame']
    return ConfigObject(user, password, repositoryURL, workspace, workDirectory, mainStream, streams, gitRepoName)


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

    def getLogPath(self, filename):
        return "%s\%s" % (self.logFolder, filename)


