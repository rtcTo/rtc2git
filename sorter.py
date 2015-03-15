def getFirstEntryFromEachKeyAsMap(changeentrymap):
    firstEntries = {}
    for key in changeentrymap.keys():
        changeentries = changeentrymap.get(key)
        if changeentries:
            firstEntries[key] = changeentries[0]
    return firstEntries


def deleteEntry(changeentrymap, changeentrytodelete):
    for key in changeentrymap.keys():
        changeentries = changeentrymap.get(key)
        if changeentries and changeentrytodelete.revision is changeentries[0].revision:
            changeentries.remove(changeentrytodelete)
            break


def tosortedlist(changeentrymap):
    sortedlist = []
    expectedlistsize = len(aslist(changeentrymap))

    while len(sortedlist) < expectedlistsize:
        firstentryfromeachkey = getFirstEntryFromEachKeyAsMap(changeentrymap)
        changeentrytoAdd = getChangeEntryWithLowestDate(firstentryfromeachkey)
        deleteEntry(changeentrymap, changeentrytoAdd)
        sortedlist.append(changeentrytoAdd)

    return sortedlist;


def getChangeEntryWithLowestDate(changeentries):
    changeentryWithEarliestDate = None
    for key in changeentries.keys():
        changeentry = changeentries.get(key)
        if not changeentryWithEarliestDate or changeentry.date < changeentryWithEarliestDate.date:
            changeentryWithEarliestDate = changeentry
    return changeentryWithEarliestDate


def aslist(anymap):
    resultlist = []
    for key in anymap.keys():
        for changeentry in anymap.get(key):
            resultlist.append(changeentry)
    return resultlist