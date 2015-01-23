from datetime import datetime

from rtc2git.ch.rtcmigration.commons import Shell


class ImportHandler:
    dateFormat = "yyyy-MM-dd" + Shell.spaceSeparator + "HH:mm:ss"
    informationSeparator = "@@"

    def __init__(self, config):
        self.workspace = config.workspace
        self.repoURL = config.repo
        self.outputFileName = config.outputFileName
        self.workDirectory = config.workDirectory

    def getChangeEntries(self, baselineToCompare):
        Shell.execute(
            "scm --show-alias n --show-uuid y compare ws " + self.workspace + " baseline " + baselineToCompare + " -r " + self.repoURL + " -I sw -C @@{name}@@ --flow-directions i -D @@\"" + self.dateFormat + "\"@@")
        changeEntries = []
        with open(self.outputFileName, 'r') as file:
            for line in file:
                splittedLines = line.split(self.informationSeparator)
                revisionWithBrackets = splittedLines[0].strip()
                revision = revisionWithBrackets[1:-1]
                author = splittedLines[1].strip()
                comment = splittedLines[2].strip()
                date = splittedLines[3].strip()
                changeEntry = ChangeEntry(revision, author, date, comment)
                changeEntries.append(changeEntry)
                # print("Revision: " + revision + " Author:" + author + " Comment" + comment + " Date: " +date)
        return changeEntries

    def acceptChangesIntoWorkspace(self, baselineToCompare):
        changeEntries = self.getChangeEntries(baselineToCompare)
        print("Start accepting changes @ " + datetime.now().strftime('%H:%M:%S'))
        for changeEntry in changeEntries:
            revision = changeEntry.revision
            print("accepting: " + changeEntry.comment + " (Date: " + changeEntry.date, " Revision: " + revision + ")")
            Shell.execute(
                "scm accept --changes " + revision + " -r " + self.repoURL + " --target " + self.workspace,
                "accept.txt", "a")
            print("Revision " + revision + " accepted")
        print(datetime.now().strftime('%H:%M:%S') + " - All changes from " + baselineToCompare + " accepted")

    def acceptChangesFromBaseLine(self, baseLineToCompare):
        self.acceptChangesIntoWorkspace(baseLineToCompare)

    def getBaseLinesFromStream(self, stream, filename):
        firstRowSkipped = False
        isComponentLine = 2
        componentBaseLinesEntries = []
        component = None
        baseline = None
        with open(filename, 'r') as file:
            for line in file:
                if (firstRowSkipped == False):
                    firstRowSkipped = True
                    continue
                splittedLines = line.split("\"")[0].split(" ")
                if isComponentLine % 2 == 0:
                    component = splittedLines[3].strip()[1:-1]
                else:
                    baseline = splittedLines[5].strip()[1:-1]

                if baseline != None and component != None:
                    componentBaseLineEntry = ComponentBaseLineEntry(component, baseline)
                    componentBaseLinesEntries.append(componentBaseLineEntry)
                    baseline = None
                    component = None

                isComponentLine += 1
        return componentBaseLinesEntries

    def acceptChangesFromStreams(self, streams):
        for stream in streams:
            fileName = "StreamComponents_" + stream + ".txt"
            Shell.execute("scm --show-alias n --show-uuid y list components -v -r " + self.repoURL + " " + stream,
                          fileName)
            for componentBaseLineEntry in self.getBaseLinesFromStream(stream, fileName):
                self.acceptChangesFromBaseLine(componentBaseLineEntry.baseline)

    def initializeWorkspace(self):
# Shell.execute("scm set component -r " + repositoryURL + " -b " + firstApplicationBaseLine + " " + workspace + " stream " + mainStream + " BP_Application BP_Application_UnitTest")
#Shell.execute("scm set component -r " + repositoryURL + " -b " + firstBaseLine + " " + workspace + " stream " + mainStream + " BT_Frame_Installer BT_Frame_Server BT_Frame_UnitTest BX_BuildEnvironment")

class ChangeEntry:
    def __init__(self, revision, author, date, comment):
        self.revision = revision
        self.author = author
        self.date = date
        self.comment = comment


class ComponentBaseLineEntry:
    def __init__(self, component, baseline):
        self.component = component
        self.baseline = baseline