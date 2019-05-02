#!/usr/bin/env bash

PACKAGE='xlines'
VERSION="$1"
PIP_CALL=$(which pip3)
GIT=$(which git)
ROOT=$(git rev-parse --show-toplevel 2>/dev/null)
VENV_DIR="$ROOT/p3_venv"
VERSION_MODULE='_version.py'

# Formatting
cyan=$(tput setaf 6)
white=$(tput setaf 7)
yellow=$(tput setaf 3)
reset=$(tput sgr0)
BOLD=`tput bold`
UNBOLD=`tput sgr0`

#
# Current Version Search Order:
#   1 - extract version of the package installed locally
#   2 - search pip repo for package, extract version if found
#   3 - extract version from local package repostory version / init module
#

# --- declarations  ------------------------------------------------------------

# indent
function indent02() { sed 's/^/  /'; }
function indent04() { sed 's/^/    /'; }


function restore_version(){
    $GIT checkout "$PACKAGE/$VERSION_MODULE"
}


function check_upgrade(){
    ## update local venv instal to avoid erroneous version reporting ##
    local package="$1"
    if [[ $($PIP_CALL list --outdated | grep $PACKAGE) ]]; then
        # package installed locally and reports valid upgrade
        return 0
    else
        return 1
    fi

}


function get_current_version(){
    ## gets current version of package in pypi or testpypi ##

    # check if installed locally
    if check_upgrade $PACKAGE; then

        version=$($PIP_CALL list --outdated | grep $PACKAGE | awk '{print $3}')
        std_message "Current version ($version) from available pypi ${yellow}$PACKAGE${reset} upgrade." INFO
        return 0

    else
        pip_local=$($PIP_CALL list | grep -i $PACKAGE  | awk '{print $2}')
    fi

    # if not, search pypi
    if [ -z $pip_local ]; then

        # search pypi repo
        pip_search=$($PIP_CALL search $PACKAGE | awk -F '(' '{print $2}' | awk -F ')' '{print $1}')

        if [ -z $pip_search ]; then
            # use local version module in package
            version=$(grep '__version__' $PACKAGE/_version.py  | head -n 1 | awk -F"'" '{print $2}')
            std_message "Current version ($version) found in ${yellow}$PACKAGE${reset} version module." INFO
        else
            std_message "Using version number from search for $PACKAGE in pypi repository." INFO
            version=$pip_search
        fi

    else
        std_message "Using locally installed $PACKAGE version number." INFO
        version=$pip_local
    fi
}


function update_minor_version(){
    ##
    ## increment minor version ##
    ##
    local force_version="$1"
    #
    if [ $force_version ]; then

        std_message "Updated_version number is: ${BOLD}$force_version${UNBOLD}" INFO
        echo "__version__ = '${force_version}'" > $ROOT/$PACKAGE/_version.py

    else

        if [ -z "$(echo $version | awk -F '.' '{print $3}')" ]; then
            add='1'
        else
            add=$(bc -l <<< "$(echo $version | awk -F '.' '{print $3}') + 1")
        fi
        updated_version="$(echo $version | awk -F '.' '{print $1"."$2}').$add"
        std_message "Updated_version number is: ${BOLD}$updated_version${UNBOLD}" INFO
        echo "__version__ = '${updated_version}'" > $ROOT/$PACKAGE/_version.py

    fi
}


function std_message(){
    local msg="$1"
    local format="$3"
    #
    [[ $quiet ]] && return
    shift
    pref="----"
    if [[ $1 ]]; then
        pref="${1:0:5}"
        shift
    fi
    if [ $format ]; then
        echo -e "${yellow}[ $cyan$pref$yellow ]$reset  $msg" | indent04
    else
        echo -e "\n${yellow}[ $cyan$pref$yellow ]$reset  $msg\n" | indent04
    fi
}


# --- main --------------------------------------------------------------------


if [ $ROOT ]; then
    cd $ROOT     # git repo ROOT dir
else
    echo -e '\nrepo ROOT not found. Exit'
    exit 1
fi

# current installed version
get_current_version

if [ $VERSION ]; then
    update_minor_version $VERSION
else
    # increment version number for upload to pypi
    update_minor_version
fi

exit 0
