#!/usr/bin/env python3

from xlines import Colors
from xlines.variables import *


c = Colors()

ACCENT = c.ORANGE               # orange accent highlight color
bdacct = c.BRIGHT_GREEN + c.BOLD      # bold orange
bdcy = c.CYAN + c.BOLD          # bold blue
lbrct = bbc + '[ ' + rst        # left bracket
rbrct = bbc + ' ]' + rst        # right bracket
vdiv = bbc + ' | ' + rst
tab = '\t'.expandtabs(24)
tab6 = '\t'.expandtabs(8).encode('utf-8')


width = 55      # legend overall width

legend = [
        bdcy + ' o' + rst + '  |  Filesystem object counted (' + bcy + 'cyan' + rst + ')',
        bdacct + ' o' + rst + '  |  Line count above high ct threshold (' + bdacct + 'green' + rst + ')',
        bwt + '->' + rst + '  |  Truncated (shortened) file path (' + bwt + 'white' + rst + ')'
    ]

res = [

    ('┌' + '─' * width + '┐').encode('utf-8')

]

fallback = """
             """ + bbl + 'o' + rst + """  |  Filesystem object counted (""" + bcy + 'cyan' + rst + """)
           --------------------------------------------------------
             """ + bdacct + 'o' + rst + """  |  Line count above high ct threshold (""" + acct + 'orange' + rst + """)
           --------------------------------------------------------
            """ + bwt + '->' + rst + """  |  Truncated (shortened) file path (""" + bwt + 'white' + rst + """)       
"""


def _map(index, content):
    return {
        0: ('│  ' + content + (' ' * int(width - 43)) + '  │').encode('utf-8'),
        1: ('│  ' + content + (' ' * int(width - 53)) + '  │').encode('utf-8'),
        2: ('│  ' + content + (' ' * int(width - 50)) + '  │').encode('utf-8')
    }.get(index)


def border_map(text_list=legend):
    """
        Render help menu legend using dict lookup module function

    Returns:
        decoded utf-8 characters printed to stdout

    """
    for index, s in enumerate(text_list):
        res.append(_map(index, s))
    res.append(('└' + '─' * width + '┘').encode('utf-8'))

    try:

        return [print((tab6 + x).decode('utf-8')) for x in res]

    except UnicodeEncodeError:
        # if problems handling unicode encoding
        #[print('\t'.expandtabs(10) + x) for x in text_list][0]
        print(fallback)


def border_list(text_list=legend):
    """
        Original working version of help menu legend

    Returns:
        decoded utf-8 characters printed to stdout

    """
    for index, s in enumerate(text_list):
        if index == 0:
            res.append(('│  ' + s + (' ' * int(width - 43)) + '  │').encode('utf-8'))
        if index == 1:
            res.append(('│  ' + s + (' ' * int(width - 53)) + '  │').encode('utf-8'))
        if index == 2:
            res.append(('│  ' + s + (' ' * int(width - 50)) + '  │').encode('utf-8'))

    res.append(('└' + '─' * width + '┘').encode('utf-8'))

    try:

        return [print((tab6 + x).decode('utf-8')) for x in res]

    except UnicodeEncodeError:
        # if problems handling unicode encoding
        [print('\t'.expandtabs(10) + x) for x in text_list][0]
