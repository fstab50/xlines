#!/usr/bin/env bash

#
#   Document: RPM Build script
#   Distribution:  Amazon Linux 2
#   Author: Blake Huber
#
#   Copyright 2019, Blake Huber
#

# --- globals --------------------------------------------------------------------------------------

pkg=$(basename $0)                                  # pkg (script) full name
pkg_root=$(echo $pkg | awk -F '.' '{print $1}')     # pkg without file extention
pkg_path=$(cd $(dirname $0); pwd -P)                # location of pkg
username="builder"
home_dir="$(echo $HOME)"
NOW=$(date +'%Y-%m-%d')
BUILDDIR="$HOME/rpmbuild"
VOLMNT="/mnt/rpm"
LOG_DIR="$HOME/logs"
LOG_FILE="$LOG_DIR/$pkg_root.log"
QUIET="false"

MAKE=$(which make)

# colors
brightwhite='\033[38;5;15m'
cyan=$(tput setaf 6)
green=$(tput setaf 2)
red=$(tput setaf 1)
yellow=$(tput setaf 3)
BOLD='\u001b[1m'                          # ansi format
bold='\u001b[1m'                          # ansi format
underline='\u001b[4m'                     # ansi format

# formatting
title=$(echo -e ${bold}${brightwhite})    # title color, white + bold
ul=$(echo -e ${underline})                # std underline
bd=$(echo -e ${bold})                     # std bold
wt=$(echo -e ${brightwhite})              # help menu accent 2
fs=$(echo -e ${yellow})                   # file path color
reset='\u001b[0m'                         # clear accents; return terminal colors

# exit codes
E_OK=0                                    # exit code if normal exit conditions
E_DEPENDENCY=1                            # exit code if missing required ec2cdependency
E_NOLOG=2                                 # exit code if failure to create log dir, log file
E_BADSHELL=3                              # exit code if incorrect shell detected
E_AUTH=4                                  # exit code if authentication failure
E_USER_CANCEL=7                           # exit code if user cancel
E_BADARG=8                                # exit code if bad input parameter
E_NETWORK_ACCESS=9                        # exit code if no network access from current location
E_EXPIRED_CREDS=10                        # exit code if temporary credentials no longer valid
E_MISC=11                                 # exit code if miscellaneous (unspecified) error


# --- declarations ------------------------------------------------------------


function _git_root(){
    ##
    ##  determines full path to current git project root
    ##
    echo "$(git rev-parse --show-toplevel 2>/dev/null)"
}


function _pip_exec(){
    ##
    ##  Finds pip executable for python3 regardless of upgrade
    ##
    if [[ $(which pip3) ]]; then
        echo "$(which pip3)"
        return 0
    elif [[ $(which pip) ]]; then
        echo "$(which pip)"
        return 0
    fi
    return 1
}


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


ROOT=$(_git_root)
_PYTHON3_PATH=$(which python3)
_YUM=$(which yum)
_SED=$(which sed)
_PIP=$(_pip_exec)
_POSTINSTALL=${ROOT}/packaging/rpm/rpm_postinstall.sh
REQUIRES='python3,python3-pip,python3-setuptools,bash-completion,mlocate,which'

# colors; functions
. "$ROOT/scripts/colors.sh"
. "$ROOT/scripts/std_functions.sh"


# prerun functions
precheck "$LOG_DIR"
parse_parameters $@
increment_package_version "$ROOT" "$VERSION"


# commence rpm package build
if lsb_release -sirc | grep -i amazon >/dev/null 2>&1; then

    # prerun update
    cd $ROOT || exit $E_DEPENDENCY
    git pull

    std_message "Dependency check: validate epel package repository installed" "INFO" $LOG_FILE

    if [[ $(sudo ${_YUM} repolist 2>/dev/null | grep epel) ]]; then
        std_message "epel Redhat extras packages repository installed." "OK" $LOG_FILE
    else
        std_message "ERROR: epel Redhat extras packages repository NOT installed. Exit" "WARN" $LOG_FILE
        exit $E_DEPENDENCY
    fi

    # strip out sudo path restrictions
    sudo $_SED -i '/env_reset/d' /etc/sudoers

    std_message "Installing OS packages" "INFO" $LOG_FILE
    sudo $_YUM -y install python3 python3-pip python3-setuptools which

    std_message "Upgrade pip, setuptools" "INFO" $LOG_FILE
    sudo -H $_PIP install -U pip setuptools

    std_message "Coping setuptools lib from /usr/local/lib to /usr/lib/" "INFO" $LOG_FILE
    sudo cp -r /usr/local/lib/python3.*/site-packages/setuptools* /usr/lib/python3.*/site-packages/

    std_message "Coping pkg_resources lib from /usr/local/lib to /usr/lib/" "INFO" $LOG_FILE
    sudo cp -r /usr/local/lib/python3.*/site-packages/pkg_resources* /usr/lib/python3.*/site-packages/

    # python3 build process
    $_PYTHON3_PATH setup_amzn.py bdist_rpm --requires=${REQUIRES} \
                                          --python='/usr/bin/python3' \
                                          --post-install=${_POSTINSTALL}

    # process completed rpm
    export_package

    # output rpm contents
    contents="RPMS/rpm-contents.txt"
    std_message "RPM Contents:" "INFO" $LOG_FILE
    rpm_contents

    std_message "Setting USER $USER ownership on docker Vol mnt post export of completed artifacts" "INFO" $LOG_FILE
    sudo chown -R $USER:$USER $VOLMNT

    # copy out completed rpm
    std_message "copy completed rpm to volume mount: $VOLMNT" "INFO" $LOG_FILE
    cp -v /home/builder/git/xlines/dist/*noarch.rpm $VOLMNT/ | sudo tee -a $LOG_FILE

    # copy out complete rpm contents index file
    std_message "copy rpm contents indext file to volume mount: $VOLMNT" "INFO" $LOG_FILE
    cp -rv ~/rpmbuild/RPMS $VOLMNT/ | sudo tee -a $LOG_FILE

else
    std_message "Not a Redhat-based Linux distribution. Exit" "WARN" $LOG_FILE
    exit 1
fi

exit 0
