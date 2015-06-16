import os
import sys

from rtcFunctions import ImportHandler
from rtcFunctions import WorkspaceHandler
from rtcFunctions import RTCInitializer
from gitFunctions import Initializer
from gitFunctions import Commiter
import configuration
import shouter


def initialize(config):
    directory = config.workDirectory
    if os.path.exists(directory):
        sys.exit("Configured directory already exists, please make sure to use a non-existing directory")
    os.makedirs(directory)
    os.chdir(directory)
    config.deletelogfolder()
    git = Initializer(config)
    git.initalize()
    RTCInitializer.initialize(config)
    git.initialcommitandpush()


def resume(config):
    os.chdir(config.workDirectory)
    os.chdir(config.clonedGitRepoName)
    if not ImportHandler(config).is_reloading_necessary():
        sys.exit("Directory is not clean, please commit untracked files or revert them")

    RTCInitializer.loginandcollectstreamuuid(config)
    if config.previousstreamname:
        prepare(config)
    else:
        WorkspaceHandler(config).load()

def migrate():
    config = configuration.read()
    rtc = ImportHandler(config)
    rtcworkspace = WorkspaceHandler(config)
    git = Commiter
    resume(config)
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
    shouter.shout("All changes of stream '%s' accepted - Migration of stream completed" % streamname)


def prepare(config):
    rtc = ImportHandler(config)
    rtcworkspace = WorkspaceHandler(config)
    # git checkout branchpoint
    Commiter.checkout(config.previousstreamname + "_branchpoint")
    # list baselines of current workspace
    componentbaselineentries = rtc.getcomponentbaselineentriesfromstream(config.previousstreamuuid)
    # set components to that baselines
    rtcworkspace.setcomponentstobaseline(componentbaselineentries, config.previousstreamuuid)
    rtcworkspace.load()

if __name__ == "__main__":
    migrate()
