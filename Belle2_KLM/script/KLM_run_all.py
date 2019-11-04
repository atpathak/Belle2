#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# Prerequisite (on kekcc): type
# source /cvmfs/belle.cern.ch/tools/b2setup release-02-01-00
#
#

import sys
import os
import subprocess
from ROOT import Belle2, TH1F, TH2F, TCanvas, THistPainter, TPad
from optparse import Option, OptionValueError, OptionParser

def submitjobs(Location):

    #RunNameList = os.listdir(Location)
    infile=open('all_new.sh','w')
    
    #RunNameList.remove("RunListCosmic~")
    #RunNameList.remove("RunListBeam")
    #RunNameList.remove("RunListCosmic")
    #RunNameList.remove("RunListBeam~")
    #RunNameList.remove("Registration")
    #RunNameList.remove("e0007")
    #RunNameList.remove("RunList~")
    #RunNameList.remove("RunListPhysics~")
    #RunNameList.remove("RunList")
    #RunNameList.remove("RunListPhysics")

    #Run = [i[2:] for i in RunNameList]

    os.chdir(Location)
    NewRunList = subprocess.Popen(['find', '.', '-type', 'd', '-mtime', '-5'], stdout=subprocess.PIPE)
    #NewRunList = subprocess.Popen(['find', '.', '-type', 'd', '-newerct', '30 Apr 2019', '!', '-newerct', '3 May 2019'], stdout=subprocess.PIPE) // directories between two dates.
    #NewRunList = subprocess.check_output(['find', '.', '-type', 'd', '-mmin', '-60']).splitlines()
    #NewRun = [i[2:].decode('ascii') for i in NewRunList]
    ls_lines = NewRunList.stdout.readlines()
    NewRun = [i[2:].decode('ascii') for i in ls_lines]
    NRun = [i[:6] for i in NewRun]
    Newlist = list(dict.fromkeys(NRun))
    Newlist.remove("e0007\n")
    Newlist.remove("")
    Newlist.remove("Regist")
    Run = [i[2:] for i in Newlist]
    
    
    
    for i in Run:
        infile.write("bsub -q lx basf2 bklm.py -- -e 7 -r " +i+"\n")
        #os.system("bsub -q l basf2 bklm.py -- -e 7 -r " + i)

    #os.system("bsub -q lx basf2 bklm.py -- -e 7 -r " + Run[0])

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
