from datetime import datetime


def shout(messageToShout):
    print("%s - %s" % (getTimeStamp(), messageToShout))

def getTimeStamp():
    return datetime.now().strftime('%H:%M:%S')