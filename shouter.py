from datetime import datetime


def getTimeStamp():
    return datetime.now().strftime('%H:%M:%S')