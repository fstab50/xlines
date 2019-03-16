#!/usr/bin/env python3
"""

#
# nlines, GPL v3 License
#
# Copyright (c) 2018-2019 Blake Huber
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the 'Software'), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED 'AS IS', WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

"""
import os
import sys
import json
import inspect
import argparse
from functools import reduce
from multiprocessing import Process, Queue
from multiprocessing.dummy import Pool
from pyaws.utils import export_json_object
from pyaws.script_utils import import_file_object, read_local_config
from pyaws.utils import stdout_message
from pyaws.colors import Colors
from nlines.statics import PACKAGE, local_config
from nlines.help_menu import menu_body
from nlines import about, logger, Colors

try:
    from pyaws.core.oscodes_unix import exit_codes
    os_type = 'Linux'
    user_home = os.getenv('HOME')
    splitchar = '/'                             # character for splitting paths (linux)
    ACCENT = Colors.ORANGE
    TEXT = Colors.LT2GRAY
    TITLE = Colors.WHITE + Colors.BOLD
except Exception:
    from pyaws.core.oscodes_win import exit_codes    # non-specific os-safe codes
    os_type = 'Windows'
    user_home = os.getenv('username')
    splitchar = '\\'                            # character for splitting paths (windows)
    ACCENT = Colors.CYAN
    TEXT = Colors.LT2GRAY
    TITLE = Colors.WHITE + Colors.BOLD


# globals
container = []
config_dir = local_config['PROJECT']['CONFIG_PATH']
expath = local_config['EXCLUSIONS']['EX_PATH']


def linecount(path):
    return len(open(path).readlines())


