"""
Summary.

    Binary file object detection

Use:

    After instantiation, class object can be called repeatly without
    re-initialization of static primitives used for detection

    >>> b = BinaryFile()
    >>> b.detect('/home/stacie/result.png')
    >>> True

"""


class BinaryFile():
    """
    Class for detecting binary encoded file objects
    """
    def __init__(self):
        self.textchars = bytearray({7, 8, 9, 10, 12, 13, 27} | set(range(0x20, 0x100)) - {0x7f})
        self.translate = lambda bytes: bool(bytes.translate(None, self.textchars))

    def detect(self, path):
        """
        Args:
            :path (str): filesystem path to a file object

        Returns:
            True (binary) | False (not-binary), TYPE: bool
        """
        try:

            f = open(path, 'rb').read(1024)
            return self.translate(f)

        except UnicodeDecodeError:
            return True
