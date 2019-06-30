"""
Summary.

    Exclusions Module -- Display, Update, and Modification
    of objects to be excluded from line count totals

"""

import inspect
from xlines.statics import local_config
from xlines import logger


class ExcludedTypes():
    """
        Class for processing file type exclusions (exclusions.list)
        File located in local configuration directory (~/.config/xlines)
    """
    def __init__(self, ex_path, ex_container=[]):
        """
        Args:
            ex_path (str): path to exclusions.list file
            ex_container (list): in memory list of all file extensions
                                 to be excluded from line counts
        """
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
            exclusions = local_config['EXCLUSIONS']['EX_EXT_PATH']
            fx = inspect.stack()[0][3]
            logger.exception('{}: Problem parsing file type exclusions ({})'.format(fx, exclusions))
            return []
