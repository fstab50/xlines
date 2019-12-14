##############################################################################
##                                                                          ##
##    Debian Build Dockerfile: Ubuntu 18 Base Image                         ##
##                                                                          ##
##    Purpose:                                                              ##
##       Build container for rpm package assembly                           ##
##                                                                          ##
##    Dependencies:  file list                                              ##
##      - bashrc                          - colors.sh                       ##
##      - motd-centos.sh                                                    ##
##      - docker-buildrpm.sh                                                ##
##                                                                          ##
##    Originally written by:                                                ##
##       "Blake Huber" <blakeca00@@gmail.com>                               ##
##                                                                          ##
##############################################################################

FROM ubuntu:18.10
MAINTAINER Cannonical, Inc.

RUN apt -y update; apt clean all
RUN apt -y install source-highlight highlight pandoc

RUN apt install -y gcc \
                   make cmake \
                   git vim figlet mlocate \
                   sudo wget \
                   automake autoconf

# python3 components required for build
RUN apt -y install python3 python3-pip python3-setuptools python3-dev

# user operations
ENV USER1 'builder'

RUN useradd $USER1 -d /home/$USER1 -u 1000 -m -G users

# mount volume here to cp completed rpm to on the host
RUN mkdir /mnt/deb
VOLUME /mnt/deb

# configure sudoers
RUN sed -i '/Defaults    secure_path/d' /etc/sudoers
RUN echo "$USER1 ALL=(ALL:ALL) NOPASSWD:ALL" >> /etc/sudoers

# dotfiles, USER1
ADD ./bashrc  /home/$USER1/.bashrc
ADD ./.gitconfig /home/$USER1/.gitconfig

# configure home for USER1
RUN mkdir -p /home/$USER1/.config/bash
RUN mkdir -p /home/$USER1/git
RUN cd /home/$USER1/git; git clone 'https://github.com/fstab50/xlines.git'
RUN cd /home/$USER1/git/xlines && git pull && git checkout develop

# bash shell configuration
ADD ./colors.sh /home/$USER1/.config/bash/colors.sh
ADD ./motd-ubuntu18.sh /home/$USER1/.config/bash/motd.sh
ADD ./loadavg-flat-layout.sh /home/$USER1/.config/bash/loadavg-flat-layout.sh

# completion actions
RUN chown -R $USER1:$USER1 /home/$USER1


# connectivity
EXPOSE 8080


# environment variables
ENV CONTAINER=debbuildD OS=ubuntu18 DIST=el7


# completion update
RUN apt -y update; apt clean all

##

# end rpm build Dockerfile
