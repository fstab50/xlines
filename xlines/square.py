#!/usr/bin/env python3

from xlines import Colors
from xlines.variables import *


c = Colors()

ACCENT = c.ORANGE               # orange accent highlight color
bdacct = c.ORANGE + c.BOLD      # bold orange
bdcy = c.CYAN + c.BOLD          # bold blue
lbrct = bbc + '[ ' + rst        # left bracket
rbrct = bbc + ' ]' + rst        # right bracket
vdiv = bbc + ' | ' + rst
tab = '\t'.expandtabs(24)
tab6 = '\t'.expandtabs(8)


legend = [
            bbl + ' o' + rst + '  |  Filesystem object counted (' + bcy + 'cyan' + rst + ')',
            bdacct + ' o' + rst + '  |  Line count above high ct threshold (' + acct + 'orange' + rst + ')',
            bwt + '->' + rst + '  |  Truncated (shortened) file path (' + bwt + 'white' + rst + ')'
    ]



def border_list(text_list=legend):
    width = 55
    res = ['┌' + '─' * width + '┐']
    for index, s in enumerate(text_list):
        if index == 0:
            res.append('│  ' + s + (' ' * int(width - 43)) + '  │')
        if index == 1:
            res.append('│  ' + s + (' ' * int(width - 54)) + '  │')
        if index == 2:
            res.append('│  ' + s + (' ' * int(width - 50)) + '  │')

    res.append('└' + '─' * width + '┘')
    return [print(tab6 + x) for x in res]
