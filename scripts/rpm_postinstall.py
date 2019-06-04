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
import sys
import platform
import subprocess
from shutil import which
from shutil import copy2 as copyfile
from setuptools.command.install import install
import getpass
from pathlib import Path
from codecs import open


_project = 'xlines'
_root = os.path.abspath(os.path.dirname(__file__))
_ex_fname = 'exclusions.list'
_ex_dirs_fname = 'directories.list'
_comp_fname = 'xlines-completion.bash'
_homedir = str(Path.home())


def create_artifact(object_path, type):
    """Creates post install filesystem artifacts"""
    if type == 'file':
        with open(object_path, 'w') as f1:
            f1.write(sourcefile_content())
    elif type == 'dir':
        os.makedirs(object_path)


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
        if self.valid_os_shell():

            completion_dir = '/etc/bash_completion.d'
            config_dir = user_home() + '/.config/' + _project

            if not os.path.exists(completion_dir):
                create_artifact(completion_dir, 'dir')
            if not os.path.exists(config_dir):
                create_artifact(config_dir, 'dir')

            # ensure installation of home directory profile artifacts (data_files)
            if not os.path.exists(os_parityPath(completion_dir + '/' + _comp_fname)):
                copyfile(
                    os_parityPath('bash' + '/' + _comp_fname),
                    os_parityPath(completion_dir + '/' + _comp_fname)
                )
            if not os.path.exists(os_parityPath(config_dir + '/' + _ex_fname)):
                copyfile(
                    os_parityPath('config' + '/' + _ex_fname),
                    os_parityPath(config_dir + '/' + _ex_fname)
                )
            if not os.path.exists(os_parityPath(config_dir + '/' + _ex_dirs_fname)):
                copyfile(
                    os_parityPath('config' + '/' + _ex_dirs_fname),
                    os_parityPath(config_dir + '/' + _ex_dirs_fname)
                )
        install.run(self)

PostInstall()
