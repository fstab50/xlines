#!/usr/bin/env bash

#
#   Purpose:  Makefile script, implements functionality for a target
#   Target:  test
#

PROJECT='xlines'
ROOT=$(git rev-parse --show-toplevel 2>/dev/null)
pkg_path=$(cd "$(dirname $0)"; pwd -P)
CUR_DIR="$ROOT"
MODULE_PATH="$CUR_DIR/$PROJECT"
VENV_DIR="$ROOT/p3_venv"
NOW="$(date +"%Y-%m-%d")"
MAKE=$(which make)
RESULTS='test-results.xml'
RESULTS_ALL="$NOW""_results-all-modules.xml"
RESULTS_DIR='./tests/results'
COVERAGE_REPORT_DIR="coverage-reports"
PYTHON3_PATH=$(which python3)

# required test modules
tests_dir=$ROOT'/tests'
REQUIREMENTS=$ROOT'/tests/requirements.txt'

# clean artifacts
SCRIPTS_DIR="$ROOT/scripts"
CLEANUP_SCRIPT="${SCRIPTS_DIR}/posttest_clean.py"

# source formatting statics
. $pkg_path/colors.sh

# formatting
bbc=$(echo -e ${bold}${a_brightcyan})
title=$(echo -e ${bold}${a_brightwhite})              # title color, white + bold
hic=$(echo -e ${bold}${a_brightyellowgreen})          # help menu accent 1
bin=$(echo -e ${bold}${a_orange})                     # help menu binary accent
ul=$(echo -e ${underline})                            # std underline
bd=$(echo -e ${bold})                                 # std bold
wt=$(echo -e ${a_brightwhite})                        # help menu accent 2
fs=$(echo -e ${yellow})                               # file path color
btext=${reset}                                        # clear accents; rtn to native term colors
frame=${btext}


# --- declarations  ------------------------------------------------------------


function help_menu(){
    cat <<EOM

                       ${title}make test${btext} command help

  ${title}DESCRIPTION${btext}

        Bash script controller for testing python projects via the
        pytest, pylint, moto, and coverage testing frameworks

  ${title}SYNOPSIS${btext}

      $ ${bin}$PROJECT${reset} -p ${bbc}<${btext}value${bbc}>${btext} ${bbc}[${btext} --complexity ${bbc}|${btext} --coverage ${bbc}|${btext} --mccabe ${bbc}]${btext}

                        [-r | --root <value>  ]
                        -v | --venv <value>
                        -p | --package-path <value>
                       [-m | --module <value> ]
                       [-a | --coverage ]
                       [-h | --help  ]
                       [-d | --pdb ]
                       [-c | --complexity ]

  ${title}OPTIONS${btext}

        ${title}-r${btext}, ${title}--root${btext}  <value>: Filesystem directory ("root") of the project
            tested (Override only -- set to default setting if missing)

        ${title}-v${btext}, ${title}--venv${btext}:  Filesystem directory  location of the python virtual
            environment (venv, Override; default setting if missing)

        ${title}-p${btext}, ${title}--package-path${btext}:  Filesystem directory  location of the python
            package contain  all modules to be tested.  Override; default
            setting if --package-path option omitted.

        ${title}-m${btext}, ${title}--module${btext}:  When given, execute tests against a single python
            module

        ${title}-d${btext}, ${title}--pdb${btext}:  Enable the python debugger module, pdb, at runtime.

        ${title}-c${btext}, ${title}--complexity${btext}: Run McCabe Complexity Measurements after pytest
            unittests. Produces html report in

        ${title}-a${btext}, ${title}--coverage${btext}:  Generate code coverage report summary to stdout.
            Detailed coverage reports generated in html format located in
            the "coverage-reports" directory in the project root.

        ${title}-h${btext}, ${title}--help${btext}:  Display this help menu.

  ___________________________________________________________________________

          To execute all tests, type:  ${title}make${btext} test from project root
  ___________________________________________________________________________

${reset}
EOM
    #
    # <-- end function help_menu -->
}


