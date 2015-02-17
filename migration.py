import os
import shutil

from rtcFunctions import ImportHandler
from gitFunctions import Initializer
from gitFunctions import Commiter
import configuration
import shouter


def initialize(directory):
    if os.path.exists(directory):
        shutil.rmtree(directory)
    os.mkdir(directory)
    os.chdir(directory)
    gitInitializer.initalize()
    rtc.initialize()
    gitInitializer.initialcommitandpush()


def resume(directory):
    os.chdir(directory)
    os.chdir(gitInitializer.clonedRepoName)
    rtc.loginandcollectstreams()


def startmigration():
    initialize(config.workDirectory)
    streamuuids = config.streamuuids
    for streamuuid in streamuuids:
        streamname = config.streamnames[streamuuids.index(streamuuid)]
        git.branch(streamname)
        componentbaselineentries = rtc.getbaselinesfromstream(streamuuid)
        for componentBaseLineEntry in componentbaselineentries:
            rtc.acceptchangesfrombaseline(componentBaseLineEntry)
        shouter.shout("All changes of stream '%s' accepted" % streamname)
        git.pushbranch(streamname)
        rtc.setcomponentsofnextstreamtoworkspace(componentbaselineentries)
        rtc.reloadworkspace()


config = configuration.readconfig()
rtc = ImportHandler(config)
gitInitializer = Initializer(config)
git = Commiter()
startmigration()
