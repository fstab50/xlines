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
RUN yum -y install rpm-build rpmdevtools source-highlight highlight

RUN yum install -y gcc gcc-c++ \
                   libtool libtool-ltdl \
                   make cmake \
                   git vim figlet \
                   pkgconfig \
                   sudo \
                   automake autoconf \
                   yum-utils  && \
    yum clean all

# user operations
ENV USER='builder'

RUN useradd $USER -d /home/$USER -u 1000 -m -G users,wheel && \
    echo "# macros"                      >  /home/$USER/.rpmmacros && \
    echo "%_topdir    /home/$USER/rpmbuild" >> /home/$USER/.rpmmacros && \
    echo "%_sourcedir %{_topdir}"        >> /home/$USER/.rpmmacros && \
    echo "%_builddir  %{_topdir}"        >> /home/$USER/.rpmmacros && \
    echo "%_specdir   %{_topdir}"        >> /home/$USER/.rpmmacros && \
    echo "%_rpmdir    %{_topdir}"        >> /home/$USER/.rpmmacros && \
    echo "%_srcrpmdir %{_topdir}"        >> /home/$USER/.rpmmacros

RUN useradd dblake -d /home/dblake -u 1001 -m -G users,wheel

# mount volume here to cp completed rpm to on the host
RUN mkdir /mnt/rpm
VOLUME /mnt/rpm

# configure sudoers
RUN sed -i '/secure_path\ =/d' /etc/sudoers
RUN echo "$USER ALL=(ALL:ALL) NOPASSWD:ALL" >> /etc/sudoers
RUN echo "dblake ALL=(ALL:ALL) NOPASSWD:ALL" >> /etc/sudoers

# rpmbuild deps
RUN cd && rpmdev-setuptree
RUN mv ~/rpmbuild /home/$USER/

# user $USER
ADD ./bashrc  /home/$USER/.bashrc
ADD ./.rpmmacros /home/$USER/
ADD ./.gitconfig /home/$USER/

# user dblake
ADD ./bashrc  /home/dblake/.bashrc
ADD ./.gitconfig /home/dblake/


EXPOSE 8080

# configure home for $USER
RUN mkdir -p /home/$USER/.config/bash
ADD ./colors.sh /home/$USER/.config/bash/
ADD ./motd-centos.sh /home/$USER/.config/bash/motd.sh

RUN chown -R $USER:$USER /home/$USER

# configure home for dblake
RUN mkdir -p /home/dblake/.config/bash
ADD ./colors.sh /home/dblake/.config/bash/
ADD ./motd-centos.sh /home/dblake/.config/bash/motd.sh

RUN chown -R dblake:dblake /home/dblake

# environment variables
ENV CONTAINER=rpmbuild OS=centos DIST=el7

##

# end rpm build Dockerfile
