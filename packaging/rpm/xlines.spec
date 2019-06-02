#
#   RPM spec: xlines, 2019 jun
#
%define name        xlines
%define version     MAJOR_VERSION
%define release     MINOR_VERSION
%define _homedir    %{echo $HOME}
%define _bindir     usr/local/bin
%define _libdir     usr/local/lib/python3.6/site-packages
%define _compdir    etc/bash_completion.d
%define _confdir    %{_homedir}/.config/xlines
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
xlines is a utility for counting lines of text in code projects. xlines
attempts to skip binary files or other file types which are not text.
.
xlines features:
  * Exclusion list of excluded file type extensions
  * Directory list of filesystem directories to exclude
  * User settable threshold for marking files with large line counts
  * Colorized output

%prep

%setup -q

%build


%install
install -m 0755 -d $RPM_BUILD_ROOT/%{_bindir}
install -m 0755 -d $RPM_BUILD_ROOT/%{_libdir}
install -m 0755 -d $RPM_BUILD_ROOT/%{_compdir}
install -m 0755 -d $RPM_BUILD_ROOT/%{_confdir}
install -m 0755 xlines $RPM_BUILD_ROOT/%{_bindir}/
install -m 0644 xlines $RPM_BUILD_ROOT/%{_libdir}/xlines
install -m 0644 version.py $RPM_BUILD_ROOT/%{_libdir}/version.py
install -m 0644 xlines-completion.bash $RPM_BUILD_ROOT/%{_compdir}/xlines-completion.bash


%files
 %defattr(-,root,root)
/%{_libdir}
/%{_bindir}
/%{_compdir}
/%{_confdir}


%post -p /bin/bash

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


##   install bash_completion (amazonlinux 1 only); other epel pkgs   ##

if [ -f '/usr/local/lib/xlines/os_distro.sh' ]; then
    if [ "$(sh /usr/local/lib/xlines/os_distro.sh | awk '{print $2}')" -eq "1" ]; then
        yum -y install bash-completion xclip  --enablerepo=epel
    fi
else
    yum -y install xclip --enablerepo=epel
fi


##   end post install   ##
exit 0
