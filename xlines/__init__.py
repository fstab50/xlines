from pyaws import logd, Colors
from xlines._version import __version__ as version
from xlines.statics import local_config


__author__ = 'Blake Huber'
__version__ = version
__email__ = "blakeca00@gmail.com"


# global logger
logd.local_config = local_config
logger = logd.getLogger(__version__)
