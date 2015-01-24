import os
import shutil

from rtc2git.ch.rtcmigration.rtc import ImportHandler
from rtc2git.ch.rtcmigration.git import Initializer
from rtc2git.ch.rtcmigration import commons


def initialize(dir):
    if os.path.exists(dir):
        shutil.rmtree(dir)
    os.mkdir(dir)
    os.chdir(dir)
    gitInitializer.initalize()
    rtcHandler.initialize()
    gitInitializer.initialCommitAndPush()


config = commons.readConfig()
rtcHandler = ImportHandler(config)
gitInitializer = Initializer(config)
initialize(config.workDirectory)
rtcHandler.acceptChangesFromStreams()



