import sys
import os
import subprocess
from ROOT import Belle2, TH1F, TH2F, TCanvas, THistPainter, TPad
from optparse import Option, OptionValueError, OptionParser

def submitjobs(Location):

    RunNameList = os.listdir(Location)
    infile=open('directories.sh','w')
    
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

    #Run = [i[2:] for i in RunNameList]

    #NewRunList = subprocess.check_output(['find', '.', '-type', 'd', '-mmin', '-60']).splitlines()
    #NewRun = [i[2:].decode('ascii') for i in NewRunList]
    #NewRun.remove("")
    
    
    for i in RunNameList:
        infile.write("mkdir -vp " +i+"\n")
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
