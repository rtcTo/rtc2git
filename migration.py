import os
import sys

from rtcFunctions import ImportHandler
from rtcFunctions import WorkspaceHandler
from rtcFunctions import RTCInitializer
from gitFunctions import Initializer, Differ
from gitFunctions import Commiter
import configuration
import shouter


def initialize():
    config = configuration.get()
    directory = config.workDirectory
    if os.path.exists(directory):
        sys.exit("Configured directory already exists, please make sure to use a non-existing directory")
    os.makedirs(directory)
    os.chdir(directory)
    config.deletelogfolder()
    git = Initializer()
    git.initalize()
    git.initialcommitandpush()
    RTCInitializer.initialize()


def resume():
    config = configuration.get()
    os.chdir(config.workDirectory)
    os.chdir(config.clonedGitRepoName)
    if Differ.has_diff():
        sys.exit("Your git repo has some uncommited changes, please add/remove them manually")
    RTCInitializer.loginandcollectstreamuuid()
    if config.previousstreamname:
        prepare()
    else:
        WorkspaceHandler().load()


def migrate():
    rtc = ImportHandler()
    rtcworkspace = WorkspaceHandler()
    git = Commiter

    initialize()

    config = configuration.get()
    streamuuid = config.streamuuid
    streamname = config.streamname
    branchname = streamname + "_branchpoint"

    componentbaselineentries = rtc.getcomponentbaselineentriesfromstream(streamuuid)
    rtcworkspace.setnewflowtargets(streamuuid)
    git.branch(branchname)

    history = rtc.readhistory(componentbaselineentries, streamname)
    changeentries = rtc.getchangeentriesofstreamcomponents(componentbaselineentries)

    rtc.acceptchangesintoworkspace(rtc.getchangeentriestoaccept(changeentries, history))
    shouter.shout("All changes until creation of stream '%s' accepted" % streamname)
    git.pushbranch(branchname)
    git.branch(streamname)

    rtcworkspace.setcomponentstobaseline(componentbaselineentries, streamuuid)
    rtcworkspace.load()

    changeentries = rtc.getchangeentriesofstream(streamuuid)
    rtc.acceptchangesintoworkspace(rtc.getchangeentriestoaccept(changeentries, history))
    git.pushbranch(streamname)
    shouter.shout("\nAll changes accepted - Migration of stream '%s' is completed. \n"
                  "You should adjust your .gitignore to ignore the same files as defined in your .jazzignore \n"
                  "Afterwards you can distribute the git-repo '%s'" % (streamname, config.gitRepoName))


def prepare():
    config = configuration.get()
    rtc = ImportHandler()
    rtcworkspace = WorkspaceHandler()
    # git checkout branchpoint
    Commiter.checkout(config.previousstreamname + "_branchpoint")
    # list baselines of current workspace
    componentbaselineentries = rtc.getcomponentbaselineentriesfromstream(config.previousstreamuuid)
    # set components to that baselines
    rtcworkspace.setcomponentstobaseline(componentbaselineentries, config.previousstreamuuid)
    rtcworkspace.load()

if __name__ == "__main__":
    migrate()
