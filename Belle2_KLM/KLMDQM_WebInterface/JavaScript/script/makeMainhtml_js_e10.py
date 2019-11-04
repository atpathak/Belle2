# write-html.py
import os
import sys
import time


Main = ''

d = os.listdir(".")
l = [i for i in d if i.endswith("1M.txt")]
#l.remove("Summary.txt")
#l.sort(reverse=True)
l.sort()
run = [i[:-4] for i in l]

def writehtml(Location):
    Main = ''
    header = r'''<!DOCTYPE HTML PUBLIC "-//IETF//DTD HTML//EN">
    <html> <head>
    <title>Belle II Run Analysis</title>
    <style>
        div.example {
            padding: 0px;
        }

        @media screen and (min-width: 601px) {
            div.example {
                    font-size: 20px;
            }
        }

        @media screen and (max-width: 1204px) {
            div.example {
                    font-size: 40px;
            }
        }
    </style>
    </head>
    <body>
    <hr>
    <h1>Expert-level DQM plots for KLM </h1>
    (runs with >1M events shown)

    <address></address>
    <!-- hhmts start -->Send comments to <a href="mailto:atanu.pathak@belle2.org">Atanu Pathak.</a><br>
    Last modified: %(date)s <!-- hhmts end -->
    <hr>
'''
    for i in range (0,len(run)):
        with open(run[i]+'.txt', 'rb') as fh:
            try:
                while True:
                    first = [next(fh).decode()]
                    last = [fh.readlines()[-1].decode()]
                    wewantfirst = [i[:4] for i in first]
                    wewantlast = [i[:4] for i in last]
                    if (run[i][5:7] == '09'):
                    	Month = 'September'
                    else:
                        Month = 'October'
                    Main +=r'''<div class="example"><h4><a href="./index_'''+run[i]+'''.htm">'''+run[i][8:10]+''' '''+Month+ ''' 2019 ('''+wewantlast[0]+'''- '''+wewantfirst[0]+''') </a></h4></div> \n
'''
            except StopIteration:
                    pass
    
    footer = r'''</body> </html>
'''
    content = header + Main + footer

    TexFile = "index_test_e10.html"
    
    with open(TexFile,'w') as f:
        f.write(content % {'date': time.ctime()})

#=========================================================================
#
#   Main routine
#
#=========================================================================


RunLocation = "."

writehtml(RunLocation)
