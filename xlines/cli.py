#!/usr/bin/env python3
"""

xlines, GPL v3 License

Copyright (c) 2018-2019 Blake Huber

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the 'Software'), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED 'AS IS', WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.

"""
import os
import sys
import re
import json
import inspect
import argparse
import subprocess
from shutil import copy2 as copyfile
from shutil import which
from pathlib import Path
from xlines import about, Colors, logger
from xlines.usermessage import stdout_message
from xlines.statics import local_config
from xlines.help_menu import menu_body
from xlines.square import border_map
from xlines.mp import multiprocessing_main
from xlines.core import absolute_paths, linecount, locate_fileobjects
from xlines.core import remove_illegal, print_footer, print_header
from xlines.exclusions import ExcludedTypes
from xlines.configure import display_exclusions, main_menupage
from xlines.colormap import ColorMap
from xlines.variables import *

cm = ColorMap()

try:
    from xlines.oscodes_unix import exit_codes
    os_type = 'Linux'
    user_home = os.getenv('HOME')
    splitchar = '/'                                   # character for splitting paths (linux)

except Exception:
    from xlines.oscodes_win import exit_codes         # non-specific os-safe codes
    os_type = 'Windows'
    user_home = os.getenv('username')
    splitchar = '\\'                                  # character for splitting paths (windows)


# globals
container = []
module = os.path.basename(__file__)
iloc = os.path.abspath(os.path.dirname(__file__))     # installed location of modules


def sp_linecount(path, abspath, exclusions):
    """
        Single threaded (sequential processing) line count

    Return:
        valid filesystem paths, TYPE: list

    """
    try:

        if os.path.isfile(path):
            return remove_illegal([path], exclusions)

        elif os.path.isdir(path):
            d = locate_fileobjects(path, abspath)
            valid_paths = remove_illegal(d, exclusions)
            return valid_paths

    except UnicodeDecodeError:
        pass


def filter_args(kwarg_dict, *args):
    """
    Summary:
        arg, kwarg validity test

    Args:
        :kwarg_dict: kwargs passed in to calling method or func
        :args:  valid keywords for the caller

    Returns:
        True if kwargs are valid; else raise exception
    """
    # unpack if iterable passed in args - TBD (here)
    if kwarg_dict is not None:
        keys = [key for key in kwarg_dict]
        unknown_arg = list(filter(lambda x: x not in args, keys))
        if unknown_arg:
            raise KeyError(
                '%s: unknown parameter(s) provided [%s]' %
                (inspect.stack()[0][3], str(unknown_arg))
            )
    return True


def help_menu():
    """
    Displays help menu contents
    """
    print(menu_body)
    border_map()
    sys.stdout.write('\n')
    return


def main(**kwargs):
    """ Main """
    keywords = ('root', 'debug', 'update', 'remediate')
    if filter_args(kwargs, *keywords):
        root = kwargs.get('root', user_home)
        update = kwargs.get('update', False)
        remediate = kwargs.get('remediate', False)
        debug = kwargs.get('debug', False)
    return False


def longest_path(parameters, exclusions):
    """
        Traces all subdirectories of provided commandline paths
        using MaxWidth object

    Args:
        :parameters (list): list of all sys.argv parameters supplied with --sum
        :exclusions (ExcludedTypes object): types to exclude

    Returns:
        width (integer), number of characters in longest path
    """
    mp = MaxWidth()     # max path object
    abspath = absolute_paths(parameters)
    container = []
    max_width = 0

    for i in parameters:
        try:
            paths = sp_linecount(i, abspath, exclusions.types)
            width = mp.calc_maxpath(paths)
            max_width = width if (width > max_width) else max_width
            container.extend(paths)
        except TypeError:
            stdout_message(message='Provided path appears to be invalid', prefix='WARN')
            sys.exit(exit_codes['EX_OSFILE']['Code'])
    return max_width, container


