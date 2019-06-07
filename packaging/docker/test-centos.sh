#!/usr/bin/env bash

#
#   Manual creation of container assets for testing
#

container='xlinesCentOS'
image='centos7:rpmbuildD'


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
source "$(_git_root)/scripts/std_functions.sh"
source "$(_git_root)/scripts/colors.sh"


# working directory
cd "$(_git_root)/packaging/docker/centos7" || false

# create image
std_message "Begin image build" "INFO"
docker build  -t  $image .

# create container
std_message "Creating and running container -- START" "INFO"
docker run  --name=$container  -d -v /tmp/rpm:/mnt/rpm  -ti  $image  tail -f /dev/null &

if container_started; then
    std_message "Container ${container} started successfully" "OK"
else
    std_message "Container ${container} failed to start" "FAIL"
fi

cd $pkg_path || true
exit 0
