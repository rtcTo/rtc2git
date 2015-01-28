import os
import shutil

from rtc2git.rtcFunctions import ImportHandler
from rtc2git.gitFunctions import Initializer
from rtc2git import commons


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



