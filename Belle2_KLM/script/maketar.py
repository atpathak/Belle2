import ROOT
from ROOT import Belle2, TH1, TH2, TCanvas, THistPainter, TPad, gROOT, gStyle, TFile  
import os
import sys
import subprocess
from optparse import Option, OptionValueError, OptionParser


def maketar(RunLocation):

    os.chdir(RunLocation)

    os.system("tar czvf r{1}.tgz r{1}/png-e{0}r{1}/RawKLMs/* r{1}/png-e{0}r{1}/RawKLM_Sector_channelMultiplicity/* r{1}/png-e{0}r{1}/mappedSectoroccupancy/* r{1}/png-e{0}r{1}/mappedChannelOccupancy/* r{1}/png-e{0}r{1}/mappedRPCTime/* r{1}/png-e{0}r{1}/mappedRPCTime_Sector/* r{1}/png-e{0}r{1}/mappedScintCtime/* r{1}/png-e{0}r{1}/mappedScintCtime_Sector/* r{1}/png-e{0}r{1}/RPC_occupancy/* r{1}/hitmap-e{0}r{1}/Hitmap/* r{1}/hitmap-e{0}r{1}/Planez/* r{1}/hitmap-e{0}r{1}/PlanePhi/* r{1}/hitmap-e{0}r{1}/LayerSciCtime/* r{1}/hitmap-e{0}r{1}/LayerRPCTDC/* ".format(exp, run))


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
                  default='0133',
                  help='Run number [default=0604]')
(options, args) = parser.parse_args()
exp = '{0:04d}'.format(int(options.eNumber))
run = '{0:05d}'.format(int(options.rNumber))
runhit = '{0:04d}'.format(int(options.rNumber))

tardir = '/ghi/fs01/belle2/bdata/group/detector/BKLM/Run_Analysis/e{0}/bklmroots/'.format(exp, run)
#pngdir = '/home/belle2/atpathak/ppcc2018/work/KLM_16Apr2019/png-e0008r01772/'
maketar(tardir)
