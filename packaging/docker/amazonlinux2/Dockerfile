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

RUN yum install -y procps wget \
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

# user operations
ENV USER='dblake'
RUN useradd $USER -d /home/$USER -u 1000 -m -G users,wheel && \
    echo "# macros"                      >  /home/$USER/.rpmmacros && \
    echo "%_topdir    /home/$USER/rpmbuild" >> /home/$USER/.rpmmacros && \
    echo "%_sourcedir %{_topdir}"        >> /home/$USER/.rpmmacros && \
    echo "%_builddir  %{_topdir}"        >> /home/$USER/.rpmmacros && \
    echo "%_specdir   %{_topdir}"        >> /home/$USER/.rpmmacros && \
    echo "%_rpmdir    %{_topdir}"        >> /home/$USER/.rpmmacros && \
    echo "%_srcrpmdir %{_topdir}"        >> /home/$USER/.rpmmacros

RUN useradd dblake -d /home/dblake -u 1001 -m -G users,wheel

# epel repository
RUN amazon-linux-extras install epel -y
RUN yum -y install figlet
RUN yum -y update; yum clean all

# install python3.7 (requires epel)
RUN yum -y install python3 python3-pip python3-setuptools
RUN pip3 install -U pip setuptools

# mount volume here to cp completed rpm to on the host
RUN mkdir /mnt/rpm
VOLUME /mnt/rpm

# configure sudoers
RUN sed -i '/Defaults    secure_path/d' /etc/sudoers
RUN echo "$USER ALL=(ALL:ALL) NOPASSWD:ALL" >> /etc/sudoers
RUN echo "dblake ALL=(ALL:ALL) NOPASSWD:ALL" >> /etc/sudoers

# rpmbuild deps
RUN cd && rpmdev-setuptree
RUN mv ~/rpmbuild /home/$USER/

ADD ./bashrc  /home/$USER/.bashrc
ADD ./.rpmmacros /home/$USER/
ADD ./docker-buildrpm.sh /home/$USER/

# configure home for $USER
RUN mkdir -p /home/$USER/.config/bash
ADD ./colors.sh /home/$USER/.config/bash/
ADD ./motd-amazonlinux2.sh /home/$USER/.config/bash/motd.sh
ADD ./loadavg-flat-layout.sh /home/$USER/.config/bash/loadavg-flat-layout.sh

# completion actions
RUN chown -R $USER /home/$USER

# connectivity
EXPOSE 8080
USER $USER

# environment variables
ENV CONTAINER=rpmbuild OS=amazonlinux DIST=amzn2

##

# end rpm build Dockerfile
