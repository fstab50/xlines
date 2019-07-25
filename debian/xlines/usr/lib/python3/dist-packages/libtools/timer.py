"""
Summary:
    - Timer class for measuring duration
    - Python3

Module Functions:
    - None

Classes:
    - TimeDuration: Measures elapsed time duration (seconds).
      User configurable precision level

"""
import time
import inspect
from libtools import logger


class TimeDuration():
    """
        Timer class; accuracy to 100th of a second (default, user changeable)

    Instantiation:
        >>>  td = TimeDuration(accuracy=2)
        >>>  s_time = td.start()
        >>>  e_time = td.end()
        >>>  print(e_time)

        $ 31.29    #  seconds
    """
    def __init__(self, accuracy=2):
        """
        Args:
            :accuracy (int): precision, number of decimal places.
                Default is hundreds of a second (two decimal places, 1.00 seconds)
        """
        self.start_time = None
        self.end_time = None
        self.precision = accuracy

    def start(self):
        """
        Summary:
            Mark point in time where timer begins duration

        Returns:
            datetime representation; self.start_time stored internally as epoch seconds
        """
        self.start_time = time.time()
        return self.__repr__()

    def __repr__(self):
        return time.strftime('%H:%M:%S', time.localtime(self.start_time))

    def end(self):
        """
        Summary:
            Mark point in time where timer ends duration

        Returns:
            elapsed time in seconds with precision, TYPE: int
            Mark point datetime representation stored in self.end_time, TYPE: datetime
        """
        try:
            end_time = time.time()
            duration = end_time - self.start_time
            self.end_time = time.strftime('%H:%M:%S', time.localtime(end_time))
        except Exception as e:
            logger.exception(
                '%s: Unknown error when calculating end time (Code: %s)' %
                (inspect.stack()[0][3], str(e)))
            return 0.00
        return round(duration, self.precision)
