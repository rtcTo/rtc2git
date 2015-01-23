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
    streams = []
    for stream in config['Migration']['Streams'].split(","):
        streams.append(stream.strip())
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


