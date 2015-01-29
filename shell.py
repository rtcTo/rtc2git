import os
from subprocess import call

spaceSeparator = "****"


def execute(commandtoexecute, outputfile=None, openmode="w"):
    command = getcommands(commandtoexecute)
    if not outputfile:
        call(command, shell=True)
    else:
        with open(outputfile, openmode) as file:
            call(command, stdout=file, shell=True)


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


def getcommands(command):
    commands = []
    for splittedcommand in command.split(' '):
        if splittedcommand.__contains__(spaceSeparator):
            splittedcommand = splittedcommand.replace(spaceSeparator, " ")
        commands.append(splittedcommand)
    return commands
