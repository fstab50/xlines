"""

xlines :  Copyright 2018-2020, Blake Huber

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
from setuptools import setup, find_packages
from setuptools.command.develop import develop
from setuptools.command.install import install
import getpass
from codecs import open
import xlines


requires = [
    'Pygments'
]


_project = 'python38-xlines'
_root = os.path.abspath(os.path.dirname(__file__))
_ex_fname = 'exclusions.list'
_ex_dirs_fname = 'directories.list'
_comp_fname = 'xlines-completion.bash'


def _git_root():
    """Returns root directory of git repository"""
    cmd = 'git rev-parse --show-toplevel 2>/dev/null'
    return subprocess.getoutput(cmd).strip()


def _project_root(projectname):
    if projectname.startswith('python'):
        return projectname.split('-')[1]
    return projectname


def _root_user():
    """
    Checks localhost root or sudo access.  Returns bool
    """
    if os.geteuid() == 0:
        return True
    elif subprocess.getoutput('echo $EUID') == '0':
        return True
    return False


def _user():
    """Returns username of caller"""
    return getpass.getuser()


def _set_pythonpath():
    """
    Temporarily reset PYTHONPATH to prevent home dir = python module home
    """
    os.environ['PYTHONPATH'] = '/'


def create_artifact(object_path, type):
    """Creates post install filesystem artifacts"""
    if type == 'file':
        with open(object_path, 'w') as f1:
            f1.write(sourcefile_content())
    elif type == 'dir':
        os.makedirs(object_path)


def _install_root():
    """Filsystem installed location of program modules"""
    return os.path.abspath(os.path.dirname(xlines.common.__file__))


def module_dir():
    """Filsystem location of Python3 modules"""
    bin_path = which('python3.6') or which('python3.7')
    bin = bin_path.split('/')[-1]
    if 'local' in bin:
        return '/usr/local/lib/' + bin + '/site-packages'
    return '/usr/lib/' + bin + '/site-packages'


def os_parityPath(path):
    """
    Converts unix paths to correct windows equivalents.
    Unix native paths remain unchanged (no effect)
    """
    path = os.path.normpath(os.path.expanduser(path))
    if path.startswith('\\'):
        return 'C:' + path
    return path


class PostInstallDevelop(develop):
    """ post-install, development """
    def run(self):
        subprocess.check_call("bash scripts/post-install-dev.sh".split())
        develop.run(self)


class PostInstallRoot(install):
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
        # bash shell + root user
        if self.valid_os_shell():

            completion_dir = '/etc/bash_completion.d'
            config_dir = os.path.join(module_dir(), 'config')

            if not os.path.exists(os_parityPath(config_dir)):
                create_artifact(os_parityPath(config_dir), 'dir')

            ## ensure installation of home directory artifacts (data_files) ##

            # bash_completion; (overwrite if exists)
            copyfile(
                os_parityPath(os.path.join('bash', _comp_fname)),
                os_parityPath(os.path.join(completion_dir, _comp_fname))
            )
            # configuration files: excluded file types
            if not os.path.exists(os_parityPath(os.path.join(config_dir,  _ex_fname))):
                copyfile(
                    os_parityPath(os.path.join('config', _ex_fname)),
                    os_parityPath(os.path.join(config_dir, _ex_fname))
                )
            # configuration files: excluded directories
            if not os.path.exists(os_parityPath(os.path.join(config_dir, _ex_dirs_fname))):
                copyfile(
                    os_parityPath(os.path.join('config', _ex_dirs_fname)),
                    os_parityPath(os.path.join(config_dir, _ex_dirs_fname))
                )
        install.run(self)


def preclean(dst):
    if os.path.exists(dst):
        os.remove(dst)
    return True


def read(fname):
    basedir = os.path.dirname(sys.argv[0])
    return open(os.path.join(basedir, fname)).read()


setup(
    name=_project,
    version=xlines.__version__,
    description='Count the number of lines of code in a project',
    long_description=read('DESCRIPTION.rst'),
    url='https://github.com/fstab50/xlines',
    author=xlines.__author__,
    author_email=xlines.__email__,
    license='GPL-3.0',
    classifiers=[
        'Topic :: Software Development :: Build Tools',
        'Development Status :: 4 - Beta',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'License :: OSI Approved :: GNU General Public License v3 (GPLv3)',
        'Operating System :: POSIX :: Linux',
    ],
    keywords='code development tools',
    packages=find_packages(exclude=['assets', 'docs', 'reports', 'scripts', 'tests']),
    include_package_data=True,
    install_requires=requires,
    python_requires='>=3.6, <4',
    data_files=[
        (
            os.path.join('/etc/bash_completion.d'),
            [os.path.join('bash', _comp_fname)]
        ),
        (
            os.path.join(module_dir(), _project_root(_project), 'config'),
            [os.path.join('config', _ex_fname)]
        ),
        (
            os.path.join(module_dir(), _project_root(_project), 'config'),
            [os.path.join('config', _ex_dirs_fname)]
        )
    ],
    entry_points={
        'console_scripts': [
            'xlines=xlines.cli:init_cli'
        ]
    },
    zip_safe=False
)
