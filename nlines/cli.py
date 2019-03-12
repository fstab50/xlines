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
from multiprocessing.dummy import Pool
from pyaws.utils import export_json_object
from pyaws.script_utils import import_file_object, read_local_config
from pyaws.utils import stdout_message
from pyaws.colors import Colors
from nlines.statics import PACKAGE, CONFIG_SCRIPT, local_config
from nlines.help_menu import menu_body
from nlines import about, __version__

try:
    from pyaws.oscodes_unix import exit_codes
    os_type = 'Linux'
    user_home = os.getenv('HOME')
    splitchar = '/'                             # character for splitting paths (linux)
    ACCENT = Colors.ORANGE
    TEXT = Colors.LT2GRAY
    TITLE = Colors.WHITE + Colors.BOLD
except Exception:
    from gitsane.oscodes_win import exit_codes    # non-specific os-safe codes
    os_type = 'Windows'
    user_home = os.getenv('username')
    splitchar = '\\'                            # character for splitting paths (windows)
    ACCENT = Colors.CYAN
    TEXT = Colors.LT2GRAY
    TITLE = Colors.WHITE + Colors.BOLD


# globals
logger = logd.getLogger(__version__)
container = []
excluded_dirs = ['.git', 'venv', 'p3_venv']
excluded_filetypes = ['.docx', '.png', '.tiff', '.pptx', '.xlsx', '.jpg']


def build_index(root):
    """
    Summary:
        - Operation to index local git repositories
        - Create index in the form of json configuration file
        - Returns object containing list of dictionaries, 1 per
          git repository
    Args:
    Returns:
        - index, TYPE: list
        - Format:

         .. code-block:: json

                [
                    {
                        "location": fullpath-including-repository,
                        "path":  path-to-repository (not incl repo),
                        "repository": repository git remote string
                    }
                ]

    """
    index = []
    for path in locate_repositories(root):
        index.append(
            {
                "location": path,
                "path": '/'.join(path.split('/')[:-1]),
                "repository": source_url(path)
            }
        )
    return index


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


def dedup(duplicates):
    uniq = []
    for i in duplicates:
        if i not in uniq:
            uniq.append(i)
    return uniq


class ExcludedTypes():
    def __init__(self, ex_container=[]):
        self.ex_container = ex_container
        if not self.ex_container:
            self.ex_container.extend(excluded_dirs)
            self.ex_container.extend(excluded_filetypes)

    def excluded(self, path):
        for i in self.ex_container:
            if i in path:
                return True
        return False


def locate_fileobjects(origin):
    """
    Summary:
        Walks local fs directories identifying all git repositories
    Returns:
        paths, TYPE: list
    """
    fobjects = []
    ex = ExcludedTypes()

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
    return dedup(fobjects)


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


def option_configure(debug=False, path=None):
    """
    Summary:
        Initiate configuration menu to customize keyup runtime options.
        Console script ```keyconfig``` invokes this option_configure directly
        in debug mode to display the contents of the local config file (if exists)
    Args:
        :path (str): full path to default local configuration file location
        :debug (bool): debug flag, when True prints out contents of local
         config file
    Returns:
        TYPE (bool):  Configuration Success | Failure
    """
    if CONFIG_SCRIPT in sys.argv[0]:
        debug = True    # set debug mode if invoked from CONFIG_SCRIPT
    if path is None:
        path = local_config['PROJECT']['CONFIG_PATH']
    if debug:
        if os.path.isfile(path):
            debug_mode('local_config file: ', local_config, debug, halt=True)
        else:
            msg = """  Local config file does not yet exist. Run:

            $ keyup --configure """
            debug_mode(msg, {'CONFIG_PATH': path}, debug, halt=True)
    r = configuration.init(debug, path)
    return r


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
    parser.add_argument("-r", "--create-repos", dest='create', type=str, required=False)
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

    elif args.configure:
        r = option_configure(args.debug, local_config['PROJECT']['CONFIG_PATH'])
        return r

    else:
        if precheck():
            count = 0
            path_list = locate_fileobjects('.')

            # --- run with concurrency ---

            pool_args = []

            # prepare args
            for path in path_list:
                count = count + linecount(path)
                pool_args.append((path))

                # run instance of main with each item set in separate thread
                # Future: Needs a return status from pool object for each process
            with Pool(processes=8) as pool:
                pool.starmap(linecount, pool_args)



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
