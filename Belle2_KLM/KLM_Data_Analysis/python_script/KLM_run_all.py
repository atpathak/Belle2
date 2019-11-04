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

def rundirectory(Location):

    os.chdir(Location)
    #NewRunList = subprocess.Popen(['find', '.', '-type', 'd', '-newerct', '5 Jun 2019', '!', '-newerct', '12 Jun 2019'], stdout=subprocess.PIPE)
    NewRunList = subprocess.Popen(['find', '.', '-type', 'd', '-newermt', ' 21 Jun 2019', '!', '-newermt', ' 28 Jun 2019'], stdout=subprocess.PIPE)
   # NewRunList = subprocess.Popen(['find', '.', '-type', 'd', '-newerct', {0}, '!', '-newerct', {1}], stdout=subprocess.PIPE).format(fromdate, todate)
    ls_lines = NewRunList.stdout.readlines()
    NewRun = [i[2:].decode('ascii') for i in ls_lines]
    NRun = [i[:6] for i in NewRun]
    Newlist = list(dict.fromkeys(NRun))
    #Newlist.remove("e0008\n")
    Newlist.remove("")
    Newlist.remove("Regist")
    #Newlist.remove("b2ccte")
    Newlist.sort()
    print (Newlist)
    Run = [i[2:] for i in Newlist]
    return Run, Newlist
    

def submitjobs(Location):

    
    infile=open('all_new.sh','w')
    
    run, mylist = rundirectory(RunLocation)    
    for i in run:
        infile.write("bsub -q lx basf2 bklm-dst.py -- -e 8 -r " +i+"\n")

def submitjobsHLT(Location):
    
    infile2 = open("needtorun.sh","w")
    
   #infile=open('killed.txt','r')
    #ls_lines = infile.readlines()
    #Run = [i[-5:-1] for i in ls_lines]
    #Run.remove("")

    #RUNAGAIN  = ['r00047', 'r00133', 'r00043', 'r00050', 'r00048', 'r00051', 'r00213', 'r00056', 'r00122', 'r00212', 'r00193', 'r00052', 'r00173', 'r00211', 'r00127', 'r00057', 'r00044', 'r00059']
    
    HLT = ["HLT1","HLT2","HLT3","HLT4","HLT5"]
    run, mylist = rundirectory(RunLocation)       
    for i in run:
        for j in HLT:
            infile2.write("bsub -q lx basf2 bklm_HLT.py -- -e 8 -r " +i+" -t "+j+"\n")

def makedirectory(Location):
    
    infile4 = open("dic_new.sh","w")
    run,mylist = rundirectory(RunLocation)
    for i in mylist:
        infile4.write("mkdir -vp "+i+"\n")

def makepng(Location):
    #Rundir = os.listdir(rootLocation)
    infile1 = open("bklmroot.sh","w")
    #run = [i[2:] for i in Rundir ]
    run, mylist = rundirectory(RunLocation)
    for i in run:
        infile1.write("python3 recurROOTplot.py -e 8 -r "+i+" \n")
        
def makepdf(self):
    #Rundir = os.listdir(rootLocation)
    infile3 = open("Slides.sh","w")
    #run = [i[2:] for i in Rundir ]
    run, mylist = rundirectory(RunLocation)
    for i in run:
        infile3.write("python3 makelatex_v2.py -e 8 -r "+i+" \npython3 makelatex_v2.py -e 8 -r "+i+" \n ")

def pngcategory(self):
    #Rundir = os.listdir(rootLocation)
    infile4 = open("pngcategory.sh","w")
    #run = [i[2:] for i in Rundir ]
    run, mylist = rundirectory(RunLocation)
    for i in run:
        infile4.write("python3 pngcategory.py -e 8 -r "+i+" \n")    

#=========================================================================
#
#   Main routine
#
#=========================================================================

parser = OptionParser()
parser.add_option('-e', '--experiment', dest='eNumber',
                  default='8',
                  help='Experiment number [default=7]')
parser.add_option('-r', '--run', dest='rNumber',
                  default='0222',
                  help='Run number [default=0604]')
parser.add_option('-f', '--fdate', dest='fdate',
                  default='21 May',
                  help='From date [default=21 May]')
parser.add_option('-t', '--tdate', dest='tdate',
                  default='25 May',
                  help='To date [default=25 May]')
(options, args) = parser.parse_args()
exp = '{0:04d}'.format(int(options.eNumber))
run = '{0:05d}'.format(int(options.rNumber))
#fromdate = str(options.fdate)
#todate = str(options.tdate)
#print(fromdate)
#print(todate)

RunLocation = "/ghi/fs01/belle2/bdata/Data/Raw/e{0}/".format(exp)
bklmroots = "/ghi/fs01/belle2/bdata/group/detector/BKLM/Run_Analysis/e{0}/bklmroots/".format(exp)
#submitjobs(RunLocation)
#submitjobsHLT(RunLocation)
#makepng(bklmroots)
makepdf(bklmroots)
#makedirectory(RunLocation)
#pngcategory(RunLocation)
