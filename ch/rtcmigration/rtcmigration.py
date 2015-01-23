
from rtc2git.ch.rtcmigration.commons import Shell
from rtc2git.ch.rtcmigration.rtc import ImportHandler
from rtc2git.ch.rtcmigration import commons



firstApplicationBaseLine = "Initial" + Shell.spaceSeparator + "CVS" + Shell.spaceSeparator + "Import"
firstBaseLine = "Initial" + Shell.spaceSeparator + "CVS" + Shell.spaceSeparator + "Migration"

config = commons.readConfig()
handler = ImportHandler(config)
# handler.acceptChangesFromStreams(streams)