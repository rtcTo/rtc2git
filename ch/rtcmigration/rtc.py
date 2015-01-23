from rtc2git.ch.rtcmigration.commons import Shell


class ImportHandler:
    dateFormat = "yyyy-MM-dd" + Shell.spaceSeparator + "HH:mm:ss"
    informationSeparator = "@@"
    workspace = None
    repositoryURL = None
    outputFileName = "output.txt"

    def __init__(self, workspace, repository):
        self.workspace = workspace
        self.repositoryURL = repository


    def getChangeEntries(self, baselineToCompare):
        Shell.execute(
            "scm --show-alias n --show-uuid y compare ws " + self.workspace + " baseline " + baselineToCompare + " -r " + self.repositoryURL + " -I sw -C @@{name}@@ --flow-directions i -D @@\"" + self.dateFormat + "\"@@")
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
        for changeEntry in changeEntries:
            revision = changeEntry.revision
            print("accepting: " + changeEntry.comment + " (Date: " + changeEntry.date, " Revision: " + revision + ")")
            Shell.execute(
                "scm accept --changes " + revision + " -r " + self.repositoryURL + " --target " + self.workspace,
                "accept.txt", "a")
            print("Revision " + revision + " accepted")
        print("All changes from " + baselineToCompare + " accepted")

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
            Shell.execute("scm --show-alias n --show-uuid y list components -v -r " + self.repositoryURL + " " + stream,
                          fileName)
            for componentBaseLineEntry in self.getBaseLinesFromStream(stream, fileName):
                self.acceptChangesFromBaseLine(componentBaseLineEntry.baseline)


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


class ComponentBaseLineEntry:
    component = None
    baseline = None

    def __init__(self, component, baseline):
        self.component = component
        self.baseline = baseline