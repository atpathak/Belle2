import sys
import os
import subprocess
import datetime
from ROOT import Belle2, TH1F, TH2F, TCanvas, THistPainter, TPad
from optparse import Option, OptionValueError, OptionParser


RUNAGAIN = ["r01366", "r01402", "r01357", "r01318", "r01310", "r01369", "r01361", "r01322", "r01585", "r01152", "r01373", "r01307", "r01358", "r01319", "r01311", "r01507", "r01323", "r01225", "r01495", "r01419", "r01308", "r01300", "r01359", "r01312", "r01417", "r00932", "r01363", "r01231", "r01324", "r02294", "r01375", "r01506", "r01155", "r01481", "r01232", "r01428", "r01313", "r01149", "r01235", "r01014", "r01509", "r01364", "r01143", "r01376", "r01114", "r01502", "r01566", "r01302", "r01492", "r01401", "r01353", "r01314", "r01505", "r01147", "r01365", "r00933", "r01514", "r00923", "r00931", "r02376", "r01013", "r01299", "r01425", "r01565", "r02283", "r01221", "r00921", "r01370", "r01224", "r01423", "r00999", "r01568", "r01513", "r01421", "r01320", "r01988", "r01020", "r01371", "r01228", "r01487", "r01516", "r01007", "r01144", "r01012", "r01485", "r01503", "r02476", "r01498", "r01234", "r01483", "r00930", "r01309", "r01136", "r01418", "r02305", "r01006", "r01011", "r00936", "r01217", "r01429", "r01118", "r00926", "r01562", "r01480", "r02315", "r01427", "r01303", "r01578", "r01315"]

def submitjobs(Location):
    infile=open("remove.sh","w")
    Run = [i[2:] for i in RUNAGAIN]
    
    for i,j in zip(RUNAGAIN, Run):
        infile.write("rm -rf " +i+ "/bklmHitmap_run"+j+".root \n")

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
        
