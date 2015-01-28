import os
import shutil

from rtc2git.rtcFunctions import ImportHandler
from rtc2git.gitFunctions import Initializer
from rtc2git import config


def initialize(directory):
    if os.path.exists(directory):
        shutil.rmtree(directory)
    os.mkdir(directory)
    os.chdir(directory)
    gitInitializer.initalize()
    rtcHandler.initialize()
    gitInitializer.initialCommitAndPush()


def resume(directory):
    os.chdir(directory)
    os.chdir(gitInitializer.clonedRepoName)

myConfig = config.readConfig()
rtcHandler = ImportHandler(myConfig)
gitInitializer = Initializer(myConfig)
initialize(myConfig.workDirectory)
rtcHandler.acceptChangesFromStreams()



