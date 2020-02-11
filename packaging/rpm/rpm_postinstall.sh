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

declare -a python_packages

python_packages=(
    'setuptools'
    'distro'
)


function _pip_exec(){
    ##
    ##  Finds pip executable for python3 regardless of upgrade
    ##
    local _pip
    logger "$loginfo: Locating Python3 pip executable..."

    if [[ $(/usr/local/bin/pip3 --version 2>/dev/null | grep "python\ 3.[6-9]") ]]; then
        _pip="/usr/local/bin/pip3"
        echo "$_pip"
        logger "$loginfo: pip3 executable path found: $_pip"
        return 0

    elif [[ $(/usr/bin/pip3 --version 2>/dev/null | grep "python\ 3.[6-9]") ]]; then
        _pip="/usr/bin/pip3"
        echo "$_pip"
        logger "$loginfo: pip3 executable path found: $_pip"
        return 0

    elif [[ $(/bin/pip3 --version 2>/dev/null | grep "python\ 3.[6-9]") ]]; then
        _pip="/bin/pip3"
        echo "$_pip"
        logger "$loginfo: pip3 executable path found: $_pip"
        return 0

    elif [[ $(/usr/local/bin/pip --version 2>/dev/null | grep "python\ 3.[6-9]") ]]; then
        _pip="/usr/local/bin/pip"
        echo "$_pip"
        logger "$loginfo: pip3 executable path found: $_pip"
        return 0
    fi

    logger "$logwarn: failed to find pip executable path"
    return 1
}


function _python_prerequisites(){
    ##
    ##  install Python3 package dependencies
    ##
    local pip_bin="$1"

    for pkg in "${python_packages[@]}"; do
        $pip_bin install -U $pkg 2>/dev/null
    done
}


function _redhat_centos(){
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
        logger "$loginfo: Amazon Linux 2 OS environment detected."
        return 0
    fi
    return 1
}


function _fedoralinux(){
    ##
    ##  determines if Amazon Linux
    ##
    if [[ $(distro 2>&1 | head -n 1 | grep -i fedora) ]]; then
        logger "$loginfo: Fedora Linux OS environment detected."
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


function set_permissions(){
    ##
    ##  Set ownership perms on ~/.config directory
    ##
    logger "$loginfo: Set USER $USER ownership on .config directory..."

    if [ "$SUDO_USER" ]; then
        chown -R $SUDO_USER:$SUDO_USER /home/$SUDO_USER/.config
    else
        chown -R $USER:$USER /home/$USER/.config
    fi
}


function sudoers_path(){
    BIN_PATH=/usr/local/bin

    # update sudoers path
    if [[ -f /etc/sudoers ]]; then

        var=$(grep secure_path /etc/sudoers)
        cur_path="$(echo ${var##*=})"

        if [[ -z "$(echo $cur_path | grep $BIN_PATH)" ]]; then
            # append secure_path (single quotes mandatory)
            sed -i '/secure_path/d' /etc/sudoers
        fi
    fi
}


# --- main --------------------------------------------------------------------


# build and update locate db
logger "$loginfo: Creating and updating local mlocate databases..."

# clear sudoers path to locate executables
sudoers_path

# locate pip executable
_PIP=$(_pip_exec)

# install python dependencies
_python_prerequisites "$_PIP"

# determine os
os="$(distro 2>&1 | head -n 1)"


if [ "$(echo $os | grep -i 'Redhat')" ] || [ "$(echo $os | grep -i 'CentOS')" ]; then
    logger "$loginfo: Redhat Linux OS environment detected, skipping dependency installation"

elif ! python_dependencies $_PIP; then
    logger "$loginfo: Missing Pygments library. Installing via pip3..."
    # install pygments
    $_PIP install pygments 2>/dev/null
fi


# Dependency installation verification
if _amazonlinux || _fedoralinux ; then
    logger "$loginfo: Amazon Linux 2 or Fedora detected, checking dependencies..."
    # install pygments
    $_PIP install pygments 2>/dev/null
fi


# generate bytecode artifacts
if which py3compile >/dev/null 2>&1; then
    logger "$loginfo: py3compile found... initating bytecode compilation"
    py3compile --package python3?-xlines
else
    logger "$loginfo: py3compile not found... skipping bytecode compilation"
fi

# return user ownership to ~/.config directory
set_permissions

# <-- end python package postinstall script -->

exit 0
