import shell
from gitFunctions import Commiter
import shouter


class ImportHandler:
    dateFormat = "yyyy-MM-dd HH:mm:ss"
    informationSeparator = "@@"

    def __init__(self, config):
        self.config = config
        self.git = Commiter()

    def initialize(self):
        config = self.config
        repo = config.repo
        self.loginandcollectstreams()
        shell.execute("lscm create workspace -r %s -s %s %s" % (repo, config.earlieststreamname, config.workspace))
        shouter.shout("Starting initial load of workspace")
        shell.execute("lscm load -r %s %s" % (repo, config.workspace))
        shouter.shout("Initial load of workspace finished")

    def loginandcollectstreams(self):
        config = self.config
        shell.execute("lscm login -r %s -u %s -P %s" % (config.repo, config.user, config.password))
        config.collectstreamuuids()

    def recreateworkspace(self, stream):
        workspace = self.config.workspace
        shouter.shout("Recreating workspace")
        shell.execute("lscm delete workspace " + workspace)
        shell.execute("lscm create workspace -s %s %s" % (stream, workspace))

    def resetcomponentstobaseline(self, componentbaselineentries, stream):
        for componentbaselineentry in componentbaselineentries:
            shouter.shout("Set component '%s' to baseline '%s'"
                          % (componentbaselineentry.componentname, componentbaselineentry.baselinename))

            replacecommand = "lscm set component -r %s -b %s %s stream %s %s --overwrite-uncommitted" % \
                             (self.config.repo, componentbaselineentry.baseline, self.config.workspace,
                              stream, componentbaselineentry.component)
            shell.execute(replacecommand)

    def setnewflowtargets(self, streamuuid):
        shouter.shout("Replacing Flowtargets")
        self.removedefaultflowtarget()
        shell.execute("lscm add flowtarget -r %s %s %s"
                      % (self.config.repo, self.config.workspace, streamuuid))
        shell.execute("lscm set flowtarget -r %s %s --default --current %s"
                      % (self.config.repo, self.config.workspace, streamuuid))

    def removedefaultflowtarget(self):
        flowtargetline = shell.getoutput("lscm --show-alias n list flowtargets -r %s %s"
                                         % (self.config.repo, self.config.workspace))[0]
        flowtargetnametoremove = flowtargetline.split("\"")[1]
        shell.execute("lscm remove flowtarget -r %s %s %s"
                      % (self.config.repo, self.config.workspace, flowtargetnametoremove))

    def reloadworkspace(self):
        shouter.shout("Start reloading/replacing current workspace")
        shell.execute("lscm load -r %s %s --force" % (self.config.repo, self.config.workspace))

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
                    if islinewithcomponent % 2 is 0:
                        component = splittedlines[3].strip()[1:-1]
                    else:
                        baseline = splittedlines[5].strip()[1:-1]

                    if baseline is not None and component is not None:
                        componentbaselinesentries.append(self.createcomponentbaselineentry(component, baseline))
                        baseline = None
                        component = None
                    islinewithcomponent += 1
        return componentbaselinesentries

    def acceptchangesintoworkspace(self, changeentries):
        for changeEntry in changeentries:
            revision = changeEntry.revision
            acceptingmsg = "Accepting: " + changeEntry.comment + " (Date: " + changeEntry.date + " Author: " \
                           + changeEntry.author + " Revision: " + revision + ")"
            shouter.shout(acceptingmsg)
            acceptcommand = "lscm accept --changes " + revision + " --overwrite-uncommitted"
            shell.execute(acceptcommand, self.config.getlogpath("accept.txt"), "a")
            self.git.addandcommit(changeEntry)

            shouter.shout("Revision '" + revision + "' accepted")

    def getchangeentriesofstream(self, componentbaselineentries):
        changeentries = []
        for componentBaseLineEntry in componentbaselineentries:
            changeentries.append(self.getchangeentries(componentBaseLineEntry.baseline))
        changeentries.sort(key=lambda change: change.date)
        return changeentries

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

    def createcomponentbaselineentry(self, component, baseline):
        componentname = self.getcomponentname(component)
        baselinename = self.getbaselinename(baseline)
        return ComponentBaseLineEntry(component, baseline, componentname, baselinename)

    def getcomponentname(self, componentuuid):
        shouter.shout("Determine componentname of " + componentuuid)
        componentname = ""
        lines = shell.getoutput("lscm --show-alias n show attributes -C %s -r %s" % (componentuuid, self.config.repo))
        if lines:
            componentname = lines[0].strip()[1:-1]
        return componentname

    def getbaselinename(self, baselineuuid):
        shouter.shout("Determine baselinename of " + baselineuuid)
        baselinename = ""
        lines = shell.getoutput("lscm --show-alias n show attributes -b %s -r %s" % (baselineuuid, self.config.repo))
        if lines:
            splittedlines = lines[0].strip().split("\"")
            baselinename = splittedlines[1].strip()
        return baselinename


class ChangeEntry:
    def __init__(self, revision, author, date, comment):
        self.revision = revision
        self.author = author
        self.date = date
        self.comment = comment


class ComponentBaseLineEntry:
    def __init__(self, component, baseline, componentname, baselinename):
        self.component = component
        self.baseline = baseline
        self.componentname = componentname
        self.baselinename = baselinename