class MaxWidth():
    def __init__(self):
        self.buffer = local_config['OUTPUT']['COUNT_COLUMN_WIDTH'] + BUFFER
        self.term_width = os.get_terminal_size().columns - self.buffer - BUFFER
        self.max_width = local_config['OUTPUT']['MIN_WIDTH']

    def calc_maxpath(self, path_list):
        for path in path_list:
            if len(path) > self.max_width:
                self.max_width = len(path)
            if len(path) > self.term_width:
                continue
        return self.max_width if (self.max_width < self.term_width) else self.term_width


def modules_location():
    """Filsystem location of Python3 modules"""
    return os.path.split(os.path.abspath(__file__))[0]


def options(parser, help_menu=False):
    """
    Summary:
        parse cli parameter options

    Returns:
        TYPE: argparse object, parser argument set

    """
    parser.add_argument("-C", "--configure", dest='configure', action='store_true', required=False)
    parser.add_argument("-d", "--debug", dest='debug', action='store_true', default=False, required=False)
    parser.add_argument("-e", "--exclude", dest='exclude', nargs='*', default=[], required=False)
    parser.add_argument("-h", "--help", dest='help', action='store_true', required=False)
    parser.add_argument("-l", "--list-exclusions", dest='exclusions', action='store_true', required=False)
    parser.add_argument("-m", "--multiprocess", dest='multiprocess', default=False, action='store_true', required=False)
    parser.add_argument("-s", "--sum", dest='sum', nargs='*', default=os.getcwd(), required=False)
    parser.add_argument("-n", "--no-whitespace", dest='whitespace', action='store_false', default=True, required=False)
    parser.add_argument("-V", "--version", dest='version', action='store_true', required=False)
    return parser.parse_known_args()


def package_version():
    """
    Prints package version and requisite PACKAGE info
    """
    print(about.about_object)
    sys.exit(exit_codes['EX_OK']['Code'])


def set_hicount_threshold():
    """
        Retrieves high line count threshold from local filesystem if exists

    Returns:
        high line count threshold || None

    """
    local_linecount_file = local_config['CONFIG']['HI_THRESHOLD_FILEPATH']
    reference_threshold = local_config['OUTPUT']['COUNT_HI_THRESHOLD']

    try:

        if os.path.exists(local_linecount_file):
            with open(local_linecount_file) as f1:
                threshold = f1.read().strip()
        else:
            # not exist; create threshold file on local filesystem
            with open(local_linecount_file, 'w') as f1:
                f1.write(str(reference_threshold) + '\n')
                threshold = reference_threshold
    except OSError:
        fx = inspect.stack()[0][3]
        logger.exception(f'{fx}: Problem reading local hicount threshold file. Abort')
        return None
    return int(threshold)


