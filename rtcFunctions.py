import sys
import os
import codecs
import sorter
import shell
from gitFunctions import Commiter
import shouter


class RTCInitializer:
    @staticmethod
    def initialize(config):
        RTCInitializer.loginandcollectstreams(config)
        workspace = WorkspaceHandler(config)
        if config.useexistingworkspace:
            shouter.shout("Use existing workspace to start migration")
            workspace.load()
        else:
            workspace.createandload(config.earlieststreamname, config.initialcomponentbaselines)

    @staticmethod
    def loginandcollectstreams(config):
        shell.execute("lscm login -r %s -u %s -P %s" % (config.repo, config.user, config.password))
        config.collectstreamuuids()


class WorkspaceHandler:
    def __init__(self, config):
        self.config = config
        self.workspace = config.workspace
        self.repo = config.repo

    def createandload(self, stream, componentbaselineentries=[], create=True):
        if create:
            shell.execute("lscm create workspace -r %s -s %s %s" % (self.config.repo, stream, self.workspace))
        if componentbaselineentries:
            self.setcomponentstobaseline(componentbaselineentries, stream)
        else:
            self.setcomponentstobaseline(ImportHandler(self.config).getcomponentbaselineentriesfromstream(stream),
                                         stream)
        self.load()

    def load(self):
        command = "lscm load -r %s %s --force" % (self.repo, self.workspace)
        shouter.shout("Start (re)loading current workspace: " + command)
        shell.execute(command)
        shouter.shout("Load of workspace finished")

    def setcomponentstobaseline(self, componentbaselineentries, streamuuid):
        for entry in componentbaselineentries:
            shouter.shout("Set component '%s' to baseline '%s'" % (entry.componentname, entry.baselinename))

            replacecommand = "lscm set component -r %s -b %s %s stream %s %s --overwrite-uncommitted" % \
                             (self.repo, entry.baseline, self.workspace, streamuuid, entry.component)
            shell.execute(replacecommand)

    def setnewflowtargets(self, streamuuid):
        shouter.shout("Set new Flowtargets")
        if not self.hasflowtarget(streamuuid):
            shell.execute("lscm add flowtarget -r %s %s %s" % (self.repo, self.workspace, streamuuid))

        command = "lscm set flowtarget -r %s %s --default --current %s" % (self.repo, self.workspace, streamuuid)
        shell.execute(command)

    def hasflowtarget(self, streamuuid):
        command = "lscm --show-uuid y --show-alias n list flowtargets -r %s %s" % (self.repo, self.workspace)
        flowtargetlines = shell.getoutput(command)
        for flowtargetline in flowtargetlines:
            splittedinformationline = flowtargetline.split("\"")
            uuidpart = splittedinformationline[0].split(" ")
            flowtargetuuid = uuidpart[0].strip()[1:-1]
            if streamuuid in flowtargetuuid:
                return True
        return False

    def recreateoldestworkspace(self):
        self.createandload(self.config.earlieststreamname, self.config.initialcomponentbaselines, False)


class Changes:
    
    latest_accept_command = ""

    @staticmethod
    def discard(workspace, *changeentries):
        idstodiscard = Changes._collectids(changeentries)
        shell.execute("lscm discard -w " + workspace + " --overwrite-uncommitted" + idstodiscard)

    @staticmethod
    def accept(workspace, logpath, *changeentries):
        for changeEntry in changeentries:
            shouter.shout("Accepting: " + changeEntry.tostring())
        revisions = Changes._collectids(changeentries)
        latest_accept_command = "lscm accept -v --overwrite-uncommitted -t " + workspace + " --changes" + revisions
        return shell.execute(latest_accept_command, logpath, "a")

    @staticmethod
    def _collectids(changeentries):
        ids = ""
        for changeentry in changeentries:
            ids += " " + changeentry.revision
        return ids


