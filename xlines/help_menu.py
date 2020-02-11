"""

Help Menu
    Help menu object containing body of help content.
    For printing with formatting

"""

from xlines.statics import PACKAGE
from xlines import Colors
from xlines.variables import acct, bbc, bbl, bcy, bdcy, bdwt, bwt, rst


c = Colors()

ACCENT = c.ORANGE               # orange accent highlight color
bdacct = c.ORANGE + c.BOLD      # bold orange
lbrct = bbc + '[ ' + rst        # left bracket
rbrct = bbc + ' ]' + rst        # right bracket
vdiv = bbc + ' | ' + rst
tab = '\t'.expandtabs(24)

menu_title = '\n' + tab + bdwt + PACKAGE + rst + ' help contents'

synopsis_cmd = (
        rst + ACCENT + PACKAGE + rst + ' --sum <values> ' +
        lbrct + '--no-whitespace' + vdiv + '--multiprocess' + rbrct
    )

url_doc = c.URL + 'http://xlines.readthedocs.io' + rst
url_sc = c.URL + 'https://github.com/fstab50/xlines' + rst


footer = """
       --------------------------------------------------------
       |  """ + bbl + 'o' + rst + """  |  Filesystem object counted (""" + bcy + 'cyan' + rst + """)              |
       --------------------------------------------------------
       |  """ + bdacct + 'o' + rst + """  |  Line count above high ct threshold (""" + acct + 'orange' + rst + """)   |
       --------------------------------------------------------
       | """ + bwt + '->' + rst + """  |  Truncated (shortened) file path (""" + bwt + 'white' + rst + """)       |
       --------------------------------------------------------

  """


menu_body = menu_title + bdwt + """

  DESCRIPTION""" + rst + """

            Count lines of text: A utility for all code projects
            Source Code Repo:  """ + url_sc + """
    """ + bdwt + """
  SYNOPSIS""" + rst + """

        $ """ + synopsis_cmd + """

                        -s, --sum
                       [-e, --exclusions ]
                       [-c, --configure  ]
                       [-d, --debug  ]
                       [-h, --help   ]
                       [-m, --multiprocess  ]
                       [-n, --no-whitespace  ]
                       [-V, --version  ]
    """ + bdwt + """
  OPTIONS
        -s, --sum""" + rst + """ (string): Sum the counts of all lines contained
            in filesystem objects referenced in the sum parameter
    """ + bdwt + """
        -c, --configure""" + rst + """:  Configure runtime parameter via the cli
            menu. Change display format, color scheme, etc values
    """ + bdwt + """
        -d, --debug""" + rst + """:  Print out additional  debugging information
    """ + bdwt + """
        -e, --exclude""" + rst + """: Objects to be excluded from the line count
    """ + bdwt + """
        -l, --list-exclusions""" + rst + """: Print list of file type extensions
            and directories excluded from line count calculations
    """ + bdwt + """
        -h, --help""" + rst + """: Show this help message, symbol legend, & exit
    """ + bdwt + """
        -m, --multiprocess""" + rst + """:  Use multiple  cpu cores for counting
            lines of text in expansive filesystem directories
    """ + bdwt + """
        -w, --no-whitespace""" + rst + """:  Exclude lines containing whitespace
            from total line counts for all objects
    """ + bdwt + """
        -V, --version""" + rst + """:  Print package version  and copyright info
    """ + bdwt + """
  LEGEND""" + rst
