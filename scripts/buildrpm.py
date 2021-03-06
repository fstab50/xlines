#!/usr/bin/env python3
"""
Summary:
    buildrpm (python3):  xlines binary operating system package (.rpm, Redhat, Redhat-based systems)

        - Automatic determination of version to be built
        - Build version can optionally be forced to a specific version
        - Resulting rpm ackage produced in packaging/rpm directory
        - To execute build, from the directory of this module, run:

    .. code-block:: python

        $ cd ../<project dir>
        $ make buildrpm

Author:
    Blake Huber
    Copyright 2017-2018, All Rights Reserved.

License:
    General Public License v3
    Additional terms may be found in the complete license agreement:
    https://bitbucket.org/blakeca00/xlinesthon3/src/master/LICENSE.md

OS Support:
    - Redhat, CentOS, Fedora, Redhat-based variants

Dependencies:
    - Requires python3, developed and tested under python3.6
"""
import argparse
import inspect
import json
import os
import sys
import subprocess
import tarfile
import fileinput
from shutil import copy2 as copyfile
from shutil import rmtree, which
import distro
import docker
import loggers
from libtools import stdout_message
from libtools.js import export_iterobject
from libtools.colors import Colors
from common import debug_header

try:
    from libtools.oscodes_unix import exit_codes
except Exception:
    from libtools.oscodes_win import exit_codes    # non-specific os-safe codes


# globals
PROJECT = 'xlines'
module = os.path.basename(__file__)
TMPDIR = '/tmp/build'
VOLMNT = '/tmp/rpm'
CONTAINER_VOLMNT = '/mnt/rpm'
DISTRO_LIST = ['centos7', 'amazonlinux2', 'redhat7']

# docker
dclient = docker.from_env()

# formatting
act = Colors.ORANGE                     # accent highlight (bright orange)
bd = Colors.BOLD + Colors.WHITE         # title formatting
bn = Colors.CYAN                        # color for main binary highlighting
lk = Colors.DARK_BLUE                   # color for filesystem path confirmations
red = Colors.RED                        # color for failed operations
yl = Colors.GOLD3                       # color when copying, creating paths
rst = Colors.RESET                      # reset all color, formatting


# global logger
logger = loggers.getLogger('1.0')


def git_root():
    """
    Summary.

        Returns root directory of git repository

    """
    cmd = 'git rev-parse --show-toplevel 2>/dev/null'
    return subprocess.getoutput(cmd).strip()


def help_menu():
    """
    Summary.

        Command line parameter options (Help Menu)

    """
    menu = '''
                          ''' + bd + module + rst + ''' help contents

  ''' + bd + '''DESCRIPTION''' + rst + '''

          Builds an installable package (.rpm) for Redhat, CentOS, and Fedora
          variants of the Linux Operatining System

  ''' + bd + '''OPTIONS''' + rst + '''

            $ python3  ''' + act + module + rst + '''  --build  [ --force-version <VERSION> ]

                         -b, --build
                         -d, --distro  <value>
                        [-c, --container  ]
                        [-D, --debug  ]
                        [-f, --force  ]
                        [-h, --help   ]
                        [-p, --parameter-file  <value> ]
                        [-s, --set-version  <value> ]

        ''' + bd + '''-b''' + rst + ''', ''' + bd + '''--build''' + rst + ''':  Build Operating System package ( *.rpm, Redhat systems )
            When given without the --set-version parameter switch, build ver-
            sion is extracted from the project repository information

        ''' + bd + '''-c''' + rst + ''', ''' + bd + '''--container''' + rst + ''':  Leave container running after rpm build; do not halt
            or remove.

        ''' + bd + '''-d''' + rst + ''', ''' + bd + '''--debug''' + rst + ''': Debug mode, verbose output.

        ''' + bd + '''-d''' + rst + ''', ''' + bd + '''--distro''' + rst + '''  <value>:  Specifies the Docker Operating System Image to
            use when building.  Allowable Values:

                    -   centos7 (DEFAULT)
                    -   amazonlinux2
                    -   redhat7

        ''' + bd + '''-F''' + rst + ''', ''' + bd + '''--force''' + rst + ''':  When given, overwrites any pre-existing build artifacts.
            DEFAULT: False

        ''' + bd + '''-h''' + rst + ''', ''' + bd + '''--help''' + rst + ''': Print this help menu

        ''' + bd + '''-p''' + rst + ''', ''' + bd + '''--parameter-file''' + rst + ''' <value>: Optional json format configuration file
            containing all configuration parameters to build rpm package (key,
            value format)

        ''' + bd + '''-s''' + rst + ''', ''' + bd + '''--set-version''' + rst + ''' (string): When given, overrides all version infor-
            mation contained in the project to build the exact version speci-
            fied by VERSION parameter


    '''
    print(menu)
    return True


