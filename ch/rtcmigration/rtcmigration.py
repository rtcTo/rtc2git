import configparser

from rtc2git.ch.rtcmigration.commons import Shell


outputFileName = "output.txt"
repositoryURL = None
user = None
password = None
workspace = None
stream = None
baseline = "_BCxObPNyEeKb7fdMNGs5Yw" #rc-1306
firstApplicationBaseLine = "Initial" + Shell.spaceSeparator + "CVS" + Shell.spaceSeparator + "Import"
firstBaseLine = "Initial" + Shell.spaceSeparator + "CVS" + Shell.spaceSeparator + "Migration"

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

class RTC:
    dateFormat = "yyyy-MM-dd" + Shell.spaceSeparator + "HH:mm:ss"
    informationSeparator = "@@"

    def compareWithBaseLine(baseLineToCompare):
        Shell.execute("lscm --show-alias n --show-uuid y compare ws " + workspace+ " baseline " + baseLineToCompare  + " -r " + repositoryURL + " -I sw -C @@{name}@@ --flow-directions i -D @@\"" +RTC.dateFormat + "\"@@")
    def getChangeEntriesFromCompareFile(noarg):
        changeEntries = []
        with open(outputFileName, 'r') as file:
            for line in file:
                splittedLines = line.split(RTC.informationSeparator)
                revisionWithBrackets = splittedLines[0].strip()
                revision = revisionWithBrackets[1:-1]
                author = splittedLines[1].strip()
                comment = splittedLines[2].strip()
                date = splittedLines[3].strip()
                changeEntry = ChangeEntry(revision, author, date, comment)
                changeEntries.append(changeEntry)
                #print("Revision: " + revision + " Author:" + author + " Comment" + comment + " Date: " +date)
        return changeEntries
    def acceptChangesIntoWorkspace(changeEntries):
        for changeEntry in changeEntries:
            revision = changeEntry.revision
            print("accepting: " + changeEntry.comment + " (rev: " + revision + ")")
            Shell.execute("lscm accept --changes " + revision + " -r " + repositoryURL +" --target " + workspace, "accept.txt", "a")
            print("Revision " + revision + " accepted")
        print("All changes from accepted")
    def acceptChangesFromBaseLine(baseLineToCompare):
        RTC.compareWithBaseLine(baseline)
        RTC.acceptChangesIntoWorkspace(RTC.getChangeEntriesFromCompareFile(""))

def init():
    Shell.execute("lscm set component -r " + repositoryURL + " -b " + firstApplicationBaseLine + " " + workspace + " stream " + stream + " BP_Application BP_Application_UnitTest")
    Shell.execute("lscm set component -r " + repositoryURL + " -b " + firstBaseLine + " " + workspace +" stream " + stream + " BT_Frame_Installer BT_Frame_Server BT_Frame_UnitTest BX_BuildEnvironment")

def readConfig():
    config = configparser.ConfigParser()
    config.read("config.ini")
    global user, password, workspace, repositoryURL, stream
    generalSection = config['General']
    user = generalSection['User']
    password = generalSection['Password']
    workspace = generalSection['WorkspaceName']
    repositoryURL = generalSection['Repo']
    stream = generalSection['Stream']




readConfig()
#init()
#RTC.acceptChangesFromBaseLine(baseline)
