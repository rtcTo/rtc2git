import os
import shutil

from rtc2git.ch.rtcmigration.rtc import ImportHandler
from rtc2git.ch.rtcmigration import commons


def initialize(dir):
    if os.path.exists(dir):
        shutil.rmtree(dir)
    os.mkdir(dir)
    os.chdir(dir)
    handler.initialize()

config = commons.readConfig()
handler = ImportHandler(config)
initialize(config.workDirectory)
# handler.acceptChangesFromStreams(streams)



