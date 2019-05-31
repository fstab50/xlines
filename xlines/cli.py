#!/usr/bin/env python3
"""

#
# xlines, GPL v3 License
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
from pathlib import Path
from pyaws.utils import stdout_message
from pyaws.colors import Colors
from xlines.statics import PACKAGE, local_config
from xlines.help_menu import menu_body
from xlines import about, logger
from xlines.mp import multiprocessing_main
from xlines.common import linecount, locate_fileobjects, remove_illegal
from xlines.common import ExcludedTypes
from xlines.colormap import ColorMap


cm = ColorMap()

try:
    from pyaws.core.oscodes_unix import exit_codes
    os_type = 'Linux'
    user_home = os.getenv('HOME')
    splitchar = '/'                             # character for splitting paths (linux)
    acct = Colors.ORANGE
    text = Colors.BRIGHT_PURPLE
    TITLE = Colors.WHITE + Colors.BOLD
except Exception:
    from pyaws.core.oscodes_win import exit_codes    # non-specific os-safe codes
    os_type = 'Windows'
    user_home = os.getenv('username')
    splitchar = '\\'                            # character for splitting paths (windows)
    acct = Colors.CYAN
    text = Colors.LT2GRAY
    TITLE = Colors.WHITE + Colors.BOLD

# universal colors
rd = Colors.RED + Colors.BOLD
yl = Colors.YELLOW + Colors.BOLD
fs = Colors.GOLD3
bd = Colors.BOLD
gn = Colors.BRIGHT_GREEN
title = Colors.BRIGHT_WHITE + Colors.BOLD
bbc = bd + Colors.BRIGHT_CYAN
frame = gn + bd
btext = text + Colors.BOLD
bwt = Colors.BRIGHT_WHITE
bdwt = Colors.BOLD + Colors.BRIGHT_WHITE
ub = Colors.UNBOLD
rst = cm.rst

# globals
container = []
config_dir = local_config['CONFIG']['CONFIG_PATH']
expath = local_config['EXCLUSIONS']['EX_EXT_PATH']
div = text + '/' + rst
div_len = 2
horiz = text + '-' + rst
arrow = bwt + '-> ' + rst
BUFFER = local_config['PROJECT']['BUFFER']


def _configure():
    """
        Add exclusions and update runtime constants

    Returns:
        Success | Failure, TYPE: bool
    """
    try:
        # clear screen
        os.system('cls' if os.name == 'nt' else 'clear')
        display_exclusions()

        with open(expath) as f1:
            exclusions = [x.strip() for x in f1.readlines()]

        # query user input for new exclusions
        response = input('  Enter file extension types to be excluded separated by commas [quit]: ')

        if not response:
            sys.exit(exit_codes['EX_OK']['Code'])
        else:
            add_list = response.split(',')

            # add new extensions to existing
            exclusions.extend(['.' + x for x in add_list if '.' not in x])

            # write out new exclusions config file
            with open(expath, 'w') as f2:
                f2.writelines([x + '\n' for x in exclusions])

            display_exclusions()    # display resulting exclusions set
            return True
    except OSError:
        stdout_message(
            message='Unable to modify local config file located at {}'.format(expath),
            prefix='WARN')
        return False


def display_exclusions():
    """
    Show list of all file type extensions which are excluded
    from line total calculations
    """
    msg = f'{expath} not found.  Run $ {PACKAGE} --configure'
    tab = '\t'.expandtabs(15)

    # numbering
    div = cm.bpl + ')' + rst

    try:

        if os.path.exists(expath):
            with open(expath) as f1:
                exclusions = [x.strip() for x in f1.readlines()]

        stdout_message(message='File types excluded from line totals:')

        for index, ext in enumerate(exclusions):
            print('{}{:>3}{}'.format(tab, index + 1, div + ':  ' + ext))

        sys.stdout.write('\n')
        return True

    except OSError as e:
        stdout_message(message=f'Error: {e}. ' + msg, prefix='WARN')
        return False


def sp_linecount(path, exclusions):
    """Single process line count"""
    p = path
    try:
        if os.path.isfile(path):
            return remove_illegal([path], exclusions)

        elif os.path.isdir(path):
            d = locate_fileobjects(path)
            valid_paths = remove_illegal(d, exclusions)
            return valid_paths
            #for p in valid_paths:
            #    print_reportline({p: linecount(p)})
    except UnicodeDecodeError:
        pass


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
    tab = '\t'.expandtabs(22)
    print(
        Colors.BOLD + '\n' + tab + PACKAGE + Colors.RESET +
        ' help contents'
        )
    print(menu_body)
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

    for i in parameters:
        try:
            paths = sp_linecount(i, exclusions.types)
            width = mp.calc_maxpath(paths)
        except TypeError:
            stdout_message(message='Provided path appears to be invalid', prefix='WARN')
            sys.exit(0)
    return width


class MaxWidth():
    def __init__(self):
        self.buffer = local_config['PROJECT']['COUNT_COLUMN_WIDTH'] + BUFFER
        self.term_width = os.get_terminal_size().columns - self.buffer
        self.max_width = 0

    def calc_maxpath(self, path_list):
        for path in path_list:
            if len(path) > self.max_width:
                self.max_width = len(path)
            if len(path) > self.term_width:
                break
        return self.max_width if self.max_width < self.term_width else self.term_width


def options(parser, help_menu=False):
    """
    Summary:
        parse cli parameter options
    Returns:
        TYPE: argparse object, parser argument set
    """
    parser.add_argument("-e", "--exclusions", dest='exclusions', action='store_true', required=False)
    parser.add_argument("-C", "--configure", dest='configure', action='store_true', required=False)
    parser.add_argument("-d", "--debug", dest='debug', action='store_true', default=False, required=False)
    parser.add_argument("-h", "--help", dest='help', action='store_true', required=False)
    parser.add_argument("-m", "--multiprocess", dest='multiprocess', default=False, action='store_true', required=False)
    parser.add_argument("-s", "--sum", dest='sum', nargs='*', default=os.getcwd(), required=False)
    parser.add_argument("-w", "--whitespace", dest='whitespace', action='store_false', default=True, required=False)
    parser.add_argument("-V", "--version", dest='version', action='store_true', required=False)
    return parser.parse_known_args()


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


def print_header(w):
    total_width = w + local_config['PROJECT']['COUNT_COLUMN_WIDTH']
    header_lhs = 'object'
    header_rhs = 'line count'
    tab = '\t'.expandtabs(total_width - len(header_lhs) - len(header_rhs))
    tab4 = '\t'.expandtabs(4)
    print(tab4 + (horiz * (total_width)))
    print(f'{tab4}{header_lhs}{tab}{header_rhs}')
    print(tab4 + (horiz * (total_width)))


def print_footer(total, object_count, w):
    total_width = w + local_config['PROJECT']['COUNT_COLUMN_WIDTH']

    # add commas
    total_lines = '{:,}'.format(object_count)

    # calc dimensions; no color codes
    msg = 'Total ({} objects):'.format(total_lines)
    tab = '\t'.expandtabs(total_width - len(msg) - len(str(total)) - 1)

    # redefine with color codes added
    msg = f'Total ({title + "{:,}".format(object_count) + rst} objects):'
    tab4 = '\t'.expandtabs(4)

    # divider pattern
    print(tab4 + (horiz * (total_width)))

    # ending summary stats line
    print(f'{tab4}{msg}{tab}{bd + "{:,}".format(total) + rst:>6}' + '\n')


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


def init_cli():

    parser = argparse.ArgumentParser(add_help=False)

    try:
        args, unknown = options(parser)
    except Exception as e:
        help_menu()
        stdout_message(str(e), 'ERROR')
        sys.exit(exit_codes['E_BADARG']['Code'])

    if len(sys.argv) == 1:
        help_menu()
        sys.exit(exit_codes['EX_OK']['Code'])

    elif len(sys.argv) == 2 and (sys.argv[1] != '.'):
        help_menu()
        sys.exit(exit_codes['EX_OK']['Code'])

    elif args.help:
        help_menu()
        sys.exit(exit_codes['EX_OK']['Code'])

    elif args.version:
        package_version()

    elif args.exclusions:
        display_exclusions()

    elif args.configure:
        _configure()

    elif args.sum and precheck():

        ex = ExcludedTypes(ex_path=str(Path.home()) + '/.config/xlines/exclusions.list')
        container = create_container(args.sum)


        if args.debug:
            print('\nargs.sum:')
            print(args.sum)
            print('\nsys.argv contents:')
            print(sys.argv)
            print(f'\ncontainer is:\n {container}')
            print(f'\nunknown object: {unknown}')
            sys.exit(0)

        if args.multiprocess:
            # --- run with concurrency --
            multiprocessing_main(container, ex, args.debug)

        elif not args.multiprocess:

            io_fail = []
            tcount, tobjects = 0, 0
            width = longest_path(container, ex)

            print_header(width)
            count_width = local_config['PROJECT']['COUNT_COLUMN_WIDTH']
            hicount_threshold = local_config['PROJECT']['COUNT_THRESHOLD']

            for i in container:

                paths = sp_linecount(i, ex.types)

                for path in paths:

                    try:

                        inc = linecount(path, args.whitespace)
                        highlight = cm.accent if inc > hicount_threshold else cm.aqu
                        tcount += inc    # total line count
                        tobjects += 1    # increment total number of objects

                        # truncation
                        lpath = os.path.split(path)[0]
                        fname = os.path.split(path)[1]

                        if width < (len(lpath) + len(fname)):
                            cutoff = (len(lpath) + len(fname)) - width
                        else:
                            cutoff = 0

                        tab = '\t'.expandtabs(width - len(lpath) - len(fname) - count_width + BUFFER)
                        tab4 = '\t'.expandtabs(4)

                        # with color codes added
                        if cutoff == 0:
                            lpath = text + lpath + rst
                        else:
                            lpath = os.path.split(path)[0][:cutoff] + arrow

                        fname = highlight + fname + rst

                        # incremental count formatting
                        ct_format = acct if inc > hicount_threshold else bwt

                        # format tabular line totals with commas
                        output_str = f'{tab4}{lpath}{div}{fname}{tab}{ct_format}{"{:,}".format(inc):>7}{rst}'
                        print(output_str)

                    except Exception:
                        io_fail.append(path)
                        continue

            print_footer(tcount, tobjects, width)

            if args.debug:
                tab4 = '\t'.expandtabs(4)
                print('\n' + tab4 + 'Skipped file objects:\n' + tab4 + ('-' * (width + count_width)))
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
