import unittest

from rtcFunctions import ChangeEntry
import sorter


class SorterTest(unittest.TestCase):
    def setUp(self):
        self.changeentriesmap = {}
        self.changesetcounter = 0

    def testSortingTwoComponents_ExpectKeepOrderingInsideSameKey(self):
        firstkey = "anyKey"
        secondkey = "anyOtherKey"
        self.put(firstkey, self.createchangeentry("1991-03-24"))
        self.put(firstkey, self.createchangeentry("1991-05-24"))
        self.put(firstkey, self.createchangeentry("1991-05-22"))
        self.put(secondkey, self.createchangeentry("1991-05-23"))
        self.put(secondkey, self.createchangeentry("1991-07-22"))
        sortedchangesets = sorter.tosortedlist(self.changeentriesmap)

        self.assertEqual("1991-03-24", sortedchangesets[0].date)  # earliestEntry firstkey
        self.assertEqual("1991-05-23", sortedchangesets[1].date)  # earliestEntry secondKey
        self.assertEqual("1991-05-24", sortedchangesets[2].date)  # secondEarliestEntry firstKey
        self.assertEqual("1991-05-22", sortedchangesets[3].date)  # lastEntry firstKey
        self.assertEqual("1991-07-22", sortedchangesets[4].date)  # lastEntry secondKey

    def createchangeentry(self, date):
        self.changesetcounter += 1
        return ChangeEntry(self.changesetcounter, "anyAuthor", "anyEmail", date, "")

    def put(self, key, changeentry):
        changeentries = self.changeentriesmap.get(key)
        if not changeentries:
            changeentries = []
        changeentries.append(changeentry)
        self.changeentriesmap[key] = changeentries
