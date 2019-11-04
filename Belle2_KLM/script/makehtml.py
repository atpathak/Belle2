# write-html.py
import os
import sys
import time
import subprocess
from ROOT import TH1F, TH2F, TCanvas, THistPainter, TPad
from optparse import Option, OptionValueError, OptionParser

run = ["1772","1808"]
Main = ''

def writehtml(Location):
    Main = ''
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
    <address></address>
    <!-- hhmts start -->Send comments to <a href="mailto:atanu.pathak@belle2.org">Atanu Pathak.</a><br> 
    Last modified: %(date)s <!-- hhmts end -->
    <hr>
'''
    for i in run:
        #Main +=r'''<h4>run'''+i+''':  <a href="./r0'''+i+'''/png-e0008r0'''+i+'''/index.html"> BKLM Plots for run'''+i+''' </a> : <a href="./r0'''+i+'''/hitmap-e0008r0'''+i+'''/index.html"> Hit map plots for run'''+i+'''</a> : <a href="./r0'''+i+'''/Short-listed/Slides_e0008_r0'''+i+'''.pdf"> Short-listed plots for run'''+i+'''</a> </h4> \n'''
        Main +=r'''<h3 class="bottom-medium"> Run '''+i+''' (<a href="./r0'''+i+'''/Short-listed/Slides_e0008_r0'''+i+'''.pdf">Summary.pdf) </a> </h3>
        <h3 class="bottom-medium"> BKLM Plots for run '''+i+''': </h3>
        <h4 class="bottom-small" style="margin-left:30px;"> <a href="./r0'''+i+'''/png-e0008r0'''+i+'''/RawKLMs/index.html"> RawKLM </a> </h4>
        <h4 class="bottom-small" style="margin-left:30px;"> <a href="./r0'''+i+'''/png-e0008r0'''+i+'''/RawKLM_Sector_size_Multihit/index.html"> RawKLM for each sector </a> </h4>
        <h4 class="bottom-small" style="margin-left:30px;"> <a href="./r0'''+i+'''/png-e0008r0'''+i+'''/RawKLM_Sector_channelMultiplicity/index.html"> Channel multiplicity for each sector </a> </h4>
        <h4 class="bottom-small" style="margin-left:30px;"> <a href="./r0'''+i+'''/png-e0008r0'''+i+'''/mappedSectoroccupancy/index.html"> Sector occupancy for (un)mapped hits </a> </h4>
        <h4 class="bottom-small" style="margin-left:30px;"> <a href="./r0'''+i+'''/png-e0008r0'''+i+'''/mappedChannelOccupancy/index.html"> In-time phi/z occupancy for each sector </a> </h4>
        <h4 class="bottom-small" style="margin-left:30px;"> <a href="./r0'''+i+'''/png-e0008r0'''+i+'''/mappedRPCTime/index.html"> RPC time </a> </h4>
        <h4 class="bottom-small" style="margin-left:30px;"> <a href="./r0'''+i+'''/png-e0008r0'''+i+'''/mappedRPCTime_Sector/index.html"> RPC time distribution for each sector </a> </h4>
        <h4 class="bottom-small" style="margin-left:30px;"> <a href="./r0'''+i+'''/png-e0008r0'''+i+'''/mappedScintCtime/index.html"> Scint ctime </a> </h4>
        <h4 class="bottom-small" style="margin-left:30px;"> <a href="./r0'''+i+'''/png-e0008r0'''+i+'''/mappedScintCtime_Sector/index.html"> Scint ctime for each sector </a> </h4>
        <h4 class="bottom-small" style="margin-left:30px;"> <a href="./r0'''+i+'''/png-e0008r0'''+i+'''/Timing/index.html"> TDC/ctime range </a> </h4>
        <h4 class="bottom-small" style="margin-left:30px;"> <a href="./r0'''+i+'''/png-e0008r0'''+i+'''/Hit/index.html"> 1D/2D hits </a> </h4>
        <h4 class="bottom-small" style="margin-left:30px;"> <a href="./r0'''+i+'''/png-e0008r0'''+i+'''/RPC_occupancy/index.html"> RPC Occupancy (x/y view) </a> </h4>
        <h3 class="bottom-medium"> Hit map plots for run '''+i+''': </h3>
        <h4 class="bottom-small" style="margin-left:30px;"> <a href="./r0'''+i+'''/hitmap-e0008r0'''+i+'''/Hitmap/index.html"> Hit map for BB/BF </a> </h4>
        <h4 class="bottom-small" style="margin-left:30px;"> <a href="./r0'''+i+'''/hitmap-e0008r0'''+i+'''/Layer/index.html"> BB/BF layer hits by sector  </a> </h4>
        <h4 class="bottom-small" style="margin-left:30px;"> <a href="./r0'''+i+'''/hitmap-e0008r0'''+i+'''/PlanezPhi/index.html"> BB/BF z/phi plane hits by sector  </a> </h4>
        <h4 class="bottom-small" style="margin-left:30px;"> <a href="./r0'''+i+'''/hitmap-e0008r0'''+i+'''/LayerRPCTDC/index.html"> RPC TDC by sector </a> </h4>
        <h4 class="bottom-small" style="margin-left:30px;"> <a href="./r0'''+i+'''/hitmap-e0008r0'''+i+'''/LayerRPCCtime/index.html"> RPC ctime diff by sector </a> </h4>
        <h4 class="bottom-small" style="margin-left:30px;"> <a href="./r0'''+i+'''/hitmap-e0008r0'''+i+'''/LayerSciTDC/index.html"> Scint TDC by sector </a> </h4>
        <h4 class="bottom-small" style="margin-left:30px;"> <a href="./r0'''+i+'''/hitmap-e0008r0'''+i+'''/LayerSciCtime/index.html"> Scint ctime diff by sector </a> </h4> 
        <hr> \n
'''
    
    footer = r'''</body> </html>
'''
    content = header + Main + footer

    TexFile = "index.html"
    
    with open(TexFile,'w') as f:
        f.write(content % {'date': time.ctime()})

#=========================================================================
#
#   Main routine
#
#=========================================================================


RunLocation = "/home/belle2/atpathak/ppcc2018/work/KLM_16Apr2019/"

writehtml(RunLocation)
