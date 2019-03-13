#
#   Autoimated Test Setup Script -- Configures an AWS Account & local awscli
#
#       PROJECT:     Project for which we are conducting automated test cases
#
#       test_user0:  supplied as $1 parameter to this script.  User, which if
#                    present in the local awscli configuration, indicates that
#                    automated testing setup of the AWS account has previously
#                    been completed.
#
#       ROOT:       git repository root of the project
#       pkg:        script name reported in logs will be the basename of the caller
#

PROJECT='keyup'
pkg=$(basename $0)                                      # pkg (script) full name
pkg_root="$(echo $pkg | awk -F '.' '{print $1}')"       # pkg without file extention
pkg_path=$(cd $(dirname $0); pwd -P)                    # location of pkg
host=$(hostname)
system=$(uname)
ROOT=$(git rev-parse --show-toplevel 2>/dev/null)
test_user0="$1"
tests_dir=$ROOT'/tests'
test_assets=$ROOT'/tests/assets'
test_credential_file="$test_assets/test-user-credentials.ini"
log_dir="$HOME/logs"
log_file="$log_dir/keyup-testsetup.log"
PROFILE='gcreds-da-atos'
VERSION='1.0'

# test users
declare -a USERS
USERS=(
    "developer1"
    "developer2"
    "developer3"
)

# required test modules
REQUIREMENTS=$ROOT'/tests/requirements.txt'
declare -a TEST_PKGS=$(cat $REQUIREMENTS)


# formatting
source $pkg_path/colors.sh
frame=$(echo -e ${brightblue})
bg=$(echo -e ${brightgreen})

# error codes
E_OK=0                        # exit code if normal exit conditions
E_DEPENDENCY=1                # exit code if missing required ec2cli dependency
E_NOLOG=2                     # exit code if failure to create log dir, log file
E_BADSHELL=3                  # exit code if incorrect shell detected
E_AUTH=4                      # exit code if authentication fails to aws
E_USER_CANCEL=7               # exit code if user cancel
E_BADARG=8                    # exit code if bad input parameter
E_NETWORK_ACCESS=9            # exit code if no network access from current location
E_MISC=11                     # exit code if miscellaneous (unspecified) error


# --- declarations  ------------------------------------------------------------


function add_awscli_user(){
    ## add new user to local awscli configuration ##
    local user="$1"
    #
    # remove any active temporary credentials (gcreds)
    gcreds_check
    # awscli credentials file
    echo -e "\n[$user]" >> $DEFAULT_CREDENTIALS
    echo -e "aws_access_key_id = AKIAXXXXXXXXXXXXXXXX" >> $DEFAULT_CREDENTIALS
    echo -e "aws_secret_access_key = e08xspFP+o/1wBCkaaaaaaaaaaaaaaaaaaaaaaaa" >> $DEFAULT_CREDENTIALS
    # awscli config file
    echo -e "\n[profile $user]" >> $DEFAULT_CONFIG
    echo -e "region = $AWS_DEFAULT_REGION" >> $DEFAULT_CONFIG
    echo -e "output = json" >> $DEFAULT_CONFIG
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
        exit $E_DEPENDENCY
    else
        std_message "AWS_DEFAULT_REGION set:\t${title}$AWS_REGION${bodytext}" "INFO" $log_file
    fi
}

function authenticated(){
    ## validates authentication using iam user or role ##
    local profilename="$1"
    local response
    #
    response=$(aws sts get-caller-identity --profile $profilename 2>&1)
    if [ "$(echo $response | grep Invalid)" ]; then
        std_message "The IAM profile provided ($profilename) failed to authenticate to AWS. Exit (Code $E_AUTH)" "AUTH"
        return 1
    elif [ "$(echo $response | grep found)" ]; then
        std_message "The IAM user or role ($profilename) cannot be found in your local awscli config. Exit (Code $E_BADARG)" "AUTH"
        return 1
    elif [ "$(echo $response | grep Expired)" ]; then
        std_message "The sts temporary credentials for the role provided ($profilename) have expired. Exit (Code $E_AUTH)" "INFO"
        return 1
    else
        return 0
    fi
}

function log_file_check(){
    ## creates log_file in correct place if not exist ##
    if [ ! -f $log_file ]; then
        touch $log_file
    fi
    return 0
}

function gcreds_check(){
    ## executed if gcreds in use on the machine ##
    local token_file=$HOME'/.gcreds/token.expiration'
    GCREDS="$(which gcreds)"
    if [ $GCREDS ] && [ -f $token_file ]; then
        if [ "$(($(date +%s) - $(cat $token_file) ))" -lt 0 ]; then
            std_message "ACTIVE Temporary Credentials found in awscli config - Clearing Config." "INFO" $log_file
            mv $HOME'/.aws/credentials.orig' $HOME'/.aws/credentials'
        fi
    fi
    return 0
}

