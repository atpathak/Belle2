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
        self.hist_nDigit = ROOT.TH1F('NDigitEKLM', expRun + '# of EKLMDigits', 50, -0.5, 199.5)
        self.hist_nHit2d = ROOT.TH1F('NHit2dEKLM', expRun+'# of EKLMHit2ds', 25, -0.5, 49.5)
        self.hist_rawKLMnodeID = ROOT.TH2F('RawKLMnodeID',
                                           expRun + 'RawKLM NodeID;' +
                                           'NodeID (bklm: 1..4, eklm:5..8);' +
                                           'Copper index',
                                           14, -0.5, 13.5, 10, -0.5, 9.5)
        self.hist_BackwardSectorOccupancy = ROOT.TH1F('EKLMBackwardSectorOccupancy', expRun+'Backward Endcap Sector occupancy of channels', 4, 0.5, 4.5)
        self.hist_ForwardSectorOccupancy = ROOT.TH1F('EKLMForwardSectorOccupancy', expRun+'Forward Endcap Sector occupancy of channels', 4, 0.5, 4.5)
        
        self.hist_BackwardSectorbyctime = ROOT.TH2F('EKLMBackwardSectorbyctime', expRun+'Backward Endcap Sector occupancy of channels', 4, 0.5, 4.5, 256, -0.5, 1023.5)
        self.hist_ForwardSectorbyctime = ROOT.TH2F('EKLMForwardSectorbyctime', expRun+'Forward Endcap Sector occupancy of channels', 4, 0.5, 4.5, 256, -0.5, 1023.5)
        
        self.hist_time = ROOT.TH1F('EKLMtime', expRun+'Time distribution;t - trigger time', 50, -5000, -4000)
        self.hist_ctime = ROOT.TH1F('EKLMctime', expRun+'CTime time', 256, -0.5, 1023.5)
        self.hist_tdc = ROOT.TH1F('EKLMtdc', expRun+'TDC time', 256, -0.5, 1023.5)
        
        self.hist_EndcapOccupancy = ROOT.TH1F('EndcapOccupancy', expRun+'Endcap occupancy of channels; sector # (0 = backword, 1 = Forward)', 10, -1.0, 9.0)
        
        self.hist_occupancyForwardXY  = ROOT.TH2F('EKLMoccupancyForwardXY', expRun+'Forward Endcap XY Occupancy for total hits', 800, -400, 400, 800, -400, 400) 
        self.hist_occupancyBackwardXY = ROOT.TH2F('EKLMoccupancyBackwardXY', expRun+'Backward Endcap XY Occupancy for total hits', 800, -400, 400, 800, -400, 400)
        
        
        self.hist_LayeroccupancyForwardRZ  = ROOT.TH2F('EKLMLayeroccupancyForwardRZ', expRun+'Forward Endcap RZ Occupancy for total hits', 16, -0.5, 15.5, 800, 0, 800) 
        self.hist_LayeroccupancyBackwardRZ = ROOT.TH2F('EKLMLayeroccupancyBackwardRZ', expRun+'Backward Endcap RZ Occupancy for total hits', 16, -0.5, 15.5, 800, 0, 800)
        
        self.hist_LayeroccupancyForward = ROOT.TH1F('EKLMLayeroccupancyForward', expRun+'Forward Endcap Layer Occupancy', 16, -0.5, 15.5)
        self.hist_LayeroccupancyBackward = ROOT.TH1F('EKLMLayeroccupancyBackward', expRun+'Backward Endcap Layer Occupancy', 16, -0.5, 15.5)
        
        self.hist_occupancyForwardXYPerLayer = []
        self.hist_occupancyBackwardXYPerLayer = []
        for layer in range(0, 14):
            labelForward = 'occupancyForwardXY_L{0:02d}'.format(layer+1)
            titleForward = '{0}:Forward Endcap XY Occupancy for layer {1} hits;x(cm);y(cm)'.format(expRun, layer+1)
            self.hist_occupancyForwardXYPerLayer.append(ROOT.TH2F(labelForward, titleForward, 800, -400, 400, 800, -400, 400))
          
       
        for layer in range(0, 12):
            labelBackward = 'occupancyBackwardXY_L{0:02d}'.format(layer+1)
            titleBackward = '{0}:Backward Endcap XY Occupancy for layer {1} hits;x(cm);y(cm)'.format(expRun, layer+1)
            self.hist_occupancyBackwardXYPerLayer.append(ROOT.TH2F(labelBackward, titleBackward, 800, -400, 400, 800, -400, 400))

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
        rawklms = Belle2.PyStoreArray('RawKLMs')
        digits = Belle2.PyStoreArray('EKLMDigits')
        hit2ds = Belle2.PyStoreArray('EKLMHit2ds')
        #klmdigi = Belle2.PyStoreArray('KLMDigitEventInfo')
        #eklmids = Belle2.PyStoreArray('EKLMHitBases')
        self.hist_nDigit.Fill(len(digits))
        self.hist_nHit2d.Fill(len(hit2ds))
        for copper in range(0, len(rawklms)):
            rawklm = rawklms[copper]
            if rawklm.GetNumEntries() != 1:
                print('##0 Event', event, 'copper', copper, ' getNumEntries=', rawklm.GetNumEntries())
                continue
            nodeID = rawklm.GetNodeID(0) - self.BKLM_ID
            if nodeID >= self.EKLM_ID - self.BKLM_ID:
                nodeID = nodeID - (self.EKLM_ID - self.BKLM_ID) + 4
            self.hist_rawKLMnodeID.Fill(nodeID, copper)
            if (nodeID < 0) or (nodeID > 4):  # skip EKLM nodes
                continue
        
        
        for digit in digits:
            sector = digit.getSector()
            endcap = digit.getEndcap()
            time = digit.getTime()
            ctime = digit.getCTime()
            tdc   = digit.getTDC()
            #klmdigi = digit.getRelatedTo('KLMDigitEventInfo')
            #triggtime = digit.getRelativeCTime()
            #print (ctime, tdc)#, triggtime)
            #print(time)
            self.hist_time.Fill(time)
            self.hist_ctime.Fill(ctime)
            self.hist_tdc.Fill(tdc)
            if (endcap == 1):
                self.hist_BackwardSectorOccupancy.Fill(sector)
                self.hist_BackwardSectorbyctime.Fill(sector, ctime)
            else:
                self.hist_ForwardSectorOccupancy.Fill(sector)
                self.hist_ForwardSectorbyctime.Fill(sector, ctime)
            
            self.hist_EndcapOccupancy.Fill(endcap)
            
            
      
        for hit2d in hit2ds:
            sector = hit2d.getSector()
            endcap = hit2d.getEndcap()
            layer  = hit2d.getLayer()
            gx     = hit2d.getPositionX()
            gy     = hit2d.getPositionY()
            gz     = hit2d.getPositionZ()
            
            if (endcap == 1):
                self.hist_occupancyBackwardXY.Fill(gx, gy)
                self.hist_LayeroccupancyBackwardRZ.Fill(layer, gz)
                self.hist_LayeroccupancyBackward.Fill(layer)
                self.hist_occupancyBackwardXYPerLayer[layer-1].Fill(gx, gy)
            else:
                self.hist_occupancyForwardXY.Fill(gx, gy)
                self.hist_LayeroccupancyForwardRZ.Fill(layer, gz)
                self.hist_LayeroccupancyForward.Fill(layer)
                self.hist_occupancyForwardXYPerLayer[layer-1].Fill(gx, gy)
            
            

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

