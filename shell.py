from subprocess import call

spaceSeparator = "****"


def execute(commandToExecute, outputfile=None, openMode="w", useShell=True):
    command = getCommands(commandToExecute)
    if not outputfile:
        call(command, shell=useShell)
    else:
        with open(outputfile, openMode) as file:
            call(command, stdout=file, shell=useShell)


def getCommands(command):
    commands = []
    for splittedcommand in command.split(' '):
        if splittedcommand.__contains__(spaceSeparator):
            splittedcommand = splittedcommand.replace(spaceSeparator, " ")
        commands.append(splittedcommand)
    return commands
