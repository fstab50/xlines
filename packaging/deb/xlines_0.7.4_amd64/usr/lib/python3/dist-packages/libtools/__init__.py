"""
Tools & Utilities Module
"""

import os

# color formatting
from libtools.colors import Colors
from libtools.colors import ColorMap, ColorAttributes

# logging
from libtools._version import __version__ as version
from libtools import logd


__author__ = 'Blake Huber'
__version__ = version
__credits__ = []
__license__ = "GPL-3.0"
__maintainer__ = "Blake Huber"
__email__ = "blakeca00@gmail.com"
__status__ = "Development"


try:

    # Linux
    from libtools.oscodes_unix import exit_codes

except Exception:
    # windows
    from libtools.oscodes_win import exit_codes


# shared, global logger object
logger = logd.getLogger(__version__)

# dependendent imports below this line
from libtools.userinput import bool_convert, bool_assignment, ascii_lowercase
from libtools.userinput import range_test, range_bind, userchoice_mapping
from libtools.time import convert_strtime_datetime, TimeDelta, convert_timedelta, convert_dt_human
from libtools.timer import TimeDuration
from libtools.usermessage import stdout_message
from libtools.concurrency import split_list
from libtools.progress import screen_dimensions, progress_meter
