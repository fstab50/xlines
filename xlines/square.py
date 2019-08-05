"""
Summary:
    Module utilising unicode characters to create
    a help menu legend surrounded by a border

Module Funtions:
    - _map (dict lookup for legend content)
    - border_map (caller)

Caller:
    - cli.py module
"""

from xlines import Colors
from xlines.variables import c, acct, gn, bbl, bbc, bcy, bdcy, bwt, rst


c = Colors()

lbrct = bbc + '[ ' + rst        # left bracket
rbrct = bbc + ' ]' + rst        # right bracket
vdiv = bbc + ' | ' + rst
tab = '\t'.expandtabs(24)
tab6 = '\t'.expandtabs(8).encode('utf-8')


width = 55      # legend overall width

legend_content = [
        bdcy + '==' + rst + '  |  Filesystem object counted (' + bcy + 'cyan' + rst + ')',
        acct + '==' + rst + '  |  Line count above high ct threshold (' + gn + 'green' + rst + ')',
        bwt + '->' + rst + '  |  Truncated (shortened) file path (' + bwt + 'white' + rst + ')'
    ]

legend_width = 57
legend_bar_top = ('_' * legend_width) + '\n'
legend_bar_bottom = ('_' * legend_width)

res = [
    ('┌' + '─' * width + '┐').encode('utf-8')
]

fallback = """
         """ + bbl + 'o' + rst + """  |  Filesystem object counted (""" + bcy + 'cyan' + rst + """)
       ----------------------------------------------------------
         """ + acct + 'o' + rst + """  |  Line count above high ct threshold (""" + acct + 'green' + rst + """)
       ----------------------------------------------------------
        """ + bwt + '->' + rst + """  |  Truncated (shortened) file path (""" + bwt + 'white' + rst + """)
"""


def _map(index, content):
    return {
        0: ('│  ' + content + (' ' * int(width - 43)) + '  │').encode('utf-8'),
        1: ('│  ' + content + (' ' * int(width - 53)) + '  │').encode('utf-8'),
        2: ('│  ' + content + (' ' * int(width - 50)) + '  │').encode('utf-8')
    }.get(index)


def border_map(text_list=legend_content):
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
        text_list.insert(0, legend_bar_top)
        text_list.insert(len(text_list), legend_bar_bottom)
        print('\t'.expandtabs(8) + text_list[0])
        [print('\t'.expandtabs(10) + x) for x in text_list[1:-1]][0]
        print('\t'.expandtabs(8) + text_list[-1])

    except Exception:
        # if any utf-8 handling host issues
        print(fallback)
