import sys
from subprocess import call, check_output, CalledProcessError

import shouter

logcommands = False
encoding = None


def execute(command, outputfile=None, openmode="w"):
    shout_command_to_log(command, outputfile)
    if not outputfile:
        return call(command, shell=True)
    else:
        with open(outputfile, openmode, encoding=encoding) as file:
            return call(command, stdout=file, shell=True)


def getoutput(command):
    shout_command_to_log(command)
    try:
        outputasbytestring = check_output(command, shell=True)
        output = outputasbytestring.decode(sys.stdout.encoding).splitlines()
    except CalledProcessError as e:
        shouter.shout(e)
        output = ""
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


def shout_command_to_log(command, outputfile=None):
    if logcommands:
        logmessage = "Executed Command: " + quote(command)
        if outputfile:
            shouter.shout(logmessage + " --> " + outputfile)
        else:
            shouter.shout(logmessage)


def setencoding(encodingtobeset):
    global encoding
    if encodingtobeset:
        encoding = encodingtobeset
