import os
import shutil

from rtcFunctions import ImportHandler
from gitFunctions import Initializer
from gitFunctions import Commiter
import configuration
import shouter


def initialize(config, rtc):
    directory = config.workDirectory
    if os.path.exists(directory):
        shutil.rmtree(directory)
    os.mkdir(directory)
    os.chdir(directory)
    git = Initializer(config)
    git.initalize()
    rtc.initialize()
    git.initialcommitandpush()


def resume(config, rtc):
    os.chdir(config.workDirectory)
    os.chdir(config.clonedGitRepoName)
    rtc.loginandcollectstreams()


def startmigration():
    config = configuration.readconfig()
    rtc = ImportHandler(config)
    git = Commiter

    initialize(config.workDirectory)
    streamuuids = config.streamuuids
    for streamuuid in streamuuids:
        streamname = config.streamnames[streamuuids.index(streamuuid)]
        git.branch(streamname)
        componentbaselineentries = rtc.getcomponentbaselineentriesfromstream(streamuuid)
        rtc.acceptchangesintoworkspace(rtc.getchangeentriesofstream(componentbaselineentries))
        shouter.shout("All changes of stream '%s' accepted" % streamname)
        git.pushbranch(streamname)
        rtc.recreateworkspace(streamuuid)
        rtc.resetcomponentstobaseline(componentbaselineentries, streamuuid)
        rtc.reloadworkspace()

startmigration()