def precheck(user_exfiles, user_exdirs, debug):
    """
    Runtime Dependency Checks: postinstall artifacts, environment
    """
    def set_environment():
        lang = 'undefined'
        if os.getenv('LANG') is None:
            lang = '{}export LANG=en_US.UTF-8{}'.format(yl, rst)
        elif 'UTF-8' not in os.getenv('LANG'):
            lang = '{}export LANG=$LANG.UTF-8{}'.format(yl, rst)
        return lang

    # local user configuration:  excluded file types
    _os_configdir = os.path.join(modules_location(), 'config')
    _ex_fname = local_config['EXCLUSIONS']['EX_FILENAME']
    _os_ex_fname = os.path.join(_os_configdir, _ex_fname)

    # local user configuration:  excluded directories
    _dir_fname = local_config['EXCLUSIONS']['EX_DIR_FILENAME']
    _os_dir_fname = os.path.join(_os_configdir, _dir_fname)
    _config_dir = local_config['CONFIG']['CONFIG_DIR']
    _language = set_environment()
    _environment_setup = 'fail' if 'UTF-8' in _language else 'success'

    if debug:
        tab = '\t'.expandtabs(16)
        stdout_message(f'_os_configdir: {_os_configdir}: system py modules location', 'DBUG')
        stdout_message(f'_os_ex_fname: {_os_ex_fname}: system exclusions.list path', 'DBUG')
        stdout_message(f'_os_dir_fname: {_os_dir_fname}: system directories.list file path', 'DBUG')
        stdout_message(f'_configdir: {_config_dir}: user home config file location', 'DBUG')
        stdout_message(f'Environment setup status: {_environment_setup.upper()}')

        if _environment_setup.upper() == 'FAIL':
            _env = _environment_setup.upper()
            msg = f'Environment setting is {_env}. Add the following code in your .bashrc file'
            stdout_message('{}:  {}'.format(msg, _language))

    try:
        # check if exists; copy
        if not os.path.exists(_config_dir):
            os.makedirs(_config_dir)

        # cp system config file to user if user config files absent
        if os.path.exists(_os_ex_fname) and os.path.exists(_os_dir_fname):

            if not os.path.exists(user_exfiles):
                copyfile(_os_ex_fname, user_exfiles)

            if not os.path.exists(user_exdirs):
                copyfile(_os_dir_fname, user_exdirs)

        # debian-style installation paths
        elif os.path.exists(os.path.join('usr/local/lib/xlines/config', _ex_fname)):

            if not os.path.exists(user_exfiles):
                copyfile(os.path.join('usr/local/lib/xlines/config', _ex_fname), user_exfiles)

            if not os.path.exists(user_exdirs):
                copyfile(os.path.join('usr/local/lib/xlines/config', _dir_fname), user_exdirs)

    except OSError:
        fx = inspect.stack()[0][3]
        logger.exception('{}: Problem installing user config files. Exit'.format(fx))
        return False
    return True


def create_container(parameters):
    """
    Summary.

        Create container list of fs artifacts to count

    Returns:
        list (iter)

    """
    container = []
    if isinstance(parameters, list):
        container.extend(parameters)
    else:
        container.append(parameters)
    return container


class RelpathProcessing():
    """Corrects relative paths"""
    def __init__(self):
        self.pattern_hidden = re.compile('^.[a-z]+')                    # hidden file (.xyz)
        self.pattern_asci = re.compile('^[a-z]+', re.IGNORECASE)        # regular, standalone file

    def normalize(self, path):
        """Prepends correct filesystem syntax if pwd counted"""
        if self.pattern_hidden.match(path) or self.pattern_asci.match(path):
            return './' + path


def remove_excluded(exclude_list, path_list):
    """Removes excluded paths from master path list"""
    rm = []

    if not exclude_list:
        return path_list

    for i in exclude_list:
        rm.extend([x for x in path_list if i in x])
    return sorted(list(set(path_list) - set(rm)))