if int(exp) == 7: # odd experiment number for physics collisions
    #inputName = '/home/belle2/atpathak/ppcc2018/work/myHead/r03123/sub00/*.{0}.{1}.HLT*.f*.root'.format(exp, run)
    inputName = '/group/belle2/dataprod/Data/Raw/e0007/r{1}/sub00/*.{0}.{1}.HLT*.f*.root'.format(exp, run)


if int(exp) == 8: # odd experiment number for physics collisions
    #inputName = '/home/belle2/atpathak/ppcc2018/work/myHead/r03123/sub00/*.{0}.{1}.HLT*.f*.root'.format(exp, run)
    inputName = '/group/belle2/dataprod/Data/Raw/e0008/r{1}/sub00/*.{0}.{1}.HLT*.f*.root'.format(exp, run)

if int(exp) == 9: # odd experiment number for physics collisions
    #inputName = '/home/belle2/atpathak/ppcc2018/work/myHead/r03123/sub00/*.{0}.{1}.HLT*.f*.root'.format(exp, run)
    inputName = '/group/belle2/dataprod/Data/Raw/e0009/r{1}/sub00/*.{0}.{1}.HLT*.f*.root'.format(exp, run)
    
if int(exp) == 10: # odd experiment number for physics collisions
    #inputName = '/home/belle2/atpathak/ppcc2018/work/myHead/r03123/sub00/*.{0}.{1}.HLT*.f*.root'.format(exp, run)
    inputName = '/group/belle2/dataprod/Data/Raw/e0010/r{1}/sub00/*.{0}.{1}.HLT*.f*.root'.format(exp, run)

print(inputName)

outputName = 'eklm-e{0}r{1}.root'.format(exp, run)
histName = '/ghi/fs01/belle2/bdata/group/detector/BKLM/Run_Analysis/e{0}/bklmroots/r{1}/eklmHists-e{0}r{1}.root'.format(exp, run)

reset_database()
use_database_chain()
use_central_database('data_reprocessing_prompt_bucket6_cdst')  # use proper global tag for data
#use_central_database('data_reprocessing_prompt')
main = create_path()
if int(exp) == 1:
    main.add_module('SeqRootInput', inputFileNames=seqInputNames)
else:
    main.add_module('RootInput', inputFileName=inputName)
    #main.add_module('RootInput', inputFileName=inputName)
    ## replace above line with next to limit the number of events . . .
    ## main.add_module('RootInput', inputFileName=inputName, entrySequences="0:1000")

rawdata.add_unpackers(main, components=['EKLM'])
main.add_module('EKLMUnpacker')
#main.add_module('EKLMRawPacker')
main.add_module('EKLMReconstructor')
main.add_module(EventInspectorEKLM())

## output = main.add_module('RootOutput')
## output.param('outputFileName', outputName)
## output.param('branchNames', ['BKLMHit2ds'])

main.add_module('ProgressBar')

#set_log_level(LogLevel.DEBUG)
process(main)
print(statistics)
