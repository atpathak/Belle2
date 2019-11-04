#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# Purpose:
#   basf module to histogram useful values in RawKLM, KLMDigit, BKLMHit1d, and BKLMHit2d
#   data-objects in a DST ROOT file and to create BKLM event displays from these data-objects.
#
import basf2
from basf2 import *
import bklmDB
import math
import ctypes
import ROOT
import sys
import simulation
import reconstruction
import rawdata
import glob
from ROOT import Belle2, TH1F, TH2F, TCanvas, THistPainter, TPad
from optparse import Option, OptionValueError, OptionParser

class EventInspectorEKLM(basf2.Module):

    BKLM_ID = 0x07000000
    EKLM_ID = 0x08000000

    BKLM_STRIP_BIT = 0
    BKLM_PLANE_BIT = 6
    BKLM_LAYER_BIT = 7
    BKLM_SECTOR_BIT = 11
    BKLM_END_BIT = 14
    BKLM_MAXSTRIP_BIT = 15
    BKLM_OUTOFTIME_BIT = 24
    BKLM_ONTRACK_BIT = 27
    BKLM_ONSTATRACK_BIT = 29

    BKLM_STRIP_MASK = 0x3f
    BKLM_PLANE_MASK = (1 << BKLM_PLANE_BIT)
    BKLM_LAYER_MASK = (15 << BKLM_LAYER_BIT)
    BKLM_SECTOR_MASK = (7 << BKLM_SECTOR_BIT)
    BKLM_END_MASK = (1 << BKLM_END_BIT)
    BKLM_MAXSTRIP_MASK = (63 << BKLM_MAXSTRIP_BIT)
    BKLM_ONTRACK_MASK = (1 << BKLM_ONTRACK_BIT)
    BKLM_ONSTATRACK_MASK = (1 << BKLM_ONSTATRACK_BIT)
    BKLM_MODULEID_MASK = (BKLM_END_MASK | BKLM_SECTOR_MASK | BKLM_LAYER_MASK)

    def __init__(self):
        """ init """
        super(EventInspectorEKLM, self).__init__()

    def initialize(self):
        """Handle job initialization: fill the mapping database, create histograms, open the event-display file"""
        self.eventDisplayCounter = 0
        print('initialize(): exp=', exp, 'run=', run)
        expRun = 'e{0:02d}r{1}: '.format(int(exp), int(run))
        
        ROOT.gStyle.SetOptStat(10)
        self.electIdToModuleId = bklmDB.fillDB()


        #: Output ROOT TFile that will contain the histograms/scatterplots
        self.histogramFile = ROOT.TFile.Open(histName, "RECREATE")
        # All histograms/scatterplots in the output file will show '# of events' only
        ROOT.gStyle.SetOptStat(10)
        ROOT.gStyle.SetOptFit(111)

        # create the rawKLM histograms

        #: histogram of the number of BKLMDigits in the event
        self.hist_nDigit = ROOT.TH1F('NDigit', expRun + '# of EKLMDigits', 100, -0.5, 49.5)
        self.hist_nHit2d = ROOT.TH1F('NHit2d', expRun+'# of EKLMHit2ds', 50, -0.5, 49.5)


    def terminate(self):

        self.histogramFile.Write()
        self.histogramFile.Close()
        print('Goodbye')

    def beginRun(self):
        EventMetaData = Belle2.PyStoreObj('EventMetaData')
        print('beginRun', EventMetaData.getRun())

    def endRun(self):
        EventMetaData = Belle2.PyStoreObj('EventMetaData')
        print('endRun', EventMetaData.getRun())


    def event(self):
        """ Return True if event is fine, False otherwise """
        someOK = False

        EventMetaData = Belle2.PyStoreObj('EventMetaData')
        event = EventMetaData.getEvent()
        digits = Belle2.PyStoreArray('EKLMDigits')
        hit2ds = Belle2.PyStoreArray('EKLMHit2ds')
        self.hist_nDigit.Fill(len(digits))
        self.hist_nHit2d.Fill(len(hit2ds))

        super(EventInspectorEKLM, self).return_value(someOK)

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
parser.add_option('-c', '--count', dest='counter',
                  default='1000',
                  help='Max # of event displays [default=1000]')
(options, args) = parser.parse_args()
exp = '{0:04d}'.format(int(options.eNumber))
run = '{0:05d}'.format(int(options.rNumber))
maxEventCounter = int(options.counter)

if int(exp) == 8: # odd experiment number for physics collisions
    inputName = '/home/belle2/atpathak/ppcc2018/work/myHead/r03123/sub00/*.{0}.{1}.HLT*.f*.root'.format(exp, run)

print(inputName)

outputName = 'eklm-e{0}r{1}.root'.format(exp, run)
histName = './eklmHists-e{0}r{1}.root'.format(exp, run)

reset_database()
use_database_chain()
use_central_database('data_reprocessing_prompt_bucket6_cdst')  # use proper global tag for data

main = create_path()
if int(exp) == 1:
    main.add_module('SeqRootInput', inputFileNames=seqInputNames)
else:
    main.add_module('RootInput', inputFileName=inputName)
    #main.add_module('RootInput', inputFileName=inputName)
    ## replace above line with next to limit the number of events . . .
    ## main.add_module('RootInput', inputFileName=inputName, entrySequences="0:1000")

rawdata.add_unpackers(main, components=['BKLM'])
main.add_module('EKLMUnpacker')
main.add_module('EKLMReconstructor')
main.add_module(EventInspectorEKLM())

## output = main.add_module('RootOutput')
## output.param('outputFileName', outputName)
## output.param('branchNames', ['BKLMHit2ds'])

main.add_module('ProgressBar')

#set_log_level(LogLevel.DEBUG)
process(main)
print(statistics)