function depcheck(){
    ## validate cis report dependencies ##
    local msg
    #
    ## test default shell ##
    if [ ! -n "$BASH" ]; then
        # shell other than bash
        msg="Default shell appears to be something other than bash. Please rerun with bash. Aborting (code $E_BADSHELL)"
        std_error_exit "$msg" $E_BADSHELL
    fi

    ## create log dir for gcreds ##
    if [[ ! -d "$log_dir" ]]; then
        if ! mkdir -p "$log_dir"; then
            std_error_exit "$pkg: failed to make log directory: $log_dir" $E_DIR
        else
            log_file_check
        fi
    else
        log_file_check
    fi

    ## check if awscli tools are configured ##
    if [[ ! -f $HOME/.aws/config ]]; then
        std_error_exit "awscli not configured, run 'aws configure'. Aborting (code $E_DEPENDENCY)" $E_DEPENDENCY
    fi

    ## check for required cli tools ##
    binary_depcheck awk grep aws keyup jq python3

    ## check python version ##
    python_version_depcheck "3.0" "3.6"

    # check aws python sdk available - SKIP, functionality in make-test.sh
    #python_module_depcheck TEST_PKGS[@]

    #
    # <<-- end function depcheck -->>
}

function binary_depcheck(){
    ## validate binary dependencies installed
    local check_list=( "$@" )
    local msg
    #
    for prog in "${check_list[@]}"; do
        if ! type "$prog" > /dev/null 2>&1; then
            msg="$prog is required and not found in the PATH. Aborting (code $E_DEPENDENCY)"
            std_error_exit "$msg" $E_DEPENDENCY
        else
            std_message "Binary ${yellow}$prog${bodytext}:\t\t${bg}installed${reset}" "INFO" $log_file "nospaces"
        fi
    done
    #
    # <<-- end function binary_depcheck -->>
}

function python_version_depcheck(){
    ## dependency check for a specific version of python binary ##
    local version
    local version_min="$1"
    local version_max="$2"
    local msg
    #
    py_bin=$(which python3)
    # determine binary version
    version=$($py_bin 2>&1 --version | awk '{print $2}' | cut -c 1-3)
    full_ver=$($py_bin 2>&1 --version | awk '{print $2}')
    #
    if (( $(echo "$version > $version_max" | bc -l) )) || \
       (( $(echo "$version < $version_min" | bc -l) ))
    then
        msg="python version $version detected - must be > $version_min, but < $version_max"
        std_error_exit "$msg" $E_DEPENDENCY
    else
        std_message "Python version detected:\t${title}$full_ver${bodytext}" "INFO" $log_file
    fi
    #
    # <<-- end function python_depcheck -->>
}

function python_module_depcheck(){
    ## validate python library dependencies
    declare -a check_list=("${!1}")
    local msg
    #
    for module in "${check_list[@]}"; do
        exitcode=$(python3 -c "import $module" > /dev/null 2>&1; echo $?)
        if [[ $exitcode == "1" ]]; then
            # module not imported, not found
            msg="$module is a required python library. Aborting (code $E_DEPENDENCY)"
            std_error_exit "$msg" $E_DEPENDENCY
        else
            std_message "Module ${yellow}$module${bodytext}:\tinstalled" "INFO" $log_file "nospaces"
        fi
    done
    #
    # <<-- end function python_module_depcheck -->>
}

function std_error(){
    local msg="$1"
    std_logger "$msg" "ERROR"
    echo -e "\n${yellow}[ ${red}ERROR${yellow} ]$reset  $msg\n" | indent04
}

function std_error_exit(){
    local msg="$1"
    local status="$2"
    std_warn "$msg"
    exit $status
}

function std_warn(){
    local msg="$1"
    std_logger "$msg" "WARN" $log_file
    if [ "$3" ]; then
        # there is a second line of the msg, to be printed by the caller
        echo -e "\n${yellow}[ ${red}WARN${yellow} ]$reset  $msg" | indent04
    else
        # msg is only 1 line sent by the caller
        echo -e "\n${yellow}[ ${red}WARN${yellow} ]$reset  $msg\n" | indent04
    fi
}

function std_logger(){
    local msg="$1"
    local prefix="$2"
    local log_file="$3"
    #
    if [ ! $prefix ]; then
        prefix="INFO"
    fi
    if [ ! -f $log_file ]; then
        # create new log file
        touch $log_file
        if [ ! -f $log_file ]; then
            echo "[$prefix]: $pkg ($VERSION): failure to call std_logger, $log_file location not writeable"
            exit $E_DIR
        fi
    else
        echo "$(date +'%Y-%m-%d %T') $host - $pkg - $VERSION - [$prefix]: $msg" >> "$log_file"
    fi
}

