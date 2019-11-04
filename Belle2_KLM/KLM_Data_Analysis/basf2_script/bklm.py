#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# Prerequisite (on kekcc): type
# source /cvmfs/belle.cern.ch/tools/b2setup release-02-01-00
#
# This uses the external python scrypt bklmDB.py, which should be in the same folder.
# 
# basf2 bklm.py -- -e # -r #
# Optional arguments:
#    -e #   to specify the experiment number, e.g., -e 3 (default is 3)
#    -r #   to specify the run number, e.g., -r 4794 (default is 4794)
#    You need the '--' before these options to tell basf2 that these are options to this script.
# Output root file is bklmHists-e#r#.root
#
# DST data files are assumed to be here on kekcc:
# /ghi/fs01/belle2/bdata/Data/Raw/e0003/r04794/sub00/physics.0003.r*****.HLT2.f00000.root
# /ghi/fs01/belle2/bdata/Data/Raw/e0004/r04794/sub00/cosmic.0004.r*****.HLT2.f00000.root
# (This script cannot analyze MDST files because they don't contain RawKLMs.)

from basf2 import *
import bklmDB
import simulation
import reconstruction
import rawdata
import math
import ctypes
import ROOT
from ROOT import Belle2, TH1F, TH2F, TCanvas, THistPainter, TPad
from optparse import Option, OptionValueError, OptionParser

#=========================================================================
#
#   EventInspectorBKLM basf2 module (must be defined before use)
#
#=========================================================================

