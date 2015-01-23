import configparser

from rtc2git.ch.rtcmigration.commons import Shell
from rtc2git.ch.rtcmigration.rtc import ImportHandler


outputFileName = "output.txt"
repositoryURL = None
user = None
password = None
workspace = None
streams = None
mainStream = None
firstApplicationBaseLine = "Initial" + Shell.spaceSeparator + "CVS" + Shell.spaceSeparator + "Import"
firstBaseLine = "Initial" + Shell.spaceSeparator + "CVS" + Shell.spaceSeparator + "Migration"


def init():
    Shell.execute(
        "scm set component -r " + repositoryURL + " -b " + firstApplicationBaseLine + " " + workspace + " stream " + mainStream + " BP_Application BP_Application_UnitTest")
    Shell.execute(
        "scm set component -r " + repositoryURL + " -b " + firstBaseLine + " " + workspace + " stream " + mainStream + " BT_Frame_Installer BT_Frame_Server BT_Frame_UnitTest BX_BuildEnvironment")

def readConfig():
    config = configparser.ConfigParser()
    config.read("config.ini")
    global user, password, workspace, repositoryURL, streams, mainStream
    generalSection = config['General']
    user = generalSection['User']
    password = generalSection['Password']
    workspace = generalSection['WorkspaceName']
    repositoryURL = generalSection['Repo']
    mainStream = generalSection['Stream']
    streams = []
    for stream in config['Migration']['Streams'].split(","):
        streams.append(stream.strip())



readConfig()
#init()
handler = ImportHandler(workspace, repositoryURL)
handler.acceptChangesFromStreams(streams)