def filter_args(kwarg_dict, *args):
    """
    Summary:
        arg, kwarg validity test

    Args:
        kwarg_dict: kwargs passed in to calling method or func
        args:  valid keywords for the caller

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
    print(
        Colors.BOLD + '\n\t\t\t  ' + PACKAGE + Colors.RESET +
        ' help contents'
        )
    print(menu_body)
    return


def remove_duplicates(duplicates):
    """
    Summary.

        Generator for removing duplicates from large scale lists

    Args:
        duplicates (list): contains repeated elements

    Returns:
        generator object (iter)
    """
    uniq = []

    def dedup(d):
        for element in duplicates:
            if element not in uniq:
                uniq.append(element)
                yield element
    return [x for x in dedup(duplicates)]


class ExcludedTypes():
    def __init__(self, ex_path, ex_container=[]):
        self.ex_container = ex_container
        if not self.ex_container:
            self.ex_container.extend(self.parse_exclusions(ex_path))

    def excluded(self, path):
        for i in self.ex_container:
            if i in path:
                return True
        return False

    def parse_exclusions(self, path):
        """
        Parse persistent fs location store for file extensions to exclude
        """
        try:
            return [x.strip() for x in open(path).readlines()]
        except OSError:
            return []


def locate_fileobjects(origin, path=expath):
    """
    Summary.

        - Walks local fs directories identifying all git repositories

    Args:
        - origin (str): filesystem directory location

    Returns:
        - paths, TYPE: list
        - Format:

         .. code-block:: json

                [
                    '/cloud-custodian/tools/c7n_mailer/c7n_mailer/utils_email.py',
                    '/cloud-custodian/tools/c7n_mailer/c7n_mailer/slack_delivery.py',
                    '/cloud-custodian/tools/c7n_mailer/c7n_mailer/datadog_delivery.py',
                    '/cloud-custodian/tools/c7n_sentry/setup.py',
                    '/cloud-custodian/tools/c7n_sentry/test_sentry.py',
                    '/cloud-custodian/tools/c7n_kube/setup.py',
                    '...
                ]

    """
    fobjects = []
    ex = ExcludedTypes(path)

    for root, dirs, files in os.walk(origin):
        for path in dirs:
            for file in files:
                try:
                    full_path = '/'.join(
                            os.path.abspath(os.path.join(root, path)).split('/')[:-1]
                        ) + '/' + file

                    if ex.excluded(full_path):
                        continue
                    else:
                        fobjects.append(full_path)
                except OSError:
                    logger.exception(
                        '%s: Read error while examining local filesystem path (%s)' %
                        (inspect.stack()[0][3], path)
                    )
                    continue
    return remove_duplicates(fobjects)


def summary(repository_list):
    """ Prints summary stats """
    count = len(repository_list)
    stdout_message(
        '%s Local git repositories detected and indexed' %
        (TITLE + str(count) + Colors.RESET))
    return True


def main(**kwargs):
    """ Main """
    keywords = ('root', 'debug', 'update', 'remediate')
    if filter_args(kwargs, *keywords):
        root = kwargs.get('root', user_home)
        update = kwargs.get('update', False)
        remediate = kwargs.get('remediate', False)
        debug = kwargs.get('debug', False)
    return False


def line_orchestrator(path):
    io_fail = []
    container = {}
    try:
        inc = linecount(path)
        fname = path.split('/')[-1]
        container[fname] = inc
    except Exception:
        io_fail.append(path)
    return container, io_fail


def options(parser, help_menu=False):
    """
    Summary:
        parse cli parameter options
    Returns:
        TYPE: argparse object, parser argument set
    """
    parser.add_argument("-i", "--index", dest='index', action='store_true', required=False)
    parser.add_argument("-C", "--configure", dest='configure', action='store_true', required=False)
    parser.add_argument("-d", "--debug", dest='debug', action='store_true', required=False)
    parser.add_argument("-h", "--help", dest='help', action='store_true', required=False)
    parser.add_argument("-s", "--sum", dest='sum', nargs='?', default='.', required=False)
    parser.add_argument("-u", "--update", dest='update', type=str, default='all', required=False)
    parser.add_argument("-V", "--version", dest='version', action='store_true', required=False)
    return parser.parse_args()


def package_version():
    """
    Prints package version and requisite PACKAGE info
    """
    print(about.about_object)
    sys.exit(exit_codes['EX_OK']['Code'])


def precheck():
    """
    Pre-execution Dependency Check
    """
    # check if git root dir set; otherwise use home
    # check logging enabled
    # check if config file
    return True


def init_cli():

    parser = argparse.ArgumentParser(add_help=False)

    try:
        args = options(parser)
    except Exception as e:
        help_menu()
        stdout_message(str(e), 'ERROR')
        sys.exit(exit_codes['E_BADARG']['Code'])

    if len(sys.argv) == 1:
        help_menu()
        sys.exit(exit_codes['EX_OK']['Code'])

    elif args.help:
        help_menu()
        sys.exit(exit_codes['EX_OK']['Code'])

    elif args.version:
        package_version()

    elif args.sum:

        if precheck():
            container = []

            io_fail = []
            count = 0
            width = 63
            for path in locate_fileobjects('.'):
                try:
                    inc = linecount(path)
                    count += inc
                    fname = path.split('/')[-1][:50]
                    lpath = path[:50]
                    tab = '\t'.expandtabs(width - len(lpath))
                    print('{}{}{:>6}'.format(lpath, tab, '{:,}'.format(inc)))
                except Exception:
                    io_fail.append(path)
                    continue
            msg = 'Total count is:'
            tab = '\t'.expandtabs(width - len(msg))
            print('{}{}{:>6}'.format(msg, tab, '{:,}'.format(count)))
            #print('Total count is {}'.format('{:,}'.format(count)))
            sys.exit(exit_codes['E_DEPENDENCY']['Code'])

            print('Skipped file objects:')
            for file in io_fail:
                print('\t{}'.format(file))   # Write this out to a file in /tmp for later viewing

            # --- run with concurrency ---

            #path_list = locate_fileobjects('.')

            if len(sys.argv) > 1:
                for i in sys.argv[1:]:
                    container.append(i)

            # prepare args with tuples
            pool_args = [(x,) for x in locate_fileobjects('.')]

            # run instance of main with each item set in separate thread
            # pool function:  return dict with {file: linecount} which can then be printed
            # out to cli
            with Pool(processes=8) as pool:
                try:
                    pool.starmap(line_orchestrator, pool_args)
                except Exception:
                    pass

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
