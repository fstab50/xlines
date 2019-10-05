#!/bin/bash

#
#  xlines preinstall script :  Copyright 2018-2019, Blake Huber
#
#  This program is free software: you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation, either version 3 of the License, or
#  (at your option) any later version.
#
#  see: https://www.gnu.org/licenses/#GPL
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  contained in the program LICENSE file.
#

#
#   Script Log Output
#
#       - Can be found in the system log location
#       - typically /var/log/messages
#
#

_project='xlines'
loginfo='[INFO]'
logwarn='[WARN]'

declare -a os_packages


function _pip_exec(){
    ##
    ##  Finds pip executable for python3 regardless of upgrade
    ##
    if [[ $(locate pip3 2>/dev/null | head -n1) ]]; then
        echo "$(locate pip3 2>/dev/null | head -n1)"
        return 0

    elif [[ $(locate pip 2>/dev/null | head -n1) ]]; then
        echo "$(locate pip 2>/dev/null | head -n1)"
        return 0
    fi
    return 1
}


function _redhat_linux(){
    ##
    ##  determines if Redhat Enterprise Linux, Centos
    ##
    if [[ -f /etc/redhat-release ]]; then
        return 0

    elif [[ $(grep -i centos /etc/os-release) ]]; then
        return 0

    elif [[ $(grep -i redhat /etc/os-release) ]]; then
        return 0
    fi

    return 1
}


function _amazonlinux(){
    ##
    ##  determines if Amazon Linux
    ##
    if [[ $(grep -i 'amazon linux' /etc/os-release) ]] && \
         [[ $(grep 'VERSION' /etc/os-release | grep '2') ]]; then
        logger "$loginfo: Amazon Linux 2 OS type detected."
        return 0
    fi
    return 1
}


function python_dependencies(){
    ##
    ##  Validates if deps installed (true) or not (false)
    ##
    local pip_bin="$1"

    if [[ $($pip_bin list | grep -i pygments) ]]; then
        logger "$loginfo: Current pygments install detected, skipping fresh install"
        return 0
    else
        return 1
    fi
}


# --- main --------------------------------------------------------------------


# build and update locate db
logger "$loginfo: Creating and updating local mlocate databases..."
updatedb

# locate pip executable
logger "$loginfo: Locating Python3 pip executable..."
_PIP=$(_pip_exec)
if [[ $_PIP ]]; then
    logger "$loginfo: pip executable path found: $_PIP"
else
    logger "$logwarn: failed to find pip executable path"
fi

logger "$loginfo: Set USER $USER ownership on .config directory..."
if [ "$SUDO_USER" ]; then
    chown -R $SUDO_USER:$SUDO_USER /home/$SUDO_USER/.config
else
    chown -R $USER:$USER /home/$USER/.config
fi

if _amazonlinux && ! python_dependencies $_PIP; then
    logger "$loginfo: Amazon Linux 2 os detected, but missing Pygments library. Installing..."
    # install pygments
    $_PIP install pygments
fi

# generate bytecode artifacts
if which py3compile >/dev/null 2>&1; then
    logger "$loginfo: py3compile found... initating bytecode compilation"
    py3compile --package python3?-xlines
else
    logger "$loginfo: py3compile not found... skipping bytecode compilation"
fi

# <-- end python package postinstall script -->

exit 0
