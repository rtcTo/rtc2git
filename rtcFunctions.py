import shell
from gitFunctions import Commiter
import shouter


class ImportHandler:
    dateFormat = "yyyy-MM-dd HH:mm:ss"
    informationSeparator = "@@"

    def __init__(self, config):
        self.config = config
        self.git = Commiter()
        config.collectstreamuuids()

    def initialize(self):
        config = self.config
        repo = config.repo
        shell.execute("lscm login -r %s -u %s -P %s" % (repo, config.user, config.password))
        shell.execute("lscm create workspace -r %s -s %s %s" % (repo, config.earlieststreamname, config.workspace))
        # implement logic here for replacing components by oldest baseline - scm set components
        shouter.shout("Starting initial load of workspace")
        shell.execute("lscm load -r %s %s" % (repo, config.workspace))
        shouter.shout("Initial load of workspace finished")

    def acceptchangesfromstreams(self):
        streamuuids = self.config.streamuuids
        for streamuuid in streamuuids:
            streamname = self.config.streamnames[streamuuids.index(streamuuid)]
            self.git.branch(streamname)
            componentbaselineentries = self.getbaselinesfromstream(streamuuid)
            for componentBaseLineEntry in componentbaselineentries:
                self.acceptchangesfrombaseline(componentBaseLineEntry)
            shouter.shout("All changes of stream '%s' accepted" % streamname)
            self.git.pushbranch(streamname)
            self.setcomponentsofnextstreamtoworkspace(componentbaselineentries)
            self.setnewflowtargets(streamuuid)
            self.reloadworkspace()

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


    def setcomponentsofnextstreamtoworkspace(self, componentbaselineentries):
        for componentbaselineentry in componentbaselineentries:
            replacecommand = "lscm set component -r %s -b % s %s stream %s %s"
            shell.execute(replacecommand %
                          (self.config.repo, componentbaselineentry.baseline, self.config.workspace,
                           self.config.mainStream, componentbaselineentry.component))

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

    def acceptchangesfrombaseline(self, componentbaselineentry):
        startcomponentmigrationmessage = "Start accepting changes in component '%s' from baseline '%s'" % \
                                         (componentbaselineentry.componentname, componentbaselineentry.baselinename)
        shouter.shoutwithdate(startcomponentmigrationmessage)

        self.acceptchangesintoworkspace(componentbaselineentry.baseline)

        componentmigratedmessage = "All changes in component '%s' from baseline '%s' are accepted" % \
                                   (componentbaselineentry.componentname, componentbaselineentry.baselinename)
        shouter.shout(componentmigratedmessage)

    def acceptchangesintoworkspace(self, baselinetocompare):
        changeentries = self.getchangeentries(baselinetocompare)
        for changeEntry in changeentries:
            revision = changeEntry.revision
            acceptingmsg = "Accepting: " + changeEntry.comment + " (Date: " + changeEntry.date + " Author: " \
                           + changeEntry.author + " Revision: " + revision + ")"
            shouter.shout(
                acceptingmsg)

            acceptcommand = "lscm accept --changes " + revision
            shell.execute(acceptcommand, self.config.getlogpath("accept.txt"), "a")
            self.git.addandcommit(changeEntry)

            shouter.shout("Revision '" + revision + "' accepted")

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
        componentname = ""
        lines = shell.getoutput("lscm --show-alias n show attributes -C %s -r %s" % (componentuuid, self.config.repo))
        if lines:
            componentname = lines[0].strip()[1:-1]
        return componentname

    def getbaselinename(self, baselineuuid):
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