def clean(directory, debug):
    """
    Summary.

        rm residual installation files from build directory

    """
    bytecode_list = list(
                        filter(
                            lambda x: x.endswith('.pyc') or x.endswith('.pyo'), os.listdir(directory)
                        )
                    )
    if debug:
        stdout_message(
                message=f'bytecode_list contents: {bytecode_list}',
                prefix='DEBUG'
            )
    for artifact in bytecode_list:
        os.remove(directory + '/' + artifact)
        logger.info('Artifact {} cleaned from {}'.format(artifact, directory))
    return True


def current_branch(path):
    """
    Returns:
        git repository source url, TYPE: str
    """
    cmd = 'git branch'
    pwd = os.getcwd()
    os.chdir(path)

    try:
        if '.git' in os.listdir('.'):

            branch = subprocess.getoutput('git branch').split('*')[1].split('\n')[0][1:]

        else:
            ex = Exception(
                '%s: Unable to identify current branch - path not a git repository: %s' %
                (inspect.stack()[0][3], path))
            raise ex

        os.chdir(pwd)      # return cursor

    except IndexError:
        logger.exception(
                '%s: problem retrieving git branch for %s' %
                (inspect.stack()[0][3], path)
            )
        return ''
    return branch


def read(fname):
    basedir = os.path.dirname(sys.argv[0])
    return open(os.path.join(basedir, fname)).read()


def pypi_version(modulename):
    """
    Returns version denoted in the master branch of the repository
    """
    command = 'pip3 search {} | grep -i latest'.format(modulename)

    try:

        # query pypi global python lib database
        version = subprocess.getoutput(command).split(':')[1]

    except Exception:
        return None
    return version.strip()


def current_version(binary, version_modpath):
    """
    Summary.

        Returns current binary package version if locally
        installed, master branch __version__ if the binary
        being built is not installed locally

    Args:
        :root (str): path to the project root directory
        :binary (str): Name of main project exectuable

    Returns:
        current version number of the project, TYPE: str

    """
    try:

        return greater_version(pypi_version(binary), __version__)

    except Exception:
        logger.info(
            '%s: Build binary %s not installed, comparing current branch version to master branch version' %
            (inspect.stack()[0][3], binary))


def greater_version(versionA, versionB):
    """
    Summary:
        Compares to version strings with multiple digits and returns greater
    Returns:
        greater, TYPE: str
    """
    try:

        list_a = versionA.split('.')
        list_b = versionB.split('.')

    except AttributeError:
        return versionA or versionB    # either A or B is None

    try:

        for index, digit in enumerate(list_a):
            if int(digit) > int(list_b[index]):
                return versionA
            elif int(digit) < int(list_b[index]):
                return versionB
            elif int(digit) == int(list_b[index]):
                continue

    except ValueError:
        return versionA or versionB    # either A or B is ''
    return versionA


def increment_version(current):
    """
    Returns current version incremented by 1 minor version number
    """
    minor = current.split('.')[-1]
    major = '.'.join(current.split('.')[:-1])
    inc_minor = int(minor) + 1
    return major + '.' + str(inc_minor)


def container_running(cid, debug=False):
    """
    Summary:
        Verifies if a container is activly running
    Args:
        :cid (str): Container name or hex identifier
        :dclient (object): global docker client
    Returns:
        True (running) | False (stopped)
        TYPE: bool
    """

    success_msg = f'Container {cid} running'

    try:
        container = dclient.containers.get(cid)

        if container.status == 'running':
            if debug:
                stdout_message(success_msg, prefix='OK')
            return True
    except Exception:
        if cid in subprocess.getoutput('docker ps'):
            stdout_message(success_msg, prefix='OK')
            return True
        else:
            stdout_message(f'Container {cid} stopped', prefix='WARN')
    return False


