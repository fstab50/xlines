"""
Summary.

    Multiprocessing module for line count

Module Functions:


"""
import os
import multiprocessing
from multiprocessing import Queue
from pyaws.utils import stdout_message, export_json_object
from pyaws.colors import Colors
from xlines.common import BUFFER, acct, bwt, text, rst, arrow, div, horiz
from xlines.statics import local_config
from xlines.common import locate_fileobjects, remove_illegal, linecount


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


def longest_path_mp(paths):
    longest = 0
    for path in paths:
        for key in path.keys():
            if len(key) > longest:
                longest = len(key)
    return longest


def mp_linecount(path, exclusions):
    """Multiprocessing line count"""
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


def print_results(object_list):

    tcount, tobjects = 0, 0
    io_fail = []
    width = longest_path_mp(object_list)

    print_header(width)
    count_width = local_config['PROJECT']['COUNT_COLUMN_WIDTH']
    hicount_threshold = local_config['PROJECT']['COUNT_THRESHOLD']

    for path_dict in object_list:

        try:
            path = path_dict.keys()
            inc = path_dict.value()
            highlight = acct if inc > hicount_threshold else Colors.AQUA
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

            output_str = f'{tab4}{lpath}{div}{fname}{tab}{ct_format}{"{:,}".format(inc):>7}{rst}'
            print(output_str)
        except Exception:
            io_fail.append(path)
            continue


def multiprocessing_main(container, exclusions):
    """Execute Operations using concurrency (multi-process) model"""

    global q
    q = Queue()

    processes = []
    for i in container:
        t = multiprocessing.Process(target=mp_linecount, args=(i, exclusions.types))
        processes.append(t)
        t.start()

    for one_process in processes:
        one_process.join()

    results = []
    while not q.empty():
        results.append(q.get())

    print_results(results)
    export_json_object(results, logging=False)
    stdout_message(message='Num of objects: {}'.format(len(results)))
    return 0
