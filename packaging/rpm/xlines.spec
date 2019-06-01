#
#   RPM spec: xlines, 2019 jun
#
%define name        xlines
%define version     MAJOR_VERSION
%define release     MINOR_VERSION
%define _bindir     usr/local/bin
%define _libdir     usr/local/lib/python3.*/site-packages
%define _compdir    etc/bash_completion.d
%define _topdir     /home/DOCKERUSER/rpmbuild
%define buildroot   %{_topdir}/%{name}-%{version}

BuildRoot:      %{buildroot}
Name:           %{name}
Version:        %{version}
Release:        %{release}
Summary:        Easily count lines of code

Group:          Development/Tools
BuildArch:      noarch
License:        GPL
URL:            PROJECT_URL
Source:         %{name}-%{version}.%{release}.tar.gz
Prefix:         /usr
Requires:      DEPLIST

%if 0%{?rhel}%{?amzn2}
Requires: bash-completion
%endif

%if 0%{?amzn1}
Requires: epel-release
%endif


%description
branchdiff is a utility for use with git version control. branchdiff
provides user access to advanced  git features without requiring any
knowledge of advanced git syntax.
.
branch diff features:
  * Illustration of differences between current working branch and master branch
  * Details when commits were made to the current branch, by whom
  * Summary statistics for all commits
  * Advanced file difference illustration between branches

%prep

%setup -q

%build


%install
install -m 0755 -d $RPM_BUILD_ROOT/%{_bindir}
install -m 0755 -d $RPM_BUILD_ROOT/%{_libdir}
install -m 0755 -d $RPM_BUILD_ROOT/%{_compdir}
install -m 0755 xlines $RPM_BUILD_ROOT/%{_bindir}/
install -m 0644 xlines $RPM_BUILD_ROOT/%{_libdir}/xlines
install -m 0644 version.py $RPM_BUILD_ROOT/%{_libdir}/version.py
install -m 0644 branchdiff-completion.bash $RPM_BUILD_ROOT/%{_compdir}/xlines-completion.bash


%files
 %defattr(-,root,root)
/%{_libdir}
/%{_bindir}
/%{_compdir}


%post
#!/usr/bin/env bash

BIN_PATH=/usr/local/bin

# path updates - root user
if [ -f "$HOME/.bashrc" ]; then
    printf -- '%s\n\n' 'PATH=$PATH:/usr/local/bin' >> "$HOME/.bashrc"
    printf -- '%s\n' 'export PATH' >> "$HOME/.bashrc"

elif [ -f "$HOME/.bash_profile" ]; then
    printf -- '%s\n\n' 'PATH=$PATH:/usr/local/bin' >> "$HOME/.bash_profile"
    printf -- '%s\n' 'export PATH' >> "$HOME/.bash_profile"

elif [ -f "$HOME/.profile" ]; then
    printf -- '%s\n\n' 'PATH=$PATH:/usr/local/bin' >> "$HOME/.profile"
    printf -- '%s\n' 'export PATH' >> "$HOME/.profile"

fi


# path updates - sudo user
if [ $SUDO_USER ]; then

    if [ -f "/home/$SUDO_USER/.bashrc" ]; then
        printf -- '%s\n\n' 'PATH=$PATH:/usr/local/bin' >> "/home/$SUDO_USER/.bashrc"
        printf -- '%s\n' 'export PATH' >> "/home/$SUDO_USER/.bashrc"

    elif [ -f "/home/$SUDO_USER/.bash_profile" ]; then
        printf -- '%s\n\n' 'PATH=$PATH:/usr/local/bin' >> "/home/$SUDO_USER/.bash_profile"
        printf -- '%s\n' 'export PATH' >> "/home/$SUDO_USER/.bash_profile"

    elif [ -f "/home/$SUDO_USER/.profile" ]; then
        printf -- '%s\n\n' 'PATH=$PATH:/usr/local/bin' >> "/home/$SUDO_USER/.profile"
        printf -- '%s\n' 'export PATH' >> "/home/$SUDO_USER/.profile"
    fi

fi


##   install bash_completion (amazonlinux 1 only); other epel pkgs   ##

if [ -f '/usr/local/lib/branchdiff/os_distro.sh' ]; then
    if [ "$(sh /usr/local/lib/branchdiff/os_distro.sh | awk '{print $2}')" -eq "1" ]; then
        yum -y install bash-completion xclip  --enablerepo=epel
    fi
else
    yum -y install xclip --enablerepo=epel
fi


##   end post install   ##
exit 0
