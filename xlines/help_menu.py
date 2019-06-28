"""

Help Menu
    Help menu object containing body of help content.
    For printing with formatting

"""

from xlines.statics import PACKAGE
from xlines import Colors

c = Colors()

ACCENT = c.ORANGE               # orange accent highlight color
wht = c.WHITE          # white only
bdacct = c.ORANGE + c.BOLD      # bold orange
bdbl = c.BLUE + c.BOLD          # bold blue
bdwt = c.WHITE + c.BOLD         # bold white
tab = '\t'.expandtabs(23)

menu_title = '\n' + c.BOLD + tab + PACKAGE + c.RESET + ' help contents'

synopsis_cmd = (
    c.RESET + ACCENT + PACKAGE +
    wht + ' --sum ' + c.RESET + ' <dir1> <dir2> <fname1> <fname2>... '
    )

url_doc = c.URL + 'http://xlines.readthedocs.io' + c.RESET
url_sc = c.URL + 'https://github.com/fstab50/xlines' + c.RESET

menu_body = menu_title + c.BOLD + """

  DESCRIPTION""" + c.RESET + """

            Count lines of text: A utility for all code projects
            Source Code Repo:  """ + url_sc + """
    """ + c.BOLD + """
  SYNOPSIS""" + c.RESET + """

            """ + synopsis_cmd + """

                        -s, --sum
                       [-e, --exclusions ]
                       [-c, --configure  ]
                       [-d, --debug  ]
                       [-h, --help   ]
                       [-m, --multiprocess  ]
                       [-w, --whitespace  ]
                       [-V, --version  ]
    """ + c.BOLD + """
  OPTIONS
        -s, --sum""" + c.RESET + """ (string): Sum the counts of all lines contained
            in filesystem objects referenced in the sum parameter
    """ + c.BOLD + """
        -c, --configure""" + c.RESET + """:  Configure runtime parameter via the cli
            menu. Change display format, color scheme, etc values
    """ + c.BOLD + """
        -d, --debug""" + c.RESET + """: Print out additional debugging information
    """ + c.BOLD + """
        -e, --exclusions""" + c.RESET + """:  Print out list of file type extensions
            and directories excluded from line count calculations
    """ + c.BOLD + """
        -h, --help""" + c.RESET + """: Show this help message and exit
    """ + c.BOLD + """
        -m, --multiprocess""" + c.RESET + """:  Use multiple cpu cores for counting
            lines of text in expansive filesystem directories
    """ + c.BOLD + """
        -w, --whitespace""" + c.RESET + """:  Perform line counts of all filesystem
            objects,  but omit lines containing only whitespace
    """ + c.BOLD + """
        -V, --version""" + c.RESET + """: Print package version and copyright info
    """ + c.BOLD + """
  LEGEND""" + c.RESET + """

          """ + bdbl + 'o' + c.RESET + """  |  Filesystem object counted (""" + bdbl + 'blue' + c.RESET + """)
        ---------------------------------------------------------
          """ + bdacct + 'o' + c.RESET + """  |  Line count above high count threshold (""" + bdacct + 'orange' + c.RESET + """)
        ---------------------------------------------------------
         """ + bdwt + '-->' + c.RESET + """ |  Truncated (shortened) file path (""" + bdwt + 'white' + c.RESET + """)

    """
