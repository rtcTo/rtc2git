from datetime import datetime


def shout(messagetoshout):
    print("%s - %s" % (gettimestamp(), messagetoshout))


def shoutwithdate(messagetoshout):
    print("%s - %s" % (getdatetimestamp(), messagetoshout))


def gettimestamp():
    return datetime.now().strftime('%H:%M:%S')


def getdatetimestamp():
    return datetime.now().strftime('%d.%m %H:%M:%S')