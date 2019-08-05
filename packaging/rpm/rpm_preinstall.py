#!/bin/python3


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
import re
import inspect
import subprocess
import platform

_project = 'xlines'
distribution = platform.linux_distribution()[0]


def _redhat_linux():
    """
    Determines if Redhat Enterprise Linux, Centos
    """
    try:
        if os.path.exists('/etc/redhat-release'):
            return True

        elif re.search('centos', distribution, re.IGNORECASE):
            return True

        elif re.search('redhat', distribution, re.IGNORECASE):
            return True
    except OSError:
        fx = inspect.stack()[0][3]
        print('{}: Problem determining Linux distribution'.format(fx))
    return False


def _package_installed(package):
    cmd = 'rpm -qi ' + package
    r = subprocess.getoutput(cmd)
    if 'Install Date' in r:
        return True
    return False


if _redhat_linux():

    cmd = 'yum -y install epel-release'

    r = subprocess.getoutput(cmd)

    if _package_installed('epel-release'):
        sys.exit(0)
    else:
        sys.exit(1)

sys.exit(0)
