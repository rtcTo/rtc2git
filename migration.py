import os
import shutil

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
        shutil.rmtree(directory)
    os.mkdir(directory)
    os.chdir(directory)
    git = Initializer(config)
    git.initalize()
    RTCInitializer.initialize(config)
    git.initialcommitandpush()


def resume(config):
    os.chdir(config.workDirectory)
    os.chdir(config.clonedGitRepoName)
    RTCInitializer.loginandcollectstreams(config)
    WorkspaceHandler(config).load()


def startmigration():
    config = configuration.readconfig()
    rtc = ImportHandler(config)
    rtcworkspace = WorkspaceHandler(config)
    git = Commiter

    initialize(config)
    streamuuids = config.streamuuids
    for streamuuid in streamuuids:
        streamname = config.streamnames[streamuuids.index(streamuuid)]
        git.branch(streamname)
        rtcworkspace.setnewflowtargets(streamuuid)
        componentbaselineentries = rtc.getcomponentbaselineentriesfromstream(streamuuid)
        rtc.acceptchangesintoworkspace(rtc.getchangeentriesofstreamcomponents(componentbaselineentries))
        shouter.shout("All changes of components of stream '%s' accepted" % streamname)
        git.pushbranch(streamname)

        rtcworkspace.setcomponentstobaseline(componentbaselineentries, streamuuid)
        rtcworkspace.load()
        rtc.acceptchangesintoworkspace(rtc.getchangeentriesofstream(streamuuid))
        git.pushbranch(streamname)
        shouter.shout("All changes of stream '%s' accepted - Migration of stream completed" % streamname)

        morestreamstomigrate = streamuuids.index(streamuuid) + 1 is not len(streamuuids)
        if morestreamstomigrate:
            rtcworkspace.recreateoldestworkspace()

startmigration()
