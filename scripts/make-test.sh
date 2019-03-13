#!/usr/bin/env bash

#
#   Purpose:  Makefile script, implements functionality for a target
#   Target:  test
#

PROJECT='keyup'
ROOT=$(git rev-parse --show-toplevel 2>/dev/null)
pkg_path=$(cd $(dirname $0); pwd -P)
CUR_DIR="$1"
VENV_DIR="$2"
MODULE_PATH="$3"
if [ "$4" = "true" ]; then
    PDB_DEBUG="true"
elif [ "$4" = "run" ]; then
    COMPLEXITY="true"
fi
MODULE="$5"
NOW="$(date +"%Y-%m-%d")"
MAKE=$(which make)
RESULTS='test-results.xml'
RESULTS_ALL="$NOW""_results-all-modules.xml"
RESULTS_DIR='./tests/results'
COVERAGE_REPORT_DIR="coverage-reports"

# required test modules
tests_dir=$ROOT'/tests'
REQUIREMENTS=$ROOT'/tests/requirements.txt'
declare -a TEST_PKGS=$(cat $REQUIREMENTS)

# source formatting statics
. $pkg_path/colors.sh


# --- declarations  ------------------------------------------------------------


function aws_default_region(){
    ## determine default aws region ##
    if [ $AWS_DEFAULT_REGION ]; then
        AWS_REGION=$AWS_DEFAULT_REGION
    else
        AWS_REGION=$(aws configure get default.region)
        # set this in the local env
        export AWS_DEFAULT_REGION=$AWS_REGION
    fi
    if [ ! $AWS_REGION ]; then
        std_message "Default AWS region could not be determined. Aborting tests" "WARN"
        exit 1
    fi
}


function virtual_environment(){
    ## setup and test of venv project prerequisites ##
    if [ ! -e $VENV_DIR ]; then
        $MAKE setup-venv
        source $VENV_DIR/bin/activate
        $VENV_DIR/bin/pip install -U $(echo ${TEST_PKGS[@]})   # install test modules

    else
        source $VENV_DIR/bin/activate

        # check for required test modules
        if [ ! "$($VENV_DIR/bin/pip list | grep pytest)" ]; then
            $VENV_DIR/bin/pip install -U $(echo ${TEST_PKGS[@]})
        fi
    fi
}

function std_logger(){
    local msg="$1"
    if [[ ! $PROJECT_log ]]; then
        echo "$pkg: failure to call std_logger, $PROJECT_log location undefined"
        exit $E_DIR
    fi
    echo "$(date +'%b %d %T') $host $pkg: $msg" >> "$PROJECT_log"
}

function std_message(){
    local msg="$1"
    local format="$3"
    #
    #std_logger "[INFO]: $msg"
    [[ $quiet ]] && return
    shift
    pref="----"
    if [[ $1 ]]; then
        pref="${1:0:5}"
        shift
    fi
    if [ $format ]; then
        printf '%*s\n\n' "${COLUMNS:-$(tput cols)}" '' | tr ' ' _
        echo -e "\n${yellow}[ $cyan$pref$yellow ]$reset  $msg\n" | indent04
    else
        echo -e "\n${yellow}[ $cyan$pref$yellow ]$reset  $msg\n" | indent04
    fi
}

function print_header(){
    ## prints header ##
    local test_module="$1"
    local description="$2"
    local end_module="$3"
    #
    printf '%*s\n\n' "${COLUMNS:-$(tput cols)}" '' | tr ' ' _
    printf "\u001b[37;1m%-14s\u001b[37;1m%-2s\033[0m %-6s\u001b[44;1m%-9s\u001b[37;0m%-15s\n" " " "  $test_module:" " $description " "$end_module" " "
    printf '%*s\n\n' "${COLUMNS:-$(tput cols)}" '' | tr ' ' _
}

function print_separator(){
    echo -e ${bold}${brightyellowgreen}
    printf '%*s\n' "${COLUMNS:-$(tput cols)}" '' | tr ' ' _
    echo -e ${reset}
}

function process_results(){
    local module=$(echo $1 | rev | awk -F '/' '{print $1}' | rev )
    local file="$RESULTS_DIR/$RESULTS_ALL"
    #
    #echo -e "\n\n<?xml version="1.0" encoding="utf-8"?><Module: $module>\n" >> $file
    cat $RESULTS >> $file
}

function pretest_setup(){
    if [ -e $RESULTS ]; then rm $RESULTS; fi
    if [ -e $RESULTS_DIR/$RESULTS_ALL ]; then rm "$RESULTS_DIR/$RESULTS_ALL"; fi
}

function clean(){
    if [ -e $RESULTS ]; then rm $RESULTS; fi
}

function functional_tests(){
    ## run py.test modules for functional tests    ##

    export PYTHONPATH=$PROJECT    # set interpreter path

    # print header
    print_header "pytest" "Modules --" "Functional Tests"

    if [ "$PDB_DEBUG" == "true" ]; then
        $VENV_DIR/bin/py.test --pdb
    elif [ $MODULE ]; then
        # module path is a single module
        $VENV_DIR/bin/py.test -v $CUR_DIR/tests/$MODULE
    else
        $VENV_DIR/bin/py.test -v $CUR_DIR/tests
    fi
}

function code_coverage(){
    ##  calculates code coverage, gen cli + html reports ##
    local report_dir="$1"
    #
    # print header
    print_header "coverage.py" "HTML Report" "Code Coverage"

    coverage run --source $PROJECT -m py.test $CUR_DIR/tests
    coverage report
    coverage html -d $report_dir
}


# --- main ---------------------------------------------------------------------


# set default AWS region
#aws_default_region

# venv initialization
virtual_environment

# verify setup of AWS Account to be used
sample_test_user='developer1'
bash $ROOT'/scripts/pretest-setup.sh' $sample_test_user || exit 1

# pre-test setup
cd $CUR_DIR
pretest_setup

# run functional tests, skip if jenkins environ (test run by coverage
functional_tests

# code coverage
code_coverage $COVERAGE_REPORT_DIR

# complexity
if [ $COMPLEXITY ]; then
    # print header
    print_header "mccabe" "Modules" "Cyclomatic Complexity"
    # set path, required for import
    export PYTHONPATH="."
    $VENV_DIR/bin/py.test -q --mccabe $MODULE_PATH
fi

print_separator
std_message "End ${title}$PROJECT${reset} Automated testing" "INFO"

# <-- end -->

exit 0
