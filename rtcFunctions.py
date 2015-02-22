import shell
from gitFunctions import Commiter
import shouter


class RTCInitializer:
    @staticmethod
    def initialize(config):
        RTCInitializer.loginandcollectstreams()
        WorkspaceHandler(config).createandload(config.earlieststreamname)

    @staticmethod
    def loginandcollectstreams(config):
        shell.execute("lscm login -r %s -u %s -P %s" % (config.repo, config.user, config.password))
        config.collectstreamuuids()


class WorkspaceHandler:
    def __init__(self, config):
        self.workspacename = config.workspace
        self.repo = config.repo

    def createandload(self, stream):
        shell.execute("lscm create workspace -r %s -s %s %s" % (self.repo, stream, self.workspacename))
        shouter.shout("Starting initial load of workspace")
        shell.execute("lscm load -r %s %s" % (self.repo, self.workspacename))
        shouter.shout("Initial load of workspace finished")

    def reload(self):
        shouter.shout("Start reloading/replacing current workspace")
        shell.execute("lscm load -r %s %s --force" % (self.repo, self.workspacename))

    def setcomponentstobaseline(self, componentbaselineentries, streamuuid):
        self.setnewflowtargets(streamuuid)
        for entry in componentbaselineentries:
            shouter.shout("Set component '%s' to baseline '%s'" % (entry.componentname, entry.baselinename))

            replacecommand = "lscm set component -r %s -b %s %s stream %s %s --overwrite-uncommitted" % \
                             (self.repo, entry.baseline, self.workspacename, streamuuid, entry.component)
            shell.execute(replacecommand)

    def setnewflowtargets(self, streamuuid):
        shouter.shout("Replacing Flowtargets")
        self.removedefaultflowtarget()
        shell.execute("lscm add flowtarget -r %s %s %s"
                      % (self.repo, self.workspace, streamuuid))
        shell.execute("lscm set flowtarget -r %s %s --default --current %s"
                      % (self.repo, self.workspace, streamuuid))

    def removedefaultflowtarget(self):
        flowtargetline = shell.getoutput("lscm --show-alias n list flowtargets -r %s %s"
                                         % (self.repo, self.workspace))[0]
        flowtargetnametoremove = flowtargetline.split("\"")[1]
        shell.execute("lscm remove flowtarget -r %s %s %s"
                      % (self.repo, self.workspace.workspace, flowtargetnametoremove))


class ImportHandler:
    def __init__(self, config):
        self.config = config

    def getcomponentbaselineentriesfromstream(self, stream):
        filename = self.config.getlogpath("StreamComponents_" + stream + ".txt")
        shell.execute(
            "lscm --show-alias n --show-uuid y list components -v -r " + self.config.repo + " " + stream, filename)
        componentbaselinesentries = []
        skippedfirstrow = False
        islinewithcomponent = 2
        component = ""
        baseline = ""
        componentname = ""
        baselinename = ""
        with open(filename, 'r') as file:
            for line in file:
                cleanedline = line.strip()
                if cleanedline:
                    if not skippedfirstrow:
                        skippedfirstrow = True
                        continue
                    splittedinformationline = line.split("\"")
                    uuidpart = splittedinformationline[0].split(" ")
                    if islinewithcomponent % 2 is 0:
                        component = uuidpart[3].strip()[1:-1]
                        componentname = splittedinformationline[1]
                    else:
                        baseline = uuidpart[5].strip()[1:-1]
                        baselinename = splittedinformationline[1]

                    if baseline and component:
                        componentbaselinesentries.append(
                            ComponentBaseLineEntry(component, baseline, componentname, baselinename))
                        baseline = ""
                        component = ""
                        componentname = ""
                        baselinename = ""
                    islinewithcomponent += 1
        return componentbaselinesentries

    def acceptchangesintoworkspace(self, changeentries):
        git = Commiter
        amountofchanges = len(changeentries)
        shouter.shout("Start accepting %s changesets" % amountofchanges)
        amountofacceptedchanges = 0
        for changeEntry in changeentries:
            amountofacceptedchanges += 1
            revision = changeEntry.revision
            acceptingmsg = "Accepting: " + changeEntry.comment + " (Date: " + changeEntry.date + " Author: " \
                           + changeEntry.author + " Revision: " + revision + ")"
            shouter.shout(acceptingmsg)
            acceptcommand = "lscm accept --changes " + revision + " --overwrite-uncommitted"
            shell.execute(acceptcommand, self.config.getlogpath("accept.txt"), "a")
            git.addandcommit(changeEntry)

            shouter.shout("Accepted change %s/%s" % (amountofacceptedchanges, amountofchanges))

    def getchangeentriesofstreamcomponents(self, componentbaselineentries):
        shouter.shout("Start collecting changeentries")
        changeentries = []
        for componentBaseLineEntry in componentbaselineentries:
            changeentries.extend(self.getchangeentriesofbaseline(componentBaseLineEntry.baseline))
        changeentries.sort(key=lambda change: change.date)
        return changeentries

    @staticmethod
    def getchangeentriesfromfile(outputfilename):
        informationseparator = "@@"
        changeentries = []
        with open(outputfilename, 'r') as file:
            for line in file:
                cleanedline = line.strip()
                if cleanedline:
                    splittedlines = cleanedline.split(informationseparator)
                    revisionwithbrackets = splittedlines[0].strip()
                    revision = revisionwithbrackets[1:-1]
                    author = splittedlines[1].strip()
                    email = splittedlines[2].strip()
                    comment = splittedlines[3].strip()
                    date = splittedlines[4].strip()
                    changeentries.append(ChangeEntry(revision, author, email, date, comment))
        return changeentries

    def getchangeentriesofbaseline(self, baselinetocompare):
        dateformat = "yyyy-MM-dd HH:mm:ss"
        outputfilename = self.config.getlogpath("Compare_" + baselinetocompare + ".txt")
        comparecommand = "lscm --show-alias n --show-uuid y compare ws %s baseline %s -r %s -I sw -C @@{name}@@{email}@@ --flow-directions i -D @@\"%s\"@@" \
                         % (self.config.workspace, baselinetocompare, self.config.repo, dateformat)
        shell.execute(comparecommand, outputfilename)
        return ImportHandler.getchangeentriesfromfile(outputfilename)

    def getchangeentriesofstream(self, streamtocompare):
        dateformat = "yyyy-MM-dd HH:mm:ss"
        outputfilename = self.config.getlogpath("CompareStream_" + streamtocompare + ".txt")
        comparecommand = "lscm --show-alias n --show-uuid y compare ws %s stream %s -r %s -I sw -C @@{name}@@{email}@@ --flow-directions i -D @@\"%s\"@@" \
                         % (self.config.workspace, streamtocompare, self.config.repo, dateformat)
        shell.execute(comparecommand, outputfilename)
        return ImportHandler.getchangeentriesfromfile(outputfilename)

class ChangeEntry:
    def __init__(self, revision, author, email, date, comment):
        self.revision = revision
        self.author = author
        self.email = email
        self.date = date
        self.comment = comment

    def getgitauthor(self):
        authorrepresentation = "%s <%s>" % (self.author, self.email)
        return shell.quote(authorrepresentation)


class ComponentBaseLineEntry:
    def __init__(self, component, baseline, componentname, baselinename):
        self.component = component
        self.baseline = baseline
        self.componentname = componentname
        self.baselinename = baselinename