function std_message(){
    #
    # Caller formats:
    #
    #   Logging to File | std_message "xyz message" "INFO" "/pathto/log_file"
    #
    #   No Logging  | std_message "xyz message" "INFO"
    #
    local msg="$1"
    local prefix="$2"
    local log_file="$3"
    local format="$4"
    #
    if [ $log_file ]; then
        std_logger "$msg" "$prefix" $log_file
    fi
    [[ $QUIET ]] && return
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

function set_awscli_defaults(){
    ## sets location of default awscli credentials
    if [ $AWS_SHARED_CREDENTIALS_FILE ]; then
        DEFAULT_CREDENTIALS=$AWS_SHARED_CREDENTIALS_FILE
        return 0
    elif [ $AWS_CONFIG_FILE ]; then
        DEFAULT_CREDENTIALS=$AWS_CONFIG_FILE
        DEFAULT_CONFIG=$AWS_CONFIG_FILE
        return 0
    elif [ -f $HOME'/.aws/credentials' ]; then
        DEFAULT_CREDENTIALS=$HOME'/.aws/credentials'
        DEFAULT_CONFIG=$HOME'/.aws/config'
        return 0
    else
        return 1
    fi
}

function presetup_check(){
    ## presetup verification ##
    local user="$1"
    #
    if [ "$(aws configure get profile.$user.aws_access_key_id)" ] && authenticated $user; then
        std_message "Presetup Check:  Automated Test setup complete" "INFO" $log_file
        exit $E_OK
    else
        std_error_exit "Presetup Check:  Fail. IAM User ($user) not found in local awscli config" $E_DEPENDENCY
    fi
}

function update_credentials(){
    ## refreshes credentials in local awscli configuration ##
    local user="$1"
    #
    keyup --profile $PROFILE --user-name $user --operation up
    std_message "Completed credential update for user $user" "INFO" $log_file
}

function update_credentials_bulk(){
    ## refreshes credentials in local awscli configuration ##
    declare -a users=("${!1}")
    #
    for user in ${users[@]}; do
        keyup --profile $PROFILE --user-name $user --operation up
        std_message "Completed credential update for user $user" "INFO" $log_file
    done
}


# --- main ---------------------------------------------------------------------


# verify if automated test setup already completed or not
if [ $test_user0 ]; then
    presetup_check $test_user0
fi

std_message "${title}keyup${bodytext} Automated Testing Setup Check -- Start" "INFO"  $log_file

# check dependencies
aws_default_region
depcheck

# set location of local awscli credentials
if set_awscli_defaults; then
    std_message "Found local awscli credentials file: ${yellow}$DEFAULT_CREDENTIALS${bodytext}" "INFO" $log_file
else
    std_error_exit "Failed to determine location of local awscli credentials. Exit" $E_DEPENDENCY
fi

test_user1=${USERS[0]}
key=$(aws configure get profile.$test_user1.aws_access_key_id)

if [ $key ]; then
    for user in ${USERS[@]}; do
        if authenticated $user; then
            std_message "User ${title}$user${bodytext} auth:\t${bg}verified${reset}" "INFO" $log_file "nospaces"
        else
            std_message "Test user account ($user) exists, but fails to authenticate. Refreshing credentials" "WARN" $log_file
            update_credentials $user
        fi
    done
    std_message "Automated Test Setup Check Complete." "INFO" $log_file
    exit $E_OK
else
    # users not exist in aws account, nor local awscli configuration
    current_users=$(aws iam list-users --profile $PROFILE | jq -r .Users[].UserName)

    # create users
    for user in ${USERS[@]}; do
        if [ ! "$(echo ${current_users[@]} | grep $user)" ]; then
            aws iam create-user --user-name $user --path "/" --profile $PROFILE
            add_awscli_user $user
            update_credentials $user
        fi
    done

    # add users and access keys to local awscli configuration
    for user in ${USERS[@]}; do
        if [ "$(aws configure get profile.$user.aws_access_key_id)" ]; then
            if ! authenticated $user; then
                update_credentials $user
            else
                std_message "Test user $user setup has valid configuration in local awscli" "INFO"
            fi
        else
            add_awscli_user $user
            update_credentials $user
        fi
    done

    # create credentials for all test users
    update_credentials_bulk USERS[@]

    # create policies

    # assign policies
fi

# --- end ----------------------------------------------------------------------

exit $E_OK
