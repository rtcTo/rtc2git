from rtc2git import shell
from rtc2git.gitFunctions import Commiter
from rtc2git import shouter


class ImportHandler:
    dateFormat = "yyyy-MM-dd" + shell.spaceSeparator + "HH:mm:ss"
    informationSeparator = "@@"

    def __init__(self, config):
        self.config = config
        self.git = Commiter()

    def getChangeEntries(self, baselineToCompare):
        outputFileName = self.config.getLogPath("Compare_" + baselineToCompare + ".txt")
        shell.execute(
            "lscm --show-alias n --show-uuid y compare ws " + self.config.workspace + " baseline " + baselineToCompare + " -r " + self.config.repo + " -I sw -C @@{name}@@ --flow-directions i -D @@\"" + self.dateFormat + "\"@@",
            outputFileName)
        changeEntries = []
        with open(outputFileName, 'r') as file:
            for line in file:
                cleanedLine = line.strip()
                if cleanedLine:
                    splittedLines = cleanedLine.split(self.informationSeparator)
                    revisionWithBrackets = splittedLines[0].strip()
                    revision = revisionWithBrackets[1:-1]
                    author = splittedLines[1].strip()
                    comment = splittedLines[2].strip()
                    date = splittedLines[3].strip()
                    changeEntry = ChangeEntry(revision, author, date, comment)
                    changeEntries.append(changeEntry)
        return changeEntries

    def acceptChangesIntoWorkspace(self, baselineToCompare):
        changeEntries = self.getChangeEntries(baselineToCompare)
        shouter.shout("Start accepting changes @ " + shouter.getTimeStamp())
        for changeEntry in changeEntries:
            revision = changeEntry.revision
            shouter.shout(
                "Accepting: " + changeEntry.comment + " (Date: " + changeEntry.date + " Revision: " + revision + ")")

            acceptCommand = "lscm accept --changes " + revision
            shell.execute(acceptCommand, self.config.getLogPath("accept.txt"), "a")
            self.git.addAndcommit(changeEntry)

            shouter.shout("Revision '" + revision + "' accepted")

    def acceptChangesFromBaseLine(self, baselineToCompare):
        self.acceptChangesIntoWorkspace(baselineToCompare)

    def getBaseLinesFromStream(self, stream):
        filename = self.config.getLogPath("StreamComponents_" + stream + ".txt")
        shell.execute("lscm --show-alias n --show-uuid y list components -v -r " + self.config.repo + " " + stream,
                      filename)
        firstRowSkipped = False
        isComponentLine = 2
        componentBaseLinesEntries = []
        component = None
        baseline = None
        with open(filename, 'r') as file:
            for line in file:
                cleanedLine = line.strip()
                if cleanedLine:
                    if firstRowSkipped == False:
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

    def acceptChangesFromStreams(self):
        for stream in self.config.streams:
            self.git.branch(stream)
            for componentBaseLineEntry in self.getBaseLinesFromStream(stream):
                self.acceptChangesFromBaseLine(componentBaseLineEntry.baseline)
                shouter.shout("All changes from Baseline '%s' and Componenent '%s' accepted" % (
                componentBaseLineEntry.baseline, componentBaseLineEntry.component))
            self.git.pushBranch(stream)

    def initialize(self):
        config = self.config
        repo = config.repo
        shell.execute("lscm login -r %s -u %s -P %s" % (repo, config.user, config.password))
        # shell.execute("lscm create workspace -r %s -s %s %s" % (repo, config.mainStream, config.workspace))
        # implement logic here for replacing components by oldest baseline - scm set components
        shouter.shout("Starting initial load of workspace")
        shell.execute("lscm load -r %s %s" % (repo, config.workspace))
        shouter.shout("Initial load of workspace finished")



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