class EventInspectorBKLM(Module):

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
        super(EventInspectorBKLM, self).__init__()

    def makeGraph(self, x, y):
        graph = ROOT.TGraph()
        for i in range(0, len(x)):
            graph.SetPoint(i, x[i], y[i])
        graph.SetLineColor(2)
        graph.SetLineWidth(1)
        return graph

    def makeText(self, x, y, s):
        text = ROOT.TLatex(x, y, s)
        text.SetTextSize(0.04)
        text.SetTextColor(2)
        text.SetTextAlign(22)
        text.SetTextAngle(90)
        return text

    def initialize(self):
        self.eventDisplayCounter = 0
        print('initialize(): exp=', exp, 'run=', run)
        expRun = 'e{0:02d}r{1}: '.format(int(exp), int(run))
        self.hist_XY = ROOT.TH2F('XY', ' ;x;y', 10, -345.0, 345.0, 10, -345.0, 345.0)
        self.hist_XY.SetStats(False)
        self.hist_ZY = ROOT.TH2F('ZY', ' ;z;y', 10, -345.0, 345.0, 10, -345.0, 345.0)
        self.hist_ZY.SetStats(False)
        ROOT.gStyle.SetOptStat(10)
        self.bklmXY = []
        r0 = 201.9 + 0.5 * 4.4 ## cm
        dr = 9.1 ## cm
        tan0 = math.tan(math.pi / 8.0)
        g = ROOT.TGraph()
        g.SetPoint(0, -200.0, 0.0)
        g.SetPoint(1, +200.0, 0.0)
        g.SetLineColor(19)
        g.SetLineWidth(1)
        g.SetLineStyle(3)
        self.bklmXY.append(g)
        g = ROOT.TGraph()
        g.SetPoint(0, 0.0, -200.0)
        g.SetPoint(1, 0.0, +200.0)
        g.SetLineColor(19)
        g.SetLineWidth(1)
        g.SetLineStyle(3)
        self.bklmXY.append(g)
        g = ROOT.TGraph()
        g.SetPoint(0, -5.0,  0.0)
        g.SetPoint(1, +5.0,  0.0)
        g.SetPoint(2,  0.0,  0.0)
        g.SetPoint(3,  0.0, +5.0)
        g.SetPoint(4,  0.0, -5.0)
        g.SetLineColor(1)
        g.SetLineWidth(1)
        self.bklmXY.append(g)
        for layer in range(0, 15):
            r = r0 + layer * dr
            x = r * tan0
            g = ROOT.TGraph()
            g.SetPoint(0, +r, -x)
            g.SetPoint(1, +r, +x)
            g.SetPoint(2, +x, +r)
            g.SetPoint(3, -x, +r)
            g.SetPoint(4, -r, +x)
            g.SetPoint(5, -r, -x)
            g.SetPoint(6, -x, -r)
            g.SetPoint(7, +x, -r)
            g.SetPoint(8, +r, -x)
            if layer < 2:
                g.SetLineColor(18)
            else:
                g.SetLineColor(17)
                if (layer % 5) == 0:
                    g.SetLineStyle(3)
            g.SetLineWidth(1)
            self.bklmXY.append(g)
        self.bklmZY = []
        rF = r0 + 14 * dr
        x0 = r0 * tan0
        z0 = 47.0 ## cm
        zL = 220.0 ## cm
        g = ROOT.TGraph()
        g.SetPoint(0, -zL + z0 - 140.0, 0.0)
        g.SetPoint(1, +zL + z0 +  70.0, 0.0)
        g.SetLineColor(19)
        g.SetLineWidth(1)
        g.SetLineStyle(3)
        self.bklmZY.append(g)
        g = ROOT.TGraph()
        g.SetPoint(0, 0.0, -315.0)
        g.SetPoint(1, 0.0, +340.0)
        g.SetLineColor(19)
        g.SetLineWidth(1)
        g.SetLineStyle(3)
        self.bklmZY.append(g)
        g = ROOT.TGraph()
        g.SetPoint(0, -5.0,  0.0)
        g.SetPoint(1, +5.0,  0.0)
        g.SetPoint(2,  0.0,  0.0)
        g.SetPoint(3,  0.0, +5.0)
        g.SetPoint(4,  0.0, -5.0)
        g.SetLineColor(1)
        g.SetLineWidth(1)
        self.bklmZY.append(g)
        g = ROOT.TGraph()
        g.SetPoint(0, -zL + z0, +x0)
        g.SetPoint(1, -zL + z0, +r0)
        g.SetLineColor(18)
        g.SetLineWidth(1)
        g.SetLineStyle(3)
        self.bklmZY.append(g)
        g = ROOT.TGraph()
        g.SetPoint(0, -zL + z0, -x0)
        g.SetPoint(1, -zL + z0, -r0)
        g.SetLineColor(18)
        g.SetLineWidth(1)
        g.SetLineStyle(3)
        self.bklmZY.append(g)
        g = ROOT.TGraph()
        g.SetPoint(0, +zL + z0, +x0)
        g.SetPoint(1, +zL + z0, +r0)
        g.SetLineColor(18)
        g.SetLineWidth(1)
        g.SetLineStyle(3)
        self.bklmZY.append(g)
        g = ROOT.TGraph()
        g.SetPoint(0, +zL + z0, -x0)
        g.SetPoint(1, +zL + z0, -r0)
        g.SetLineColor(18)
        g.SetLineWidth(1)
        g.SetLineStyle(3)
        self.bklmZY.append(g)
        g = ROOT.TGraph()
        g.SetPoint(0, -zL + z0, r0)
        g.SetPoint(1, +zL + z0, r0)
        g.SetPoint(2, +zL + z0, rF)
        g.SetPoint(3, -zL + z0, rF)
        g.SetPoint(4, -zL + z0, r0)
        g.SetLineColor(18)
        g.SetLineWidth(1)
        self.bklmZY.append(g)
        g = ROOT.TGraph()
        g.SetPoint(0, -zL + z0, -r0)
        g.SetPoint(1, +zL + z0, -r0)
        g.SetPoint(2, +zL + z0, -rF)
        g.SetPoint(3, -zL + z0, -rF)
        g.SetPoint(4, -zL + z0, -r0)
        g.SetLineColor(18)
        g.SetLineWidth(1)
        self.bklmZY.append(g)
        g = ROOT.TGraph()
        g.SetPoint(0, -zL + z0, -x0)
        g.SetPoint(1, +zL + z0, -x0)
        g.SetPoint(2, +zL + z0, +x0)
        g.SetPoint(3, -zL + z0, +x0)
        g.SetPoint(4, -zL + z0, -x0)
        g.SetLineColor(18)
        g.SetLineWidth(1)
        self.bklmZY.append(g)
        # fill the readout <-> detector map from the information retrieved from the conditions database
        self.electIdToModuleId = bklmDB.fillDB()
        # maps for sectorFB <-> data concentrator
        self.sectorFBToDC = [ 11, 15, 2, 6, 10, 14, 3, 7, 9, 13, 0, 4, 8, 12, 1, 5 ]
        self.dcToSectorFB = [ 10, 14, 2, 6, 11, 15, 3, 7, 12, 8, 4, 0, 13, 9, 5, 1 ]
        # per-sector calibration adjustments (ns)
        # old self.t0Cal = 312.62 # for rawKLMs
        # old self.t0Cal2d = 293.2 # for BKLMHit2ds
        # old self.ct0Cal = -1148.01
        # old self.t0RPC = [7.85, -14.04, -5.58, -17.45, -6.34, 10.03, 13.29, 8.61, -3.3, -11.0, 0, -16.04, 4.97, 8.99, 9.64, 7.26]
        # old self.ct0Scint = [0.70, -7.40, -11.54, -8.30, 0.50, 9.11, 11.12, 8.41, 0.69, -7.64, 0, -9.10, 0.82, 6.55, 10.57, 7.19]
        self.t0Cal = 312.77 # for rawKLMs
        self.t0Cal2d = 293.64 # for BKLMHit2ds
        self.ct0Cal = 905.61
        self.ct0Cal2d = 905.61
        self.t0RPC = [8.07, -13.98, -6.73, -17.52, -4.91, 9.24, 12.83, 8.92, -1.44, -10.46, 0, -15.57, 2.44, 7.68, 9.92, 8.23]
        self.ct0Scint = [0.67, -7.70, -12.70, -9.05, 0.14, 7.12, 10.14, 7.73, 0.17, -7.92, 0, -9.10, 0.19, 5.86, 10.67, 5.51]
        self.histogramFile = ROOT.TFile.Open(histName, "RECREATE")
        # create the rawKLM histograms
        self.hist_nDigit = ROOT.TH1F('NDigit', expRun+'# of BKLMDigits', 500, -0.5, 499.5)
        self.hist_nRawKLM = ROOT.TH1F('NRawKLM', expRun+'# of RawKLMs', 10, -0.5, 9.5)
        self.hist_rawKLMnumEvents = ROOT.TH1F('RawKLMnumEvents', expRun+'RawKLM NumEvents;(should be 1)', 10, -0.5, 9.5)
        self.hist_rawKLMnumNodes = ROOT.TH1F('RawKLMnumNodes', expRun+'RawKLM NumNodes;(should be 1)', 10, -0.5, 9.5)
        self.hist_rawKLMnodeID = ROOT.TH2F('RawKLMnodeID', expRun+'RawKLM NodeID;NodeID (bklm: 1..4, eklm:5..8);Copper index', 10, -0.5, 9.5, 10, -0.5, 9.5)
        self.hist_rawKLMlaneFlag = ROOT.TH2F('rawKLMlaneFlag', expRun+'RawKLM lane vs flag;Flag (1=RPC, 2=Scint);Lane (scint: 1..7, RPC: 8..20)', 4, -0.5, 3.5, 21, -0.5, 20.5)
        self.hist_rawKLMtExtraRPC = ROOT.TH2F('rawKLMtExtraRPC', expRun+'RawKLM RPC tExtra bits;Sector # (0-7 = backward, 8-15 = forward);tExtra [should be 0]', 16, -0.5, 15.5, 32, -0.5, 31.5)
        self.hist_rawKLMqExtraRPC = ROOT.TH2F('rawKLMqExtraRPC', expRun+'RawKLM RPC qExtra bits;Sector # (0-7 = backward, 8-15 = forward);qExtra [should be 0]', 16, -0.5, 15.5, 16, -0.5, 15.5)
        self.hist_rawKLMtExtraScint = ROOT.TH2F('rawKLMtExtraScint', expRun+'RawKLM Scint tExtra bits;Sector # (0-7 = backward, 8-15 = forward);tExtra [should be 0]', 16, -0.5, 15.5, 32, -0.5, 31.5)
        self.hist_rawKLMqExtraScint = ROOT.TH2F('rawKLMqExtraScint', expRun+'RawKLM Scint qExtra bits;Sector # (0-7 = backward, 8-15 = forward);qExtra [should be 0]', 16, -0.5, 15.5, 16, -0.5, 15.5)
        self.hist_rawKLMsizeMultihit = ROOT.TH1F('rawKLMsizeMultihit', expRun+'RawKLM word count (N/channel)', 400, -0.5, 799.5)
        self.hist_rawKLMsize = ROOT.TH1F('rawKLMsize', expRun+'RawKLM word count (1/channel)', 200, -0.5, 199.5)
        self.hist_rawKLMsizeByDCMultihit = []
        self.hist_rawKLMsizeByDC = []
        for dc in range(0, 16):
            copper = dc & 0x03
            finesse = dc >> 2
            label = 'rawKLM{0}{1}sizeMultihit'.format(copper, finesse)
            title = '{0}rawKLM[{1}] finesse[{2}] word count (N/channel)'.format(expRun, copper, finesse)
            self.hist_rawKLMsizeByDCMultihit.append(ROOT.TH1F(label, title, 100, -0.5, 99.5))
            label = 'rawKLM{0}{1}size'.format(copper, finesse)
            title = '{0}rawKLM[{1}] finesse[{2}] word count (1/channel)'.format(expRun, copper, finesse)
            self.hist_rawKLMsizeByDC.append(ROOT.TH1F(label, title, 100, -0.5, 99.5))
        self.hist_rawKLMchannelMultiplicity = []
        self.hist_rawKLMchannelMultiplicityFine = []
        for dc in range(0, 16):
            sectorFB = self.dcToSectorFB[dc]
            copper = dc & 0x03
            finesse = dc >> 2
            label = 'rawKLM{0}{1}channelMultiplicity'.format(copper, finesse)
            title = '{0}RawKLM[{1}] finesse[{2}] sector {3} per-channel multiplicity (N/channel > 1);Per-channel multiplicity;(Lane #) * 2 + (Axis #)'.format(expRun, copper, finesse, sectorFB)
            self.hist_rawKLMchannelMultiplicity.append(ROOT.TH2F(label, title, 30, -0.5, 29.5, 42, -0.5, 41.5))
            label = 'rawKLM{0}{1}channelMultiplicityFine'.format(copper, finesse)
            title = '{0}RawKLM[{1}] finesse[{2}] sector {3} per-channel multiplicity (N/channel > 1);Per-channel multiplicity;(Lane #) * 256 + (Axis #) * 128 + (Channel #)'.format(expRun, copper, finesse, sectorFB)
            self.hist_rawKLMchannelMultiplicityFine.append(ROOT.TH2F(label, title, 30, -0.5, 29.5, 8192, -0.5, 8191.5))
        self.hist_mappedSectorOccupancyMultihit = ROOT.TH1F('mappedSectorOccupancyMultihit', expRun+'Sector occupancy of mapped channels (N/channel);Sector # (0-7 = backward, 8-15 = forward)', 16, -0.5, 15.5)
        self.hist_unmappedSectorOccupancyMultihit = ROOT.TH1F('unmappedSectorOccupancyMultihit', expRun+'Sector occupancy of unmapped channels (N/channel);Sector # (0-7 = backward, 8-15 = forward)', 16, -0.5, 15.5)
        self.hist_mappedSectorOccupancy = ROOT.TH1F('mappedSectorOccupancy', expRun+'Sector occupancy of mapped channels (1/channel);Sector # (0-7 = backward, 8-15 = forward)', 16, -0.5, 15.5)
        self.hist_unmappedSectorOccupancy = ROOT.TH1F('unmappedSectorOccupancy', expRun+'Sector occupancy of unmapped channels (1/channel);Sector # (0-7 = backward, 8-15 = forward)', 16, -0.5, 15.5)
        self.hist_mappedRPCSectorOccupancy = ROOT.TH1F('mappedRPCSectorOccupancy', expRun+'Sector occupancy of mapped RPC channels (1/channel);Sector # (0-7 = backward, 8-15 = forward)', 16, -0.5, 15.5)
        self.hist_mappedRPCLaneAxisOccupancy = ROOT.TH2F('mappedRPCLaneAxisOccupancy', expRun+'Lane/axis occupancy of mapped RPC channels (1/channel);Sector # (0-7 = backward, 8-15 = forward);(Lane #) * 2 + (Axis #)', 16, -0.5, 15.5, 42, -0.5, 41.5)
        self.hist_unmappedRPCSectorOccupancy = ROOT.TH1F('unmappedRPCSectorOccupancy', expRun+'Sector occupancy of unmapped RPC channels (1/channel);Sector # (0-7 = backward, 8-15 = forward)', 16, -0.5, 15.5)
        self.hist_unmappedRPCLaneAxisOccupancy = ROOT.TH2F('unmappedRPCLaneAxisOccupancy', expRun+'Lane/axis occupancy of unmapped RPC channels (1/channel);Sector # (0-7 = backward, 8-15 = forward);(Lane #) * 2 + (Axis #)', 16, -0.5, 15.5, 42, -0.5, 41.5)
        self.hist_mappedScintSectorOccupancy = ROOT.TH1F('mappedScintSectorOccupancy', expRun+'Sector occupancy of mapped scint channels (1/channel);Sector # (0-7 = backward, 8-15 = forward)', 16, -0.5, 15.5)
        self.hist_mappedScintLaneAxisOccupancy = ROOT.TH2F('mappedScintLaneAxisOccupancy', expRun+'Lane/axis occupancy of mapped scint channels (1/channel);Sector # (0-7 = backward, 8-15 = forward);(Lane #) * 2 + (Axis #)', 16, -0.5, 15.5, 42, -0.5, 41.5)
        self.hist_unmappedScintSectorOccupancy = ROOT.TH1F('unmappedScintSectorOccupancy', expRun+'Sector occupancy of unmapped scint channels (1/channel);Sector # (0-7 = backward, 8-15 = forward)', 16, -0.5, 15.5)
        self.hist_unmappedScintLaneAxisOccupancy = ROOT.TH2F('unmappedScintLaneAxisOccupancy', expRun+'Lane/axis occupancy of unmapped scint channels (1/channel);Sector # (0-7 = backward, 8-15 = forward);(Lane #) * 2 + (Axis #)', 16, -0.5, 15.5, 42, -0.5, 41.5)
        self.hist_mappedChannelOccupancyPrompt = [ [0, 0], [0, 0], [0, 0], [0, 0], [0, 0], [0, 0], [0, 0], [0, 0], [0, 0], [0, 0], [0, 0], [0, 0], [0, 0], [0, 0], [0, 0], [0, 0] ]
        self.hist_mappedChannelOccupancyBkgd = [ [0, 0], [0, 0], [0, 0], [0, 0], [0, 0], [0, 0], [0, 0], [0, 0], [0, 0], [0, 0], [0, 0], [0, 0], [0, 0], [0, 0], [0, 0], [0, 0] ]
        self.hist_unmappedChannelOccupancy = [ [0, 0], [0, 0], [0, 0], [0, 0], [0, 0], [0, 0], [0, 0], [0, 0], [0, 0], [0, 0], [0, 0], [0, 0], [0, 0], [0, 0], [0, 0], [0, 0] ]
        for sectorFB in range(0, 16):
            label = 'mappedChannelOccupancy_a0s{0}Prompt'.format(sectorFB)
            title = '{0}In-time mapped channel occupancy for axis 0 sector {1};lane;channel'.format(expRun, sectorFB)
            self.hist_mappedChannelOccupancyPrompt[sectorFB][0] = ROOT.TH2F(label, title, 42, -0.25, 20.75, 128, -0.25, 63.75)
            label = 'mappedChannelOccupancy_a0s{0}Bkgd'.format(sectorFB)
            title = '{0}Out-of-time mapped channel occupancy for axis 0 sector {1};lane;channel'.format(expRun, sectorFB)
            self.hist_mappedChannelOccupancyBkgd[sectorFB][0] = ROOT.TH2F(label, title, 42, -0.25, 20.75, 128, -0.25, 63.75)
            label = 'unmappedChannelOccupancy_a0s{0}'.format(sectorFB)
            title = '{0}Unmapped channel occupancy for axis 0 sector {1};lane;channel'.format(expRun, sectorFB)
            self.hist_unmappedChannelOccupancy[sectorFB][0] = ROOT.TH2F(label, title, 42, -0.25, 20.75, 128, -0.25, 63.75)
            label = 'mappedChannelOccupancy_a1s{0}Prompt'.format(sectorFB)
            title = '{0}In-time mapped occupancy for axis 1 sector {1};lane;channel'.format(expRun, sectorFB)
            self.hist_mappedChannelOccupancyPrompt[sectorFB][1] = ROOT.TH2F(label, title, 42, -0.25, 20.75, 128, -0.25, 63.75)
            label = 'mappedChannelOccupancy_a1s{0}Bkgd'.format(sectorFB)
            title = '{0}Out-of-time mapped occupancy for axis 1 sector {1};lane;channel'.format(expRun, sectorFB)
            self.hist_mappedChannelOccupancyBkgd[sectorFB][1] = ROOT.TH2F(label, title, 42, -0.25, 20.75, 128, -0.25, 63.75)
            label = 'unmappedChannelOccupancy_a1s{0}'.format(sectorFB)
            title = '{0}Unmapped channel occupancy for axis 1 sector {1};lane;channel'.format(expRun, sectorFB)
            self.hist_unmappedChannelOccupancy[sectorFB][1] = ROOT.TH2F(label, title, 42, -0.25, 20.75, 128, -0.25, 63.75)
        self.hist_RPCTimeLowBitsBySector = ROOT.TH2F('RPCTimeLowBitsBySector', expRun+'RPC TDC lowest-order bits;Sector # (0-7 = backward, 8-15 = forward);TDC % 4 (ns) [should be 0]', 16, -0.5, 15.5, 4, -0.5, 3.5)
        self.hist_mappedRPCTime = ROOT.TH1F('mappedRPCTime', expRun+'RPC mapped-strip time distribution;t - ct(trigger) (ns)', 256, -0.5, 1023.5)
        self.hist_mappedRPCTimeCal = ROOT.TH1F('mappedRPCTimeCal', expRun+'RPC mapped-strip time distribution;t - ct(trigger) - dt(sector) (ns)', 256, -0.5, 1023.5)
        self.hist_mappedRPCTimeCal2 = ROOT.TH1F('mappedRPCTimeCal2', expRun+'RPC mapped-strip time distribution;t - ct(trigger) - dt(sector) - t(index) (ns)', 256, -0.5, 1023.5)
        self.hist_mappedRPCTimePerSector = []
        self.hist_mappedRPCTimePerLayer = []
        for sectorFB in range(0, 16):
            label = 'mappedRPCTime_S{0:02d}'.format(sectorFB)
            title = '{0}RPC sector {1} time distribution;t - ct(trigger) (ns)'.format(expRun, sectorFB)
            self.hist_mappedRPCTimePerSector.append(ROOT.TH1F(label, title, 256, -0.5, 1023.5))
            self.hist_mappedRPCTimePerLayer.append([0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0])
            for layer in range(0, 15):
                label = 'mappedRPCTime_S{0:02d}L{1:02d}'.format(sectorFB, layer)
                title = '{0}RPC sector {1} layer {2} time distribution;t - ct(trigger) (ns)'.format(expRun, sectorFB, layer)
                self.hist_mappedRPCTimePerLayer[sectorFB][layer] = ROOT.TH1F(label, title, 256, -0.5, 1023.5)
        self.hist_mappedRPCTimeBySector = ROOT.TH2F('mappedRPCTimeBySector', expRun+'RPC mapped-strip time;Sector # (0-7 = backward, 8-15 = forward);t - ct(trigger) (ns)', 16, -0.5, 15.5, 128, -0.5, 1023.5)
        self.hist_mappedRPCTimeCalBySector = ROOT.TH2F('mappedRPCTimeCalBySector', expRun+'RPC mapped-strip time;Sector # (0-7 = backward, 8-15 = forward);t - ct(trigger) - dt(sector) (ns)', 16, -0.5, 15.5, 128, -0.5, 1023.5)
        self.hist_mappedRPCCtimeRangeBySector = ROOT.TH2F('mappedRPCCtimeRangeBySector', expRun+'RPC ctime-range in event;Sector # (0-7 = backward, 8-15 = forward);ctimeMax - ctimeMin (ns)', 16, -0.5, 15.5, 128, -0.5, 8191.5)
        self.hist_unmappedRPCTime = ROOT.TH1F('unmappedRPCTime', expRun+'RPC unmapped-strip time distribution;t - ct(trigger) (ns)', 256, -0.5, 1023.5)
        self.hist_unmappedRPCTimeBySector = ROOT.TH2F('unmappedRPCTimeBySector', expRun+'RPC unmapped-strip time;Sector # (0-7 = backward, 8-15 = forward);t - ct(trigger) (ns)', 16, -0.5, 15.5, 128, -0.5, 1023.5)
        self.hist_ScintTimeLowBitsBySector = ROOT.TH2F('ScintTimeLowBitsbySector', expRun+'Scint TDC lowest-order bits;Sector # (0-7 = backward, 8-15 = forward);TDC % 4 (ns)', 16, -0.5, 15.5, 4, -0.5, 3.5)
        self.hist_mappedScintCtime0 = ROOT.TH1F('mappedScintCtime0', expRun+'Scint mapped-strip ctime distribution;ctime (ns)', 32, -0.5, 1023.5)
        self.hist_mappedScintCtime1 = ROOT.TH2F('mappedScintCtime1', expRun+'Scint mapped-strip ctime distribution;Sector # (0-7 = backward, 8-15 = forward);ctime (ns)', 16, -0.5, 15.5, 32, -0.5, 1023.5)
        self.hist_mappedScintCtime = ROOT.TH1F('mappedScintCtime', expRun+'Scint mapped-strip ctime distribution;ctime - ct(trigger) (ns)', 32, -0.5, 1023.5)
        self.hist_mappedScintCtimeBySector = ROOT.TH2F('mappedScintCtimeBySector', expRun+'Scint mapped-strip ctime;Sector # (0-7 = backward, 8-15 = forward);ctime - ct(trigger) (ns)', 16, -0.5, 15.5, 32, -0.5, 1023.5)
        self.hist_mappedScintCtimeCal = ROOT.TH1F('mappedScintCtimeCal', expRun+'Scint mapped-strip ctime distribution;ctime - ct(trigger) - dt(sector) (ns)', 32, -0.5, 1023.5)
        self.hist_mappedScintCtimeCalBySector = ROOT.TH2F('mappedScintCtimeCalBySector', expRun+'Scint mapped-strip ctime;Sector # (0-7 = backward, 8-15 = forward);ctime - ct(trigger) - dt(sector) (ns)', 16, -0.5, 15.5, 32, -0.5, 1023.5)
        self.hist_mappedScintCtimePerSector = []
        self.hist_mappedScintCtimePerLayer = []
        for sectorFB in range(0, 16):
            label = 'mappedScintCtime_S{0:02d}'.format(sectorFB)
            title = '{0}Scint sector {1} ctime distribution;ctime - ct(trigger) (ns)'.format(expRun, sectorFB)
            self.hist_mappedScintCtimePerSector.append(ROOT.TH1F(label, title, 32, -0.5, 1023.5))
            self.hist_mappedScintCtimePerLayer.append([0, 0])
            for layer in range(0, 2):
                label = 'mappedScintCtime_S{0:02d}L{1:02d}'.format(sectorFB, layer)
                title = '{0}Scint sector {1} layer {2} ctime distribution;ctime - ct(trigger) (ns)'.format(expRun, sectorFB, layer)
                self.hist_mappedScintCtimePerLayer[sectorFB][layer] = ROOT.TH1F(label, title, 32, -0.5, 1023.5)
        self.hist_mappedScintCtimeRangeBySector = ROOT.TH2F('mappedScintCtimeRangeBySector', expRun+'Scint ctime-range in event;Sector # (0-7 = backward, 8-15 = forward);ctimeMax - ctimeMin (ns)', 16, -0.5, 15.5, 128, -0.5, 8191.5)
        self.hist_unmappedScintCtime = ROOT.TH1F('unmappedScintCtime', expRun+'Scint unmapped-strip ctime distribution;ctime - ct(trigger) (ns)', 32, -0.5, 1023.5)
        self.hist_unmappedScintCtimeBySector = ROOT.TH2F('unmappedScintCtimeBySector', expRun+'Scint unmapped-strip ctime;Sector # (0-7 = backward, 8-15 = forward);ctime - ct(trigger) (ns)', 16, -0.5, 15.5, 32, -0.5, 1023.5)
        self.hist_mappedScintTDC = ROOT.TH1F('mappedScintTDC', expRun+'Scint mapped-strip TDC distribution;t (ns)', 32, -0.5, 31.5)
        self.hist_mappedScintTime = ROOT.TH1F('mappedScintTime', expRun+'Scint mapped-strip time distribution;t - ct(trigger) (ns)', 32, -0.5, 31.5)
        self.hist_mappedScintTDCBySector = ROOT.TH2F('mappedScintTDCBySector', expRun+'Scint mapped-strip TDC;Sector # (0-7 = backward, 8-15 = forward);t (ns)', 16, -0.5, 15.5, 32, -0.5, 31.5)
        self.hist_mappedScintTimeBySector = ROOT.TH2F('mappedScintTimeBySector', expRun+'Scint mapped-strip time;Sector # (0-7 = backward, 8-15 = forward);t - ct(trigger) (ns)', 16, -0.5, 15.5, 32, -0.5, 31.5)
        self.hist_unmappedScintTime = ROOT.TH1F('unmappedScintTime', expRun+'Scint unmapped-strip time distribution;t - ct(trigger) (ns)', 32, -0.5, 31.5)
        self.hist_unmappedScintTimeBySector = ROOT.TH2F('unmappedScintTimeBySector', expRun+'Scint unmapped-strip time;Sector # (0-7 = backward, 8-15 = forward);t - ct(trigger) (ns)', 16, -0.5, 15.5, 32, -0.5, 31.5)
        # Create the BKLMHit1d-related histograms
        self.hist_nHit1d = ROOT.TH1F('NHit1d', expRun+'# of BKLMHit1ds', 100, -0.5, 99.5)
        self.hist_nHit1dRPCPrompt = ROOT.TH1F('NHit1dRPCPrompt', expRun+'# of prompt RPC BKLMHit1ds', 100, -0.5, 99.5)
        self.hist_nHit1dRPCBkgd = ROOT.TH1F('NHit1dRPCBkgd', expRun+'# of background RPC BKLMHit1ds', 100, -0.5, 99.5)
        self.hist_nHit1dScint = ROOT.TH1F('NHit1dScint', expRun+'# of scintillator BKLMHit1ds', 100, -0.5, 99.5)
        self.hist_nHit1dPrompt = ROOT.TH1F('NHit1dPrompt', expRun+'# of prompt BKLMHit1ds', 100, -0.5, 99.5)
        self.hist_nHit1dBkgd = ROOT.TH1F('NHit1dBkgd', expRun+'# of bkgd BKLMHit1ds', 100, -0.5, 99.5)
        self.hist_n1dPhiZ = ROOT.TH2F('NHit1dPhiZ', expRun+'Distribution of BKLMHit1ds;# of phi BKLMHit1ds;# of z BKLMHit1ds', 60, -0.5, 59.5, 60, -0.5, 59.5)
        self.hist_multiplicityPhiBySector = ROOT.TH2F('Hit1dMultiplicityPhiBySector', expRun+'BKLMHit1d phi-strip multiplicity;sector # (0-7 = backward, 8-15 = forward);# of strips', 16, -0.5, 15.5, 8, -0.5, 7.5)
        self.hist_multiplicityZBySector = ROOT.TH2F('Hit1dMultiplicityZBySector', expRun+'BKLMHit1d z-strip multiplicity;sector # (0-7 = backward, 8-15 = forward);# of strips', 16, -0.5, 15.5, 8, -0.5, 7.5)
        self.hist_tphiRPCCal1d = ROOT.TH1F('tphiRPCCal1d', expRun+'RPC BKLMHit1d phi-strip time distribution;t(phi) - ct(trigger) - dt(sector) (ns)', 256, -0.5, 1023.5)
        self.hist_tzRPCCal1d = ROOT.TH1F('tzRPCCal1d', expRun+'RPC BKLMHit1d z-strip time distribution;t(z) - ct(trigger) - dt(sector) (ns)', 256, -0.5, 1023.5)
        self.hist_tRPCCal1d = ROOT.TH1F('tRPCCal1d', expRun+'RPC BKLMHit1d x 2 calibrated average-time distribution;0.5*[t(phi) + t(z)] - ct(trigger) - dt(sector) (ns)', 256, -0.5, 1023.5)
        self.hist_dtRPC1d = ROOT.TH1F('dtRPC1d', expRun+'RPC BKLMHit1d x 2 time-difference distribution;t(phi) - t(z) (ns)', 50, -100.0, 100.0)
        self.hist_tphiScintCal1d = ROOT.TH1F('tphiScintCal1d', expRun+'Scintillator BKLMHit1d phi-strip ctime distribution;ctime(phi) - ct(trigger) - dt(sector) (ns)', 128, -0.5, 1023.5)
        self.hist_tzScintCal1d = ROOT.TH1F('tzScintCal1d', expRun+'Scintillator BKLMHit1d z-strip ctime distribution;ctime(z) - ct(trigger) - dt(sector) (ns)', 128, -0.5, 1023.5)
        self.hist_tScintCal1d = ROOT.TH1F('tScintCal1d', expRun+'Scintillator BKLMHit1d x 2 calibrated average-time distribution;0.5*[ctime(phi) + ctime(z)] - ct(trigger) - dt(sector) (ns)', 128, -0.5, 1023.5)
        self.hist_dtScint1d = ROOT.TH1F('dtScint1d', expRun+'Scintillator BKLMHit1d x 2 time-difference distribution;ctime(phi) - ctime(z) (ns)', 50, -100.0, 100.0)
        # Create the BKLMHit2d-related histograms
        self.hist_nHit2d = ROOT.TH1F('NHit2d', expRun+'# of BKLMHit2ds', 50, -0.5, 49.5)
        self.hist_hit2dOutOfTime = ROOT.TH1F('NHit2dOutOfTime', expRun+'BKLMHit2d out-of-time flag', 2, -0.5, 1.5)
        self.hist_hit2dOnTrack = ROOT.TH1F('NHit2dOnTrack', expRun+'BKLMHit2d on-ext-track flag', 2, -0.5, 1.5)
        self.hist_hit2dOnStaTrack = ROOT.TH1F('NHit2dOnStaTrack', expRun+'BKLMHit2d on-standalone-track flag', 2, -0.5, 1.5)
        self.hist_occupancyForwardXYPrompt = ROOT.TH2F('occupancyForwardXYPrompt', expRun+'Forward xy RPC occupancy for in-time hits;x(cm);y(cm)', 230, -345.0, 345.0, 230, -345.0, 345.0)
        self.hist_occupancyBackwardXYPrompt = ROOT.TH2F('occupancyBackwardXYPrompt', expRun+'Backward xy RPC occupancy for in-time hits;x(cm);y(cm)', 230, -345.0, 345.0, 230, -345.0, 345.0)
        self.hist_occupancyForwardXYBkgd = ROOT.TH2F('occupancyForwardXYBkgd', expRun+'Forward xy RPC occupancy for out-of-time hits;x(cm);y(cm)', 230, -345.0, 345.0, 230, -345.0, 345.0)
        self.hist_occupancyBackwardXYBkgd = ROOT.TH2F('occupancyBackwardXYBkgd', expRun+'Backward xy RPC occupancy for out-of-time hits;x(cm);y(cm)', 230, -345.0, 345.0, 230, -345.0, 345.0)
        self.hist_occupancyRZPrompt = ROOT.TH2F('occupancyRZPrompt', expRun+'layer-z occupancy for in-time hits;z(cm);layer', 48, -190.0, 290.0, 16, -0.5, 15.5)
        self.hist_occupancyZPrompt = ROOT.TH1F('occupancyZPrompt', expRun+'z occupancy for in-time hits;z(cm)', 48, -190.0, 290.0)
        self.hist_occupancyRPrompt = ROOT.TH1F('occupancyRPrompt', expRun+'layer occupancy for in-time hits;layer', 16, -0.5, 15.5)
        self.hist_occupancyRZBkgd = ROOT.TH2F('occupancyRZBkgd', expRun+'layer-z occupancy for out-of-time hits;z(cm);layer', 48, -190.0, 290.0, 16, -0.5, 15.5)
        self.hist_occupancyZBkgd = ROOT.TH1F('occupancyZBkgd', expRun+'z occupancy for out-of-time hits;z(cm)', 48, -190.0, 290.0)
        self.hist_occupancyRBkgd = ROOT.TH1F('occupancyRBkgd', expRun+'layer occupancy for out-of-time hits;layer', 16, -0.5, 15.5)
        self.hist_ctimeRPCtCal = ROOT.TH2F('ctimeRPCtCal', expRun+'RPC tCal vs ctime;t - ct(trigger) - dt(sector) (ns);ctime - minCtime', 16, 281.5, 345.5, 16, -0.5, 255.5)
        self.hist_ctimeRPCtCal2 = ROOT.TH2F('ctimeRPCtCal2', expRun+'RPC tCal vs ctime;t - ct(trigger) - dt(sector) - dt(index) (ns);ctime - minCtime', 16, 281.5, 345.5, 16, -0.5, 255.5)
        self.hist_jRPCtCal = ROOT.TH2F('jRPCtCal', expRun+'RPC tCal vs hit index;t - ct(trigger) - dt(sector) (ns);Hit index', 16, 281.5, 345.5, 50, -0.5, 49.5)
        self.hist_jRPCtCal2 = ROOT.TH2F('jRPCtCal2', expRun+'RPC tCal vs hit index;t - ct(trigger) - dt(sector) - dt(index) (ns);Hit index', 16, 281.5, 345.5, 50, -0.5, 49.5)
        self.hist_tRPCCal2d = ROOT.TH1F('tRPCCal2d', expRun+'RPC BKLMHit2d time distribution;t - ct(trigger) - dt(sector) (ns)', 256, -0.5, 1023.5)
        self.hist_tRPCCal2dBySector = ROOT.TH2F('tRPCCal2dBySector', expRun+'RPC BKLMHit2d time distribution;sector # (0-7 = backward, 8-15 = forward);t - ct(trigger) - dt(sector) (ns)', 16, -0.5, 15.5, 256, -0.5, 1023.5)
        self.hist_ctScintCal2d = ROOT.TH1F('ctScintCal2d', expRun+'Scint BKLMHit2d ctime distribution;ct - ct(trigger) - dt(sector) (ns)', 128, -0.5, 1023.5)
        self.hist_ctScintCal2dBySector = ROOT.TH2F('ctScintCal2dBySector', expRun+'Scint BKLMHit2d ctime distribution;sector # (0-7 = backward, 8-15 = forward);ct - ct(trigger) - dt(sector) (ns)', 16, -0.5, 15.5, 128, -0.5, 1023.5)

    def terminate(self):
        for sectorFB in range(0, 16):
            mappedScintSectorOccupancy = self.hist_mappedScintSectorOccupancy.GetBinContent(sectorFB+1)
            if mappedScintSectorOccupancy > 0:
                for laneAxis in range(0, 42):
                    numerator = self.hist_mappedScintLaneAxisOccupancy.GetBinContent(sectorFB+1, laneAxis+1)
                    self.hist_mappedScintLaneAxisOccupancy.SetBinContent(sectorFB+1, laneAxis+1, 100.0 * numerator / mappedScintSectorOccupancy)
            mappedRPCSectorOccupancy = self.hist_mappedRPCSectorOccupancy.GetBinContent(sectorFB+1)
            if mappedRPCSectorOccupancy > 0:
                for laneAxis in range(0, 42):
                    numerator = self.hist_mappedRPCLaneAxisOccupancy.GetBinContent(sectorFB+1, laneAxis+1)
                    self.hist_mappedRPCLaneAxisOccupancy.SetBinContent(sectorFB+1, laneAxis+1, 100.0 * numerator / mappedRPCSectorOccupancy)
            unmappedScintSectorOccupancy = self.hist_unmappedScintSectorOccupancy.GetBinContent(sectorFB+1)
            if unmappedScintSectorOccupancy > 0:
                for laneAxis in range(0, 42):
                    numerator = self.hist_unmappedScintLaneAxisOccupancy.GetBinContent(sectorFB+1, laneAxis+1)
                    self.hist_unmappedScintLaneAxisOccupancy.SetBinContent(sectorFB+1, laneAxis+1, 100.0 * numerator / unmappedScintSectorOccupancy)
            unmappedRPCSectorOccupancy = self.hist_unmappedRPCSectorOccupancy.GetBinContent(sectorFB+1)
            if unmappedRPCSectorOccupancy > 0:
                for laneAxis in range(0, 42):
                    numerator = self.hist_unmappedRPCLaneAxisOccupancy.GetBinContent(sectorFB+1, laneAxis+1)
                    self.hist_unmappedRPCLaneAxisOccupancy.SetBinContent(sectorFB+1, laneAxis+1, 100.0 * numerator / unmappedRPCSectorOccupancy)
        #if maxEventCounter > 0:
         #   self.eventCanvas.Clear()
          #  self.eventCanvas.SaveAs(eventPdfName)
           # title = '{0}]'.format(eventPdfName)
            #self.eventCanvas.SaveAs(title)
                
        
        
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
        digits = Belle2.PyStoreArray('BKLMDigits')
        hit1ds = Belle2.PyStoreArray('BKLMHit1ds')
        hit2ds = Belle2.PyStoreArray('BKLMHit2ds')
        self.hist_nRawKLM.Fill(len(rawklms))
        self.hist_nDigit.Fill(len(digits))
        self.hist_nHit1d.Fill(len(hit1ds))
        self.hist_nHit2d.Fill(len(hit2ds))

        tCal1d = []
        for hit1d in hit1ds:
            tCal1d.append(hit1d.getTime())
        tCal2d = []
        for hit2d in hit2ds:
            tCal2d.append(hit2d.getTime())

        countAllMultihit = 0
        countAll = 0
        count = [ 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0 ]
        rawFb     = [ [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [] ]
        rawSector = [ [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [] ]
        rawLayer  = [ [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [] ]
        rawPlane  = [ [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [] ]
        rawStrip  = [ [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [] ]
        rawCtime  = [ [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [] ]
        for copper in range(0, len(rawklms)):
            rawklm = rawklms[copper]
            self.hist_rawKLMnumEvents.Fill(rawklm.GetNumEvents())
            self.hist_rawKLMnumNodes.Fill(rawklm.GetNumNodes())
            if rawklm.GetNumEntries() != 1:
                print('##0 Event', event, 'copper', copper, ' getNumEntries=', rawklm.GetNumEntries())
                continue
            nodeID = rawklm.GetNodeID(0) - self.BKLM_ID
            if nodeID >= self.EKLM_ID - self.BKLM_ID:
                nodeID = nodeID - (self.EKLM_ID - self.BKLM_ID) + 4
            self.hist_rawKLMnodeID.Fill(nodeID, copper)
            if (nodeID < 0) or (nodeID > 4): # skip EKLM nodes
                continue
            trigCtime0 = (rawklm.GetTTCtime(0) & 0x7ffffff) << 3 # (ns)
            x = (rawklm.GetTrailerChksum(0) & 0x0ffff) << 0 # (ns?)
            for finesse in range(0, 4):
                dc = (finesse << 2) + copper
                n = rawklm.GetDetectorNwords(0, finesse)
                countAllMultihit = countAllMultihit + n
                self.hist_rawKLMsizeByDCMultihit[dc].Fill(n)
                bufSlot = rawklm.GetDetectorBuffer(0, finesse)
                if n > 0:
                    lastWord = bufSlot[n-1]
                    if lastWord & 0xffff != 0:
                        print("##1 Event", event, 'copper', copper, 'finesse', finesse, 'n=', n, 'lastWord=', hex(lastWord))
                    if (n % 2) == 0:
                        print("##2 Event", event, 'copper', copper, 'finesse', finesse, 'n=', n, 'should be odd -- skipping')
                    else:
                        xxx = ((lastWord >> 16) << 3) & 0xffff ## DIVOT
                        if int(exp) == 3:
                            xxx =  trigCtime0 - 0x3b0
                        ##DIVOT print("event {0} node {1} finesse {2}: trigCtime = {3:04x} trigTime = {4:04x} diff = {5:04x}".format(event, nodeID, finesse, (trigCtime0 & 0xffff), (xxx & 0xffff), ((trigCtime0 - xxx) & 0xffff)))
                        trigCtime = xxx
                        countAll = countAll + 1
                        count[dc] = count[dc] + 1
                        sectorFB = self.dcToSectorFB[dc]
                        n = n >> 1
                        channelMultiplicity = { }
                        minCtime = 99999
                        minRPCCtime = 99999
                        maxRPCCtime = 0
                        minScintCtime = 99999
                        maxScintCtime = 0
                        for j in range(0, n):
                            word0 = bufSlot[j*2]
                            word1 = bufSlot[j*2+1]
                            laneAxisChannel = (word0 >> 16) & 0x1fff
                            if laneAxisChannel not in channelMultiplicity:
                                countAll = countAll + 2
                                count[dc] = count[dc] + 2
                                channelMultiplicity[laneAxisChannel] = 0
                            channelMultiplicity[laneAxisChannel] = channelMultiplicity[laneAxisChannel] + 1
                            ctime   =  word0        & 0xffff
                            channel = (word0 >> 16) & 0x7f
                            axis    = (word0 >> 23) & 0x01
                            lane    = (word0 >> 24) & 0x1f # crate's slot number
                            flag    = (word0 >> 30) & 0x03
                            charge  =  word1        & 0x0fff
                            tExtra  = (word1 >> 27) & 0x1f
                            qExtra  = (word1 >> 12) & 0x0f
                            isRPC = (flag == 1)
                            isScint = (flag == 2)
                            if (int(exp) <= 3) and (lane <= 2):
                                trigCtx = trigCtime >> 3
                                ctime = trigCtx - ((trigCtx - ctime) << 2)
                            if (ctime < minCtime) and (lane > 2):
                                minCtime = ctime
                            self.hist_rawKLMlaneFlag.Fill(flag, lane)
                            if isRPC:
                                self.hist_rawKLMtExtraRPC.Fill(sectorFB, tExtra)
                                self.hist_rawKLMqExtraRPC.Fill(sectorFB, qExtra)
                            elif isScint:
                                self.hist_rawKLMtExtraScint.Fill(sectorFB, tExtra)
                                self.hist_rawKLMqExtraScint.Fill(sectorFB, qExtra)
                            fb = -1
                            sector = -1
                            layer = -1
                            plane = -1
                            strip = -1
                            electId = (channel << 12) | (axis << 11) | (lane << 6) | (finesse << 4) | nodeID
                            if electId in self.electIdToModuleId:
                                if isRPC:
                                    if ctime < minRPCCtime:
                                        minRPCCtime = ctime
                                    if ctime > maxRPCCtime:
                                        maxRPCCtime = ctime
                                elif isScint:
                                    if ctime < minScintCtime:
                                        minScintCtime = ctime
                                    if ctime > maxScintCtime:
                                        maxScintCtime = ctime
                                self.hist_mappedSectorOccupancyMultihit.Fill(sectorFB)
                                moduleId = self.electIdToModuleId[electId]
                                fb = (moduleId & self.BKLM_END_MASK) >> self.BKLM_END_BIT
                                sector = (moduleId & self.BKLM_SECTOR_MASK) >> self.BKLM_SECTOR_BIT
                                layer = (moduleId & self.BKLM_LAYER_MASK) >> self.BKLM_LAYER_BIT
                                plane = (moduleId & self.BKLM_PLANE_MASK) >> self.BKLM_PLANE_BIT
                                strip = (moduleId & self.BKLM_STRIP_MASK) >> self.BKLM_STRIP_BIT
                            else:
                                self.hist_unmappedSectorOccupancyMultihit.Fill(sectorFB)
                            rawFb[dc].append(fb)
                            rawSector[dc].append(sector)
                            rawLayer[dc].append(layer)
                            rawPlane[dc].append(plane)
                            rawStrip[dc].append(strip)
                            rawCtime[dc].append(ctime)
                        if n > 1:
                            if maxRPCCtime > 0:
                                self.hist_mappedRPCCtimeRangeBySector.Fill(sectorFB, (maxRPCCtime - minRPCCtime) << 3)
                            if maxScintCtime > 0:
                                self.hist_mappedScintCtimeRangeBySector.Fill(sectorFB, (maxScintCtime - minScintCtime) << 3)
                        for j in range(0, n):
                            word0 = bufSlot[j*2]
                            word1 = bufSlot[j*2+1]
                            laneAxisChannel = (word0 >> 16) & 0x1fff
                            if laneAxisChannel in channelMultiplicity:
                                if channelMultiplicity[laneAxisChannel] > 1:
                                    axis    = (word0 >> 23) & 0x01
                                    lane    = (word0 >> 24) & 0x1f # crate's slot number (1..7 for scints, 8..20 for RPCs)
                                    laneAxis = axis if ((lane < 1) or (lane > 20)) else ((lane << 1) + axis)
                                    self.hist_rawKLMchannelMultiplicity[dc].Fill(channelMultiplicity[laneAxisChannel], laneAxis)
                                    self.hist_rawKLMchannelMultiplicityFine[dc].Fill(channelMultiplicity[laneAxisChannel], laneAxisChannel)
                                ### DIVOT del channelMultiplicity[laneAxisChannel] # consider only first hit in the channel/axis/lane of this dc
                                ctime   =  word0        & 0xffff
                                channel = (word0 >> 16) & 0x7f
                                axis    = (word0 >> 23) & 0x01
                                lane    = (word0 >> 24) & 0x1f # crate's slot number (1..7 for scints, 8..20 for RPCs)
                                flag    = (word0 >> 30) & 0x03 # 1 for RPCs, 2 for scints
                                electId = (channel << 12) | (axis << 11) | (lane << 6) | (finesse << 4) | nodeID
                                tdc     = (word1 >> 16) & 0x07ff
                                charge  =  word1        & 0x0fff
                                tExtra  = (word1 >> 27) & 0x1f
                                qExtra  = (word1 >> 12) & 0x0f
                                if (int(exp) <= 3) and (lane <= 2):
                                    trigCtx = trigCtime >> 3
                                    ctime = trigCtx - ((trigCtx - ctime) << 2)
                                isRPC = (flag == 1)
                                isScint = (flag == 2)
                                laneAxis = axis if ((lane < 1) or (lane > 20)) else ((lane << 1) + axis)
                                t   = (tdc - trigCtime) & 0x03ff # in ns, range is 0..1023
                                t0j = 0.75 * j
                                ct  = (ctime << 3) - (trigCtime & 0x7fff8) # in ns, range is only 8 bits in SCROD (??)
                                ct  = ct & 0x3ff
                                if electId in self.electIdToModuleId:
                                    self.hist_mappedSectorOccupancy.Fill(sectorFB)
                                    #if count[dc] > 60:
                                    #if (lane > 2) and (channelMultiplicity[laneAxisChannel] > 1):
                                        #module  = self.electIdToModuleId[electId]
                                        #fb     = (module & self.BKLM_END_MASK) >> self.BKLM_END_BIT
                                        #sector = (module & self.BKLM_SECTOR_MASK) >> self.BKLM_SECTOR_BIT
                                        #layer  = (module & self.BKLM_LAYER_MASK) >> self.BKLM_LAYER_BIT
                                        #plane  = (module & self.BKLM_PLANE_MASK) >> self.BKLM_PLANE_BIT
                                        #strip  = (module & self.BKLM_STRIP_MASK) >> self.BKLM_STRIP_BIT
                                        #print('Event {0:5d} r{1:1d} f{2:1d} {3:3d} c{4:02d} a{5:1d} l{6:02d} g{7:1d} ct{8:5d} t{9:5d} q{10:4d} te{11:1d} qe{12:1d} E{13:1d} S{14:1d} L{15:02d} P{16:1d} s{17:2d} dc{18:2d}'.format(event, copper, finesse, j, channel, axis, lane, flag, ctime, tdc, charge, tExtra, qExtra, fb, sector, layer, plane, strip, dc))
                                    if isRPC:
                                        self.hist_RPCTimeLowBitsBySector.Fill(sectorFB, (tdc & 3))
                                        tCal = t - self.t0RPC[sectorFB]
                                        if abs(tCal - self.t0Cal) < 25:
                                            if n > 60:
                                                self.hist_ctimeRPCtCal.Fill(tCal, ctime - minCtime)
                                                self.hist_ctimeRPCtCal2.Fill(tCal - t0j, ctime - minCtime)
                                                self.hist_jRPCtCal.Fill(tCal, j)
                                                self.hist_jRPCtCal2.Fill(tCal - t0j, j)
                                            self.hist_mappedChannelOccupancyPrompt[sectorFB][axis].Fill(lane, channel)
                                        elif abs(tCal - self.t0Cal) > 50:
                                            self.hist_mappedChannelOccupancyBkgd[sectorFB][axis].Fill(lane, channel)
                                        self.hist_mappedRPCSectorOccupancy.Fill(sectorFB)
                                        self.hist_mappedRPCLaneAxisOccupancy.Fill(sectorFB, laneAxis)
                                        self.hist_mappedRPCTime.Fill(t)
                                        self.hist_mappedRPCTimeCal.Fill(tCal)
                                        self.hist_mappedRPCTimeCal2.Fill(tCal - t0j)
                                        self.hist_mappedRPCTimeBySector.Fill(sectorFB, t)
                                        self.hist_mappedRPCTimeCalBySector.Fill(sectorFB, tCal - t0j)
                                        self.hist_mappedRPCTimePerSector[sectorFB].Fill(t)
                                        self.hist_mappedRPCTimePerLayer[sectorFB][lane-6].Fill(t)
                                    elif isScint:
                                        self.hist_ScintTimeLowBitsBySector.Fill(sectorFB, (tdc & 3))
                                        ctCal = ct - self.ct0Scint[sectorFB]
                                        if abs(ctCal - self.ct0Cal) < 10:
                                            self.hist_mappedChannelOccupancyPrompt[sectorFB][axis].Fill(lane, channel)
                                        elif (abs(ctCal - self.ct0Cal) > 20):
                                            self.hist_mappedChannelOccupancyBkgd[sectorFB][axis].Fill(lane, channel)
                                        self.hist_mappedScintSectorOccupancy.Fill(sectorFB)
                                        self.hist_mappedScintLaneAxisOccupancy.Fill(sectorFB, laneAxis)
                                        self.hist_mappedScintTime.Fill(t & 0x1f)
                                        self.hist_mappedScintTimeBySector.Fill(sectorFB, t & 0x1f)
                                        self.hist_mappedScintTDC.Fill(tdc)
                                        self.hist_mappedScintTDCBySector.Fill(sectorFB, tdc)
                                        self.hist_mappedScintCtime0.Fill((ctime << 3) & 0x3ff)
                                        self.hist_mappedScintCtime1.Fill(sectorFB, (ctime << 3) & 0x3ff)
                                        self.hist_mappedScintCtime.Fill(ct)
                                        self.hist_mappedScintCtimeBySector.Fill(sectorFB, ct)
                                        self.hist_mappedScintCtimeCal.Fill(ctCal)
                                        self.hist_mappedScintCtimeCalBySector.Fill(sectorFB, ctCal)
                                        self.hist_mappedScintCtimePerSector[sectorFB].Fill(ct)
                                        self.hist_mappedScintCtimePerLayer[sectorFB][lane-1].Fill(ct)
                                else:
                                    self.hist_unmappedSectorOccupancy.Fill(sectorFB)
                                    #if count[dc] > 60:
                                    #    print('Event {0:5d} r{1:1d} f{2:1d} {3:3d} c{4:02d} a{5:1d} l{6:02d} g{7:1d} ct{8:5d} t{9:5d} q{10:4d} te{11:1d} qe{12:1d} E{13:1d} S{14:1d} L{15:02d} P{16:1d} s{17:2d} dc{18:2d}'.format(event, copper, finesse, j, channel, axis, lane, flag, ctime, tdc, charge, tExtra, qExtra, fb, sector, layer, plane, strip, dc))
                                    self.hist_unmappedChannelOccupancy[sectorFB][axis].Fill(lane, channel)
                                    if isRPC:
                                        self.hist_RPCTimeLowBitsBySector.Fill(sectorFB, (tdc & 3))
                                        self.hist_unmappedRPCSectorOccupancy.Fill(sectorFB)
                                        self.hist_unmappedRPCLaneAxisOccupancy.Fill(sectorFB, laneAxis)
                                        self.hist_unmappedRPCTime.Fill(t)
                                        self.hist_unmappedRPCTimeBySector.Fill(sectorFB, t)
                                    elif isScint:
                                        self.hist_ScintTimeLowBitsBySector.Fill(sectorFB, (tdc & 3))
                                        self.hist_unmappedScintSectorOccupancy.Fill(sectorFB)
                                        self.hist_unmappedScintLaneAxisOccupancy.Fill(sectorFB, laneAxis)
                                        self.hist_unmappedScintTime.Fill(t & 0x1f)
                                        self.hist_unmappedScintTimeBySector.Fill(sectorFB, t & 0x1f)
                                        self.hist_unmappedScintCtime.Fill(ct)
                                        self.hist_unmappedScintCtimeBySector.Fill(sectorFB, ct)
                self.hist_rawKLMsizeByDC[dc].Fill(count[dc])
                if count[dc] > 60:  # at least 60 1D hits? (1/channel)
                    someOK = True
        self.hist_rawKLMsizeMultihit.Fill(countAllMultihit)
        self.hist_rawKLMsize.Fill(countAll)

        # Process the BKLMHit1ds

        phiTimes = { }
        zTimes = { }
        nphihits = 0
        nzhits = 0
        nRPCPrompt = 0
        nRPCBkgd = 0
        nScint = 0
        for hit1d in hit1ds:
            key = hit1d.getModuleID()
            fb = (key & self.BKLM_END_MASK) >> self.BKLM_END_BIT
            sector = (key & self.BKLM_SECTOR_MASK) >> self.BKLM_SECTOR_BIT
            layer = (key & self.BKLM_LAYER_MASK) >> self.BKLM_LAYER_BIT
            plane = (key & self.BKLM_PLANE_MASK) >> self.BKLM_PLANE_BIT
            stripMin = (key & self.BKLM_STRIP_MASK) >> self.BKLM_STRIP_BIT
            stripMax = (key & self.BKLM_MAXSTRIP_MASK) >> self.BKLM_MAXSTRIP_BIT
            sectorFB = sector if fb == 0 else sector + 8
            dc = self.sectorFBToDC[sectorFB]
            copper = dc & 0x03
            finesse = dc >> 2
            n = rawklms[copper].GetDetectorNwords(0, finesse) >> 1
            trigCtime = (rawklms[copper].GetTTCtime(0) & 0x07ffffff) << 3
            tCal = -1
            ctDiffMax = 99999
            for j in range(0, n):
                if layer != rawLayer[dc][j]:
                    continue
                if sector != rawSector[dc][j]:
                    continue
                if fb != rawFb[dc][j]:
                    continue
                if plane != rawPlane[dc][j]:
                    continue
                strip = rawStrip[dc][j]
                if strip < stripMin:
                    continue
                if strip > stripMax:
                    continue
                if layer < 2: # it's a scint layer
                    ctime = rawCtime[dc][j] << 3
                    ct = ctime - trigCtime - self.ct0Scint[sectorFB] # in ns, range is only 8 bits in SCROD (??)
                    ctTrunc = int(ct) & 0x3ff
                    if abs(ctTrunc - self.ct0Cal) < ctDiffMax:
                        ctDiffMax = int(abs(ctTrunc - self.ct0Cal))
                        tCal = ct
                        if ctDiffMax == 0:
                            break
                else: # it's an RPC layer
                    tCal = ((int(hit1d.getTime()) - trigCtime) & 0x03ff) - self.t0RPC[sectorFB] - 0.75 * j
                    break
            if layer < 2:
                nScint = nScint + 1
            else:
                if abs(tCal - self.t0Cal) < 25:
                    nRPCPrompt = nRPCPrompt + 1
                    if plane == 1:
                        self.hist_multiplicityPhiBySector.Fill(sectorFB, stripMax - stripMin + 1)
                    else:
                        self.hist_multiplicityZBySector.Fill(sectorFB, stripMax - stripMin + 1)
                else:
                    nRPCBkgd = nRPCBkgd + 1
            if plane == 1:
                nphihits = nphihits + 1
                phiTimes[key] = tCal
                if layer < 2:
                    self.hist_tphiScintCal1d.Fill(int(tCal) & 0x3ff)
                else:
                    self.hist_tphiRPCCal1d.Fill(tCal)
            else:
                nzhits = nzhits + 1
                zTimes[key] = tCal
                if layer < 2:
                    self.hist_tzScintCal1d.Fill(int(tCal) & 0x3ff)
                else:
                    self.hist_tzRPCCal1d.Fill(tCal)
        self.hist_nHit1dRPCPrompt.Fill(nRPCPrompt)
        self.hist_nHit1dRPCBkgd.Fill(nRPCBkgd)
        self.hist_nHit1dScint.Fill(nScint)
        if nRPCPrompt > 2:
            self.hist_nHit1dPrompt.Fill(nScint + nRPCBkgd + nRPCPrompt)
        else:
            self.hist_nHit1dBkgd.Fill(nScint + nRPCBkgd + nRPCPrompt)
        self.hist_n1dPhiZ.Fill(nphihits, nzhits)
        for phiKey in phiTimes:
            mphi = phiKey & self.BKLM_MODULEID_MASK
            layer = (mphi & self.BKLM_LAYER_MASK) >> self.BKLM_LAYER_BIT
            sector = (mphi & self.BKLM_SECTOR_MASK) >> self.BKLM_SECTOR_BIT
            fb = (mphi & self.BKLM_END_MASK) >> self.BKLM_END_BIT
            sectorFB = sector if fb == 0 else sector + 8
            tphi = phiTimes[phiKey]
            for zKey in zTimes:
                mz = zKey & self.BKLM_MODULEID_MASK
                if mphi == mz:
                    tz = zTimes[zKey]
                    dt = tphi - tz
                    t = int((tphi + tz) * 0.5) & 0x3ff
                    if layer < 2:
                        self.hist_dtScint1d.Fill(dt)
                    else:
                        self.hist_dtRPC1d.Fill(dt)
                    if abs(dt) < 40:
                        if layer < 2:
                            self.hist_tScintCal1d.Fill(t)
                        else:
                            self.hist_tRPCCal1d.Fill(t)

        # Process the BKLMHit2ds

        xyList = []
        zyList = []
        rpcHits = [ 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0 ]
        for hit2d in hit2ds:
            key = hit2d.getModuleID()
            layer = (key & self.BKLM_LAYER_MASK) >> self.BKLM_LAYER_BIT
            sector = (key & self.BKLM_SECTOR_MASK) >> self.BKLM_SECTOR_BIT
            fb = (key & self.BKLM_END_MASK) >> self.BKLM_END_BIT
            phiStripMin = hit2d.getPhiStripMin() - 1
            phiStripMax = hit2d.getPhiStripMax() - 1
            zStripMin = hit2d.getZStripMin() - 1
            zStripMax = hit2d.getZStripMax() - 1
            sectorFB = sector if fb == 0 else sector + 8
            if layer >= 2:
                rpcHits[sectorFB] = rpcHits[sectorFB] + 1
            dc = self.sectorFBToDC[sectorFB]
            copper = dc & 0x03
            finesse = dc >> 2
            n = rawklms[copper].GetDetectorNwords(0, finesse) >> 1
            trigCtime = (rawklms[copper].GetTTCtime(0) & 0x07ffffff) << 3
            ctDiffMax = 99999
            tCal = -1
            jZ = -1
            jPhi = -1
            ctZ = 0
            ctPhi = 0
            for j in range(0, n):
                if layer != rawLayer[dc][j]:
                    continue
                if sector != rawSector[dc][j]:
                    continue
                if fb != rawFb[dc][j]:
                    continue
                strip = rawStrip[dc][j]
                plane = rawPlane[dc][j]
                if plane == 0: # it's a z strip
                    if strip < zStripMin:
                        continue
                    if strip > zStripMax:
                        continue
                    ctZ = rawCtime[dc][j] << 3 # in ns, range is only 8 bits in SCROD (??)
                    jZ = j
                else: # it's a phi strip
                    if strip < phiStripMin:
                        continue
                    if strip > phiStripMax:
                        continue
                    ctPhi = rawCtime[dc][j] << 3 # in ns, range is only 8 bits in SCROD (??)
                    jPhi = j
                if (jZ >= 0) and (jPhi >= 0):
                    if layer < 2: # it's a scint layer
                        if abs(ctZ - ctPhi) > 40:
                            continue
                        ct = int((ctZ + ctPhi) * 0.5 - trigCtime - self.ct0Scint[sectorFB]) & 0x3ff
                        if abs(ct - self.ct0Cal) < ctDiffMax:
                            ctDiffMax = int(abs(ct - self.ct0Cal))
                            tCal = ct
                            if ctDiffMax == 0:
                                break
                    else: # it's an RPC layer
                        tCal = ((int(hit2d.getTime()) - trigCtime) & 0x03ff) - self.t0RPC[sectorFB] - 0.75 * jPhi - 0.75 * jZ
                        break
            x = hit2d.getGlobalPositionX()
            y = hit2d.getGlobalPositionY()
            z = hit2d.getGlobalPositionZ()
            r = math.sqrt(x*x + y*y)
            self.hist_hit2dOutOfTime.Fill(hit2d.isOutOfTime())
            self.hist_hit2dOnTrack.Fill(hit2d.isOnTrack())
            self.hist_hit2dOnStaTrack.Fill(hit2d.isOnStaTrack())
            isPromptHit = False
            promptColor = 3
            bkgdColor = 2
            if layer < 2:
                promptColor = 7
                bkgdColor = 4
                self.hist_ctScintCal2d.Fill(tCal)
                self.hist_ctScintCal2dBySector.Fill(sectorFB, tCal)
                if abs(tCal - self.ct0Cal2d) < 20:
                    isPromptHit = True
                    if fb == 0: # backward
                        self.hist_occupancyBackwardXYPrompt.Fill(x, y)
                    else: # forward
                        self.hist_occupancyForwardXYPrompt.Fill(x, y)
                else:
                    if fb == 0: # backward
                        self.hist_occupancyBackwardXYBkgd.Fill(x, y)
                    else: # forward
                        self.hist_occupancyForwardXYBkgd.Fill(x, y)
            else:
                self.hist_tRPCCal2d.Fill(tCal)
                self.hist_tRPCCal2dBySector.Fill(sectorFB, tCal)
                if abs(tCal - self.t0Cal2d) < 20:
                    isPromptHit = True
                    self.hist_occupancyRZPrompt.Fill(z, layer)
                    self.hist_occupancyZPrompt.Fill(z)
                    self.hist_occupancyRPrompt.Fill(layer)
                    if fb == 0: # backward
                        self.hist_occupancyBackwardXYPrompt.Fill(x, y)
                    else: # forward
                        self.hist_occupancyForwardXYPrompt.Fill(x, y)
                elif abs(tCal - self.t0Cal2d) > 40:
                    self.hist_occupancyRZBkgd.Fill(z, layer)
                    self.hist_occupancyZBkgd.Fill(z)
                    self.hist_occupancyRBkgd.Fill(layer)
                    if fb == 0: # backward
                        self.hist_occupancyBackwardXYBkgd.Fill(x, y)
                    else: # forward
                        self.hist_occupancyForwardXYBkgd.Fill(x, y)
            if self.eventDisplayCounter >= maxEventCounter:
                continue
            gXY = ROOT.TGraph()
            gXY.SetPoint(0, x - 1.0, y - 1.0)
            gXY.SetPoint(1, x - 1.0, y + 1.0)
            gXY.SetPoint(2, x + 1.0, y + 1.0)
            gXY.SetPoint(3, x + 1.0, y - 1.0)
            gXY.SetPoint(4, x - 1.0, y - 1.0)
            gXY.SetLineWidth(1)
            gZY = ROOT.TGraph()
            gZY.SetPoint(0, z - 1.0, y - 1.0)
            gZY.SetPoint(1, z - 1.0, y + 1.0)
            gZY.SetPoint(2, z + 1.0, y + 1.0)
            gZY.SetPoint(3, z + 1.0, y - 1.0)
            gZY.SetPoint(4, z - 1.0, y - 1.0)
            gZY.SetLineWidth(1)
            if isPromptHit:
              gXY.SetLineColor(promptColor)
              gZY.SetLineColor(promptColor)
            else:
              gXY.SetLineColor(bkgdColor)
              gZY.SetLineColor(bkgdColor)
            xyList.append(gXY)
            zyList.append(gZY)
        if self.eventDisplayCounter < maxEventCounter:
            hasManyRPCHits = False
            for count in rpcHits:
                if count > 5:
                    hasManyRPCHits = True
                    break
            if hasManyRPCHits:
                self.eventDisplayCounter = self.eventDisplayCounter + 1
                title = 'e{0:02d}r{1}: event {2}'.format(int(exp), int(run), event)
                self.hist_XY.SetTitle(title)
                self.hist_ZY.SetTitle(title)
                #self.eventCanvas.cd(1)
                self.hist_XY.Draw()
                for g in self.bklmXY:
                    g.Draw("L")
                for g in xyList:
                    g.Draw("L")
                #self.eventCanvas.cd(2)
                self.hist_ZY.Draw()
                for g in self.bklmZY:
                    g.Draw("L")
                for g in zyList:
                    g.Draw("L")
                #self.eventCanvas.Print(eventPdfName, "Title:{0}".format(event))
        super(EventInspectorBKLM, self).return_value(someOK)

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

if int(exp) == 4: # even experiment number for cosmics
    inputName = '/ghi/fs01/belle2/bdata/Data/Raw/e{0}/r{1}/sub00/cosmic.{0}.{1}.HLT2.f*.root'.format(exp, run)
elif int(exp) == 3: # odd experiment number for physics collisions
    inputName = '/ghi/fs01/belle2/bdata/Data/Raw/e{0}/r{1}/sub00/physics.{0}.{1}.HLT2.f*.root'.format(exp, run)
elif int(exp) == 7: # odd experiment number for physics collisions
    inputName = '/ghi/fs01/belle2/bdata/Data/Raw/e{0}/r{1}/sub00/*.{0}.{1}.HLT*.f*.root'.format(exp, run)
    #inputName = '/home/belle2/atpathak/ppcc2018/work/KLM_4Apr2019/e{0}/r{1}/sub00/*.{0}.{1}.HLT*.f*.root'.format(exp, run)
elif int(exp) == 8: # odd experiment number for physics collisions
    inputName = '/ghi/fs01/belle2/bdata/Data/Raw/e{0}/r{1}/sub00/*.{0}.{1}.HLT*.f*.root'.format(exp, run)
elif int(exp) == 1: # experiment number for local run 
    seqInputNames = '190306.ut3trg.VasilyFW.{0}.run{1}.sroot'.format(exp, run)
elif int(exp) == 2: # experiment number for local run 
    inputName = '190306.ut3trg.VasilyFW.{0}.run{1}.root'.format(exp, run)
elif int(exp) == 6: # experiment number for local run with sroot file
    seqInputNames = '19Feb2019.poisson.5kHz.5M.{0}.{1}.nobeam_AllbutBF2.sroot'.format(exp, run)
elif int(exp) == 10: # new cosmic runs
    prefix = '/ghi/fs01/belle2/bdata/group/detector/BKLM/2019_10/0x18FF/'
   #prefix = '/group/belle/users/stottler/bklm/localRuns/root/rawFiles/'
    if int(run) == 1924:
        seqInputNames = [ prefix + 'klm.0010.01924.HLT1.f00000.sroot' ]
    if int(run) == 33:
        seqInputNames = [ prefix + 'stottler_aux_run33_firmwareBaseline.sroot', prefix ] ## true run number is 34!
    if int(run) == 34:
        seqInputNames = [ prefix + 'stottler_aux_run33_firmwareBaseline.sroot', prefix + 'stottler_aux_run35_firmwareBaseline.sroot', prefix + 'stottler_aux_run36_firmwareBaseline.sroot' ]
    if int(run) == 35:
        seqInputNames = [ prefix + 'stottler_aux_run35_firmwareBaseline.sroot' ]
    if int(run) == 36:
        seqInputNames = [ prefix + 'stottler_aux_run36_firmwareBaseline.sroot' ]
    if int(run) == 38:
        seqInputNames = [ prefix + 'stottler_aux_run38_scrodFirmwareTest_v181207.sroot' ]
    if int(run) == 44:
        seqInputNames = [ prefix + 'stottler_aux_run44_dcFirmwareTest_v190110.sroot' ]
    if int(run) == 45:
        seqInputNames = [ prefix + 'stottler_aux_run45_dcFirmwareTest_v190110.sroot' ]
    if int(run) == 46:
        seqInputNames = [ prefix + 'stottler_30kHzPoisson_run46_dcFirmwareTest_v190110.sroot' ]
#print(inputName)
print (seqInputNames)

#if not os.path.exists('/ghi/fs01/belle2/bdata/group/detector/BKLM/Run_Analysis/e{0}/bklmroots/r{1}/'.format(exp, run)):
 #   os.makedirs('/ghi/fs01/belle2/bdata/group/detector/BKLM/Run_Analysis/e{0}/bklmroots/r{1}/'.format(exp, run))

outputName = 'bklm-e{0}r{1}.root'.format(exp, run)
histName = './bklmHists-e{0}r{1}.root'.format(exp, run)
#pdfName = 'bklmPlots-e{0}r{1}.pdf'.format(exp, run)
#eventPdfName = 'bklmEvents-e{0}r{1}.pdf'.format(exp, run)

reset_database()
use_database_chain()
use_central_database('data_reprocessing_prod6')  # use proper global tag for data

main = create_path()
if int(exp) == 10:
    main.add_module('SeqRootInput', inputFileNames=seqInputNames)
else:
    main.add_module('RootInput', inputFileName=inputName)
    #main.add_module('RootInput', inputFileName=inputName)
    ## replace above line with next to limit the number of events . . .
    ## main.add_module('RootInput', inputFileName=inputName, entrySequences="0:1000")

rawdata.add_unpackers(main, components=['BKLM'])
main.add_module('BKLMReconstructor')
main.add_module(EventInspectorBKLM())

## output = main.add_module('RootOutput')
## output.param('outputFileName', outputName)
## output.param('branchNames', ['BKLMHit2ds'])

main.add_module('ProgressBar')

#set_log_level(LogLevel.DEBUG)
process(main)
print(statistics)
