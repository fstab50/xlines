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

_project='xlines'


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
    if [[ -f /etc/redhat-release ]]; then
        return 0

    elif [[ $(grep -i centos /etc/os-release) ]]; then
        return 0

    elif [[ $(grep -i redhat /etc/os-release) ]]; then
        return 0
    fi

    return 1
}


if [ "$SUDO_USER" ]; then
    chown -R $SUDO_USER:$SUDO_USER /home/$SUDO_USER/.config
else
    chown -R $USER:$USER /home/$USER/.config
fi

exit 0
