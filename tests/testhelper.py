from contextlib import contextmanager
import tempfile
import os
import shutil

from configuration import Builder
from gitFunctions import Initializer
import configuration


@contextmanager
def mkchdir(subfolder, folderprefix="rtc2test_case"):
    tempfolder = tempfile.mkdtemp(prefix=folderprefix + subfolder)
    os.chdir(tempfolder)
    try:
        yield tempfolder
    finally:
        shutil.rmtree(tempfolder, ignore_errors=True)  # on windows folder remains in temp, git process locks it


@contextmanager
def createrepo(reponame="test.git", folderprefix="rtc2test_case"):
    repodir = tempfile.mkdtemp(prefix=folderprefix)
    configuration.config = Builder().setworkdirectory(repodir).setgitreponame(reponame).build()
    initializer = Initializer()
    os.chdir(repodir)
    initializer.initalize()
    try:
        yield
    finally:
        shutil.rmtree(repodir, ignore_errors=True)  # on windows folder remains in temp, git process locks it
