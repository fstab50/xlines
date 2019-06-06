#!/usr/bin/env bash

#
#   Manual creation of container assets for testing
#

container='AML2test'


function _git_root(){
    ##
    ##  determines full path to current git project root
    ##
    echo "$(git rev-parse --show-toplevel 2>/dev/null)"
}


function container_started(){
    ##
    ##  check container status
    ##
    if [[ $(docker ps | grep $container) ]]; then
        return 0
    else
        return 1
    fi
}


pkg_path=$(cd "$(dirname $0)"; pwd -P)
source "$_git_root/scripts/std_functions.sh"


# working directory
cd amazonlinux2 || false

# create image
std_message "Begin image build" "INFO"
docker build -t amazonlinux:rpmbuildA .

# create container
std_message "Creating and running container -- START" "INFO"
docker run --name=$container -d -v /tmp/rpm:/mnt/rpm -ti amazonlinux:rpmbuildA tail -f /dev/null &

if container_started; then
    std_message "Container ${container} started successfully" "OK"
else
    std_message "Container ${container} failed to start" "FAIL"
fi

cd $pkg_path || true
exit 0
