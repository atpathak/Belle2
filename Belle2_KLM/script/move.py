import sys
import os
import subprocess
import datetime
from ROOT import Belle2, TH1F, TH2F, TCanvas, THistPainter, TPad
from optparse import Option, OptionValueError, OptionParser

infile = open("move.sh","w")
RunNameList = os.listdir("/ghi/fs01/belle2/bdata/group/detector/BKLM/Run_Analysis/e0007/bklmroots/")
RunName = [i for i in RunNameList if i.startswith('r00')]
Run = [i[3:] for i in RunName]
Runid = [i[2:] for i in RunName]

for i,j,k in zip(RunName, Run, Runid):
    infile.write("mv " +i+ "/bklmHitmap_run"+j+".root "+i+"/bklmHitmap_run"+k+".root \n")
    