class ImportHandler:
    def __init__(self, config):
        self.config = config
        self.acceptlogpath = config.getlogpath("accept.txt")

    def getcomponentbaselineentriesfromstream(self, stream):
        filename = self.config.getlogpath("StreamComponents_" + stream + ".txt")
        command = "lscm --show-alias n --show-uuid y list components -v -r " + self.config.repo + " " + stream
        shell.execute(command, filename)
        componentbaselinesentries = []
        skippedfirstrow = False
        islinewithcomponent = 2
        component = ""
        baseline = ""
        componentname = ""
        baselinename = ""
        with codecs.open(filename, 'r', "utf-8-sig") as file:
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
        shouter.shoutwithdate("Start accepting %s changesets" % amountofchanges)
        amountofacceptedchanges = 0
        skipnextchangeset = False
        reloaded = False
        for changeEntry in changeentries:
            amountofacceptedchanges += 1
            if skipnextchangeset:
                skipnextchangeset = False
                continue
            acceptedsuccesfully = Changes.accept(self.config.workspace, self.acceptlogpath, changeEntry) is 0
            if not acceptedsuccesfully:
                shouter.shout("Change wasnt succesfully accepted into workspace")
                skipnextchangeset = self.retryacceptincludingnextchangeset(changeEntry, changeentries)
            elif not reloaded:
                if self.is_reloading_necessary():
                    WorkspaceHandler(self.config).load()
                reloaded = True
            shouter.shout("Accepted change %s/%s into working directory" % (amountofacceptedchanges, amountofchanges))
            git.addandcommit(changeEntry)

    @staticmethod
    def is_reloading_necessary():
        return shell.execute("git diff --exit-code") is 0

    def retryacceptincludingnextchangeset(self, change, changes):
        successfull = False
        nextchangeentry = self.getnextchangeset(change, changes)
        if nextchangeentry and (change.author == nextchangeentry.author or "merge" in nextchangeentry.comment.lower()):
            shouter.shout("Next changeset: " + nextchangeentry.tostring())
            if input("Press Enter to try to accept it with next changeset together, press any other key to skip this"
                     " changeset and continue"):
                return False
            Changes.discard(self.config.workspace, change)
            successfull = Changes.accept(self.config.workspace, self.acceptlogpath, change, nextchangeentry) is 0
            if not successfull:
                Changes.discard(self.config.workspace, change, nextchangeentry)

        if not successfull:
            shouter.shout("Last executed command: \n" + Changes.latest_accept_command)
            shouter.shout("Apropriate git commit command \n" + Commiter.getcommitcommand(change))
            if not input("Press Enter to continue or any other key to exit the program and rerun it with resume"):
                sys.exit("Please check the output and rerun programm with resume")
        return successfull

    @staticmethod
    def getnextchangeset(currentchangeentry, changeentries):
        nextchangeentry = None
        nextindex = changeentries.index(currentchangeentry) + 1
        has_next_changeset = nextindex is not len(changeentries)
        if has_next_changeset:
            nextchangeentry = changeentries[nextindex]
        return nextchangeentry

    def getchangeentriesofstreamcomponents(self, componentbaselineentries):
        missingchangeentries = {}
        shouter.shout("Start collecting changeentries")
        changeentriesbycomponentbaselineentry = {}
        for componentBaseLineEntry in componentbaselineentries:
            changeentries = self.getchangeentriesofbaseline(componentBaseLineEntry.baseline)
            for changeentry in changeentries:
                missingchangeentries[changeentry.revision] = changeentry
        return missingchangeentries

    def readhistory(self, componentbaselineentries, streamname):
        if not self.config.useprovidedhistory:
            warning = "Warning - UseProvidedHistory is set to false, merge-conflicts are more likely to happen. \n " \
                      "For more information see https://github.com/WtfJoke/rtc2git/wiki/Getting-your-History-Files"
            shouter.shout(warning)
            return None
        historyuuids = {}
        shouter.shout("Start reading history files")
        for componentBaseLineEntry in componentbaselineentries:
            history = self.gethistory(componentBaseLineEntry.componentname, streamname)
            historyuuids[componentBaseLineEntry.component] = history
        return historyuuids

    @staticmethod
    def getchangeentriestoaccept(missingchangeentries, history):
        changeentriestoaccept = []
        if history:
            historywithchangeentryobject = {}
            for key in history.keys():
                currentuuids = history.get(key)
                changeentries = []
                for uuid in currentuuids:
                    changeentry = missingchangeentries.get(uuid)
                    if changeentry:
                        changeentries.append(changeentry)
                historywithchangeentryobject[key] = changeentries
            changeentriestoaccept = sorter.tosortedlist(historywithchangeentryobject)
        else:
            changeentriestoaccept.extend(missingchangeentries.values())
            # simple sort by date - same as returned by compare command
            changeentriestoaccept.sort(key=lambda change: change.date)
        return changeentriestoaccept

    @staticmethod
    def getchangeentriesfromfile(outputfilename):
        informationseparator = "@@"
        numberofexpectedinformationseparators = 5
        changeentries = []

        with codecs.open(outputfilename, 'r', "utf-8-sig") as file:
            currentline = ""
            currentinformationpresent = 0
            for line in file:
                cleanedline = line.strip()
                if cleanedline:
                    currentinformationpresent += cleanedline.count(informationseparator)
                    if currentline:
                        currentline += os.linesep
                    currentline += cleanedline
                    if currentinformationpresent >= numberofexpectedinformationseparators:
                        splittedlines = currentline.split(informationseparator)
                        revisionwithbrackets = splittedlines[0].strip()
                        revision = revisionwithbrackets[1:-1]
                        author = splittedlines[1].strip()
                        email = splittedlines[2].strip()
                        comment = splittedlines[3].strip()
                        date = splittedlines[4].strip()

                        changeentries.append(ChangeEntry(revision, author, email, date, comment))

                        currentinformationpresent = 0
                        currentline = ""
        return changeentries

    @staticmethod
    def getsimplehistoryfromfile(outputfilename):
        revisions = []
        if not os.path.isfile(outputfilename):
            shouter.shout("History file not found: " + outputfilename)
            shouter.shout("Skipping this part of history")
            return revisions

        with codecs.open(outputfilename, 'r', "utf-8-sig") as file:
            for line in file:
                revisions.append(line.strip())
        revisions.reverse()  # to begin by the oldest
        return revisions

    def getchangeentriesofbaseline(self, baselinetocompare):
        return self.getchangeentriesbytypeandvalue("baseline", baselinetocompare)

    def getchangeentriesofstream(self, streamtocompare):
        shouter.shout("Start collecting changes since baseline creation")
        missingchangeentries = {}
        changeentries = self.getchangeentriesbytypeandvalue("stream", streamtocompare)
        for changeentry in changeentries:
            missingchangeentries[changeentry.revision] = changeentry
        return missingchangeentries

    def getchangeentriesbytypeandvalue(self, comparetype, value):
        dateformat = "yyyy-MM-dd HH:mm:ss"
        outputfilename = self.config.getlogpath("Compare_" + comparetype + "_" + value + ".txt")
        comparecommand = "lscm --show-alias n --show-uuid y compare ws %s %s %s -r %s -I sw -C @@{name}@@{email}@@ --flow-directions i -D @@\"%s\"@@" \
                         % (self.config.workspace, comparetype, value, self.config.repo, dateformat)
        shell.execute(comparecommand, outputfilename)
        return ImportHandler.getchangeentriesfromfile(outputfilename)

    def gethistory(self, componentname, streamname):
        outputfilename = self.config.gethistorypath("History_%s_%s.txt" % (componentname, streamname))
        return ImportHandler.getsimplehistoryfromfile(outputfilename)


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

    def tostring(self):
        return self.comment + " (Date: " + self.date + ", Author: " + self.author + ", Revision: " + self.revision + ")"


class ComponentBaseLineEntry:
    def __init__(self, component, baseline, componentname, baselinename):
        self.component = component
        self.baseline = baseline
        self.componentname = componentname
        self.baselinename = baselinename
