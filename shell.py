import os
from subprocess import call

spaceSeparator = "****"


def execute(commandToExecute, outputfile=None, openMode="w", useShell=True):
    command = getCommands(commandToExecute)
    if not outputfile:
        call(command, shell=useShell)
    else:
        with open(outputfile, openMode) as file:
            call(command, stdout=file, shell=useShell)


def getoutput(commandtoexecute):
    tempfile = "tempOutput.txt"
    execute(commandtoexecute, tempfile)
    strippedlines = []

    with open(tempfile, 'r') as file:
        for line in file:
            cleanedline = line.strip()
            if cleanedline:
                strippedlines.append(cleanedline)
    os.remove(tempfile)
    return strippedlines


def getCommands(command):
    commands = []
    for splittedcommand in command.split(' '):
        if splittedcommand.__contains__(spaceSeparator):
            splittedcommand = splittedcommand.replace(spaceSeparator, " ")
        commands.append(splittedcommand)
    return commands
