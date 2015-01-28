import configparser
import os
from subprocess import call
from datetime import datetime



class Shell:
    spaceSeparator = "****"

    def execute(self, commandToExecute, outputfile=None, openMode="w", useShell=True):
        command = getCommands(commandToExecute)
        if not outputfile:
            call(command, shell=useShell)
        else:
            with open(outputfile, openMode) as file:
                call(command, stdout=file, shell=useShell)


def getCommands(command):
    commands = []
    for splittedcommand in command.split(' '):
        if splittedcommand.__contains__(Shell.spaceSeparator):
            splittedcommand = splittedcommand.replace(Shell.spaceSeparator, " ")
        commands.append(splittedcommand)
    return commands


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
    streams = []
    for stream in migrationSection['Streams'].split(","):
        streams.append(stream.strip())
    initialComponentBaseLines = []
    definedBaseLines = migrationSection['InitialBaseLine']
    if definedBaseLines:
        componentBaseLines = definedBaseLines.split(",")
        for entry in componentBaseLines:
            componentBaseLine = entry.split("=")
            component = componentBaseLine[0].strip()
            baseline = componentBaseLine[1].strip()
            if " " in baseline:
                baseLine = baseline.replace(" ", Shell.spaceSeparator)
    gitRepoName = generalSection['GIT-Reponame']
    return Config(user, password, repositoryURL, workspace, workDirectory, mainStream, streams, gitRepoName)


def getTimeStamp():
    return datetime.now().strftime('%H:%M:%S')

class Config:
    outputFileName = "output.txt"

    def __init__(self, user, password, repo, workspace, workDirectory, mainStream, streams, gitRepoName):
        self.user = user
        self.password = password
        self.repo = repo
        self.workspace = workspace
        self.workDirectory = workDirectory
        self.mainStream = mainStream
        self.streams = streams
        self.gitRepoName = gitRepoName
        self.clonedGitRepoName = gitRepoName[:-4]
        self.logFolder = os.getcwd()

    def getLogPath(self, filename):
        return "%s\%s" % (self.logFolder, filename)