def display_package_contents(rpm_path, contents):
    """
    Summary:
        Output newly built package contents.
    Args:
        :build_root (str):  location of newly built rpm package
        :version (str):  current version string, format:  '{major}.{minor}.{patch num}'
    Returns:
        Success | Failure, TYPE: bool
    """
    tab = '\t'.expandtabs(2)
    tab4 = '\t'.expandtabs(4)
    width = 120
    package = os.path.split(rpm_path)[1]
    path, discard = os.path.split(contents)
    pwd = os.getcwd()
    os.chdir('.') if not path else os.chdir(path)

    with open(contents) as f1:
        unformatted = f1.readlines()

    # title header and subheader
    header = '\n\t\tPackage Contents:  ' + bd + package + rst + '\n'
    print(header)
    subheader = tab + 'Permission' + tab + ' Owner/Group' + '\t' + 'ctime' \
        + '\t'.expandtabs(8) + 'File'
    print(subheader)

    # divider line
    print('  ', end='')
    list(filter(lambda x: print('-', end=''), range(0, width + 1))), print('\r')

    # content
    for line in unformatted:
        permissions = [tab + line.split()[0]]
        raw = tab4 + 'root root'
        ctime = line.split()[5:8]
        f_ctime = tab4 + ''.join([x + ' ' for x in ctime])
        content_path = tab4 + yl + line.split()[-1] + rst
        fline = permissions[0] + raw + f_ctime + content_path
        print(fline)
    print('\n')
    os.chdir(pwd)
    return True


def docker_daemon_up():
    """
    Summary:
        Determines if docker installed and running by
        evaluating the exit code of docker images cmd
    Returns:
        True (running) | False, TYPE: bool
    """
    cmd = 'docker images >/dev/null 2>&1; echo $?'
    if which('docker') and int(subprocess.getoutput(cmd)) == 0:
        return True
    else:
        stdout_message('Docker engine not running or not accessible', prefix='WARN')
    return False


def docker_configure_container(c_object, root_dir, buildscript, version):
    """
    Execute build commands internal to configure container,
    then execute rpm package build for a specific os type
    """
    def command_exec(index):
        return {
            0: f"docker exec -i {c_object.name} sh -c \'cd {root_dir} && git checkout develop\'",
            1: f"docker exec -i {c_object.name} sh -c \'sleep 1\'",
            2: f"docker exec -i {c_object.name} sh -c \'cd {root_dir} && git pull\'",
            3: f"docker exec -i {c_object.name} sh -c \'sleep 2\'",
            4: f"docker exec -i {c_object.name} sh -c \'cd {root_dir} && sh scripts/{buildscript} -s {version}\'"
        }.get(index, 0)

    for index in range(5):
        print(subprocess.getoutput(command_exec(index)))
    return True


