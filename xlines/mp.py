"""
Summary.

    Multiprocessing module for line count

Module Functions:


"""
import os
import multiprocessing
import inspect
from xlines.usermessage import stdout_message
from xlines import Colors
from xlines.core import BUFFER, acct, bwt, text, rst, arrow, div
from xlines.core import linecount, print_header, print_footer
from xlines.export import export_json_object
from xlines import local_config, logger
from xlines.variables import *


def cpu_cores(logical=True):
    """
        Finds number of physical and logical cores on machine
        Defaults to logical cores unless logical set to False

    Returns:
        # of logical cores (int) || physical cores (int)

    """
    physical_cores = multiprocessing.cpu_count()
    return len(os.sched_getaffinity(0)) if logical else physical_cores


def longest_path_mp(object_list):
    """
        Multiprocessing version of longest_path() module function. Sorts a
        list of dict by a key value (path) in order of descending length. Allows
        easy extraction of the longest path in position [0] dict in the list.

    Args:
        :object_list (list):  Format:
            [
                {
                    'path': '/var/lib/dpkg/info/xtrans-dev.list',
                    'count': 531
                },
                {
                    'path': '/var/lib/dpkg/transitive.list',
                    'count': 249
                },
            ]

    Returns:
        longest path (int)

    """
    s = sorted(object_list, key=lambda x: len(x['path']), reverse=True)
    return len(s[0]['path'])


def mp_linecount(path_list, exclusions, no_whitespace):
    """Multiprocessing line count"""
    for path in path_list:
        try:
            if os.path.isfile(path):

                path_value = os.path.abspath(path) if path.startswith('/') else ('./' + os.path.relpath(path))

                q.put(
                        {
                            'path': path_value,
                            'count': linecount(path, no_whitespace)
                        }
                    )

            elif os.path.isdir(path):
                for p in [os.path.join(path, x) for x in os.listdir(path)]:
                    q.put({'path': p, 'count': linecount(p, no_whitespace)})

        except UnicodeDecodeError:
            continue


def print_results(object_list, _ct_threshold, width):
    """
        Outputs paths and filesystem objects to which line counts
        were calculated.  Single process operation combines output
        from multiprocessing count by recombining lists of dict
        processed separately by each cpu core

    Args:
        :object_list (list):  Format:

        .. code: json

            [
                {
                    'path': '/var/lib/dpkg/info/xtrans-dev.list',
                    'count': 531
                },
                {
                    'path': '/var/lib/dpkg/transitive.list',
                    'count': 249
                },
            ]

        :_ct_threshold (int): path rec highlight color if object linecount
            is at or above this threshold
        :width (int): width in characters of the output pattern

    Returns:
        True | False, TYPE: bool

    """
    tcount, tobjects = 0, 0
    io_fail = []

    print_header(width)
    count_width = local_config['OUTPUT']['COUNT_COLUMN_WIDTH']

    for object_dict in sorted(object_list, key=lambda x: x['path']):

        try:
            path = object_dict['path']
            inc = object_dict['count']
            highlight = acct if inc > _ct_threshold else Colors.AQUA
            tcount += inc    # total line count
            tobjects += 1    # increment total number of objects

            # truncation
            lpath, fname = os.path.split(path)

            if (len(path) + BUFFER * 2) > width:
                cutoff = (len(path) + BUFFER * 2) - width
            else:
                cutoff = 0

            tab = '\t'.expandtabs(width - len(lpath) - len(fname) - count_width + BUFFER)
            tab4 = '\t'.expandtabs(4)

            # with color codes added
            if cutoff == 0:
                lpath = text + lpath + rst
            else:
                lpath = text + os.path.split(path)[0][:len(lpath) - cutoff - BUFFER] + rst + arrow
                tab = '\t'.expandtabs(width - len(lpath) - len(fname) + count_width + BUFFER + cut_corr)

            fname = highlight + fname + rst

            # incremental count formatting
            ct_format = acct if inc > _ct_threshold else bwt

            output_str = f'{tab4}{lpath}{div}{fname}{tab}{ct_format}{"{:,}".format(inc):>10}{rst}'
            print(output_str)
        except Exception:
            io_fail.append(path)
            continue

    print_footer(tcount, tobjects, width)
    return True


def split_list(mlist, n):
    """
    Summary.

        splits a list into equal parts as allowed, given n segments

    Args:
        :mlist (list):  a single list containing multiple elements
        :n (int):  Number of segments in which to split the list

    Returns:
        generator object

    """
    k, m = divmod(len(mlist), n)
    return (mlist[i * k + min(i, m):(i + 1) * k + min(i + 1, m)] for i in range(n))


def get_varname(var):
    callers_local_vars = inspect.currentframe().f_back.f_locals.items()
    return [var_name for var_name, var_val in callers_local_vars if var_val is var]


def multiprocessing_main(valid_paths, max_width, _threshold, wspace, exclusions, debug):
    """
        Execute Operations using concurrency (multi-process) model

    Args:
        :valid_paths (list): list of filesystem paths (str) filtered for binary,
            other uncountable objects
        :max_width (int): width of output pattern, sans line count total column
        :_threshold (int): high line count threshold value (highlighted objects)
        :wspace (bool): when True, omit whitespace lines from count (DEFAULT:  False)
        :exclusions (ex object): instance of ExcludedTypes
        :debug (boot): debug flag

    """
    def debug_messages(flag, paths):
        if flag:
            stdout_message('Objects contained in container directories:', prefix='DEBUG')
            for i in paths:
                print(i)

    def queue_generator(q, p):
        """Generator which offloads a queue before full"""
        while p.is_alive():
            p.join(timeout=1)
            while not q.empty():
                yield q.get(block=False)

    global q
    q = multiprocessing.Queue()
    processes, results = [], []
    debug_messages(debug, valid_paths)

    # maximum cores is 4 due to i/o contention single drive systems
    cores = 4 if cpu_cores() >= 4 else cpu_cores()
    equal_lists = [sorted(x) for x in split_list(valid_paths, cores)]

    for i in equal_lists:
        t = multiprocessing.Process(target=mp_linecount, args=(i, exclusions.types, wspace))
        processes.append(t)
        t.start()

        results.extend([x for x in queue_generator(q, t)])

        if debug:
            print('Completed: list {}'.format(get_varname(i)))    # show progress

    print_results(results, _threshold, max_width)

    if debug:
        export_json_object(results, logging=False)
        stdout_message(message='Num of objects: {}'.format(len(results)))
    return 0
