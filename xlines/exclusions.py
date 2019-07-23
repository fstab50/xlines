"""
Summary.

    Exclusions Module -- Display, Update, and Modification
    of objects to be excluded from line count totals

"""

import os
import inspect
from shutil import copy2 as copyfile
from xlines.statics import local_config
from xlines import logger

module = os.path.basename(__file__)
library_location = os.path.split(module)[0]
types_fname = local_config['EXCLUSIONS']['EX_FILENAME']
dirs_fname = local_config['EXCLUSIONS']['EX_DIR_FILENAME']
excluded_types = os.path.join(library_location, types_fname)
excluded_dirs = os.path.join(library_location, dirs_fname)
config_location = local_config['CONFIG']['CONFIG_DIR']


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


class ProcessExclusions():
    """
        Class definition for reading excluded file types from a
        configuration file if exists.

    Use:
        >>> ex = ProcessExclusions()
        >>> ex.get_exclusions('/path/to/configuration/file')
        >>> ['.docx', '.pptx', '.png', '.tiff']

    Returns:
        exclusions (list) |  [] (empty) and creates new config
        file if not found

    """
    def __init__(self, path):
        """
        Args:
            :path (str): filesystem path to file object for parsing

        """
        self.path = path
        self.basedir = os.path.dirname(path)
        self.exclusions = self.process_exclusions(path)

    def process_exclusions(self, path=None):
        """
        Read and parse local config file if exists
        """
        if (os.path.exists(self.path) if path is None else os.path.exists(path)):
            try:
                with open(path) as f1:
                    return [x.strip() for x in f1.readlines()]
            except OSError:
                logger.info(f'path provided does not yet exist -- creating path')
        return self._touch(self.path) if path is None else self._touch(path)

    def _touch(self, path):
        """If not exist, create new filesystem object"""
        if not os.path.exists(path):
            os.makedirs(path)
            # self._create_ex_types(path)
            # self._create_ex_dirs(path)
        return self.process_exclusions(os.path.join(config_location, types_fname))

    def _create_ex_types(self, path):
        """Create excluded file types file via reference"""
        copyfile(excluded_types, os.path.join(config_location, types_fname))

    def _create_ex_dirfile(self, path):
        """Create excluded file types file via reference"""
        copyfile(excluded_dirs, os.path.join(config_location, dirs_fname))