def docker_init(src, builddir, _version, osimage, param_dict, debug):
    """
    Summary:
        Creates docker image and container

    Args:
        src (str):
        :builddir (str): build directory where all docker artifacts reside on local fs

    Returns:
        Container id (Name) | Failure (None)
    """
    imagename = osimage + ':' + param_dict['DockerImage']    # image name
    cname = param_dict['DockerContainer']                    # container id
    _root = param_dict['RepositoryRoot']                     # git repository root
    _buildscript = param_dict['DockerBuildScript'].strip()   # container-resident script to build rpm
    host_mnt = VOLMNT                                        # host volume mount point
    container_mnt = CONTAINER_VOLMNT                         # container volume internal mnt pt
    docker_user = 'builder'
    bash_cmd = '/bin/sleep 300'

    try:

        # create host mount for container volume
        if not os.path.exists(host_mnt):
            os.makedirs(host_mnt)
            stdout_message(f'Created host mount {host_mnt} for container volume')

        # if image rpmbuild not exist, create
        try:

            image = dclient.images.get(imagename)

            if image:
                stdout_message('Image already exists. Creating Container...')

        except Exception:
            # create new docker image
            os.chdir(src)
            cmd = 'docker build -t {} . '.format(imagename)
            subprocess.call([cmd], shell=True, cwd=src)
            stdout_message('Built image', prefix='OK')

        # start container detached
        container = dclient.containers.run(
                name=cname,
                image=imagename,
                command=bash_cmd,
                volumes={host_mnt: {'bind': container_mnt, 'mode': 'rw'}},
                user=docker_user,
                security_opt=['label:disable'],
                detach=True
            )

        # verify container is running
        if not container_running(cname):
            stdout_message(f'Container {cname} not started - abort', prefix='WARN')
            return False

        # copy build files to container
        stdout_message('Begin cp files into container')

        # copy files from temporary build directory to container
        os.chdir(builddir)

        buildfile_list = list(
            filter(
                lambda x: x.endswith('.tar.gz') or x.endswith('.spec') or x.endswith('.sh'), os.listdir('.')
            )
        )

        if debug:
            print(f'buildfile_list contains:\n\n\t%s' % export_iterobject(buildfile_list))
            print(f'osimage is: {osimage}')
            print(f'imagename is: {imagename}')
            print(f'container name is: {container.name}')

        # exec rpmbuild script
        docker_configure_container(container, _root, _buildscript, _version)

        if container_running(container.name):
            return container
    except OSError as e:
        logger.exception(
            '%s: Problem while updating builddir contents: %s' %
            (inspect.stack()[0][3], str(e)))
    return None


def docker_teardown(container_object):
    """
        Halt Docker Container, clean/ remove residual artifacts

    Returns
        Success | Failure, TYPE: bool
    """
    try:
        # stop and rm container
        cmd = f'docker stop {container_object.name}'
        subprocess.getoutput(cmd)

        # status
        if not container_running(container_object.name):
            stdout_message(f'{container_object.name} successfully halted', prefix='OK')
            cmd = f'docker rm {container_object.name}'
            subprocess.getoutput(cmd)
    except Exception as e:
        name = container_object.name
        fx = inspect.stack()[0][5]
        logger.exception(
            '{}: Error halting and deleting active container ({}): {}'.format(fx, name, e))
    return True


def main(setVersion, environment, package_configpath, force=False, retain=False, debug=False):
    """
    Summary:
        Create build directories, populate contents, update contents
    Args:
        :setVersion (str): version number of rpm created
        :environment (str):
        :package_configpath (str): full path to json configuration file
        :data (dict): build parameters for rpm build process
        :force (bool): If True, overwrites any pre-existing build artifacts
        :retain (bool): If True, leave container running; do not clean/ remove
    Returns:
        Success | Failure, TYPE: bool
    """
    # all globals declared here
    global PROJECT_BIN
    PROJECT_BIN = 'xlines'
    global PROJECT_ROOT
    PROJECT_ROOT = git_root()
    global SCRIPT_DIR
    SCRIPT_DIR = PROJECT_ROOT + '/' + 'scripts'
    global BUILD_ROOT
    BUILD_ROOT = TMPDIR
    global RPM_SRC
    RPM_SRC = PROJECT_ROOT + '/packaging/rpm'
    global LIB_DIR
    LIB_DIR = PROJECT_ROOT + '/' + PROJECT
    global CURRENT_VERSION
    CURRENT_VERSION = current_version(PROJECT_BIN, os.path.join(LIB_DIR, '_version.py'))

    # sort out version numbers, forceVersion is overwrite of pre-existing build artifacts
    global VERSION
    if setVersion:
        VERSION = setVersion
    elif CURRENT_VERSION:
        VERSION = CURRENT_VERSION
    else:
        stdout_message('Could not determine current {} version'.format(bd + PROJECT + rst))
        sys.exit(exit_codes['EX_DEPENDENCY']['Code'])

    # log
    stdout_message(f'Current version of last build: {bd + CURRENT_VERSION + rst}')
    stdout_message(f'Version to be used for this build: {act + VERSION + rst}')

    # create initial binary working dir
    BUILDDIRNAME = PROJECT + '-' + '.'.join(VERSION.split('.')[:2])

    # sub in current values
    parameter_obj = ParameterSet(package_configpath, VERSION)
    vars = parameter_obj.create()

    VERSION_FILE = vars['VersionModule']

    if debug:
        print(json.dumps(vars, indent=True, sort_keys=True))

    # launch docker container and execute final build steps
    if vars and VERSION_FILE:

        # trigger docker build based on environment:
        container = docker_init(
                os.path.join(PROJECT_ROOT, 'packaging/docker', environment),
                BUILD_ROOT,
                VERSION,
                environment,
                vars,
                debug
            )
        if container:
            return postbuild(PROJECT_ROOT, container, RPM_SRC, SCRIPT_DIR, VERSION_FILE, VERSION, retain)
    return False


