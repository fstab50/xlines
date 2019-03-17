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
import multiprocessing
from multiprocessing import Queue
from multiprocessing.dummy import Pool
from pyaws.utils import export_json_object
from pyaws.script_utils import import_file_object, read_local_config
from pyaws.utils import stdout_message, export_json_object
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

# universal colors
rd = Colors.RED + Colors.BOLD
yl = Colors.YELLOW + Colors.BOLD
fs = Colors.GOLD3
bd = Colors.BOLD
gn = Colors.BRIGHTGREEN
frame = gn + bd
btext = TEXT + Colors.BOLD
bdwt = Colors.BOLD + Colors.BRIGHTWHITE
ub = Colors.UNBOLD
rst = Colors.RESET

# globals
container = []
config_dir = local_config['PROJECT']['CONFIG_PATH']
expath = local_config['EXCLUSIONS']['EX_PATH']

div = frame + ' | ' + rst
div_len = 2
horiz = frame + '_' + rst


def linecount(path):
    return len(open(path).readlines())


def mp_linecount(path, exclusions):
    p = path
    try:
        if os.path.isfile(path):
            q.put({os.path.abspath(path): linecount(path)})

        elif os.path.isdir(path):
            d = locate_fileobjects(path)
            valid_paths = remove_illegal(d, exclusions)
            for p in valid_paths:
                q.put({p: linecount(p)})
    except UnicodeDecodeError:
        q.put({p: None})
        return


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

        Module function utilsing a generator to remove duplicates
        from large scale lists with minimal resource use

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


def remove_illegal(d, illegal):
    """Removes excluded file types"""
    bad = []

    for path in d:
        for t in illegal:
            if t in path:
                bad.append(path)
    return list(filter(lambda x: x not in bad, d))


class ExcludedTypes():
    def __init__(self, ex_path, ex_container=[]):
        self.types = ex_container
        if not self.types:
            self.types.extend(self.parse_exclusions(ex_path))

    def excluded(self, path):
        for i in self.types:
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

    if os.path.isfile(origin):
        return [origin]

    for root, dirs, files in os.walk(origin):
        for file in [f for f in files if '.git' not in root]:
            try:

                full_path = os.path.abspath(os.path.join(root, file))

                #if not ex.excluded(full_path):
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
    parser.add_argument("-m", "--multiprocess", dest='multiprocess', default=False, action='store_true', required=False)
    parser.add_argument("-s", "--sum", dest='sum', nargs='*', default='.', required=False)
    parser.add_argument("-u", "--update", dest='update', type=str, default='all', required=False)
    parser.add_argument("-V", "--version", dest='version', action='store_true', required=False)
    return parser.parse_args()


def package_version():
    """
    Prints package version and requisite PACKAGE info
    """
    print(about.about_object)
    sys.exit(exit_codes['EX_OK']['Code'])


def path_width(words):
    max_len = 0
    for word in words:
        if len(str(word)) > max_len:
            max_len = len(str(word))
    return 100 if max_len > 100 else max_len


def precheck():
    """
    Pre-execution Dependency Check
    """
    # check if git root dir set; otherwise use home
    # check logging enabled
    # check if config file
    return True


def print_footer(total, w):
    msg = 'Total count:'
    tab = '\t'.expandtabs((w if w < 100 else 100) - len(msg) - len(str(total)) - div_len - 4)
    tab2 = '\t'.expandtabs(2)
    tab3 = '\t'.expandtabs(3)
    print(tab3 + (horiz * (w if w < 100 else 100)) + '\n')
    print(f'{tab2}{div}{msg}{tab}{"{:,}".format(total):>6}{div}')  # msg, tab, '{:,}'.format(total))
    print(tab3 + (horiz * (w if w < 100 else 100))  + '\n')


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

    elif args.sum and precheck():

        ex = ExcludedTypes(ex_path='/home/blake/.config/nlines/exclusions.list')
        container = []

        if args.debug:
            print('\nargs.sum:')
            print(args.sum)
            print('\nsys.argv contents:')
            print(sys.argv)
            sys.exit(0)

        if args.multiprocess:
            # --- run with concurrency --

            global q
            q = Queue()

            container.extend(args.sum)

            processes = []
            for i in container:
                t = multiprocessing.Process(target=mp_linecount, args=(i,ex.types))
                processes.append(t)
                t.start()

            for one_process in processes:
                one_process.join()

            mylist = []
            while not q.empty():
                mylist.append(q.get())

            stdout_message(message='Length of resultset: {}'.format(len(mylist)))
            export_json_object(mylist)
            stdout_message(message='Done')
            return 0

            pool_args = []
            if len(sys.argv) > 2:
                container.extend(sys.argv[1:])
            elif '.' in sys.argv:
                container.append('.')

                for element in container:
                    pool_args.extend([(x,) for x in locate_fileobjects(element)])
            # Pool multiprocess module
            # prepare args with tuples
            for element in container:
                pool_args.extend([(x,) for x in locate_fileobjects(element)])

            # run instance of main with each item set in separate thread
            # pool function:  return dict with {file: linecount} which can then be printed
            # out to cli
            with Pool(processes=8) as pool:
                try:
                    pool.starmap(line_orchestrator, pool_args)
                except Exception:
                    pass
            sys.exit(exit_codes['EX_OK']['Code'])

        elif not args.multiprocess:

            io_fail = []
            tcount = 0

            d = locate_fileobjects('.')
            good = remove_illegal(d, ex.types)
            width = path_width(good)
            fname_max = 25

            for path in good:
                try:
                    inc = linecount(path)
                    tcount += inc    # total count
                    count_len = len(str(inc)) + 2
                    fname = path.split('/')[-1][:fname_max - 1]
                    lpath = path[:(width - count_len)]
                    tab = '\t'.expandtabs(width - len(lpath))
                    tab2 = '\t'.expandtabs(2)
                    tabName = ' \t'.expandtabs(fname_max - len(fname))
                    output_str = f'{tab2}{div}{fname}{tabName}{div}{lpath}{tab}{div}{inc:>6}{div}'
                    print(output_str)
                except Exception:
                    io_fail.append(path)
                    continue

            print_footer(tcount, len(output_str))

            if args.debug:
                print('Skipped file objects:')
                for file in io_fail:
                    print('\t{}'.format(file))   # Write this out to a file in /tmp for later viewing
            sys.exit(exit_codes['E_DEPENDENCY']['Code'])

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
