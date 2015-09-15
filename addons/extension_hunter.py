import os
import argparse
from os.path import join, getsize


def parsecommandline():
    parser = argparse.ArgumentParser()
    directoryhelp = 'the root directory to start with'
    parser.add_argument('-d', '--directory', metavar='directory', dest='directory', help=directoryhelp, required=True)
    extensionshelp = 'a list of file extensions, such as: .zip .jar .exe (you can omit the leading .)'
    parser.add_argument('-e', '--extensions', metavar='extension', dest='extensions', help=extensionshelp, nargs='+', required=True)
    ignorehelp = 'directories to ignore, such as: bin out (common directories are listed in .directoryignore)'
    parser.add_argument('-i', '--ignoredirectories', metavar='directory', dest='directoriestoignore', help=ignorehelp, nargs='+', default=[], required=False)
    arguments = parser.parse_args()
    extensions = arguments.extensions
    i = 0
    for extension in extensions:
        if extension[0] != '.':
            extensions[i] = '.' + extension
        i += 1
    return (arguments.directory, extensions, arguments.directoriestoignore)


def read_directoryignore():
    directoriestoignore = []
    with open('./.directoryignore', 'r') as ignore:
        lines = ignore.readlines()
    for line in lines:
        directoriestoignore.append(line.strip())
    return directoriestoignore


if __name__ == "__main__":
    (directory, extensions, directoriestoignore) = parsecommandline()
    for defaultdirectory in read_directoryignore():
        directoriestoignore.append(defaultdirectory)

    for dir, subdirs, files in os.walk(directory):
        for directorytoignore in directoriestoignore:
            if directorytoignore in subdirs:
                subdirs.remove(directorytoignore)
        for file in files:
            for extension in extensions:
                if len(file) >= len(extension):
                    if file.endswith(extension):
                        filename = join(dir, file)
                        print('%10d  %s' % (getsize(filename), filename))
