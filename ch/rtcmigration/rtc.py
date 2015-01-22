from rtc2git.ch.rtcmigration.commons import Shell
from rtc2git.ch.rtcmigration import rtcmigration


class ImportHandler:
    dateFormat = "yyyy-MM-dd" + Shell.spaceSeparator + "HH:mm:ss"
    informationSeparator = "@@"

    def compareWithBaseLine(baseLineToCompare):
        Shell.execute(
            "lscm --show-alias n --show-uuid y compare ws " + rtcmigration.workspace + " baseline " + baseLineToCompare + " -r " + rtcmigration.repositoryURL + " -I sw -C @@{name}@@ --flow-directions i -D @@\"" + ImportHandler.dateFormat + "\"@@")

    def getChangeEntriesFromCompareFile(noarg):
        changeEntries = []
        with open(rtcmigration.outputFileName, 'r') as file:
            for line in file:
                splittedLines = line.split(ImportHandler.informationSeparator)
                revisionWithBrackets = splittedLines[0].strip()
                revision = revisionWithBrackets[1:-1]
                author = splittedLines[1].strip()
                comment = splittedLines[2].strip()
                date = splittedLines[3].strip()
                changeEntry = ChangeEntry(revision, author, date, comment)
                changeEntries.append(changeEntry)
                # print("Revision: " + revision + " Author:" + author + " Comment" + comment + " Date: " +date)
        return changeEntries

    def acceptChangesIntoWorkspace(baselineToCompare):
        ImportHandler.compareWithBaseLine(baselineToCompare)
        changeEntries = ImportHandler.getChangeEntriesFromCompareFile("")
        for changeEntry in changeEntries:
            revision = changeEntry.revision
            print("accepting: " + changeEntry.comment + " (rev: " + revision + ")")
            Shell.execute(
                "lscm accept --changes " + revision + " -r " + rtcmigration.repositoryURL + " --target " + rtcmigration.workspace,
                "accept.txt", "a")
            print("Revision " + revision + " accepted")
        print("All changes from " + baselineToCompare + " accepted")

    def acceptChangesFromBaseLine(baseLineToCompare):
        ImportHandler.acceptChangesIntoWorkspace(baseLineToCompare)


class ChangeEntry:
    revision = None
    author = None
    date = None
    comment = None

    def __init__(self, revision, author, date, comment):
        self.revision = revision
        self.author = author
        self.date = date
        self.comment = comment