"""

Help Menu
    Help menu object containing body of help content.
    For printing with formatting

"""

from gitsane.statics import PACKAGE, CONFIG_SCRIPT
from gitsane.colors import Colors


PKG_ACCENT = Colors.ORANGE
PARAM_ACCENT = Colors.WHITE


synopsis_cmd = (
    Colors.RESET + PKG_ACCENT + PACKAGE +
    PARAM_ACCENT + ' --profile ' + Colors.RESET + ' [PROFILE] ' +
    PARAM_ACCENT + '--operation ' + Colors.RESET + '[OPERATION]'
    )

url_doc = Colors.URL + 'http://gitsane.readthedocs.io' + Colors.RESET
url_sc = Colors.URL + 'https://github.com/fstab50/gitsane' + Colors.RESET

menu_body = Colors.BOLD + """
  DESCRIPTION""" + Colors.RESET + """
            Manage local git repositories en mass

            Documentation:  """ + url_doc + """
            Source Code:  """ + url_sc + """
    """ + Colors.BOLD + """
  SYNOPSIS""" + Colors.RESET + """
                """ + synopsis_cmd + """

                    -u, --update <value>
                    -c, --create <value>
                   [-i, --index    <value> ]
                   [-q, --quiet     ]
                   [-c, --configure]
                   [-V, --version  ]
                   [-d, --debug    ]
                   [-h, --help     ]
    """ + Colors.BOLD + """
  OPTIONS
        -i, --index""" + Colors.RESET + """ (string) : Discover local git repos and
        exit. Does not update any repositories
        -u, --update""" + Colors.RESET + """ (string) : Discover and update all local
        git repositories
        -c, --create <value>""" + Colors.RESET + """ (string) : Duplicates the repositories
        and filesystem structure described in configuration file provided as a
        parameter.
    """ + Colors.BOLD + """
        -o, --operation""" + Colors.RESET + """ (string) : Operation to be conducted on the access key
            of the IAM user noted by the PROFILE value. There are 2 operations:

                Valid Operations: {list, update}

                    - list       : List keys and key metadata
                    - up         : Rotate keys by creating new keys, install
                                   keys, then delete deprecated keyset

                    Default: """ + Colors.BOLD + 'list' + Colors.RESET + """
    """ + Colors.BOLD + """
        -q, --quiet""" + Colors.RESET + """ : Suppress output to stdout when """ + PACKAGE + """ triggered via a
            scheduler such as cron or other automated means to update git repo-
            sitories in the background
    """ + Colors.BOLD + """
        -c, --configure""" + Colors.RESET + """ :  Configure parameters to custom values.  If the local
            config file does not exist, option writes a new local configuration
            file to disk.  If file exists, overwrites existing config with up-
            dated values.

               Configure runtime options:   |   Display local config file:
                                            |
                  $ """ + PKG_ACCENT + PACKAGE + PARAM_ACCENT + ' --configure' + Colors.RESET + """     |       $ """ + PKG_ACCENT + CONFIG_SCRIPT + PARAM_ACCENT + """
    """ + Colors.BOLD + """
        -d, --debug""" + Colors.RESET + """ : when True, do not write to the local awscli configuration
            file(s). Instead, write to a temporary location for testing the int-
            grity of the credentials file format that is written to disk.
    """ + Colors.BOLD + """
        -V, --version""" + Colors.RESET + """ : Print package version
    """ + Colors.BOLD + """
        -h, --help""" + Colors.RESET + """ : Show this help message and exit

    """
