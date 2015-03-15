def tosortedlist(changeentrymap):
    sortedlist = []
    expectedlistsize = len(__aslist(changeentrymap))

    while len(sortedlist) < expectedlistsize:
        firstentryfromeachkey = __getfirstentryfromeachkeyasmap(changeentrymap)
        changesetwithearliestdate = __getchangeentrywithearliestdate(firstentryfromeachkey)
        __deleteentry(changeentrymap, changesetwithearliestdate)
        sortedlist.append(changesetwithearliestdate)

    return sortedlist


def __getfirstentryfromeachkeyasmap(changeentrymap):
    firstentries = {}
    for key in changeentrymap.keys():
        changeentries = changeentrymap.get(key)
        if changeentries:
            firstentries[key] = changeentries[0]
    return firstentries


def __deleteentry(changeentrymap, changeentrytodelete):
    for key in changeentrymap.keys():
        changeentries = changeentrymap.get(key)
        if changeentries and changeentrytodelete.revision is changeentries[0].revision:
            changeentries.remove(changeentrytodelete)
            break


def __getchangeentrywithearliestdate(changeentries):
    changeentrywithearliestdate = None
    for key in changeentries.keys():
        changeentry = changeentries.get(key)
        if not changeentrywithearliestdate or changeentry.date < changeentrywithearliestdate.date:
            changeentrywithearliestdate = changeentry
    return changeentrywithearliestdate


def __aslist(anymap):
    resultlist = []
    for key in anymap.keys():
        for changeentry in anymap.get(key):
            resultlist.append(changeentry)
    return resultlist