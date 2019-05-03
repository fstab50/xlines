"""
Summary.

    Multiprocessing module for line count

Module Functions:


"""
import os
import multiprocessing
from multiprocessing import Queue
from xlines.cli import linecount, locate_fileobjects, remove_illegal, BUFFER, acct, text, rst
from xlines.cli import print_header, print_footer
from xlines.cli import BUFFER, acct, bwt, text, rst, arrow, div
from xlines.statics import local_config
from pyaws.utils import stdout_message, export_json_object
from pyaws.colors import Colors


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
