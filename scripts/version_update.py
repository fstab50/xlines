"""
Handles incremental changes to project version id

Use & Restrictions:
    - version format X.Y.Z
    - x, y, z integers
    - can have 0 as either x, y, or z

"""

import os
import sys
import argparse
import inspect
import subprocess
from libtools import stdout_message, logd
from config import script_config

# global logger
script_version = '1.0'
logd.local_config = script_config
logger = logd.getLogger(script_version)

try:
    from libtools.oscodes_unix import exit_codes
    os_type = 'Linux'
    user_home = os.getenv('HOME')

except Exception:
    from libtools.oscodes_win import exit_codes         # non-specific os-safe codes
    os_type = 'Windows'
    user_home = os.getenv('username')


def _root():
    """Returns root directory of git project repository"""
    cmd = 'git rev-parse --show-toplevel 2>/dev/null'
    return subprocess.getoutput(cmd).strip()


def current_version(module_path):
    with open(module_path) as f1:
        f2 = f1.read()
    return f2.split('=')[1].strip()[1:-1]


def locate_version_module(directory):
    files = list(filter(lambda x: x.endswith('.py'), os.listdir(directory)))
    return [f for f in files if 'version' in f][0]


def increment_version(current):
    major = '.'.join(current.split('.')[:2])
    minor = int(current.split('.')[-1][0]) + 1
    return '.'.join([major, str(minor)])


def options(parser, help_menu=True):
    """
    Summary:
        parse cli parameter options

    Returns:
        TYPE: argparse object, parser argument set

    """
    parser.add_argument("-d", "--debug", dest='debug', action='store_true', default=False, required=False)
    parser.add_argument("-h", "--help", dest='help', action='store_true', required=False)
    parser.add_argument("-s", "--set-version", dest='set', default=None, nargs='?', type=str, required=False)
    parser.add_argument("-V", "--version", dest='version', action='store_true', required=False)
    return parser.parse_known_args()


def package_name(artifact):
    with open(artifact) as f1:
        f2 = f1.readlines()
    for line in f2:
        if line.startswith('PACKAGE'):
            return line.split(':')[1].strip()
    return None


def update_signature(version, path):
    """Updates version number module with new"""
    try:
        with open(path, 'w') as f1:
            f1.write("__version__ = '{}'\n".format(version))
            return True
    except OSError:
        stdout_message('Version module unwriteable. Failed to update version')
    return False


def update_version(force_version=None, debug=False):
    """
    Summary.
        Increments project version by 1 minor increment
        or hard sets to version signature specified

    Args:
        :force_version (Nonetype): Version signature (x.y.z)
            if version number is hardset insetead of increment

    Returns:
        Success | Failure, TYPE: bool
    """
    # prerequisities
    PACKAGE = package_name(os.path.join(_root(), 'DESCRIPTION.rst'))
    module = locate_version_module(PACKAGE)

    module_path = os.path.join(_root(), PACKAGE, str(module))

    # current version
    current = current_version(module_path)
    stdout_message('Current project version found: {}'.format(current))

    # next version
    if force_version is None:
        version_new = increment_version(current)

    elif valid_version(force_version):
        version_new = force_version

    else:
        stdout_message('You must enter a valid version (x.y.z)')
        sys.exit(1)

    stdout_message('Incremental project version: {}'.format(version_new))
    return update_signature(version_new, module_path)


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
    if isinstance(parameter, int):
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
    except ValueError:
        fx = inspect.stack()[0][3]
        invalid_msg = 'One or more version numerical components are not integers'
        logger.exception('{}: {}'.format(fx, invalid_msg))
        return False
    return True


if __name__ == '__main__':

    parser = argparse.ArgumentParser(add_help=False)

    try:

        args, unknown = options(parser)

    except Exception as e:
        stdout_message(str(e), 'ERROR')
        sys.exit(exit_codes['E_BADARG']['Code'])

    if args.help:
        parser.print_help()
        sys.exit(0)

    elif update_version(args.set, args.debug):
        sys.exit(0)
    sys.exit(1)