def options(parser, help_menu=False):
    """
    Summary:
        parse cli parameter options
    Returns:
        TYPE: argparse object, parser argument set
    """
    parser.add_argument("-b", "--build", dest='build', default=False, action='store_true', required=False)
    parser.add_argument("-c", "--container", dest='container', default=False, action='store_true', required=False)
    parser.add_argument("-D", "--debug", dest='debug', default=False, action='store_true', required=False)
    parser.add_argument("-d", "--distro", dest='distro', default='centos7', nargs='?', type=str, required=False)
    parser.add_argument("-F", "--force", dest='force', default=False, action='store_true', required=False)
    parser.add_argument("-p", "--parameter-file", dest='parameter_file', default='.rpm.json', nargs='?', required=False)
    parser.add_argument("-s", "--set-version", dest='set', default=None, nargs='?', type=str, required=False)
    parser.add_argument("-h", "--help", dest='help', default=False, action='store_true', required=False)
    return parser.parse_args()


def is_installed(binary):
    """
    Verifies if program installed on Redhat-based Linux system
    """
    cmd = 'rpm -qa | grep ' + binary
    return True if subprocess.getoutput(cmd) else False


def ospackages(pkg_list):
    """Summary
        Install OS Package Prerequisites
    Returns:
        Success | Failure, TYPE: bool
    """
    try:
        for pkg in pkg_list:

            if is_installed(pkg):
                logger.info(f'{pkg} binary is already installed - skip')
                continue

            elif which('dnf'):
                cmd = 'sudo dnf install ' + pkg + ' 2>/dev/null'
                print(subprocess.getoutput(cmd))

            elif which('yum'):
                cmd = 'sudo yum install ' + pkg + ' 2>/dev/null'
                print(subprocess.getoutput(cmd))

            else:
                logger.warning(
                    '%s: Dependent OS binaries not installed - package manager not identified' %
                    inspect.stack()[0][3])

    except OSError as e:
        logger.exception('{}: Problem installing os package {}'.format(inspect.stack()[0][3], pkg))
        return False
    return True


def prebuild(builddir, libsrc, volmnt, parameter_file):
    """Summary:
        Prerequisites and dependencies for build execution
    Returns:
        Success | Failure, TYPE: bool
    """
    def preclean(dir, artifact=''):
        """Cleans residual build artifacts by removing """
        try:
            if artifact:
                if os.path.exists(libsrc + '/' + artifact):
                    rmtree(libsrc + '/' + artifact)    # clean artifact from inside an existing dir
            elif os.path.exists(dir):
                rmtree(dir)     # rm entire directory
        except OSError as e:
            logger.exception(
                '%s: Error while cleaning residual build artifacts: %s' %
                (inspect.stack()[0][3], str(e)))
            return False
        return True

    version_module = json.loads(read(parameter_file))['VersionModule']

    try:

        if preclean(builddir) and preclean(volmnt) and preclean(libsrc, '__pycache__'):
            stdout_message(f'Removed pre-existing build artifacts ({builddir}, {volmnt})')
        os.makedirs(builddir)
        os.makedirs(volmnt)

        root = git_root()
        src = os.path.join(root, PROJECT, version_module)
        dst = os.path.join(root, 'scripts', version_module)

        # deal with leftover build artifacts
        if os.path.exists(dst):
            os.remove(dst)

        # cp version module to scripts dir for import
        r_cf = copyfile(src, dst)
        global __version__
        from _version import __version__

        if r_cf and __version__ and docker_daemon_up():
            return True

    except Exception as e:
        logger.exception(
            '{}: Failure to import __version__ parameter'.format(inspect.stack()[0][3])
        )
    return False


