"""
Summary.

    Multiprocessing module for line count

Module Functions:


"""
import os
import multiprocessing
from xlines.usermessage import stdout_message
from xlines import Colors
from xlines.core import BUFFER, acct, bwt, text, rst, arrow, div
from xlines.core import linecount, print_header, print_footer
from xlines.export import export_json_object
from xlines import local_config, logger


def cpu_cores(logical=True):
    """
        Finds number of physical and logical cores on machine
        Defaults to logical cores unless logical set to False

    Returns:
        # of logical cores (int) || physical cores (int)
    """
    physical_cores = multiprocessing.cpu_count()
    if logical:
        return len(os.sched_getaffinity(0))
    return physical_cores


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
                q.put(
                        {
                            'path': os.path.abspath(path),
                            'count': linecount(path, no_whitespace)
                        }
                    )

            elif os.path.isdir(path):
                for p in [os.path.join(path, x) for x in os.listdir(path)]:
                    q.put({'path': p, 'count': linecount(p, no_whitespace)})
        except UnicodeDecodeError:
            continue


def print_results(object_list, width):
    """

        Outputs paths and filesystem objects to which line counts
        were calculated.  Single process operation combines output
        from multiprocessing count by recombining lists of dict
        processed separately by each cpu core

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
        :width (int): width in characters of the output pattern

    Returns:
        True
    """
    tcount, tobjects = 0, 0
    io_fail = []
    #width = longest_path_mp(object_list)

    print_header(width)
    count_width = local_config['OUTPUT']['COUNT_COLUMN_WIDTH']
    hicount_threshold = local_config['OUTPUT']['COUNT_HI_THRESHOLD']

    for object_dict in sorted(object_list, key=lambda x: x['path']):

        try:
            path = object_dict['path']
            inc = object_dict['count']
            highlight = acct if inc > hicount_threshold else Colors.AQUA
            tcount += inc    # total line count
            tobjects += 1    # increment total number of objects

            # truncation
            lpath = os.path.split(path)[0]
            fname = os.path.split(path)[1]

            if (len(lpath) + len(fname) + BUFFER * 2) > width:
                cutoff = (len(lpath) + len(fname) + BUFFER * 2) - width
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
            ct_format = acct if inc > hicount_threshold else bwt

            output_str = f'{tab4}{lpath}{div}{fname}{tab}{ct_format}{"{:,}".format(inc):>10}{rst}'
            print(output_str)
        except Exception:
            io_fail.append(path)
            continue

    print_footer(tcount, tobjects, width)
    return True


def split_list(monolith, n):
    """
    Summary.

        splits a list into equal parts as allowed, given n segments

    Args:
        :monolith (list):  a single list containing multiple elements
        :n (int):  Number of segments in which to split the list

    Returns:
        generator object

    """
    k, m = divmod(len(monolith), n)
    return (monolith[i * k + min(i, m):(i + 1) * k + min(i + 1, m)] for i in range(n))


def multiprocessing_main(valid_paths, max_width, wspace, exclusions, debug):
    """
        Execute Operations using concurrency (multi-process) model

    Args:
        :valid_paths (list): list of filesystem paths (str) filtered for binary,
            other uncountable objects
        :max_width (int): width of output pattern, sans line count total column
        :wspace (bool): when True, omit whitespace lines from count (DEFAULT:  False)
        :exclusions (ex object): instance of ExcludedTypes
        :debug (boot): debug flag

    """
    def deconstruct(alist):
        """Creates list of subdirs in all top-level directories"""
        d_list = []
        for i in alist:
            if os.path.isdir(i):
                d_list.extend([os.path.join(i, x) for x in os.listdir(i)])
            else:
                d_list.append(i)
        return d_list

    def queue_generator(q, p):
        while p.is_alive():
            p.join(timeout=1)
            while not q.empty():
                yield q.get(block=False)

    if debug:
        stdout_message('Objects contained in container directories:', prefix='DEBUG')
        for i in valid_paths:
            print(i)

    global q
    q = multiprocessing.Queue()

    cores = 4
    a, b, c, d = sorted([x for x in split_list(valid_paths, cores)])

    processes, results = [], []
    for i in (a, b, c, d):
        t = multiprocessing.Process(target=mp_linecount, args=(i, exclusions.types, wspace))
        processes.append(t)
        t.start()

        for result in queue_generator(q, t):
            results.append(result)

    print_results(results, max_width)

    if debug:
        export_json_object(results, logging=False)
        stdout_message(message='Num of objects: {}'.format(len(results)))
    return 0
