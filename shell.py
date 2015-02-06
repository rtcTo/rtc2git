import sys

from subprocess import call
from subprocess import check_output

def execute(command, outputfile=None, openmode="w"):
    if not outputfile:
        call(command, shell=True)
    else:
        with open(outputfile, openmode) as file:
            call(command, stdout=file, shell=True)


def getoutput(command):
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