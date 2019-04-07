import os
import re
import sys
from enum import Enum, unique

import configuration
import shell
import shouter
import sorter
from configuration import ComponentBaseLineEntry
from gitFunctions import Commiter, Differ

loginCredentialsCommand = "-u '%s' -P '%s'"

class RTCInitializer:
    @staticmethod
    def initialize():
        RTCLogin.loginandcollectstreamuuid()
        workspace = WorkspaceHandler()
        config = configuration.get()
        if config.useexistingworkspace:
            shouter.shout("Use existing workspace to start migration")
            workspace.load()
        else:
            workspace.createandload(config.streamuuid, config.initialcomponentbaselines)


class RTCLogin:
    @staticmethod
    def loginandcollectstreamuuid():
        global loginCredentialsCommand
        config = configuration.get()
        if not config.stored:
            loginHeaderCommand = "%s login -r %s "
            exitcode = shell.execute((loginHeaderCommand + loginCredentialsCommand) % (config.scmcommand, config.repo, config.user, config.password))
            if exitcode is not 0:
                shouter.shout("Login failed. Trying again without quotes.")
                loginCredentialsCommand = "-u %s -P %s"
                exitcode = shell.execute((loginHeaderCommand + loginCredentialsCommand) % (config.scmcommand, config.repo, config.user, config.password))
                if exitcode is not 0:
                    sys.exit("Login failed. Please check your connection and credentials.")
        config.collectstreamuuids()

    @staticmethod
    def logout():
        config = configuration.get()
        if not config.stored:
            shell.execute("%s logout -r %s" % (config.scmcommand, config.repo))


class WorkspaceHandler:
    def __init__(self):
        self.config = configuration.get()
        self.workspace = self.config.workspace
        self.repo = self.config.repo
        self.scmcommand = self.config.scmcommand
        self.rtcversion = self.config.rtcversion

    def createandload(self, stream, componentbaselineentries=[]):
        shell.execute("%s create workspace -r %s -s %s %s" % (self.scmcommand, self.repo, stream, self.workspace))
        if componentbaselineentries:
            self.setcomponentstobaseline(componentbaselineentries, stream)
        else:
            self.setcomponentstobaseline(ImportHandler().determineinitialbaseline(stream),
                                         stream)
        self.load()

    def load(self):
        command = "%s load -r %s %s --force" % (self.scmcommand, self.repo, self.workspace)
        if self.config.includecomponentroots:
            command += " --include-root"
        shouter.shout("Start (re)loading current workspace: " + command)
        shell.execute(command)
        shouter.shout("Load of workspace finished")
        Commiter.restore_shed_gitignore(Commiter.get_untracked_statuszlines())


    def setcomponentstobaseline(self, componentbaselineentries, streamuuid):
        for entry in componentbaselineentries:
            shouter.shout("Set component '%s'(%s) to baseline '%s' (%s)" % (entry.componentname, entry.component,
                                                                            entry.baselinename, entry.baseline))

            replacecommand = "%s set component -r %s -b %s %s stream %s %s --overwrite-uncommitted" % \
                             (self.scmcommand, self.repo, entry.baseline, self.workspace, streamuuid, entry.component)
            shell.execute(replacecommand)

    def setnewflowtargets(self, streamuuid):
        shouter.shout("Set new Flowtargets")
        if not self.hasflowtarget(streamuuid):
            shell.execute("%s add flowtarget -r %s %s %s" % (self.scmcommand, self.repo, self.workspace, streamuuid))

        flowarg = ""
        if self.rtcversion >= 6:
            # Need to specify an arg to default and current option or
            # set flowtarget command will fail.
            # Assume that this is mandatory for RTC version >= 6.0.0
            flowarg = "b"
        command = "%s set flowtarget -r %s %s --default %s --current %s %s" % (self.scmcommand, self.repo, self.workspace,
                                                                               flowarg, flowarg, streamuuid)
        shell.execute(command)

    def hasflowtarget(self, streamuuid):
        command = "%s --show-uuid y --show-alias n list flowtargets -r %s %s" % (self.scmcommand, self.repo, self.workspace)
        flowtargetlines = shell.getoutput(command)
        for flowtargetline in flowtargetlines:
            splittedinformationline = flowtargetline.split("\"")
            uuidpart = splittedinformationline[0].split(" ")
            flowtargetuuid = uuidpart[0].strip()[1:-1]
            if streamuuid in flowtargetuuid:
                return True
        return False


