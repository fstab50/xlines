from core._version import __version__ as version
from pyaws import logd

__author__ = 'Blake Huber'
__version__ = version
__email__ = "blake.huber@atos.net"

PACKAGE = 'core'
enable_logging = True
log_mode = 'STREAM'          # log to cloudwatch logs
log_filename = ''
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

# global logger
logd.local_config = log_config
logger = logd.getLogger(__version__)
