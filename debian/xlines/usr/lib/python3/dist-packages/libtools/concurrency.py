"""
Summary.

    Parallel processing module

"""
import multiprocessing
from multiprocessing.dummy import Pool
from libtools import logger


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


def assemble_args(container, process_ct):
    """
    Summary.

        Assumbles pool args for multiprocessing

    Args:
        :container (list):  list containing multiple elements
        :process_ct (int): number of concurrent processes
    Returns:
        pool_args (list) for use in multiprocessing array

    """
    pool_args = []
    for x in split_list(container, process_ct):
        pool_args.append(x)
    return pool_args


def process(input_list, function_object, count):
    with Pool(processes=count) as pool:
        pool.starmap(function_object, assemble_args(input_list))
