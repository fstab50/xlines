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
tab6 = '\t'.expandtabs(8)


legend = [
            bdcy + ' o' + rst + '  |  Filesystem object counted (' + bcy + 'cyan' + rst + ')',
            bdacct + ' o' + rst + '  |  Line count above high ct threshold (' + bdacct + 'green' + rst + ')',
            bwt + '->' + rst + '  |  Truncated (shortened) file path (' + bwt + 'white' + rst + ')'
    ]


width = 55
res = ['┌' + '─' * width + '┐']

def _map(index, content):
    return {
        0: res.append('│  ' + content + (' ' * int(width - 43)) + '  │'),
        1: res.append('│  ' + content + (' ' * int(width - 53)) + '  │'),
        2: res.append('│  ' + content + (' ' * int(width - 50)) + '  │')
    }.get(index)


def border_map(text_list=legend):
    for index, s in enumerate(text_list):
        _map(index, s)
    res.append('└' + '─' * width + '┘')
    return [print(tab6 + x) for x in res]


def border_list(text_list=legend):
    width = 55
    res = ['┌' + '─' * width + '┐']
    for index, s in enumerate(text_list):
        if index == 0:
            res.append('│  ' + s + (' ' * int(width - 43)) + '  │')
        if index == 1:
            res.append('│  ' + s + (' ' * int(width - 53)) + '  │')
        if index == 2:
            res.append('│  ' + s + (' ' * int(width - 50)) + '  │')

    res.append('└' + '─' * width + '┘')
    return [print(tab6 + x) for x in res]
