import configparser
from subprocess import call


class Shell:
    spaceSeparator = "****"

    def execute(commandToExecute, outputfile="output.txt", openMode="w"):
        commands = []
        for splittedcommand in commandToExecute.split(' '):
            if splittedcommand.__contains__(Shell.spaceSeparator):
                splittedcommand = splittedcommand.replace(Shell.spaceSeparator, " ")
            commands.append(splittedcommand)
        with open(outputfile, openMode) as file:
            call(commands, stdout=file)


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
            if (" " in baseline):
                baseLine = baseline.replace(" ", Shell.spaceSeparator)

    return Config(user, password, repositoryURL, workspace, workDirectory, mainStream, streams)


class Config:
    outputFileName = "output.txt"

    def __init__(self, user, password, repo, workspace, workDirectory, mainStream, streams):
        self.user = user
        self.password = password
        self.repo = repo
        self.workspace = workspace
        self.workDirectory = workDirectory
        self.mainStream = mainStream
        self.streams = streams


