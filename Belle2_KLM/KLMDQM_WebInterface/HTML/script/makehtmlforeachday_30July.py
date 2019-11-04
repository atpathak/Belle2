# write-html.py
import os
import sys
import time
import subprocess

#run = ["1772","1808"]
Main = ''

def findrun(Location):
    lst = []
    file = open(Textfile+'.txt')
    for line in file:
        lst.append([ x for x in line.split()])
    column1 = [ x[0] for x in lst]
    #Runtxt = [i[:4] for i in column1]
    Runtxt = [str(i).zfill(4) for i in column1]
    Avbklm = os.listdir("/ghi/fs01/belle2/bdata/group/detector/BKLM/Run_Analysis/e0008/bklmroots/")
    Avbklmrun = [i[2:] for i in Avbklm]
    Run = [i for i in Runtxt if i in Avbklmrun]
    Run.sort()
    return Run 


def writehtml(Location):
    Main = ''
    run = findrun(RunLocation)
    s = ''
    for i in run:
        s += '''<a href="#'''+i+'''">'''+i+'''</a>, '''
    
    header = r'''<!DOCTYPE HTML PUBLIC "-//IETF//DTD HTML//EN">
    <html> <head>
    <title>Belle II Run Analysis</title>
    </head>
    <body>
    <style>
    .bottom-medium {
    line-height: 0.5;
    }
    </style>
    
    <style>
    .bottom-small {
    line-height: 0.3;
    }
    </style>
    <hr>
    <h1>Expert-level DQM plots for KLM </h1>
    (runs with >1M events shown)
    <h4> '''+Textfile[8:10]+''' '''+Month+''' 2019 ('''+s[:-2]+''') </h4>
    <address></address>
    <!-- hhmts start -->Send comments to <a href="mailto:atanu.pathak@belle2.org">Atanu Pathak.</a><br> 
    Last modified: %(date)s <!-- hhmts end -->
    <hr>
'''
    
    for i in run:
        #Main +=r'''<h4>run'''+i+''':  <a href="./r0'''+i+'''/png-e0008r0'''+i+'''/index.html"> BKLM Plots for run'''+i+''' </a> : <a href="./r0'''+i+'''/hitmap-e0008r0'''+i+'''/index.html"> Hit map plots for run'''+i+'''</a> : <a href="./r0'''+i+'''/Short-listed/Slides_e0008_r0'''+i+'''.pdf"> Short-listed plots for run'''+i+'''</a> </h4> \n'''
        Main +=r'''<h3 class="bottom-medium" id="'''+i+'''"> Run '''+i+''' </h3>
        <h3 class="bottom-medium"> BKLM Plots for run '''+i+''': </h3>
        <h4 class="bottom-small" style="margin-left:30px;"> <a href="./r0'''+i+'''/png-e0008r0'''+i+'''/RawKLMs/index.html"> RawKLM </a> </h4>
        <h4 class="bottom-small" style="margin-left:30px;"> <a href="./r0'''+i+'''/png-e0008r0'''+i+'''/mappedSectoroccupancy/index.html"> Sector occupancy for (un)mapped hits </a> </h4>
        <h4 class="bottom-small" style="margin-left:30px;"> <a href="./r0'''+i+'''/png-e0008r0'''+i+'''/mappedRPCTime/index.html"> RPC time </a> </h4>
        <h4 class="bottom-small" style="margin-left:30px;"> <a href="./r0'''+i+'''/png-e0008r0'''+i+'''/mappedScintCtime/index.html"> Scint ctime </a> </h4>
        <h4 class="bottom-small" style="margin-left:30px;"> <a href="./r0'''+i+'''/png-e0008r0'''+i+'''/RPC_occupancy/index.html"> RPC Occupancy (x/y view) </a> </h4>
        <h3 class="bottom-medium"> Hit map plots for run '''+i+''': </h3>
        <h4 class="bottom-small" style="margin-left:30px;"> <a href="./r0'''+i+'''/hitmap-e0008r0'''+i+'''/Planez/index.html"> BB/BF z plane hits by sector  </a> </h4>
        <h4 class="bottom-small" style="margin-left:30px;"> <a href="./r0'''+i+'''/hitmap-e0008r0'''+i+'''/PlanePhi/index.html"> BB/BF phi plane hits by sector  </a> </h4>
        <hr> \n
'''
    
    footer = r'''</body> </html>
'''
    content = header + Main + footer

    TexFile = "index_"+Textfile+".html"
    
    with open(TexFile,'w') as f:
        f.write(content % {'date': time.ctime()})

#=========================================================================
#
#   Main routine
#
#=========================================================================

Textfile = sys.argv[1]

if Textfile[5:7] == '06':
    Month = 'Jun'
else:
    Month = 'May'

#RunLocation = "/home/belle2/atpathak/ppcc2018/work/KLM_16Apr2019/"
RunLocation = "."

writehtml(RunLocation)
