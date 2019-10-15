"""
Summary.

    Build rpm, Fedora OS Environment (Version 30)

        - Document: RPM Build script
        - Distribution:  Amazon Linux 2
        - Author: Blake Huber
        - Copyright 2019, Blake Huber

"""

import os
import sys
import argparse
import datetime
import subprocess
from shutil import which
from colors import Colors
from libtools import stdout_message, logd
from config import script_config

# global logger
script_version = '1.0'
logd.local_config = script_config
logger = logd.getLogger(script_version)

c = Colors()


# --- globals --------------------------------------------------------------------------------------

pkg = subprocess.getoutput('basename $0')                       # pkg (script) full name
pkg_root = pkg.split('.')[1]                                    # pkg without file extention
pkg_path = subprocess.getoutput('cd $(dirname $0); pwd -P')     # location of pkg
VERSION = sys.argv[1]
username = 'builder'
home_dir = os.environ.get('HOME')
NOW = datetime.datetime.now().date().isoformat()
BUILDDIR = os.path.join(home_dir, 'rpmbuild')
VOLMNT = '/mnt/rpm'
LOG_DIR = os.path.join(home_dir, 'logs')
LOG_FILE = os.path.join(LOG_DIR, pkg_root + '.log')
QUIET = False

MAKE = which('make')

# colors
cyan = c.BRIGHT_CYAN
green = c.GREEN
rd = c.RED
yl = c.YELLOW
bd = c.BOLD                          # ansi format
ul = c.UNDERLINE                     # ansi format

# formatting
title = c.BOLD + c.BRIGHT_WHITE      # title color, white + bold
wt = c.BRIGHT_WHITE                  # help menu accent 2
fs = c.GOLD3                         # file path color
rst = c.RESET                        # clear accents; return terminal colors

# exit codes
E_OK = 0                                    # exit code if normal exit conditions
E_DEPENDENCY = 1                            # exit code if missing required ec2cdependency
E_NOLOG = 2                                 # exit code if failure to create log dir, log file
E_BADSHELL = 3                              # exit code if incorrect shell detected
E_AUTH = 4                                  # exit code if authentication failure
E_USER_CANCEL = 7                           # exit code if user cancel
E_BADARG = 8                                # exit code if bad input parameter
E_NETWORK_ACCESS = 9                        # exit code if no network access from current location
E_EXPIRED_CREDS = 10                        # exit code if temporary credentials no longer valid
E_MISC = 11                                 # exit code if miscellaneous (unspecified) error


# --- declarations ------------------------------------------------------------


def _git_root():
    """Determines full path to current git project root"""
    cmd = 'git rev-parse --show-toplevel 2>/dev/null'
    return subprocess.getoutput(cmd).strip()


def _pip_exec():
    """Finds pip executable for python3 regardless of upgrade"""
    if which('pip3'):
        return which('pip3')
    elif which('pip'):
        return which('pip')



function export_package(){
    ##
    ##  Copy newly created rpm package out of container
    ##
    local package
    local external='/mnt/rpm'

    cd "$(_git_root)/dist"

    package=$(find . -name "python37-xlines-[0-9].[0-9].*-[0-9].noarch.rpm")

    # truncate additional ./ chars
    package=$(echo $package | cut -c 3-50)

    cp "$package" "$external/$package"
    return 0

    if [[ -f "$external/$package" ]]; then
        return 0
    fi
    return 1
}


function increment_package_version(){
    ##
    ##  Runs version_update script to increment package
    ##  version -- OR -- hard set package version id
    ##
    local _root="$1"
    local version="$2"
    local python3bin=$(which python3)

    std_message "Initiating package version update (version $version)" 'INFO' $LOG_FILE
    # cd $_root && $python3bin "scripts/version_update.py"
    if [[ "$version" ]]; then
        std_message "Hard set version detected; using this version lable" 'INFO' $LOG_FILE
        cd $_root && $python3bin $_root/scripts/version_update.py --set-version "$version"
    else
        cd $_root && $python3bin $_root/scripts/version_update.py
    fi
}


function parse_parameters(){
    ##
    ##  Process command line parameters
    ##
    while [ $# -gt 0 ]; do
        case $1 in
            -h | --help)
                help_menu
                shift 1
                exit 0
                ;;

            -s | --set-version)
                VERSION="$2"
                shift 2
                ;;

            *)
                std_error_exit "Unknown parameter ($1). Exiting"
                ;;
        esac
    done

    if [[ $VERSION ]]; then
        std_message "VERSION number passed for hardset:  $VERSION"  'INFO' $LOG_FILE
    else
        std_message "No VERSION number passed into $pkg; increment existing version label" 'INFO' $LOG_FILE
    fi
    #
    # <-- end function parse_parameters -->
}


function precheck(){
    ##
    ##  Validate and create prerun structures
    ##
    local dir="$1"

    if [ ! -f "$dir" ]; then
        mkdir -p $dir
    fi

    std_message "Installing Python3 libraries & dependencies" "INFO" $LOG_FILE
    sudo -H $_PIP install -U libtools
}


function rpm_contents(){
    ##
    ##  Displays detailed view of all rpm contents
    ##
    local rpmfile="/home/builder/git/xlines/dist/python??-xlines*.noarch.rpm"
    local contents="/home/builder/rpmbuild/RPMS/rpm-contents.txt"

    rpm -qlpv $rpmfile > "$contents"
    return 0
}


# --- main --------------------------------------------------------------------