def init_cli():
    ex_files = local_config['EXCLUSIONS']['EX_EXT_PATH']
    ex_dirs = local_config['EXCLUSIONS']['EX_DIR_PATH']

    # process commandline args
    parser = argparse.ArgumentParser(add_help=False)

    try:

        args, unknown = options(parser)

    except Exception as e:
        help_menu()
        stdout_message(str(e), 'ERROR')
        sys.exit(exit_codes['E_BADARG']['Code'])

    # validate configuration files
    if precheck(ex_files, ex_dirs, args.debug):
        _ct_threshold = set_hicount_threshold() or local_config['OUTPUT']['COUNT_HI_THRESHOLD']

    if len(sys.argv) == 1 or args.help:
        help_menu()
        sys.exit(exit_codes['EX_OK']['Code'])

    elif args.version:
        package_version()

    elif args.exclusions:
        display_exclusions(ex_files, ex_dirs)

    elif args.configure:
        main_menupage(ex_files, ex_dirs)

    elif len(sys.argv) == 2 and (sys.argv[1] != '.'):
        help_menu()
        sys.exit(exit_codes['EX_OK']['Code'])

    elif args.sum:

        ex = ExcludedTypes(ex_path=str(Path.home()) + '/.config/xlines/exclusions.list')
        container = create_container(args.sum)
        abspath = absolute_paths(container)

        if args.debug:
            stdout_message(f'xlines command line option parameter detail', prefix='DEBUG')
            print('\targs.sum: {}'.format(args.sum))
            print('\n\tsys.argv contents:\n')
            for i in sys.argv:
                print('\t\to  {}'.format(i))
            print(f'\n\tcontainer is:\t{container}')
            print(f'\n\tobject "unknown" is:\t{unknown}')
            print('\tabspath bool is {}\n'.format(abspath))
            print('\tmultiprocess bool is {}\n'.format(args.multiprocess))

        if args.multiprocess:
            # --- run with concurrency --
            width, paths = longest_path(container, ex)
            paths = remove_excluded(args.exclude, paths)
            multiprocessing_main(paths, width, _ct_threshold, args.whitespace, ex, args.debug)

        elif not args.multiprocess:

            io_fail = []
            tcount, tobjects = 0, 0
            width, paths = longest_path(container, ex)

            paths = remove_excluded(args.exclude, paths)

            print_header(width)
            count_width = local_config['OUTPUT']['COUNT_COLUMN_WIDTH']

            for path in paths:

                try:

                    inc = linecount(path, args.whitespace)
                    highlight = acct if inc > _ct_threshold else cm.aqu
                    tcount += inc    # total line count
                    tobjects += 1    # increment total number of objects

                    # truncation
                    lpath, fname = os.path.split(path)

                    if (len(path) + BUFFER * 2) > width:
                        cutoff = (len(path) + BUFFER * 2) - width
                    else:
                        cutoff = 0

                    tab = '\t'.expandtabs(width - len(lpath) - len(fname) - count_width + BUFFER)

                    # with color codes added
                    if cutoff == 0:
                        lpath = text + lpath + rst
                    else:
                        lpath = text + os.path.split(path)[0][:len(lpath) - cutoff - BUFFER] + rst + arrow
                        tab = '\t'.expandtabs(width - len(lpath) - len(fname) + count_width + BUFFER + cut_corr)

                    tab4 = '\t'.expandtabs(4)
                    fname = highlight + fname + rst

                    # incremental count formatting
                    ct_format = acct if inc > _ct_threshold else bwt

                    # format tabular line totals with commas
                    output_str = f'{tab4}{lpath}{div}{fname}{tab}{ct_format}{"{:,}".format(inc):>10}{rst}'
                    print(output_str)

                    if args.debug:
                        print(tab4*2 + 'lpath is {}'.format(lpath))
                        print(tab4*2 + 'fname is {}\n'.format(fname))

                except Exception:
                    io_fail.append(path)
                    continue

            print_footer(tcount, tobjects, width)

            if args.debug:
                tab4 = '\t'.expandtabs(4)
                stdout_message(f'cli screen columns variable, width: {cm.bdwt}{width}{cm.rst}', prefix='DBUG')
                print('\n' + tab4 + 'Skipped file objects:\n' + tab4 + ('-' * (width + count_width)))
                if io_fail:
                    for file in io_fail:
                        print('\t{}'.format(file))   # Write this out to a file in /tmp for later viewing
                else:
                    print('\tNone')
                sys.stdout.write('\n')

            sys.exit(exit_codes['EX_OK']['Code'])

    else:
        stdout_message(
            'Dependency check fail %s' % json.dumps(args, indent=4),
            prefix='AUTH',
            severity='WARNING'
            )
        sys.exit(exit_codes['E_DEPENDENCY']['Code'])

    failure = """ : Check of runtime parameters failed for unknown reason.
    Please ensure you have both read and write access to local filesystem. """
    logger.warning(failure + 'Exit. Code: %s' % sys.exit(exit_codes['E_MISC']['Code']))
    print(failure)
