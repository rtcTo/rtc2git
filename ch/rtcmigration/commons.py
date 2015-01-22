from subprocess import call



class Shell:
    spaceSeparator = "****"

    def execute(commandToExecute, outputfile="output.txt", openMode="w"):
        commands = []
        for splittedcommand in commandToExecute.split(' '):
            if splittedcommand.__contains__(Shell.spaceSeparator):
                splittedcommand = splittedcommand.replace(Shell.spaceSeparator, " ")
            commands.append(splittedcommand)
        with open(outputfile, openMode) as file:
            call(commands, stdout=file)
