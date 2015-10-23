import os

if __name__ == "__main__":
    ignoredbutexist = []
    directory = '/home/huo/tmp/migrate_ESL/ESL'
    os.chdir(directory)
    ignorelines = []
    with open('.gitignore', 'r') as gitignore:
        ignorelines = gitignore.readlines()
    for line in ignorelines:
        if os.path.exists(line):
            ignoredbutexist.append(line)
    if len(ignoredbutexist) > 0:
        print("The following files have been ignored in the new git repository, but still exist in the actual RTC workspace:")
        for ignored in ignoredbutexist:
            print(ignored)
