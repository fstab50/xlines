"""
Summary.

    Commons Module -- Common Functionality

"""
import os
import json
import inspect
import platform
from pathlib import Path
from xlines import Colors
from xlines import logger
from xlines.statics import local_config


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
rst = Colors.RESET

# globals
container = []
config_dir = local_config['CONFIG']['CONFIG_PATH']
expath = local_config['EXCLUSIONS']['EX_EXT_PATH']
div = text + '/' + rst
div_len = 2
horiz = text + '-' + rst
arrow = bwt + '-> ' + rst
BUFFER = local_config['PROJECT']['BUFFER']


def linecount(path, whitespace=True):
    if whitespace:
        return len(open(path).readlines())
    return len(list(filter(lambda x: x != '\n', open(path).readlines())))


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
    msg = 'Total ({} objects):'.format(str(object_count))
    tab = '\t'.expandtabs(total_width - len(msg) - len(str(total)) - 1)

    # redefine with color codes added
    msg = f'Total ({title + "{:,}".format(object_count) + rst} objects):'
    tab4 = '\t'.expandtabs(4)
    print(tab4 + (horiz * (total_width)))
    print(f'{tab4}{msg}{tab}{bd + "{:,}".format(total) + rst:>6}' + '\n')


def remove_duplicates(duplicates):
    """
    Summary.

        Module function utilsing a generator to remove duplicates
        from large scale lists with minimal resource use

    Args:
        duplicates (list): contains repeated elements

    Returns:
        list object (iter)
    """
    uniq = []

    def dedup(d):
        for element in d:
            if element not in uniq:
                uniq.append(element)
                yield element
    return [x for x in dedup(duplicates)]


def remove_illegal(d, illegal):
    """
        Removes excluded file types

    Args:
        :d (list): list of filesystem paths ending with object
        :illegal (list):  list of file type extensions for ommission

    Returns:
        legal filesystem paths (str)
    """
    def parse_list(path):
        """Reads in list from file object"""
        with open(path) as f1:
            return [x.strip() for x in f1.readlines()]

    bad = []

    try:
        illegal_dirs = parse_list(local_config['EXCLUSIONS']['EX_DIR_PATH'])
    except KeyError:
        illegal_dirs = ['pycache', 'venv']

    for fpath in d:

        # filter for illegal file extensions
        fobject = os.path.split(fpath)[1]
        if ('.' in fobject) and ('.' + fobject.split('.')[1] in illegal):
            bad.append(fpath)

        # filter for illegal dirs
        elif list(filter(lambda x: x in fpath, illegal_dirs)):
            bad.append(fpath)
    return sorted(list(set(d) - set(bad)))


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


def get_os(detailed=False):
    """
    Summary:
        Retrieve local operating system environment characteristics
    Args:
        :user (str): USERNAME, only required when run on windows os
    Returns:
        TYPE: dict object containing key, value pairs describing
        os information
    """
    try:

        os_type = platform.system()

        if os_type == 'Linux':
            os_detail = platform.platform()
            distribution = platform.linux_distribution()[0]
            HOME = str(Path.home())
            username = os.getenv('USER')
        elif os_type == 'Windows':
            os_detail = platform.platform()
            username = os.getenv('username') or os.getenv('USER')
            HOME = 'C:\\Users\\' + username
        else:
            logger.warning('Unsupported OS. No information')
            os_type = 'Java'
            os_detail = 'unknown'
            HOME = os.getenv('HOME')
            username = os.getenv('USER')

    except OSError as e:
        raise e
    except Exception as e:
        logger.exception(
            '%s: problem determining local os environment %s' %
            (inspect.stack()[0][3], str(e))
            )
    if detailed and os_type == 'Linux':
        return {
                'os_type': os_type,
                'os_detail': os_detail,
                'linux_distribution': distribution,
                'username': username,
                'HOME': HOME
            }
    elif detailed:
        return {
                'os_type': os_type,
                'os_detail': os_detail,
                'username': username,
                'HOME': HOME
            }
    return {'os_type': os_type}


def import_file_object(filename):
    """
    Summary:
        Imports block filesystem object
    Args:
        :filename (str): block filesystem object
    Returns:
        dictionary obj (valid json file), file data object
    """
    try:
        handle = open(filename, 'r')
        file_obj = handle.read()
        dict_obj = json.loads(file_obj)

    except OSError as e:
        logger.critical(
            'import_file_object: %s error opening %s' % (str(e), str(filename))
        )
        raise e
    except ValueError:
        logger.info(
            '%s: import_file_object: %s not json. file object returned' %
            (inspect.stack()[0][3], str(filename))
        )
        return file_obj    # reg file, not valid json
    return dict_obj


def read_local_config(cfg):
    """ Parses local config file for override values

    Args:
        :local_file (str):  filename of local config file

    Returns:
        dict object of values contained in local config file
    """
    try:
        if os.path.exists(cfg):
            config = import_file_object(cfg)
            return config
        else:
            logger.warning(
                '%s: local config file (%s) not found, cannot be read' %
                (inspect.stack()[0][3], str(cfg)))
    except OSError as e:
        logger.warning(
            'import_file_object: %s error opening %s' % (str(e), str(cfg))
        )
    return {}


def os_parityPath(path):
    """
    Converts unix paths to correct windows equivalents.
    Unix native paths remain unchanged (no effect)
    """
    path = os.path.normpath(os.path.expanduser(path))
    if path.startswith('\\'):
        return 'C:' + path
    return path


def user_home():
    """Returns os specific home dir for current user"""
    try:
        if platform.system() == 'Linux':
            return os.path.expanduser('~')

        elif platform.system() == 'Windows':
            username = os.getenv('username')
            return 'C:\\Users\\' + username

        elif platform.system() == 'Java':
            print('Unable to determine home dir, unsupported os type')
            sys.exit(1)
    except OSError as e:
        raise e
