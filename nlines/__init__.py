from pyaws import logd
from nlines._version import __version__ as version
from nlines.statics import local_config

__author__ = 'Blake Huber'
__version__ = version
__email__ = "blakeca00@gmail.com"

"""
PACKAGE = 'nlines'
enable_logging = True
log_mode = 'FILE'          # log to cloudwatch logs
log_filename = 'nlines.log'
log_dir = '/tmp'
log_path = log_dir + '/' + log_filename


log_config = {
    "PROJECT": {
        "PACKAGE": PACKAGE,
        "CONFIG_VERSION": __version__,
    },
    "LOGGING": {
        "ENABLE_LOGGING": enable_logging,
        "LOG_FILENAME": log_filename,
        "LOG_DIR": log_dir,
        "LOG_PATH": log_path,
        "LOG_MODE": log_mode,
        "SYSLOG_FILE": False
    }
}
"""
# global logger
logd.local_config = local_config
logger = logd.getLogger(__version__)