def locate_artifact(filext, origin):
    """
    Summary.

        Finds rpm file object after creation
    Args:
        :filext (str): File extension searching for (".rpm")
        :origin (str): Starting directory for recursive search
    Returns:
        full path to rpm file | None if not found
    """
    for root, dirs, files in os.walk(origin):
        for file in files:
            if file.endswith(filext):
                return os.path.abspath(os.path.join(root, file))
    return None


def postbuild(root, container, rpm_root, scripts_dir, version_module, version, persist):
    """
    Summary:
        Post-build clean up
    Args:
        :container (object): Docker container object
        :rpm_root (str):  target dir for rpm package files
        :script_dir (str): directory where scripts
        :version_module (str): name of module containing version number
        :version (str): current version label (Example: 1.6.8)
        :persist (bool): When True, retain container build environment intact
            and running; do not clean and remove container
    Returns:
        Success | Failure, TYPE: bool
    """
    project_dirname = root.split('/')[-1]
    major = '.'.join(version.split('.')[:2])
    minor = version.split('.')[-1]
    volmnt = VOLMNT
    delete = True

    try:

        # cp rpm created to repo
        package = locate_artifact('.rpm', volmnt)
        if package:
            copyfile(locate_artifact('.rpm', volmnt), rpm_root)
            package_path = rpm_root + '/' + os.path.split(package)[1]

        # rpm contents text file
        contents = locate_artifact('.txt', volmnt)

        if persist is False:
            # stop and rm container
            cmd = f'docker stop {container.name}'
            subprocess.getoutput(cmd)

            # status
            if not container_running(container.name):
                stdout_message(f'{container.name} successfully halted', prefix='OK')
                cmd = f'docker rm {container.name}'
                subprocess.getoutput(cmd)

        # remove temp version module copied to scripts dir
        if os.path.exists(os.path.join(scripts_dir, version_module)):
            os.remove(os.path.join(scripts_dir, version_module))

        # rewrite version file with 67rrent build version
        with open(os.path.join(root, PROJECT, version_module), 'w') as f3:
            f2 = ["__version__ = \'" + version + "\'" + '\n']
            f3.writelines(f2)
            path = project_dirname + (root + '/' + PROJECT + '/' + version_module)[len(root):]
            stdout_message(
                '{}: Module {} successfully updated.'.format(inspect.stack()[0][3], yl + path + rst)
                )

    except OSError as e:
        logger.exception('{}: Postbuild clean up failure'.format(inspect.stack()[0][3]))
        return ''
    return package_path, contents


class ParameterSet():
    """Recursion class for processing complex dictionary schema."""

    def __init__(self, parameter_file, version):
        """
        Summary.

            Retains major and minor version numbers + parameters
            in json form for later use

        Args:
            :parameter_file (str): path to json file obj containing
             parameter keys and values
            :version (str): current build version
        """
        self.parameter_dict = json.loads(read(parameter_file))
        self.version = version
        self.major = '.'.join(self.version.split('.')[:2])
        self.minor = self.version.split('.')[-1]

    def create(self, parameters=None):
        """
        Summary.

            Update parameter dict with current values appropriate
            for the active build

        Args:
            :parameters (dict): dictionary of all parameters used to gen rpm
            :version (str):  the version of the current build, e.g. 1.6.7

        Returns:
            parameters, TYPE: dict

        """
        if parameters is None:
            parameters = self.parameter_dict

        for k, v in parameters.items():
            if isinstance(v, dict):
                self.create(v)
            else:
                if k == 'Version':
                    parameters[k] = self.major
                elif k == 'Release':
                    parameters[k] = self.minor
                elif k == 'Source':
                    parameters[k] = PROJECT + '-' + self.major + '.' + self.minor + '.tar.gz'
                elif k == 'BuildDirName':
                    parameters[k] = PROJECT + '-' + self.major
        return parameters


