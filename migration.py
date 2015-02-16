import os
import shutil

from rtcFunctions import ImportHandler
from gitFunctions import Initializer
import config


def initialize(directory):
    if os.path.exists(directory):
        shutil.rmtree(directory)
    os.mkdir(directory)
    os.chdir(directory)
    gitInitializer.initalize()
    rtcHandler.initialize()
    gitInitializer.initialcommitandpush()


def resume(directory):
    os.chdir(directory)
    os.chdir(gitInitializer.clonedRepoName)
    rtcHandler.loginandcollectstreams()
    rtcHandler.reloadworkspace()  # remove any locks which are left over from previous try


myConfig = config.readconfig()
rtcHandler = ImportHandler(myConfig)
gitInitializer = Initializer(myConfig)
initialize(myConfig.workDirectory)
rtcHandler.acceptchangesfromstreams()
