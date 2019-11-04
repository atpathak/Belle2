#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# Prerequisite (on kekcc): type
# source /cvmfs/belle.cern.ch/tools/b2setup release-02-01-00
#
#

import sys
import os
import subprocess
import datetime
from ROOT import Belle2, TH1F, TH2F, TCanvas, THistPainter, TPad
from optparse import Option, OptionValueError, OptionParser

def submitjobs(Location):
    RunNameList = os.listdir(Location)
    infile=open('all.sh','w')
    
    RunNameList.remove("RunListCosmic~")
    RunNameList.remove("RunListBeam")
    RunNameList.remove("RunListCosmic")
    RunNameList.remove("RunListBeam~")
    RunNameList.remove("Registration")
    RunNameList.remove("e0007")
    RunNameList.remove("RunList~")
    RunNameList.remove("RunListPhysics~")
    RunNameList.remove("RunList")
    RunNameList.remove("RunListPhysics")

    today = str(datetime.datetime.now())[:10].replace('-','')

    for i in RunNameList:
        infile.write("bsub -q lx basf2 scripts/recoGlobalRun_onlyBKLM.py "+Location+i+"/sub00/ /ghi/fs01/belle2/bdata/group/detector/BKLM/Run_Analysis/e0007/bklmroots/"+i+"/ "+today+" 0 \n")

#=========================================================================
#
#   Main routine
#
#=========================================================================

parser = OptionParser()
parser.add_option('-e', '--experiment', dest='eNumber',
                  default='7',
                  help='Experiment number [default=7]')
parser.add_option('-r', '--run', dest='rNumber',
                  default='1505',
                  help='Run number [default=0604]')
(options, args) = parser.parse_args()
exp = '{0:04d}'.format(int(options.eNumber))
run = '{0:05d}'.format(int(options.rNumber))

RunLocation = "/ghi/fs01/belle2/bdata/Data/Raw/e{0}/".format(exp)
submitjobs(RunLocation)