def valid_version(parameter, min=0, max=100):
    """
    Summary.

        User input validation.  Validates version string made up of integers.
        Example:  '1.6.2'.  Each integer in the version sequence must be in
        a range of > 0 and < 100. Maximum version string digits is 3
        (Example: 0.2.3 )

    Args:
        :parameter (str): Version string from user input
        :min (int): Minimum allowable integer value a single digit in version
            string provided as a parameter
        :max (int): Maximum allowable integer value a single digit in a version
            string provided as a parameter

    Returns:
        True if parameter valid or None, False if invalid, TYPE: bool

    """
    # type correction and validation
    if parameter is None:
        return True

    elif isinstance(parameter, int):
        return False

    elif isinstance(parameter, float):
        parameter = str(parameter)

    component_list = parameter.split('.')
    length = len(component_list)

    try:

        if length <= 3:
            for component in component_list:
                if isinstance(int(component), int) and int(component) in range(min, max + 1):
                    continue
                else:
                    return False

    except ValueError as e:
        fx = inspect.stack()[0][3]
        stdout_message(f'{fx}: Invalid version number supplied: {e}')
        return False
    return True


def init_cli():
    """Collect parameters and call main."""
    try:
        parser = argparse.ArgumentParser(add_help=False)
        args = options(parser)
    except Exception as e:
        help_menu()
        stdout_message(str(e), 'ERROR')
        return exit_codes['EX_MISC']['Code']

    if not os.path.isfile(args.parameter_file):
        stdout_message(
            message='Path to parmeters file not found. Abort',
            prefix='WARN'
        )
        return exit_codes['EX_DEPENDENCY']['Code']

    if args.debug:
        max_length = 44
        print(debug_header)

        stdout_message(
                message='Set (--set-version):{}{}'.format('\t'.expandtabs(14), args.set),
                prefix='DBUG'
            )
        stdout_message(
                message='Build Flag (--build):{}{}'.format('\t'.expandtabs(13), args.build),
                prefix='DBUG'
            )
        stdout_message(
                message='Docker Image (--distro):{}{}'.format('\t'.expandtabs(10), args.distro),
                prefix='DBUG'
            )
        stdout_message(
                message='Parameter File (--parameters):{}{}'.format('\t'.expandtabs(4), args.parameter_file),
                prefix='DBUG'
            )
        stdout_message(
                message='Debug Flag:{}{}'.format('\t'.expandtabs(23), args.debug),
                prefix='DBUG'
            )

    if len(sys.argv) == 1:
        help_menu()
        return exit_codes['EX_OK']['Code']

    elif args.help:
        help_menu()
        return exit_codes['EX_OK']['Code']

    elif args.build:
        libsrc = os.path.join(git_root(), PROJECT)
        if valid_version(args.set) and prebuild(TMPDIR, libsrc, VOLMNT, args.parameter_file):
            package, contents = main(
                        setVersion=args.set,
                        environment=args.distro,
                        package_configpath=args.parameter_file,
                        force=args.force,
                        retain=args.container,
                        debug=args.debug
                    )
            if package:
                stdout_message(f'New package created: {yl + package + rst}')
                stdout_message(f'RPM build process completed successfully. End', prefix='OK')

                if contents:
                    display_package_contents(package, contents)
                else:
                    stdout_message(
                        message=f'Unable to locate a rpm contents file in {VOLMNT}.',
                        prefix='WARN')
                    return False
                return exit_codes['EX_OK']['Code']
            else:
                stdout_message(
                    '{}: Problem creating rpm installation package. Exit'.format(inspect.stack()[0][3]),
                    prefix='WARN',
                    severity='WARNING'
                )
                return exit_codes['EX_MISC']['Code']

        elif not valid_version(args.set):
            stdout_message(
                'You must enter a valid version when using --set-version parameter. Ex: 1.6.3',
                prefix='WARN',
                severity='WARNING'
                )
            return exit_codes['EX_DEPENDENCY']['Code']
        else:
            logger.warning('{} Failure in prebuild stage'.format(inspect.stack()[0][3]))
            return exit_codes['EX_DEPENDENCY']['Code']
    return True

sys.exit(init_cli())