class Changes:
    
    latest_accept_command = ""

    @staticmethod
    def discard(*changeentries):
        config = configuration.get()
        idstodiscard = Changes._collectids(changeentries)
        exitcode = shell.execute(config.scmcommand + " discard -w " + config.workspace + " -r " + config.repo + " -o" + idstodiscard)
        if exitcode is 0:
            for changeEntry in changeentries:
                changeEntry.setUnaccepted()

    @staticmethod
    def accept(logpath, *changeentries):
        for changeEntry in changeentries:
            shouter.shout("Accepting: " + changeEntry.tostring())
        revisions = Changes._collectids(changeentries)
        config = configuration.get()
        Changes.latest_accept_command = config.scmcommand + " accept --verbose --overwrite-uncommitted --accept-missing-changesets --no-merge --repository-uri " + config.repo + " --target " + \
                                        config.workspace + " --changes" + revisions
        exitcode = shell.execute(Changes.latest_accept_command, logpath, "a")
        if exitcode is 0:
            for changeEntry in changeentries:
                changeEntry.setAccepted()
            return True
        else:
            return False

    @staticmethod
    def _collectids(changeentries):
        ids = ""
        for changeentry in changeentries:
            ids += " " + changeentry.revision
        return ids

    @staticmethod
    def tostring(*changes):
        logmessage = "Changes: \n"
        for change in changes:
            logmessage += change.tostring() + "\n"
        shouter.shout(logmessage)


