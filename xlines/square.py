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


legend =  """ """ + tab6 +  bbl + 'o' + rst + """  |  Filesystem object counted (""" + bcy + 'cyan' + rst + """)
       --------------------------------------------------------
          """ + bdacct + 'o' + rst + """  |  Line count above high ct threshold (""" + acct + 'orange' + rst + """)
       --------------------------------------------------------
         """ + bwt + '->' + rst + """  |  Truncated (shortened) file path (""" + bwt + 'white' + rst + """) """




def bordered(text):
    lines = text.splitlines()
    width = int(max(len(s) for s in lines) * .7)
    res = ['┌' + '─' * width + '┐']
    #print(res[0])
    for s in lines:
        res.append('│' + (s + ' ' * width)[:width] + '│')

    res.append('└' + '─' * width + '┘')
    #print(res[2])
    return [print(x) for x in res]

bordered(legend )
