from datetime import datetime
import sys


def shout(messagetoshout):
    safeshout("%s - %s" % (gettimestamp(), messagetoshout))


def shoutwithdate(messagetoshout):
    safeshout("%s - %s" % (getdatetimestamp(), messagetoshout))


def safeshout(messagetoshout):
    print(messagetoshout.encode('utf8').decode(sys.stdout.encoding))


def gettimestamp():
    return datetime.now().strftime('%H:%M:%S')


def getdatetimestamp():
    return datetime.now().strftime('%d.%m %H:%M:%S')