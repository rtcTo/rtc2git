import sys
from subprocess import call
from subprocess import check_output

spaceSeparator = "****"


def execute(commandtoexecute, outputfile=None, openmode="w"):
    command = getcommands(commandtoexecute)
    if not outputfile:
        call(command, shell=True)
    else:
        with open(outputfile, openmode) as file:
            call(command, stdout=file, shell=True)


def getoutput(commandtoexecute):
    command = getcommands(commandtoexecute)
    outputasbytestring = check_output(command, shell=True)
    output = outputasbytestring.decode(sys.stdout.encoding).splitlines()
    strippedlines = []
    for line in output:
        cleanedline = line.strip()
        if cleanedline:
            strippedlines.append(cleanedline)
    return strippedlines


def getcommands(command):
    commands = []
    for commandswithspaces in command.split(' '):
        commands.append(replacespaces(commandswithspaces))
    return commands


def replacespaces(stringwithspaces):
    if stringwithspaces.__contains__(' '):
        stringwithspaces = stringwithspaces.replace(' ', spaceSeparator)
    return stringwithspaces