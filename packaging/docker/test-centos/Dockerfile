##############################################################################
##                                                                          ##
##    RPM Build Dockerfile: CentOS 7 Base image                             ##
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

FROM centos:centos7
MAINTAINER The CentOS Project <cloud-ops@centos.org>

RUN yum -y update; yum clean all
RUN yum -y groups mark convert
RUN yum -y groupinstall "Development Tools"
RUN yum -y install epel-release
RUN yum -y update; yum clean all
RUN yum -y install rpm-build rpmdevtools source-highlight highlight pandoc

RUN yum install -y gcc gcc-c++ \
                   libtool libtool-ltdl \
                   make cmake \
                   git vim figlet \
                   pkgconfig mlocate \
                   sudo wget \
                   automake autoconf \
                   yum-utils  && \
    yum clean all

# user operations
ENV USER1 'builder'
ENV USER2 'dblake'

RUN useradd $USER1 -d /home/$USER1 -u 1000 -m -G users,wheel && \
    echo "# macros"                      >  /home/$USER1/.rpmmacros && \
    echo "%_topdir    /home/$USER/rpmbuild" >> /home/$USER1/.rpmmacros && \
    echo "%_sourcedir %{_topdir}"        >> /home/$USER1/.rpmmacros && \
    echo "%_builddir  %{_topdir}"        >> /home/$USER1/.rpmmacros && \
    echo "%_specdir   %{_topdir}"        >> /home/$USER1/.rpmmacros && \
    echo "%_rpmdir    %{_topdir}"        >> /home/$USER1/.rpmmacros && \
    echo "%_srcrpmdir %{_topdir}"        >> /home/$USER1/.rpmmacros

RUN useradd $USER2 -d /home/$USER2 -u 1001 -m -G users,wheel

# mount volume here to cp completed rpm to on the host
RUN mkdir /mnt/rpm
VOLUME /mnt/rpm

# configure sudoers
RUN sed -i '/Defaults    secure_path/d' /etc/sudoers
RUN echo "$USER1 ALL=(ALL:ALL) NOPASSWD:ALL" >> /etc/sudoers
RUN echo "$USER2 ALL=(ALL:ALL) NOPASSWD:ALL" >> /etc/sudoers

# rpmbuild deps
RUN cd && rpmdev-setuptree
RUN mv ~/rpmbuild /home/$USER1/

# dotfiles, USER1
ADD ./bashrc  /home/$USER1/.bashrc
ADD ./.rpmmacros /home/$USER1/.rpmmacros
ADD ./.gitconfig /home/$USER1/.gitconfig

# configure home for USER1
RUN mkdir -p /home/$USER1/.config/bash
RUN mkdir -p /home/$USER1/git
RUN cd /home/$USER1/git; git clone 'https://github.com/fstab50/xlines.git'
ADD ./colors.sh /home/$USER1/.config/bash/colors.sh
ADD ./motd-centos7.sh /home/$USER1/.config/bash/motd.sh
ADD ./loadavg-flat-layout.sh /home/$USER1/.config/bash/loadavg-flat-layout.sh

# completion actions
RUN chown -R $USER1:$USER1 /home/$USER1

# dotfiles, USER2
ADD ./bashrc  /home/$USER2/.bashrc
ADD ./.gitconfig /home/USER2/.gitconfig

# configure home for USER2
RUN mkdir -p /home/$USER2/.config/bash
ADD ./colors.sh /home/$USER2/.config/bash/colors.sh
ADD ./motd-centos7.sh /home/$USER2/.config/bash/motd.sh
ADD ./loadavg-flat-layout.sh /home/$USER2/.config/bash/loadavg-flat-layout.sh

# completion actions
RUN chown -R $USER2:$USER2 /home/$USER2


# connectivity
EXPOSE 8080


# environment variables
ENV CONTAINER=rpmbuildD OS=centos DIST=el7


# completion update
RUN yum -y update; yum clean all

##

# end rpm build Dockerfile
