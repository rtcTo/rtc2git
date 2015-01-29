from datetime import datetime


def shout(messagetoshout):
    print("%s - %s" % (gettimestamp(), messagetoshout))


def gettimestamp():
    return datetime.now().strftime('%H:%M:%S')