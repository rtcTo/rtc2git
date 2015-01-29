from rtc2git import shell
from rtc2git.gitFunctions import Commiter
from rtc2git import shouter


class ImportHandler:
    dateFormat = "yyyy-MM-dd" + shell.spaceSeparator + "HH:mm:ss"
    informationSeparator = "@@"

    def __init__(self, config):
        self.config = config
        self.git = Commiter()

    def getchangeentries(self, baselinetocompare):
        outputfilename = self.config.getlogpath("Compare_" + baselinetocompare + ".txt")
        shell.execute(
            "lscm --show-alias n --show-uuid y compare ws " + self.config.workspace + " baseline " + baselinetocompare + " -r " + self.config.repo + " -I sw -C @@{name}@@ --flow-directions i -D @@\"" + self.dateFormat + "\"@@",
            outputfilename)
        changeentries = []
        with open(outputfilename, 'r') as file:
            for line in file:
                cleanedline = line.strip()
                if cleanedline:
                    splittedlines = cleanedline.split(self.informationSeparator)
                    revisionwithbrackets = splittedlines[0].strip()
                    revision = revisionwithbrackets[1:-1]
                    author = splittedlines[1].strip()
                    comment = splittedlines[2].strip()
                    date = splittedlines[3].strip()
                    changeentry = ChangeEntry(revision, author, date, comment)
                    changeentries.append(changeentry)
        return changeentries

    def acceptchangesintoworkspace(self, baselinetocompare):
        changeentries = self.getchangeentries(baselinetocompare)
        shouter.shout("Start accepting changes @ " + shouter.gettimestamp())
        for changeEntry in changeentries:
            revision = changeEntry.revision
            shouter.shout(
                "Accepting: " + changeEntry.comment + " (Date: " + changeEntry.date + " Revision: " + revision + ")")

            acceptcommand = "lscm accept --changes " + revision
            shell.execute(acceptcommand, self.config.getlogpath("accept.txt"), "a")
            self.git.addandcommit(changeEntry)

            shouter.shout("Revision '" + revision + "' accepted")

    def acceptchangesfrombaseline(self, componentbaselineentry):
        self.acceptchangesintoworkspace(componentbaselineentry.baseline)
        componentmigratedmessage = "All changes in Component '%s' from Baseline '%s' are accepted" % \
                                   (componentbaselineentry.component, componentbaselineentry.baseline)
        shouter.shout(componentmigratedmessage)

    def getbaselinesfromstream(self, stream):
        filename = self.config.getlogpath("StreamComponents_" + stream + ".txt")
        shell.execute("lscm --show-alias n --show-uuid y list components -v -r " + self.config.repo + " " + stream,
                      filename)
        componentbaselinesentries = []
        skippedfirstrow = False
        islinewithcomponent = 2
        component = None
        baseline = None
        with open(filename, 'r') as file:
            for line in file:
                cleanedline = line.strip()
                if cleanedline:
                    if not skippedfirstrow:
                        skippedfirstrow = True
                        continue
                    splittedlines = line.split("\"")[0].split(" ")
                    if islinewithcomponent % 2 == 0:
                        component = splittedlines[3].strip()[1:-1]
                    else:
                        baseline = splittedlines[5].strip()[1:-1]

                    if baseline is not None and component is not None:
                        componentbaselinesentries.append(ComponentBaseLineEntry(component, baseline))
                        baseline = None
                        component = None
                    islinewithcomponent += 1
        return componentbaselinesentries

    def acceptchangesfromstreams(self):
        for stream in self.config.streams:
            self.git.branch(stream)
            for componentBaseLineEntry in self.getbaselinesfromstream(stream):
                self.acceptchangesfrombaseline(componentBaseLineEntry)
            self.git.pushbranch(stream)

    def initialize(self):
        config = self.config
        repo = config.repo
        shell.execute("lscm login -r %s -u %s -P %s" % (repo, config.user, config.password))
        shell.execute("lscm create workspace -r %s -s %s %s" % (repo, config.mainStream, config.workspace))
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