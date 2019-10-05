##############################################################################
##                                                                          ##
##    RPM Build Dockerfile: Amazon Linux 2 Base image                       ##
##                                                                          ##
##    Purpose:                                                              ##
##       Build container for rpm package assembly                           ##
##                                                                          ##
##    Dependencies:  file list                                              ##
##      - bashrc                          - colors.sh                       ##
##      - .rpmmacros                      - motd-centos.sh                  ##
##      - docker-buildrpm.sh                                                ##
##                                                                          ##
##    Originally written by:                                                ##
##       "Blake Huber" <blakeca00@@gmail.com>                               ##
##                                                                          ##
##############################################################################

FROM amazonlinux:2
MAINTAINER Amazon AWS

RUN yum -y update; yum clean all
RUN yum -y groups mark convert
RUN yum -y groupinstall "Development Tools"

# install epel repository
RUN amazon-linux-extras install epel -y
RUN yum -y install figlet
RUN yum -y update; yum clean all

RUN yum install -y procps wget mlocate \
                   highlight source-highlight \
                   git vim jq bc mlocate initscripts

RUN yum install -y gcc gcc-c++ \
                   libtool libtool-ltdl \
                   make cmake \
                   pkgconfig which util-linux \
                   sudo man-pages \
                   automake autoconf \
                   yum-utils shadow-utils rsync && \
    yum clean all

# rpmbuild tools
RUN yum -y install rpm-build rpmdevtools
RUN yum -y install system-lsb

# user operations
ENV USER1 'builder'

RUN useradd $USER1 -d /home/$USER1 -u 1000 -m -G users,wheel && \
    echo "# macros"                      >  /home/$USER1/.rpmmacros && \
    echo "%_topdir    /home/$USER/rpmbuild" >> /home/$USER1/.rpmmacros && \
    echo "%_sourcedir %{_topdir}"        >> /home/$USER1/.rpmmacros && \
    echo "%_builddir  %{_topdir}"        >> /home/$USER1/.rpmmacros && \
    echo "%_specdir   %{_topdir}"        >> /home/$USER1/.rpmmacros && \
    echo "%_rpmdir    %{_topdir}"        >> /home/$USER1/.rpmmacros && \
    echo "%_srcrpmdir %{_topdir}"        >> /home/$USER1/.rpmmacros


# install python3.7 (requires epel)
RUN yum -y install python3 python3-pip python3-setuptools
RUN pip3 install -U pip setuptools
RUN pip install -U pip setuptools

# mount volume here to cp completed rpm to on the host
RUN mkdir /mnt/rpm
VOLUME /mnt/rpm

# configure sudoers
RUN sed -i '/Defaults    secure_path/d' /etc/sudoers
RUN echo "$USER1 ALL=(ALL:ALL) NOPASSWD:ALL" >> /etc/sudoers

# rpmbuild deps
RUN cd && rpmdev-setuptree
RUN mv ~/rpmbuild /home/$USER1/

# user USER1
ADD ./bashrc  /home/$USER1/.bashrc
ADD ./.rpmmacros /home/$USER1/.rpmmacros
ADD ./.gitconfig /home/$USER1/.gitconfig

# configure home for USER1
RUN mkdir -p /home/$USER1/.config/bash
RUN mkdir -p /home/$USER1/git
RUN cd /home/$USER1/git; git clone 'https://github.com/fstab50/xlines.git'
RUN cd /home/$USER1/git/xlines && git pull && git checkout develop

ADD ./colors.sh /home/$USER1/.config/bash/colors.sh
ADD ./motd-amazonlinux2.sh /home/$USER1/.config/bash/motd.sh
ADD ./loadavg-flat-layout.sh /home/$USER1/.config/bash/loadavg-flat-layout.sh


# completion actions
RUN chown -R $USER1:$USER1 /home/$USER1


# connectivity
EXPOSE 8080


# environment variables
ENV CONTAINER=rpmbuildF OS=amazonlinux2 DIST=amzn2


# completion update
RUN yum -y update; yum clean all

##

# end rpm build Dockerfile