function artifact_clean_operation(){
    print_separator
    # print header
    print_header "make" "::" "Clean Test Artifacts"
    #$PYTHON3_PATH $SCRIPTS_DIR/posttest_clean.py
    $MAKE clean-tests
    print_separator
}


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
    ##
    ## setup and test of venv project prerequisites ##
    ##
    local venv_dir="$1"

    if [ ! -e $venv_dir ]; then
        $MAKE setup-venv
        source "$venv_dir/bin/activate"
        $venv_dir/bin/pip install -r  ${REQUIREMENTS}  # install test modules

    else
        source "$venv_dir/bin/activate"

        # check for required test modules
        if [ ! "$($venv_dir/bin/pip list | grep pytest)" ]; then
            $venv_dir/bin/pip install -r  ${REQUIREMENTS}  # install test modules
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
    printf "\u001b[37;1m%-14s\u001b[37;1m%-2s\033[0m %-4s\u001b[44;1m%-7s\u001b[37;0m%-15s\n" " " "  $test_module" " $description " "$end_module" " "
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
    ##
    ## run py.test modules for functional tests    ##
    ##
    local module="$1"

    export PYTHONPATH=$PROJECT    # set interpreter path

    # print header
    print_header "pytest" "Modules --" "Functional Tests"

    if [ "$PDB_DEBUG" = "true" ]; then
        $VENV_DIR/bin/py.test --pdb

    elif [ $module ]; then
        # module path is a single module
        $VENV_DIR/bin/py.test -v $CUR_DIR/tests/$module
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


function parse_parameters(){
    ##
    ##  Parse all command-line parameters
    ##

    local var command

    if [[ ! "$*" ]]; then

        help_menu
        exit 0

    else
        while [ $# -gt 0 ]; do
            case $1 in
                '-c' | '--complexity')
                    COMPLEXITY="true"
                    shift 1
                    ;;

                '-a' | '--coverage')
                    COVERAGE="true"
                    shift 1
                    ;;

                '-d' | '--pdb')
                    PDB_DEBUG="true"
                    shift 1
                    ;;

                '-h' | '--help')
                    help_menu
                    exit 0
                    ;;

                '-m' | '--module')
                    MODULE="$2"
                    shift 2
                    ;;

                '-p' | '--package-path')
                    MODULE_PATH="$2"
                    shift 2
                    ;;

                '-r' | '--root')
                    CUR_DIR="$2"
                    shift 2
                    ;;

                '-v' | '--venv')
                    VENV_DIR="$2"
                    shift 2
                    ;;

                *)
                    std_warn "You must provide a valid parameter or None"
                    exit 1
                    ;;
            esac
        done
    fi
    #
    # <-- end function parse_parameters -->
}


# --- main ---------------------------------------------------------------------


# set default AWS region
#aws_default_region

parse_parameters "$@"

# venv initialization
virtual_environment "$VENV_DIR"

# verify setup of AWS Account to be used
sample_test_user='developer1'
bash $ROOT'/scripts/pretest-setup.sh' $sample_test_user || exit 1

# pre-test setup
cd $CUR_DIR
pretest_setup

# run functional tests, skip if jenkins environ (test run by coverage
functional_tests "$MODULE"

# clean aws account and iam artifacts

if [ $COVERAGE ]; then

    artifact_clean_operation

    # code coverage
    code_coverage $COVERAGE_REPORT_DIR
fi

# mccabe complexity
if [ "$COMPLEXITY" ]; then
    # print header
    print_header "mccabe" "Modules" "Cyclomatic Complexity"
    # set path, required for import
    export PYTHONPATH="."
    $VENV_DIR/bin/py.test -q --mccabe $MODULE_PATH
fi

std_message "${title}$PROJECT${reset} test clean: Begin post-test artifact cleanup" "INFO"
artifact_clean_operation
std_message "End ${title}$PROJECT${reset} Automated testing" "INFO"


# <-- end -->

exit 0
