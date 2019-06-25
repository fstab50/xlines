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
from setuptools import setup, find_packages
import getpass
from pathlib import Path
from codecs import open
import xlines


requires = [
    'pygments'
]


_project = 'xlines'
_root = os.path.abspath(os.path.dirname(__file__))
_ex_fname = 'exclusions.list'
_ex_dirs_fname = 'directories.list'
_comp_fname = 'xlines-completion.bash'


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


def preclean(dst):
    if os.path.exists(dst):
        os.remove(dst)
    return True


def read(fname):
    basedir = os.path.dirname(sys.argv[0])
    return open(os.path.join(basedir, fname)).read()


def sourcefile_content():
    sourcefile = """
    for bcfile in ~/.bash_completion.d/* ; do
        [ -f "$bcfile" ] && . $bcfile
    done\n
    """
    return sourcefile


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
        'Development Status :: 3 - Alpha',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'License :: OSI Approved :: GNU General Public License v3 (GPLv3)',
        'Operating System :: POSIX :: Linux',
    ],
    keywords='code development tools',
    packages=find_packages(exclude=['assets', 'docs', 'reports', 'scripts', 'tests']),
    include_package_data=True,
    install_requires=requires,
    python_requires='>=3.6, <4',
    data_files=[
        (os_parityPath('/etc/bash_completion.d'), ['bash/' + _comp_fname]),
        (os_parityPath(module_dir() + '/' + _project + '/config/'), ['config/' + _ex_fname]),
        (os_parityPath(module_dir() +  '/' + _project + '/config/'), ['config/' + _ex_dirs_fname])
    ],
    entry_points={
        'console_scripts': [
            'xlines=xlines.cli:init_cli'
        ]
    },
    #options={'bdist_rpm': {'post_install': 'scripts/rpm_postinstall.py'}},
    zip_safe=False
)
