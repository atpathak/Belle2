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



#RUNAGAIN = ['r02422', 'r02423', 'r02426', 'r02427', 'r02430', 'r02431', 'r02432', 'r02523', 'r02524', 'r02525', 'r02526', 'r02538', 'r02539', 'r02540', 'r02542', 'r02543', 'r02545', 'r02546', 'r02547', 'r02549', 'r02550', 'r02551', 'r02552', 'r02556', 'r02559', 'r02560', 'r02561']
#RUNAGAIN = ['r02562', 'r02563', 'r02564', 'r02565', 'r02567', 'r02568', 'r02569', 'r02575', 'r02578', 'r02579', 'r02580', 'r02581', 'r02584', 'r02585', 'r02586', 'r02588', 'r02592', 'r02593', 'r02594', 'r02595', 'r02599', 'r02600', 'r02605', 'r02606', 'r02607', 'r02608', 'r02609', 'r02610', 'r02611', 'r02612', 'r02614', 'r02615', 'r02616', 'r02617', 'r02618', 'r02620', 'r02621', 'r02622', 'r02623', 'r02624', 'r02625', 'r02626', 'r02627', 'r02628', 'r02629', 'r02630', 'r02631', 'r02632', 'r02633', 'r02634', 'r02635', 'r02636', 'r02637', 'r02638', 'r02639', 'r02640', 'r02641', 'r02642', 'r02643', 'r02644', 'r02645', 'r02646', 'r02647', 'r02648', 'r02652', 'r02653', 'r02654', 'r02655', 'r02656', 'r02657', 'r02658', 'r02659', 'r02660', 'r02661', 'r02662', 'r02663']

#RUNAGAIN = ['r02671', 'r02672', 'r02695', 'r02696', 'r02697', 'r02698', 'r02699', 'r02700', 'r02702', 'r02703', 'r02704', 'r02705', 'r02706', 'r02709', 'r02711', 'r02729', 'r02731', 'r02732', 'r02733', 'r02734', 'r02736', 'r02737', 'r02738', 'r02739', 'r02741', 'r02742', 'r02743', 'r02744', 'r02746', 'r02747', 'r02749', 'r02750', 'r02755', 'r02756', 'r02758', 'r02759', 'r02760', 'r02761', 'r02762', 'r02783', 'r02784', 'r02785', 'r02786', 'r02788', 'r02789', 'r02791', 'r02792', 'r02793', 'r02795', 'r02797', 'r02798', 'r02799', 'r02802', 'r02803', 'r02804', 'r02808', 'r02888', 'r02897', 'r02898', 'r02899', 'r02900', 'r02901', 'r02902', 'r02903', 'r02904', 'r02905', 'r02906', 'r02909', 'r02934', 'r02935', 'r02939', 'r02940', 'r02941', 'r02942', 'r02943', 'r02944', 'r02945', 'r02949', 'r02950', 'r02951', 'r02952', 'r02953', 'r02954', 'r02970', 'r02971', 'r02972', 'r02973', 'r02974', 'r03041', 'r03042', 'r03043', 'r03044', 'r03045', 'r03046', 'r03047', 'r03048', 'r03052', 'r03053', 'r03054', 'r03055', 'r03056', 'r03057', 'r03058', 'r03059', 'r03071', 'r03074', 'r03075', 'r03076', 'r03077', 'r03078', 'r03080', 'r03085', 'r03087', 'r03088', 'r03089', 'r03090', 'r03091', 'r03092']
#RUNAGAIN = ['r03115', 'r03118', 'r03119', 'r03120', 'r03121', 'r03122', 'r03123']

RUNAGAIN = ['r01055', 'r01058', 'r01059', 'r01060', 'r01061', 'r01064', 'r01065', 'r01068', 'r01163', 'r01175', 'r01190', 'r01213', 'r01217', 'r01238', 'r01240', 'r01288', 'r01289', 'r01291', 'r01293', 'r01295', 'r01296', 'r01307', 'r01309', 'r01315']
HLT = ["HLT1","HLT2","HLT3","HLT4","HLT5"]

def submitjobs(Location):
    RunNameList = os.listdir(Location)
    infile=open('needtorun.sh','w')

    today = str(datetime.datetime.now())[:10].replace('-','')

    for i in RUNAGAIN:
        for j in HLT:
            infile.write("bsub -q lx basf2 -n 200000 scripts/recoGlobalRun_onlyBKLM.py "+Location+i+"/sub00/ /ghi/fs01/belle2/bdata/group/detector/BKLM/Run_Analysis/e0008/bklmroots/"+i+"/ "+today+" 0 " +j+ "\n")

def makepng(rootLocation):
    Rundir = os.listdir(rootLocation)
    infile1 = open("hitmaproot.sh","w")
    #run = [i[2:] for i in Rundir ]
    run = [i[2:] for i in RUNAGAIN ]
    for i in run:
        infile1.write("python3 recurROOTplot.py -e 8 -r "+i+" \n")

def Hitpngcategory(Location):
    #Rundir = os.listdir(rootLocation)
    infile2 = open("Hitpngcategory.sh","w")
    #run = [i[2:] for i in Rundir ]
    run = [i[2:] for i in RUNAGAIN ]
    for i in run:
        infile2.write("python3 Hitpngcategory.py -e 8 -r "+i+" \n")

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
                  default='0220',
                  help='Run number [default=0604]')
(options, args) = parser.parse_args()
exp = '{0:04d}'.format(int(options.eNumber))
run = '{0:05d}'.format(int(options.rNumber))

RunLocation = "/ghi/fs01/belle2/bdata/Data/Raw/e{0}/".format(exp)
hitroots = "/ghi/fs01/belle2/bdata/group/detector/BKLM/Run_Analysis/e{0}/bklmroots/".format(exp)
submitjobs(RunLocation)
makepng(hitroots)
Hitpngcategory(".")
