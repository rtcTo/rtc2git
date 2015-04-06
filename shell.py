import sys
from subprocess import call
from subprocess import check_output

import shouter


logcommands = False


def execute(command, outputfile=None, openmode="w"):
    shout_command_to_log(command)
    if not outputfile:
        return call(command, shell=True)
    else:
        with open(outputfile, openmode) as file:
            return call(command, stdout=file, shell=True)


def getoutput(command):
    shout_command_to_log(command)
    outputasbytestring = check_output(command, shell=True)
    output = outputasbytestring.decode(sys.stdout.encoding).splitlines()
    strippedlines = []
    for line in output:
        cleanedline = line.strip()
        if cleanedline:
            strippedlines.append(cleanedline)
    return strippedlines


def quote(stringtoquote):
    stringtoquote = stringtoquote.replace('\"', "'")  # replace " with '
    quotedstring = '\"' + stringtoquote + '\"'
    return quotedstring


def shout_command_to_log(command):
    if logcommands:
        shouter.shout("Executed Command: " + command)