class ImportHandler:
    def __init__(self):
        self.config = configuration.get()
        self.acceptlogpath = self.config.getlogpath("accept.txt")

    def getcomponentbaselineentriesfromstream(self, stream):
        filename = self.config.getlogpath("StreamComponents_" + stream + ".txt")
        command = "%s --show-alias n --show-uuid y list components -v -m 30 -r %s %s" % (self.config.scmcommand,
                                                                                         self.config.repo, stream)
        shell.execute(command, filename)
        componentbaselinesentries = []
        skippedfirstrow = False
        islinewithcomponent = 2
        component = ""
        baseline = ""
        componentname = ""
        baselinename = ""

        with open(filename, 'r', encoding=shell.encoding) as file:
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
                        if self.config.rtcversion >= 6:
                            # fix trim brackets for vers. 6.x.x
                            baseline = uuidpart[7].strip()[1:-1]
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

    def determineinitialbaseline(self, stream):
        regex = "\(_[\w-]+\)"
        pattern = re.compile(regex)
        config = self.config
        componentbaselinesentries = self.getcomponentbaselineentriesfromstream(stream)
        logincredentials = ""
        if not config.stored:
            logincredentials = loginCredentialsCommand % (config.user, config.password)
        for entry in componentbaselinesentries:
            shouter.shout("Determine initial baseline of " + entry.componentname)
            # use always scm, lscm fails when specifying maximum over 10k
            command = "scm --show-alias n --show-uuid y list baselines --components %s -r %s %s -m 20000" % \
                      (entry.component, config.repo, logincredentials)
            baselineslines = shell.getoutput(command)
            baselineslines.reverse()  # reverse to have earliest baseline on top

            for baselineline in baselineslines:
                matcher = pattern.search(baselineline)
                if matcher:
                    matchedstring = matcher.group()
                    uuid = matchedstring[1:-1]
                    entry.baseline = uuid
                    entry.baselinename = "Automatically detected initial baseline"
                    shouter.shout("Initial baseline is: %s" % baselineline)
                    break
        return componentbaselinesentries

    def acceptchangesintoworkspace(self, changeentries):
        amountofchanges = len(changeentries)
        if amountofchanges == 0:
            shouter.shout("Found no changes to accept")
        else:
            shouter.shoutwithdate("Start accepting %s changesets" % amountofchanges)
        amountofacceptedchanges = 0

        for changeEntry in changeentries:
            amountofacceptedchanges += 1
            if not changeEntry.isAccepted(): # change could already be accepted from a retry
                if not Changes.accept(self.acceptlogpath, changeEntry):
                    shouter.shout(
                        "Change wasnt succesfully accepted into workspace, please load your workspace in eclipse and check whats wrong")
                    self.is_user_aborting(changeEntry)
                    # self.retryacceptincludingnextchangesets(changeEntry, changeentries)
                if not Differ.has_diff():
                    # no differences found - force reload of the workspace
                    shouter.shout("No changes for commiting in git detected, going to reload the workspace")
                    WorkspaceHandler().load()
                    if not Differ.has_diff():
                        shouter.shout("Still no changes... Please load your workspace in eclipse and check whats wrong")
                        # still no differences, something wrong
                        self.is_user_aborting(changeEntry)
                shouter.shout("Accepted change %d/%d into working directory" % (amountofacceptedchanges, amountofchanges))
                Commiter.addandcommit(changeEntry)
        return amountofacceptedchanges

    @staticmethod
    def collect_changes_to_accept_to_avoid_conflicts(changewhichcantbeacceptedalone, changes, maxchangesetstoaccepttogether):
        changestoaccept = [changewhichcantbeacceptedalone]
        nextchange = ImportHandler.getnextchangeset_fromsamecomponent(changewhichcantbeacceptedalone, changes)

        while True:
            if nextchange and len(changestoaccept) < maxchangesetstoaccepttogether:
                changestoaccept.append(nextchange)
                nextchange = ImportHandler.getnextchangeset_fromsamecomponent(nextchange, changes)
            else:
                break
        return changestoaccept

    def retryacceptincludingnextchangesets(self, change, changes):
        issuccessful = False
        changestoaccept = ImportHandler.collect_changes_to_accept_to_avoid_conflicts(change, changes, self.config.maxchangesetstoaccepttogether)
        amountofchangestoaccept = len(changestoaccept)

        if amountofchangestoaccept > 1:
            Changes.tostring(*changestoaccept)
            if self.config.useautomaticconflictresolution or self.is_user_agreeing_to_accept_next_change(change):
                shouter.shout("Trying to resolve conflict by accepting multiple changes")
                for index in range(1, amountofchangestoaccept):
                    toaccept = changestoaccept[0:index + 1]  # accept least possible amount of changes
                    if Changes.accept(self.acceptlogpath, *toaccept):
                        issuccessful = True
                        break
                    # ++++ check ++++
                    #else:
                    #    Changes.discard(*toaccept)  # revert initial state
        if not issuccessful:
            self.is_user_aborting(change)

    @staticmethod
    def is_user_agreeing_to_accept_next_change(change):
        messagetoask = "Press Y for accepting following changes, press N to skip"
        while True:
            answer = input(messagetoask).lower()
            if answer == "y":
                return True
            elif answer == "n":
                return not ImportHandler.is_user_aborting(change)
            else:
                shouter.shout("Please answer with Y/N, input was " + answer)

    @staticmethod
    def is_user_aborting(change):
        shouter.shout("Last executed command: \n" + Changes.latest_accept_command)
        shouter.shout("Appropriate git commit command \n" + Commiter.getcommitcommand(change))
        reallycontinue = "Do you want to continue? Y for continue, any key for abort"
        if input(reallycontinue).lower() == "y":
            return True
        else:
            sys.exit("Please check the output/log and rerun program with resume")

    @staticmethod
    def getnextchangeset_fromsamecomponent(currentchangeentry, changeentries):
        nextchangeentry = None
        component = currentchangeentry.component
        nextindex = changeentries.index(currentchangeentry) + 1
        while not nextchangeentry and nextindex < len(changeentries):
            candidateentry = changeentries[nextindex]
            if not candidateentry.isAccepted() and candidateentry.component == component:
                nextchangeentry = candidateentry
            nextindex += 1
        return nextchangeentry

    def getchangeentriesofstreamcomponents(self, componentbaselineentries):
        missingchangeentries = {}
        shouter.shout("Start collecting changeentries")
        for componentBaseLineEntry in componentbaselineentries:
            shouter.shout("Collect changes until baseline %s of component %s" %
                          (componentBaseLineEntry.baselinename, componentBaseLineEntry.componentname))
            changeentries = self.getchangeentriesofbaseline(componentBaseLineEntry.baseline)
            for changeentry in changeentries:
                missingchangeentries[changeentry.revision] = changeentry
        return missingchangeentries

    def readhistory(self, componentbaselineentries, streamname):
        if not self.config.useprovidedhistory:
            warning = "Warning - UseProvidedHistory is set to false, merge-conflicts are more likely to happen. \n " \
                      "For more information see https://github.com/rtcTo/rtc2git/wiki/Getting-your-History-Files"
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
            # simple sort by date
            changeentriestoaccept.sort(key=lambda change: change.date)
        return changeentriestoaccept

    @staticmethod
    def getchangeentriesfromfile(outputfilename):
        informationseparator = "@@"
        numberofexpectedinformationseparators = 5
        changeentries = []
        component="unknown"
        componentprefix = "Component ("

        with open(outputfilename, 'r', encoding=shell.encoding) as file:
            currentline = ""
            currentinformationpresent = 0
            for line in file:
                cleanedline = line.strip()
                if cleanedline:
                    if cleanedline.startswith(componentprefix):
                        length = len(componentprefix)
                        component = cleanedline[length:cleanedline.index(")", length)]
                    else:
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

                            changeentries.append(ChangeEntry(revision, author, email, date, comment, component))

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

        with open(outputfilename, 'r', encoding=shell.encoding) as file:
            for line in file:
                revisions.append(line.strip())
        revisions.reverse()  # to begin by the oldest
        return revisions

    def getchangeentriesofbaseline(self, baselinetocompare):
        return self.getchangeentriesbytypeandvalue(CompareType.baseline, baselinetocompare)

    def getchangeentriesofstream(self, streamtocompare):
        shouter.shout("Start collecting changes since baseline creation")
        missingchangeentries = {}
        changeentries = self.getchangeentriesbytypeandvalue(CompareType.stream, streamtocompare)
        for changeentry in changeentries:
            missingchangeentries[changeentry.revision] = changeentry
        return missingchangeentries

    def getchangeentriesofworkspace(self, workspacetocompare):
        missingchangeentries = {}
        changeentries = self.getchangeentriesbytypeandvalue(CompareType.workspace, workspacetocompare)
        for changeentry in changeentries:
            missingchangeentries[changeentry.revision] = changeentry
        return missingchangeentries

    def getchangeentriesbytypeandvalue(self, comparetype, value):
        dateformat = "yyyy-MM-dd HH:mm:ss"
        outputfilename = self.config.getlogpath("Compare_" + comparetype.name + "_" + value + ".txt")
        comparecommand = "%s --show-alias n --show-uuid y compare ws %s %s %s -r %s -I swc -C @@{name}@@{email}@@ --flow-directions i -D @@\"%s\"@@" \
                         % (self.config.scmcommand, self.config.workspace, comparetype.name, value, self.config.repo,
                            dateformat)
        shell.execute(comparecommand, outputfilename)
        return ImportHandler.getchangeentriesfromfile(outputfilename)

    def gethistory(self, componentname, streamname):
        outputfilename = self.config.gethistorypath("History_%s_%s.txt" % (componentname, streamname))
        return ImportHandler.getsimplehistoryfromfile(outputfilename)


class ChangeEntry:
    def __init__(self, revision, author, email, date, comment, component="unknown"):
        self.revision = revision
        self.author = author
        self.email = email
        self.date = date
        self.comment = comment
        self.component = component
        self.setUnaccepted()

    def getgitauthor(self):
        authorrepresentation = "%s <%s>" % (self.author, self.email)
        return shell.quote(authorrepresentation)

    def setAccepted(self):
        self.accepted = True

    def setUnaccepted(self):
        self.accepted = False

    def isAccepted(self):
        return self.accepted

    def tostring(self):
        return "%s (Date: %s, Author: %s, Revision: %s, Component: %s, Accepted: %s)" % \
               (self.comment, self.date, self.author, self.revision, self.component, self.accepted)


@unique
class CompareType(Enum):
    baseline = 1
    stream = 2
    workspace = 3
