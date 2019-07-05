#!/usr/bin/python3
"""

xlines :  Copyright 2018-2019, Blake Huber

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

see: https://www.gnu.org/licenses/#GPL

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
contained in the program LICENSE file.

"""

import os
import platform
import subprocess
from shutil import which
from shutil import copy2 as copyfile
from setuptools.command.install import install
from pathlib import Path
from codecs import open


_project = 'xlines'
_root = os.path.abspath(os.path.dirname(__file__))
_ex_fname = 'exclusions.list'
_ex_dirs_fname = 'directories.list'
_comp_fname = 'xlines-completion.bash'
_homedir = str(Path.home())


def os_parityPath(path):
    """
    Converts unix paths to correct windows equivalents.
    Unix native paths remain unchanged (no effect)
    """
    path = os.path.normpath(os.path.expanduser(path))
    if path.startswith('\\'):
        return 'C:' + path
    return path


class PostInstall(install):
    """
    Summary.

        Postinstall script to place bash completion artifacts
        on local filesystem

    """
    def valid_os_shell(self):
        """
        Summary.

            Validates install environment for Linux and Bash shell

        Returns:
            Success | Failure, TYPE bool

        """
        if platform.system() == 'Windows':
            return False
        elif which('bash'):
            return True
        elif 'bash' in subprocess.getoutput('echo $SHELL'):
            return True
        return False

    def run(self):
        """
        Summary.

            Executes post installation configuration only if correct
            environment detected

        """
        py_version = os.path.split(which('python3.7'))[1] or os.path.split(which('python3.6'))[1]
        pygments_core = 'pygments'
        pygments_dist = 'Pygments-*.dist-info'
        _libdir = '/usr/local/lib64/' + py_version + '/site-packages'

        # ensure installation of pygments in correct location
        if not os.path.exists(os_parityPath(_libdir + '/' + pygments_core)):
            copyfile(
                os_parityPath(pygments_core),
                os_parityPath(_libdir + '/' + pygments_core)
            )
            copyfile(
                os_parityPath(pygments_dist),
                os_parityPath(_libdir + '/' + pygments_dist)
            )
        install.run(self)


PostInstall()
