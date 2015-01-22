import configparser

from rtc2git.ch.rtcmigration.commons import Shell


outputFileName = "output.txt"
repositoryURL = None
user = None
password = None
workspace = None
stream = None
baseline = "_BCxObPNyEeKb7fdMNGs5Yw" #rc-1306
firstApplicationBaseLine = "Initial" + Shell.spaceSeparator + "CVS" + Shell.spaceSeparator + "Import"
firstBaseLine = "Initial" + Shell.spaceSeparator + "CVS" + Shell.spaceSeparator + "Migration"


def init():
    Shell.execute("lscm set component -r " + repositoryURL + " -b " + firstApplicationBaseLine + " " + workspace + " stream " + stream + " BP_Application BP_Application_UnitTest")
    Shell.execute("lscm set component -r " + repositoryURL + " -b " + firstBaseLine + " " + workspace +" stream " + stream + " BT_Frame_Installer BT_Frame_Server BT_Frame_UnitTest BX_BuildEnvironment")

def readConfig():
    config = configparser.ConfigParser()
    config.read("config.ini")
    global user, password, workspace, repositoryURL, stream
    generalSection = config['General']
    user = generalSection['User']
    password = generalSection['Password']
    workspace = generalSection['WorkspaceName']
    repositoryURL = generalSection['Repo']
    stream = generalSection['Stream']




readConfig()
#init()
#RTC.acceptChangesFromBaseLine(baseline)
