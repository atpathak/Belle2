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
    Avbklm = os.listdir("/group/belle2/dataprod/Data/Raw/e0010/")
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
    
    header = r'''<html>
    <head>
    <meta charset="UTF-8">
    <meta http-equiv="X-UA-Compatible" content="IE=edge">
    <title>ExpressReco DQM Display for Past Runs</title>
    <style>
    div.example {
      padding: 20px;
    }

    @media screen and (min-width: 601px) {
      div.example {
        font-size: 20px;
        line-height:2px;
      }
    }

    @media screen and (max-width: 1204px) {
      div.example {
        font-size: 50px;
        line-height:120%;
        }
    }
    </style>
    </head>
    <body>
'''
    
    for i in run:
        #Main +=r'''<h4>run'''+i+''':  <a href="./r0'''+i+'''/png-e0008r0'''+i+'''/index.html"> BKLM Plots for run'''+i+''' </a> : <a href="./r0'''+i+'''/hitmap-e0008r0'''+i+'''/index.html"> Hit map plots for run'''+i+'''</a> : <a href="./r0'''+i+'''/Short-listed/Slides_e0008_r0'''+i+'''.pdf"> Short-listed plots for run'''+i+'''</a> </h4> \n'''
        Main +=r'''<div class="example"><a href="../show_plot.htm?rootfile=e0010/r0'''+i+'''/klmHists-e0010r0'''+i+'''.root"><b>Run '''+i+'''</b></a></div> \n
'''
    
    footer = r'''</body> </html>
'''
    content = header + Main + footer

    TexFile = "index_"+Textfile+".htm"
    
    with open(TexFile,'w') as f:
        f.write(content)

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
