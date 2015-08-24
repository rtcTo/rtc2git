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
    previousdir = os.getcwd()
    os.chdir(tempfolder)
    try:
        yield tempfolder
    finally:
        os.chdir(previousdir)
        shutil.rmtree(tempfolder, ignore_errors=True)  # on windows folder remains in temp, git process locks it


@contextmanager
def createrepo(reponame="test.git", folderprefix="rtc2test_case"):
    repodir = tempfile.mkdtemp(prefix=folderprefix)
    configuration.config = Builder().setworkdirectory(repodir).setgitreponame(reponame).build()
    initializer = Initializer()
    previousdir = os.getcwd()
    os.chdir(repodir)
    initializer.initalize()
    try:
        yield
    finally:
        os.chdir(previousdir)
        shutil.rmtree(repodir, ignore_errors=True)  # on windows folder remains in temp, git process locks it


@contextmanager
def cd(newdir):
    """
    Change directory to newdir and return to the previous upon completion
    :param newdir: directory to change to
    """
    previousdir = os.getcwd()
    os.chdir(os.path.expanduser(newdir))
    try:
        yield
    finally:
        os.chdir(previousdir)
