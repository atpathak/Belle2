#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# Purpose:
#   basf module to histogram useful values in RawKLM, KLMDigit, BKLMHit1d, and BKLMHit2d
#   data-objects in a DST ROOT file and to create BKLM event displays from these data-objects.
#

import basf2
import bklmDB
import math
import ctypes
import ROOT
from ROOT import Belle2, TH1F, TH2F, TCanvas, THistPainter, TPad


class EventInspector(basf2.Module):
    """Fill BKLM histograms of values from RawKLMs, KLMDigits, BKLMHit1ds, and BKLMHit2ds;
    (optionally) draw event displays from these data-objects."""

    #: COPPER base identifier for BKLM readout
    BKLM_ID = 0x07000000
    #: COPPER base identifier for EKLM readout
    EKLM_ID = 0x08000000
    #: bit position for strip-1 [0..47]
    BKLM_STRIP_BIT = 0
    #: bit position for plane-1 [0..1]; 0 is inner-plane
    BKLM_PLANE_BIT = 6
    #: bit position for layer-1 [0..14]; 0 is innermost
    BKLM_LAYER_BIT = 7
    #: bit position for sector-1 [0..7]; 0 is on the +x axis and 2 is on the +y axis
    BKLM_SECTOR_BIT = 11
    #: bit position for detector end [0..1]; forward is 0
    BKLM_END_BIT = 14
    #: bit position for maxStrip-1 [0..47]
    BKLM_MAXSTRIP_BIT = 15
    #: bit mask for strip-1 [0..47]
    BKLM_STRIP_MASK = 0x3f
    #: bit mask for plane-1 [0..1]; 0 is inner-plane
    BKLM_PLANE_MASK = (1 << BKLM_PLANE_BIT)
    #: bit mask for layer-1 [0..15]; 0 is innermost and 14 is outermost
    BKLM_LAYER_MASK = (15 << BKLM_LAYER_BIT)
    #: bit mask for sector-1 [0..7]; 0 is on the +x axis and 2 is on the +y axis
    BKLM_SECTOR_MASK = (7 << BKLM_SECTOR_BIT)
    #: bit mask for detector end [0..1]; forward is 0
    BKLM_END_MASK = (1 << BKLM_END_BIT)
    #: bit mask for maxStrip-1 [0..47]
    BKLM_MAXSTRIP_MASK = (63 << BKLM_MAXSTRIP_BIT)
    #: bit mask for unique module identifier (end, sector, layer)
    BKLM_MODULEID_MASK = (BKLM_END_MASK | BKLM_SECTOR_MASK | BKLM_LAYER_MASK)

    def __init__(self, exp, run, histName, maxDisplays, minRPCHits, legacyTimes, singleEntry, view):
        """Constructor

        Arguments:
            exp (str): formatted experiment number
            run (str): formatter run number
            histName (str): path name of the output histogram ROOT file
            pdfName (str): path name of the output histogram PDF file
            eventPdfName (str): path name of the output event-display PDF file
            maxDisplays (int): max # of events displays to write
            minRPCHits (int): min # of RPC BKLMHit2ds in any sector for event display
            legacyTimes (bool): true to correct BKLMHit{1,2}d times in legacy reconstruction, False otherwise
            singleEntry (int): select events with any (0) or exactly one (1) or more than one (2) entries/channel
            view (int): view event displays using one-dimensional (1) or two-dimensional (2) BKLMHits
        """
        super().__init__()
        #: internal copy of experiment number
        self.exp = exp
        #: internal copy of run number
        self.run = run
        #: internal copy of the pathname of the output histogram ROOT file
        self.histName = histName
        #: internal copy of the pathname of the output histogram PDF file
        self.maxDisplays = maxDisplays
        #: internal copy of the minimum number of RPC BKLMHit2ds in any sector for event display
        self.minRPCHits = minRPCHits
        #: calculate prompt time for legacy BKLMHit1ds and BKLMHit2ds (True) or use stored time (False)
        self.legacyTimes = legacyTimes
        #: select events with any (0) or exactly one (1) or more than one (2) entries/channel
        self.singleEntry = singleEntry
        #: view event displays using one-dimensional (1) or two-dimensional (2) hits
        self.view = view
        #: event counter (needed for PDF table of contents' ordinal event#)
        self.eventCounter = 0
        #: event-display counter
        self.eventDisplays = 0
        #: title of the last-drawn event display (needed for PDF table of contents' last event)
        self.lastTitle = ''

    def makeGraph(self, x, y):
        """Create and return a ROOT TGraph

        Arguments:
          x[] (real): x coordinates
          y[] (real): y coordinates
        """
        graph = ROOT.TGraph()
        for i in range(0, len(x)):
            graph.SetPoint(i, x[i], y[i])
        graph.SetLineColor(2)
        graph.SetLineWidth(1)
        return graph

    def makeText(self, x, y, s):
        """Create and return a ROOT TLatex with the following properties:
        size = 0.04, color = red, alignment = middle centre, angle = 90 degrees

        Arguments:
          x (real): x coordinate
          y (real): y coordinate
          s (str):  character string
        """
        text = ROOT.TLatex(x, y, s)
        text.SetTextSize(0.04)
        text.SetTextColor(2)
        text.SetTextAlign(22)
        text.SetTextAngle(90)
        return text

    def initialize(self):
        """Handle job initialization: fill the mapping database, create histograms, open the event-display file"""

        expRun = 'e{0:02d}r{1}: '.format(int(self.exp), int(self.run))
        #: blank scatterplot to define the bounds of the BKLM end view
        self.hist_XY = ROOT.TH2F('XY', ' ;x;y', 10, -345.0, 345.0, 10, -345.0, 345.0)
        self.hist_XY.SetStats(False)
        #: blank scatterplot to define the bounds of the BKLM side view for 1D hits
        self.hist_ZY1D = [0, 0]
        self.hist_ZY1D[0] = ROOT.TH2F('ZY0', ' ;z;y', 10, -200.0, 300.0, 10, -150.0, 350.0)
        self.hist_ZY1D[1] = ROOT.TH2F('ZY1', ' ;z;y', 10, -200.0, 300.0, 10, -150.0, 350.0)
        self.hist_ZY1D[0].SetStats(False)
        self.hist_ZY1D[0].SetStats(False)
        #: blank scatterplot to define the bounds of the BKLM side view for 2D hits
        self.hist_ZY = ROOT.TH2F('ZY', ' ;z;y', 10, -345.0, 345.0, 10, -345.0, 345.0)
        self.hist_ZY.SetStats(False)

        # All histograms/scatterplots in the output file will show '# of events' only
        ROOT.gStyle.SetOptStat(10)
        #: readout <-> detector map (from the information retrieved from the conditions database)
        self.electIdToModuleId = bklmDB.fillDB()
        #: map for sectorFB -> data concentrator
        self.sectorFBToDC = [11, 15, 2, 6, 10, 14, 3, 7, 9, 13, 0, 4, 8, 12, 1, 5]
        #: map for data concentrator -> sectorFB
        self.dcToSectorFB = [10, 14, 2, 6, 11, 15, 3, 7, 12, 8, 4, 0, 13, 9, 5, 1]
        #: Time-calibration constants obtained from experiment 7 run 1505
        #: RPC-time calibration adjustment (ns) for rawKLMs
        self.t0Cal = 312
        #: RPC-time calibration adjustment (ns) for BKLMHit1ds
        self.t0Cal1d = 325
        #: RPC-time calibration adjustment (ns) for BKLMHit2ds
        self.t0Cal2d = 308
        #: scint-ctime calibration adjustment (ns) for rawKLMs
        self.ct0Cal = 455
        #: scint-ctime calibration adjustment (ns) for BKLMHit1ds
        self.ct0Cal1d = 533
        #: scint-ctime calibration adjustment (ns) for BKLMHit2ds
        self.ct0Cal2d = 520
        #: per-sector variations in RPC-time calibration adjustment (ns) for rawKLMs
        self.t0RPC = [8, -14, -6, -14, -2, 10, 9, 13, 0, -10, -14, -20, 2, 6, 14, 11]
        #: per-sector variations in scint-ctime calibration adjustment (ns) for rawKLMs
        self.ct0Scint = [-1, -33, -46, -33, -2, 32, 51, 32, 0, -32, -45, -33, -4, 34, 45, 27]

        #: Output ROOT TFile that will contain the histograms/scatterplots
        self.histogramFile = ROOT.TFile.Open(self.histName, "RECREATE")
        # All histograms/scatterplots in the output file will show '# of events' only
        ROOT.gStyle.SetOptStat(10)
        ROOT.gStyle.SetOptFit(111)

        # create the rawKLM histograms

        #: histogram of the number of BKLMDigits in the event
        self.hist_nDigit = ROOT.TH1F('NDigit', expRun + '# of BKLMDigits', 500, -0.5, 499.5)
        #: histogram of the number of RawKLMs in the event (should be 1)
        self.hist_nRawKLM = ROOT.TH1F('NRawKLM', expRun + '# of RawKLMs', 10, -0.5, 9.5)
        #: histogram of the RawKLM's NumEvents (should be 1)
        self.hist_rawKLMnumEvents = ROOT.TH1F('RawKLMnumEvents', expRun + 'RawKLM NumEvents;(should be 1)', 10, -0.5, 9.5)
        #: histogram of the RawKLM's NumNodes (should be 1)
        self.hist_rawKLMnumNodes = ROOT.TH1F('RawKLMnumNodes', expRun + 'RawKLM NumNodes;(should be 1)', 10, -0.5, 9.5)
        #: scatterplot of the RawKLM's COPPER index vs NodeID relative to the base BKLM/EKLM values
        self.hist_rawKLMnodeID = ROOT.TH2F('RawKLMnodeID',
                                           expRun + 'RawKLM NodeID;' +
                                           'NodeID (bklm: 1..4, eklm:5..8);' +
                                           'Copper index',
                                           10, -0.5, 9.5, 10, -0.5, 9.5)
        #: scatterplot of the RawKLM hit's lane vs flag (1=RPC, 2=Scint)
        self.hist_rawKLMlaneFlag = ROOT.TH2F('rawKLMlaneFlag',
                                             expRun + 'RawKLM lane vs flag;' +
                                             'Flag (1=RPC, 2=Scint);' +
                                             'Lane (scint: 1..7, RPC: 8..20)',
                                             4, -0.5, 3.5, 21, -0.5, 20.5)
        #: scatterplot of the RawKLM RPC hit's extra bits vs sector in the third (time) word
        self.hist_rawKLMtdcExtraRPC = ROOT.TH2F('rawKLMtdcExtraRPC',
                                                expRun + 'RawKLM RPC tdcExtra bits;' +
                                                'Sector # (0-7 = backward, 8-15 = forward);' +
                                                'tdcExtra [should be 0]',
                                                16, -0.5, 15.5, 32, -0.5, 31.5)
        #: scatterplot of the RawKLM RPC hit's extra bits vs sector in the fourth (adc) word
        self.hist_rawKLMadcExtraRPC = ROOT.TH2F('rawKLMadcExtraRPC',
                                                expRun + 'RawKLM RPC adcExtra bits;' +
                                                'Sector # (0-7 = backward, 8-15 = forward);' +
                                                'adcExtra [should be 0]',
                                                16, -0.5, 15.5, 16, -0.5, 15.5)
        #: scatterplot of the RawKLM scint hit's extra bits vs sector in the third (time) word
        self.hist_rawKLMtdcExtraScint = ROOT.TH2F('rawKLMtdcExtraScint',
                                                  expRun + 'RawKLM Scint tdcExtra bits;' +
                                                  'Sector # (0-7 = backward, 8-15 = forward);' +
                                                  'tdcExtra',
                                                  16, -0.5, 15.5, 32, -0.5, 31.5)
        #: scatterplot of the RawKLM scint hit's extra bits vs sector in the fourth (adc) word
        self.hist_rawKLMadcExtraScint = ROOT.TH2F('rawKLMadcExtraScint',
                                                  expRun + 'RawKLM Scint adcExtra bits;' +
                                                  'Sector # (0-7 = backward, 8-15 = forward);' +
                                                  'adcExtra',
                                                  16, -0.5, 15.5, 16, -0.5, 15.5)
        #: histogram of number of hits, including multiple entries on one readout channel
        self.hist_rawKLMsizeMultihit = ROOT.TH1F('rawKLMsizeMultihit', expRun + 'RawKLM word count (N/channel)', 400, -0.5, 799.5)
        #: histogram of number of hits, at most one entry per readout channel
        self.hist_rawKLMsize = ROOT.TH1F('rawKLMsize', expRun + 'RawKLM word count (1/channel)', 250, -0.5, 499.5)
        #: histograms of number of hits, including multiple entries on one readout channel, indexed by sector#
        self.hist_rawKLMsizeByDCMultihit = []
        #: histograms of number of hits, at most one entry per readout channel, indexed by sector#
        self.hist_rawKLMsizeByDC = []
        for sectorFB in range(0, 16):
            dc = self.sectorFBToDC[sectorFB]
            copper = dc & 0x03
            finesse = dc >> 2
            label = 'rawKLM_S{0:02d}_sizeMultihit'.format(sectorFB)
            title = '{0}sector {1} [COPPER {2} finesse {3}] word count (N/channel)'.format(expRun, sectorFB, copper, finesse)
            self.hist_rawKLMsizeByDCMultihit.append(ROOT.TH1F(label, title, 100, -0.5, 199.5))
            label = 'rawKLM_S{0:02d}_size'.format(sectorFB)
            title = '{0}sector {1} [COPPER {2} finesse {3}] word count (1/channel)'.format(expRun, sectorFB, copper, finesse)
            self.hist_rawKLMsizeByDC.append(ROOT.TH1F(label, title, 100, -0.5, 199.5))
        #: scatterplots of multiplicity of entries in one readout channel vs lane/axis, indexed by sector#
        self.hist_rawKLMchannelMultiplicity = []
        #: scatterplots of multiplicity of entries in one readout channel vs lane/axis/channel, indexed by sector#
        self.hist_rawKLMchannelMultiplicityFine = []
        for sectorFB in range(0, 16):
            dc = self.sectorFBToDC[sectorFB]
            copper = dc & 0x03
            finesse = dc >> 2
            label = 'rawKLM_S{0:02d}_channelMultiplicity'.format(sectorFB)
            title = '{0}sector {1} [COPPER {2} finesse {3}] per-channel multiplicity (N/channel > 1);'.format(
                expRun, sectorFB, copper, finesse) + 'Per-channel multiplicity;(Lane #) * 2 + (Axis #)'
            self.hist_rawKLMchannelMultiplicity.append(ROOT.TH2F(label, title, 30, -0.5, 29.5, 42, -0.5, 41.5))
            label = 'rawKLM_S{0:02d}_channelMultiplicityFine'.format(sectorFB)
            title = '{0}sector {1} [COPPER {2} finesse {3}] per-channel multiplicity (N/channel > 1);'.format(
                expRun, sectorFB, copper, finesse) + 'Per-channel multiplicity;(Lane #) * 256 + (Axis #) * 128 + (Channel #)'
            self.hist_rawKLMchannelMultiplicityFine.append(ROOT.TH2F(label, title, 30, -0.5, 29.5, 8192, -0.5, 8191.5))
        #: histogram of number of mapped hits by sector, including multiple entries on one readout channel
        self.hist_mappedSectorOccupancyMultihit = ROOT.TH1F(
            'mappedSectorOccupancyMultihit',
            expRun + 'Sector occupancy of mapped channels (N/channel);' +
            'Sector # (0-7 = backward, 8-15 = forward)',
            16, -0.5, 15.5)
        #: histogram of number of unmapped hits by sector, including multiple entries on one readout channel
        self.hist_unmappedSectorOccupancyMultihit = ROOT.TH1F(
            'unmappedSectorOccupancyMultihit',
            expRun + 'Sector occupancy of unmapped channels (N/channel);' +
            'Sector # (0-7 = backward, 8-15 = forward)',
            16, -0.5, 15.5)
        #: histogram of number of mapped hits by sector, at most one entry per readout channel
        self.hist_mappedSectorOccupancy = ROOT.TH1F(
            'mappedSectorOccupancy',
            expRun + 'Sector occupancy of mapped channels (1/channel);' +
            'Sector # (0-7 = backward, 8-15 = forward)',
            16, -0.5, 15.5)
        #: histogram of number of unmapped hits by sector, at most one entry per readout channel
        self.hist_unmappedSectorOccupancy = ROOT.TH1F(
            'unmappedSectorOccupancy',
            expRun + 'Sector occupancy of unmapped channels (1/channel);' +
            'Sector # (0-7 = backward, 8-15 = forward)',
            16, -0.5, 15.5)
        #: histogram of number of mapped RPC hits by sector, at most one entry per readout channel
        self.hist_mappedRPCSectorOccupancy = ROOT.TH1F(
            'mappedRPCSectorOccupancy',
            expRun + 'Sector occupancy of mapped RPC channels (1/channel);' +
            'Sector # (0-7 = backward, 8-15 = forward)',
            16, -0.5, 15.5)
        #: scatterplot of number of mapped RPC hits by lane/axis vs sector, at most one entry per readout channel
        self.hist_mappedRPCLaneAxisOccupancy = ROOT.TH2F(
            'mappedRPCLaneAxisOccupancy',
            expRun + 'Lane/axis occupancy of mapped RPC channels (1/channel);' +
            'Sector # (0-7 = backward, 8-15 = forward);' +
            '(Lane #) * 2 + (Axis #)',
            16, -0.5, 15.5, 42, -0.5, 41.5)
        #: histogram of number of unmapped RPC hits by sector, at most one entry per readout channel
        self.hist_unmappedRPCSectorOccupancy = ROOT.TH1F(
            'unmappedRPCSectorOccupancy',
            expRun + 'Sector occupancy of unmapped RPC channels (1/channel);' +
            'Sector # (0-7 = backward, 8-15 = forward)',
            16, -0.5, 15.5)
        #: scatterplot of number of unmapped RPC hits by lane/axis vs sector, at most one entry per readout channel
        self.hist_unmappedRPCLaneAxisOccupancy = ROOT.TH2F(
            'unmappedRPCLaneAxisOccupancy',
            expRun + 'Lane/axis occupancy of unmapped RPC channels (1/channel);' +
            'Sector # (0-7 = backward, 8-15 = forward);' +
            '(Lane #) * 2 + (Axis #)',
            16, -0.5, 15.5, 42, -0.5, 41.5)
        #: scatterplot of number of mapped scint hits by lane/axis vs sector, at most one entry per readout channel
        self.hist_mappedScintSectorOccupancy = ROOT.TH1F(
            'mappedScintSectorOccupancy',
            expRun + 'Sector occupancy of mapped scint channels (1/channel);' +
            'Sector # (0-7 = backward, 8-15 = forward)',
            16, -0.5, 15.5)
        #: scatterplot of number of mapped scint hits by lane/axis vs sector, at most one entry per readout channel
        self.hist_mappedScintLaneAxisOccupancy = ROOT.TH2F(
            'mappedScintLaneAxisOccupancy',
            expRun + 'Lane/axis occupancy of mapped scint channels (1/channel);' +
            'Sector # (0-7 = backward, 8-15 = forward);' +
            '(Lane #) * 2 + (Axis #)',
            16, -0.5, 15.5, 42, -0.5, 41.5)
        #: histogram of number of unmapped scint hits by sector, at most one entry per readout channel
        self.hist_unmappedScintSectorOccupancy = ROOT.TH1F(
            'unmappedScintSectorOccupancy',
            expRun + 'Sector occupancy of unmapped scint channels (1/channel);' +
            'Sector # (0-7 = backward, 8-15 = forward)',
            16, -0.5, 15.5)
        #: scatterplot of number of unmapped scint hits by lane/axis vs sector, at most one entry per readout channel
        self.hist_unmappedScintLaneAxisOccupancy = ROOT.TH2F(
            'unmappedScintLaneAxisOccupancy',
            expRun + 'Lane/axis occupancy of unmapped scint channels (1/channel);' +
                     'Sector # (0-7 = backward, 8-15 = forward);' +
                     '(Lane #) * 2 + (Axis #)',
            16, -0.5, 15.5, 42, -0.5, 41.5)
        #: scatterplots of in-time mapped channel occupancy (1 hit per readout channel), indexed by sector#
        self.hist_mappedChannelOccupancyPrompt = [
            [0, 0], [0, 0], [0, 0], [0, 0], [0, 0], [0, 0], [0, 0], [0, 0],
            [0, 0], [0, 0], [0, 0], [0, 0], [0, 0], [0, 0], [0, 0], [0, 0]]
        #: scatterplots of out-of-time mapped channel occupancy (1 hit per readout channel), indexed by sector#
        self.hist_mappedChannelOccupancyBkgd = [
            [0, 0], [0, 0], [0, 0], [0, 0], [0, 0], [0, 0], [0, 0], [0, 0],
            [0, 0], [0, 0], [0, 0], [0, 0], [0, 0], [0, 0], [0, 0], [0, 0]]
        #: scatterplots of unmapped channel occupancy (1 hit per readout channel), indexed by sector#
        self.hist_unmappedChannelOccupancy = [
            [0, 0], [0, 0], [0, 0], [0, 0], [0, 0], [0, 0], [0, 0], [0, 0],
            [0, 0], [0, 0], [0, 0], [0, 0], [0, 0], [0, 0], [0, 0], [0, 0]]
        for sectorFB in range(0, 16):
            label = 'mappedChannelOccupancy_S{0:02d}ZPrompt'.format(sectorFB)
            title = '{0}In-time mapped channel occupancy for sector {1} z hits;lane;channel'.format(expRun, sectorFB)
            self.hist_mappedChannelOccupancyPrompt[sectorFB][0] = ROOT.TH2F(label, title, 42, -0.25, 20.75, 128, -0.25, 63.75)
            label = 'mappedChannelOccupancy_S{0:02d}ZBkgd'.format(sectorFB)
            title = '{0}Out-of-time mapped channel occupancy for sector {1} z hits;lane;channel'.format(expRun, sectorFB)
            self.hist_mappedChannelOccupancyBkgd[sectorFB][0] = ROOT.TH2F(label, title, 42, -0.25, 20.75, 128, -0.25, 63.75)
            label = 'unmappedChannelOccupancy_S{0:02d}Z'.format(sectorFB)
            title = '{0}Unmapped channel occupancy for sector {1} z hits;lane;channel'.format(expRun, sectorFB)
            self.hist_unmappedChannelOccupancy[sectorFB][0] = ROOT.TH2F(label, title, 42, -0.25, 20.75, 128, -0.25, 63.75)
            label = 'mappedChannelOccupancy_S{0:02d}PhiPrompt'.format(sectorFB)
            title = '{0}In-time mapped occupancy for sector {1} phi hits;lane;channel'.format(expRun, sectorFB)
            self.hist_mappedChannelOccupancyPrompt[sectorFB][1] = ROOT.TH2F(label, title, 42, -0.25, 20.75, 128, -0.25, 63.75)
            label = 'mappedChannelOccupancy_S{0:02d}PhiBkgd'.format(sectorFB)
            title = '{0}Out-of-time mapped occupancy for sector {1} phi hits;lane;channel'.format(expRun, sectorFB)
            self.hist_mappedChannelOccupancyBkgd[sectorFB][1] = ROOT.TH2F(label, title, 42, -0.25, 20.75, 128, -0.25, 63.75)
            label = 'unmappedChannelOccupancy_S{0:02d}Phi'.format(sectorFB)
            title = '{0}Unmapped channel occupancy for sector {1} phi hits;lane;channel'.format(expRun, sectorFB)
            self.hist_unmappedChannelOccupancy[sectorFB][1] = ROOT.TH2F(label, title, 42, -0.25, 20.75, 128, -0.25, 63.75)
        #: scatterplot of RPC TDC low-order bits vs sector (should be 0 since granularity is 4 ns)
        self.hist_RPCTimeLowBitsBySector = ROOT.TH2F('RPCTimeLowBitsBySector',
                                                     expRun + 'RPC TDC lowest-order bits;' +
                                                     'Sector # (0-7 = backward, 8-15 = forward);' +
                                                     'TDC % 4 (ns) [should be 0]',
                                                     16, -0.5, 15.5, 4, -0.5, 3.5)
        #: histogram of RPC mapped-channel TDC value relative to event's trigger time
        self.hist_mappedRPCTime = ROOT.TH1F(
            'mappedRPCTime', expRun + 'RPC mapped-strip time distribution;t - t(trigger) (ns)', 256, -0.5, 1023.5)
        #: histogram of RPC mapped-channel TDC value relative to event's trigger time, corrected for inter-sector variation
        self.hist_mappedRPCTimeCal = ROOT.TH1F(
            'mappedRPCTimeCal', expRun + 'RPC mapped-strip time distribution;t - t(trigger) - dt(sector) (ns)', 256, -0.5, 1023.5)
        #: histogram of RPC mapped-channel TDC relative to trigger time, corrected for inter-sector var'n and DC-processing delay
        self.hist_mappedRPCTimeCal2 = ROOT.TH1F('mappedRPCTimeCal2',
                                                expRun + 'RPC mapped-strip time distribution;' +
                                                't - t(trigger) - dt(sector) - t(index) (ns)',
                                                256, -0.5, 1023.5)
        #: histograms of RPC mapped-channel TDC value relative to event's trigger time, indexed by sector
        self.hist_mappedRPCTimePerSector = []
        #: histograms of RPC mapped-channel TDC value relative to event's trigger time, indexed by sector/layer
        self.hist_mappedRPCTimePerLayer = []
        for sectorFB in range(0, 16):
            label = 'mappedRPCTime_S{0:02d}'.format(sectorFB)
            title = '{0}RPC sector {1} time distribution;t - t(trigger) (ns)'.format(expRun, sectorFB)
            self.hist_mappedRPCTimePerSector.append(ROOT.TH1F(label, title, 256, -0.5, 1023.5))
            self.hist_mappedRPCTimePerLayer.append([0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0])
            for layer in range(0, 15):
                label = 'mappedRPCTime_S{0:02d}L{1:02d}'.format(sectorFB, layer)
                title = '{0}RPC sector {1} layer {2} time distribution;t - t(trigger) (ns)'.format(expRun, sectorFB, layer)
                self.hist_mappedRPCTimePerLayer[sectorFB][layer] = ROOT.TH1F(label, title, 256, -0.5, 1023.5)
        #: scatterplot of RPC mapped-channel TDC value relative to event's trigger time vs sector
        self.hist_mappedRPCTimeBySector = ROOT.TH2F('mappedRPCTimeBySector',
                                                    expRun + 'RPC mapped-strip time;' +
                                                    'Sector # (0-7 = backward, 8-15 = forward);' +
                                                    't - t(trigger) (ns)',
                                                    16, -0.5, 15.5, 128, -0.5, 1023.5)
        #: scatterplot of RPC mapped-channel TDC relative to trigger time, corrected for inter-sector variation, by sector
        self.hist_mappedRPCTimeCalBySector = ROOT.TH2F('mappedRPCTimeCalBySector',
                                                       expRun + 'RPC mapped-strip time;' +
                                                       'Sector # (0-7 = backward, 8-15 = forward);' +
                                                       't - t(trigger) - dt(sector) (ns)',
                                                       16, -0.5, 15.5, 128, -0.5, 1023.5)
        #: histogram of RPC mapped-channel REVO9 range in event
        self.hist_mappedRPCCtimeRange = ROOT.TH1F('mappedRPCCtimeRange',
                                                  expRun + 'RPC Ctime-range in event;' +
                                                  'CtimeMax - CtimeMin (ns)',
                                                  128, -0.5, 8191.5)
        #: scatterplot of RPC mapped-channel REVO9 range in event vs sector
        self.hist_mappedRPCCtimeRangeBySector = ROOT.TH2F('mappedRPCCtimeRangeBySector',
                                                          expRun + 'RPC Ctime-range in event;' +
                                                          'Sector # (0-7 = backward, 8-15 = forward);' +
                                                          'CtimeMax - CtimeMin (ns)',
                                                          16, -0.5, 15.5, 128, -0.5, 8191.5)
        #: histogram of RPC unmapped-channel TDC value relative to event's trigger time
        self.hist_unmappedRPCTime = ROOT.TH1F('unmappedRPCTime',
                                              expRun + 'RPC unmapped-strip time distribution;' +
                                              't - t(trigger) (ns)',
                                              256, -0.5, 1023.5)
        #: scatterplot of RPC unmapped-channel TDC value relative to event's trigger time, by sector
        self.hist_unmappedRPCTimeBySector = ROOT.TH2F('unmappedRPCTimeBySector',
                                                      expRun + 'RPC unmapped-strip time;' +
                                                      'Sector # (0-7 = backward, 8-15 = forward);' +
                                                      't - t(trigger) (ns)',
                                                      16, -0.5, 15.5, 128, -0.5, 1023.5)
        #: scatterplot of scint TDC low-order bits vs sector
        self.hist_ScintTimeLowBitsBySector = ROOT.TH2F('ScintTimeLowBitsBySector',
                                                       expRun + 'Scint TDC lowest-order bits;' +
                                                       'Sector # (0-7 = backward, 8-15 = forward);' +
                                                       'TDC % 4 (ns)',
                                                       16, -0.5, 15.5, 4, -0.5, 3.5)
        #: histogram of scint mapped-channel CTIME value (NOT relative to event's trigger Ctime)
        self.hist_mappedScintCtime0 = ROOT.TH1F('mappedScintCtime0',
                                                expRun + 'Scint mapped-strip ctime distribution;' +
                                                'ctime (ns)',
                                                32, -0.5, 1023.5)
        #: scatterplot of scint mapped-channel CTIME value (NOT relative to event's trigger Ctime)
        self.hist_mappedScintCtime1 = ROOT.TH2F('mappedScintCtime1',
                                                expRun + 'Scint mapped-strip ctime distribution;' +
                                                'Sector # (0-7 = backward, 8-15 = forward);' +
                                                'ctime (ns)',
                                                16, -0.5, 15.5, 32, -0.5, 1023.5)
        #: histogram of scint mapped-channel CTIME value relative to event's trigger Ctime
        self.hist_mappedScintCtime = ROOT.TH1F('mappedScintCtime',
                                               expRun + 'Scint mapped-strip ctime distribution;' +
                                               'ctime - ct(trigger) (ns)',
                                               32, -0.5, 1023.5)
        #: scatterplot of scint mapped-channel CTIME value relative to event's trigger Ctime vs sector
        self.hist_mappedScintCtimeBySector = ROOT.TH2F('mappedScintCtimeBySector',
                                                       expRun + 'Scint mapped-strip ctime;' +
                                                       'Sector # (0-7 = backward, 8-15 = forward);' +
                                                       'ctime - ct(trigger) (ns)',
                                                       16, -0.5, 15.5, 32, -0.5, 1023.5)
        #: histogram of scint mapped-channel CTIME value relative to event's trigger Ctime, corrected for inter-sector variation
        self.hist_mappedScintCtimeCal = ROOT.TH1F('mappedScintCtimeCal',
                                                  expRun + 'Scint mapped-strip ctime distribution;' +
                                                  'ctime - ct(trigger) - dt(sector) (ns)',
                                                  32, -0.5, 1023.5)
        #: scatterplot of scint mapped-channel CTIME relative to trigger Ctime, corrected for inter-sector variation, by sector
        self.hist_mappedScintCtimeCalBySector = ROOT.TH2F('mappedScintCtimeCalBySector',
                                                          expRun + 'Scint mapped-strip ctime;' +
                                                          'Sector # (0-7 = backward, 8-15 = forward);' +
                                                          'ctime - ct(trigger) - dt(sector) (ns)',
                                                          16, -0.5, 15.5, 32, -0.5, 1023.5)
        #: histograms of scint mapped-channel CTIME value relative to event's trigger Ctime, indexed by sector
        self.hist_mappedScintCtimePerSector = []
        #: histograms of scint mapped-channel CTIME value relative to event's trigger Ctime, indexed by sector/layer
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
        #: histogram of scint mapped-channel CTIME range in event
        self.hist_mappedScintCtimeRange = ROOT.TH1F('mappedScintCtimeRange',
                                                    expRun + 'Scint ctime-range in event;' +
                                                    'ctimeMax - ctimeMin (ns)',
                                                    128, -0.5, 1023.5)
        #: scatterplot of scint mapped-channel CTIME range in event vs sector
        self.hist_mappedScintCtimeRangeBySector = ROOT.TH2F('mappedScintCtimeRangeBySector',
                                                            expRun + 'Scint ctime-range in event;' +
                                                            'Sector # (0-7 = backward, 8-15 = forward);' +
                                                            'ctimeMax - ctimeMin (ns)',
                                                            16, -0.5, 15.5, 128, -0.5, 1023.5)
        #: histogram of scint unmapped-channel CTIME value relative to event's trigger Ctime
        self.hist_unmappedScintCtime = ROOT.TH1F('unmappedScintCtime',
                                                 expRun + 'Scint unmapped-strip ctime distribution;' +
                                                 'ctime - ct(trigger) (ns)',
                                                 32, -0.5, 1023.5)
        #: scatterplot of scint unmapped-channel CTIME value relative to event's trigger Ctime, by sector
        self.hist_unmappedScintCtimeBySector = ROOT.TH2F('unmappedScintCtimeBySector',
                                                         expRun + 'Scint unmapped-strip ctime;' +
                                                         'Sector # (0-7 = backward, 8-15 = forward);' +
                                                         'ctime - ct(trigger) (ns)',
                                                         16, -0.5, 15.5, 32, -0.5, 1023.5)
        #: histogram of scint mapped-channel TDC value (NOT relative to event's trigger Ctime)
        self.hist_mappedScintTDC = ROOT.TH1F('mappedScintTDC',
                                             expRun + 'Scint mapped-strip TDC distribution;' +
                                             't (ns)',
                                             32, -0.5, 31.5)
        #: histogram of scint mapped-channel TDC value relative to event's trigger Ctime
        self.hist_mappedScintTime = ROOT.TH1F('mappedScintTime',
                                              expRun + 'Scint mapped-strip time distribution;' +
                                              't - t(trigger) (ns)', 32, -0.5, 31.5)
        #: scatterplot of scint mapped-channel TDC value (NOT relative to event's trigger Ctime) vs sector
        self.hist_mappedScintTDCBySector = ROOT.TH2F('mappedScintTDCBySector',
                                                     expRun + 'Scint mapped-strip TDC;' +
                                                     'Sector # (0-7 = backward, 8-15 = forward);' +
                                                     't (ns)',
                                                     16, -0.5, 15.5, 32, -0.5, 31.5)
        #: scatterplot of scint mapped-channel TDC value relative to event's trigger Ctime vs sector
        self.hist_mappedScintTimeBySector = ROOT.TH2F('mappedScintTimeBySector',
                                                      expRun + 'Scint mapped-strip time;' +
                                                      'Sector # (0-7 = backward, 8-15 = forward);' +
                                                      't - t(trigger) (ns)',
                                                      16, -0.5, 15.5, 32, -0.5, 31.5)
        #: histogram of scint unmapped-channel TDC value relative to event's trigger Ctime
        self.hist_unmappedScintTime = ROOT.TH1F('unmappedScintTime',
                                                expRun + 'Scint unmapped-strip time distribution;' +
                                                't - t(trigger) (ns)',
                                                32, -0.5, 31.5)
        #: scatterplot of scint unmapped-channel TDC value relative to event's trigger Ctime vs sector
        self.hist_unmappedScintTimeBySector = ROOT.TH2F('unmappedScintTimeBySector',
                                                        expRun + 'Scint unmapped-strip time;' +
                                                        'Sector # (0-7 = backward, 8-15 = forward);' +
                                                        't - t(trigger) (ns)',
                                                        16, -0.5, 15.5, 32, -0.5, 31.5)

        # Create the RPC time-calibration/diagnostic histograms

        #: scatterplot of RPC calibrated time vs hit's Ctime relative to earliest-Ctime
        self.hist_ctimeRPCtCal = ROOT.TH2F('CtimeRPCtCal',
                                           expRun + 'RPC tCal vs relative Ctime;' +
                                           't - t(trigger) - dt(sector) (ns);' +
                                           'Ctime - minCtime',
                                           16, 281.5, 345.5, 16, -0.5, 255.5)
        #: scatterplot of RPC calibrated time vs hit's Ctime relative to earliest-Ctime, corrected for DC-processing delay
        self.hist_ctimeRPCtCalCorr = ROOT.TH2F('ctimeRPCtCalCorr',
                                               expRun + 'RPC tCal vs relative Ctime;' +
                                               't - t(trigger) - dt(sector) - dt(index) (ns);' +
                                               'Ctime - minCtime',
                                               16, 281.5, 345.5, 16, -0.5, 255.5)
        #: scatterplot of RPC calibrated time vs hit's index
        self.hist_jRPCtCal = ROOT.TH2F('jRPCtCal',
                                       expRun + 'RPC tCal vs hit index;' +
                                       't - t(trigger) - dt(sector) (ns);' +
                                       'Hit index',
                                       16, 281.5, 345.5, 50, -0.5, 49.5)
        #: scatterplot of RPC calibrated time vs hit's index, corrected for DC-processing delay
        self.hist_jRPCtCalCorr = ROOT.TH2F('jRPCtCalCorr',
                                           expRun + 'RPC tCal vs hit index;' +
                                           't - t(trigger) - dt(sector) - dt(index) (ns);' +
                                           'Hit index',
                                           16, 281.5, 345.5, 50, -0.5, 49.5)
        #: histogram of RawKLM[] header's trigger CTIME relative to its final-data-word trigger REVO9 time
        self.hist_trigCtimeVsTrigRevo9time = ROOT.TH1F('trigCtimeVsTrigRevo9time',
                                                       expRun + 'trigCtime - trigRevo9time (ns)',
                                                       256, -1024.5, 1023.5)
        #: histogram of RPC TDC range
        self.hist_tdcRangeRPC = ROOT.TH1F('tdcRangeRPC',
                                          expRun + 'RPC TDC range;' +
                                          'maxTDC - minTDC (ns)',
                                          128, -0.5, 1023.5)
        #: histogram of RPC Ctime range
        self.hist_ctimeRangeRPC = ROOT.TH1F('ctimeRangeRPC',
                                            expRun + 'RPC Ctime range;' +
                                            'maxCtime - minCtime (ns)',
                                            128, -0.5, 1023.5)
        #: scatterplot of RPC TDC range vs Ctime range
        self.hist_tdcRangeVsCtimeRangeRPC = ROOT.TH2F('tdcRangeVsCtimeRangeRPC',
                                                      expRun + 'RPC Ctime range vs TDC range;' +
                                                      'maxTDC - minTDC (ns);' +
                                                      'maxCtime - minCtime (ns)',
                                                      128, -0.5, 1023.5, 128, -0.5, 1023.5)
        #: scatterplot of RPC TDC range vs time
        self.hist_tdcRangeVsTimeRPC = ROOT.TH2F('tdcRangeVsTimeRPC',
                                                expRun + 'RPC TDC range vs time;' +
                                                't - t(trigger) (ns);' +
                                                'maxTDC - minTDC (ns)',
                                                128, -0.5, 1023.5, 128, -0.5, 1023.5)
        #: scatterplot of RPC Ctime range vs time
        self.hist_ctimeRangeVsTimeRPC = ROOT.TH2F('ctimeRangeVsTimeRPC',
                                                  expRun + 'RPC Ctime range vs time;' +
                                                  't - t(trigger) (ns);' +
                                                  'maxCtime - minCtime (ns)',
                                                  128, -0.5, 1023.5, 128, -0.5, 1023.5)

        # Create the BKLMHit1d-related histograms

        #: histogram of the number of BKLMHit1ds
        self.hist_nHit1d = ROOT.TH1F('NHit1d', expRun + '# of BKLMHit1ds', 100, -0.5, 99.5)
        #: histogram of the number of in-time RPC BKLMHit1ds
        self.hist_nHit1dRPCPrompt = ROOT.TH1F('NHit1dRPCPrompt', expRun + '# of prompt RPC BKLMHit1ds', 100, -0.5, 99.5)
        #: histogram of the number of out-of-time RPC BKLMHit1ds
        self.hist_nHit1dRPCBkgd = ROOT.TH1F('NHit1dRPCBkgd', expRun + '# of background RPC BKLMHit1ds', 100, -0.5, 99.5)
        #: histogram of the number of scint BKLMHit1ds
        self.hist_nHit1dScint = ROOT.TH1F('NHit1dScint', expRun + '# of scintillator BKLMHit1ds', 100, -0.5, 99.5)
        #: histogram of the number of in-time scint BKLMHit1ds
        self.hist_nHit1dPrompt = ROOT.TH1F('NHit1dPrompt', expRun + '# of prompt BKLMHit1ds', 100, -0.5, 99.5)
        #: histogram of the number of out-of-time scint BKLMHit1ds
        self.hist_nHit1dBkgd = ROOT.TH1F('NHit1dBkgd', expRun + '# of bkgd BKLMHit1ds', 100, -0.5, 99.5)
        #: scatterplot of #Z BKLMHit1ds vs #Phi BKLMHit1ds
        self.hist_n1dPhiZ = ROOT.TH2F('NHit1dPhiZ',
                                      expRun + 'Distribution of BKLMHit1ds;# of phi BKLMHit1ds;# of z BKLMHit1ds',
                                      60, -0.5, 59.5, 60, -0.5, 59.5)
        #: scatterplot of #Phi BKLMHit1ds vs sector
        self.hist_multiplicityPhiBySector = ROOT.TH2F('Hit1dMultiplicityPhiBySector',
                                                      expRun + 'BKLMHit1d phi-strip multiplicity;' +
                                                      'sector # (0-7 = backward, 8-15 = forward);' +
                                                      '# of strips',
                                                      16, -0.5, 15.5, 8, -0.5, 7.5)
        #: scatterplot of #Z BKLMHit1ds vs sector
        self.hist_multiplicityZBySector = ROOT.TH2F('Hit1dMultiplicityZBySector',
                                                    expRun + 'BKLMHit1d z-strip multiplicity;' +
                                                    'sector # (0-7 = backward, 8-15 = forward);' +
                                                    '# of strips',
                                                    16, -0.5, 15.5, 8, -0.5, 7.5)
        #: histogram of RPC-phi BKLMHit1d time relative to event's trigger time, corrected for inter-sector variation
        self.hist_tphiRPCCal1d = ROOT.TH1F('tphiRPCCal1d',
                                           expRun + 'RPC BKLMHit1d phi-strip time distribution;' +
                                           't(phi) - t(trigger) - dt(sector) (ns)',
                                           256, -0.5, 1023.5)
        #: histogram of RPC-z BKLMHit1d time relative to event's trigger time, corrected for inter-sector variation
        self.hist_tzRPCCal1d = ROOT.TH1F('tzRPCCal1d',
                                         expRun + 'RPC BKLMHit1d z-strip time distribution;' +
                                         't(z) - t(trigger) - dt(sector) (ns)',
                                         256, -0.5, 1023.5)
        #: histogram of RPC-phi and -z BKLMHit1d avg time relative to event's trigger time, corrected for inter-sector variation
        self.hist_tRPCCal1d = ROOT.TH1F('tRPCCal1d',
                                        expRun + 'RPC BKLMHit1d x 2 calibrated average-time distribution;' +
                                        '0.5*[t(phi) + t(z)] - t(trigger) - dt(sector) (ns)',
                                        256, -0.5, 1023.5)
        #: histogram of RPC-phi and -z BKLMHit1d time difference
        self.hist_dtRPC1d = ROOT.TH1F('dtRPC1d',
                                      expRun + 'RPC BKLMHit1d x 2 time-difference distribution;' +
                                      't(phi) - t(z) (ns)',
                                      50, -100.0, 100.0)
        #: histogram of scint-phi BKLMHit1d time relative to event's trigger Ctime, corrected for inter-sector variation
        self.hist_ctphiScintCal1d = ROOT.TH1F('ctphiScintCal1d',
                                              expRun + 'Scintillator BKLMHit1d phi-strip ctime distribution;' +
                                              'ctime(phi) - ct(trigger) - dt(sector) (ns)',
                                              128, -0.5, 1023.5)
        #: histogram of scint-z BKLMHit1d time relative to event's trigger Ctime, corrected for inter-sector variation
        self.hist_ctzScintCal1d = ROOT.TH1F('ctzScintCal1d',
                                            expRun + 'Scintillator BKLMHit1d z-strip ctime distribution;' +
                                            'ctime(z) - ct(trigger) - dt(sector) (ns)',
                                            128, -0.5, 1023.5)
        #: histogram of scint-phi and -z BKLMHit1d avg time relative to event's trigger Ctime, corrected for inter-sector variation
        self.hist_ctScintCal1d = ROOT.TH1F('ctScintCal1d',
                                           expRun + 'Scintillator BKLMHit1d x 2 calibrated average-time distribution;' +
                                           '0.5*[ctime(phi) + ctime(z)] - ct(trigger) - dt(sector) (ns)',
                                           128, -0.5, 1023.5)
        #: histogram of scint-phi and -z BKLMHit1d time difference
        self.hist_dtScint1d = ROOT.TH1F('dtScint1d',
                                        expRun + 'Scintillator BKLMHit1d x 2 time-difference distribution;' +
                                        'ctime(phi) - ctime(z) (ns)',
                                        50, -100.0, 100.0)

        # Create the BKLMHit2d-related histograms

        #: histogram of the number of BKLMHit2ds
        self.hist_nHit2d = ROOT.TH1F('NHit2d', expRun + '# of BKLMHit2ds', 50, -0.5, 49.5)
        #: scatterplot of end view of forward BKLM for in-time BKLMHit2ds
        self.hist_occupancyForwardXYPrompt = ROOT.TH2F('occupancyForwardXYPrompt',
                                                       expRun + 'Forward xy RPC occupancy for in-time hits;x(cm);y(cm)',
                                                       230, -345.0, 345.0, 230, -345.0, 345.0)
        #: scatterplot of end view of backward BKLM for in-time BKLMHit2ds
        self.hist_occupancyBackwardXYPrompt = ROOT.TH2F('occupancyBackwardXYPrompt',
                                                        expRun + 'Backward xy RPC occupancy for in-time hits;x(cm);y(cm)',
                                                        230, -345.0, 345.0, 230, -345.0, 345.0)
        #: scatterplot of end view of forward BKLM for out-of-time BKLMHit2ds
        self.hist_occupancyForwardXYBkgd = ROOT.TH2F('occupancyForwardXYBkgd',
                                                     expRun + 'Forward xy RPC occupancy for out-of-time hits;x(cm);y(cm)',
                                                     230, -345.0, 345.0, 230, -345.0, 345.0)
        #: scatterplot of end view of backward BKLM for out-of-time BKLMHit2ds
        self.hist_occupancyBackwardXYBkgd = ROOT.TH2F('occupancyBackwardXYBkgd',
                                                      expRun + 'Backward xy RPC occupancy for out-of-time hits;x(cm);y(cm)',
                                                      230, -345.0, 345.0, 230, -345.0, 345.0)
        
        #------ adding by me -----------------------------------------------------------------------------
        #: scatterplot of end view of backward BKLM for in-time BKLMHit2ds
        self.hist_occupancyBackwardXYPromptBkgd = ROOT.TH2F('occupancyBackwardXYPromptBkgd',
                                                        expRun + 'Backward xy RPC occupancy for total hits;x(cm);y(cm)',
                                                        230, -345.0, 345.0, 230, -345.0, 345.0)
        #: scatterplot of end view of forward BKLM for out-of-time BKLMHit2ds
        self.hist_occupancyForwardXYPromptBkgd = ROOT.TH2F('occupancyForwardXYPromptBkgd',
                                                     expRun + 'Forward xy RPC occupancy for total hits;x(cm);y(cm)',
                                                     230, -345.0, 345.0, 230, -345.0, 345.0)
        #------------ up to this point -----------------------------------------------------------------------

        #------ adding by me -----------------------------------------------------------------------------
        #: Occupancy for Forward and Backward per layers.
        self.hist_occupancyForwardXY = []
        self.hist_occupancyBackwardXY = []
        
        for layer in range(0, 15):
            labelForward = 'occupancyForwardXYPromptBkgd_L{0:02d}'.format(layer)
            titleForward = '{0}:Forward XY RPC Occupancy for layer {1} hits;x(cm);y(cm)'.format(expRun, layer)

            labelBackward = 'occupancyBackwardXYPromptBkgd_L{0:02d}'.format(layer)
            titleBackward = '{0}:Backward XY RPC Occupancy for layer {1} hits;x(cm);y(cm)'.format(expRun, layer)
            
            self.hist_occupancyForwardXY.append(ROOT.TH2F(labelForward, titleForward, 230, -345.0, 345.0, 230, -345.0, 345.0))
            self.hist_occupancyBackwardXY.append(ROOT.TH2F(labelBackward, titleBackward, 230, -345.0, 345.0, 230, -345.0, 345.0))
            
        #------------ up to this point -----------------------------------------------------------------------
        
        #: scatterplot of side view of forward BKLM for in-time BKLMHit2ds
        self.hist_occupancyRZPrompt = ROOT.TH2F('occupancyRZPrompt',
                                                expRun + 'layer-z occupancy for in-time hits;z(cm);layer',
                                                48, -190.0, 290.0, 16, -0.5, 15.5)
        #: histogram of z coordinate for in-time BKLMHit2ds
        self.hist_occupancyZPrompt = ROOT.TH1F('occupancyZPrompt',
                                               expRun + 'z occupancy for in-time hits;z(cm)',
                                               48, -190.0, 290.0)
        #: histogram of layer# for in-time BKLMHit2ds
        self.hist_occupancyRPrompt = ROOT.TH1F('occupancyRPrompt',
                                               expRun + 'layer occupancy for in-time hits;layer',
                                               16, -0.5, 15.5)
        #: scatterplot of side view of forward BKLM for in-time BKLMHit2ds
        self.hist_occupancyRZBkgd = ROOT.TH2F('occupancyRZBkgd',
                                              expRun + 'layer-z occupancy for out-of-time hits;z(cm);layer',
                                              48, -190.0, 290.0, 16, -0.5, 15.5)
        #: histogram of z coordinate for out-of-time BKLMHit2ds
        self.hist_occupancyZBkgd = ROOT.TH1F('occupancyZBkgd',
                                             expRun + 'z occupancy for out-of-time hits;z(cm)',
                                             48, -190.0, 290.0)
        #: histogram of layer# for out-of-time BKLMHit2ds
        self.hist_occupancyRBkgd = ROOT.TH1F('occupancyRBkgd',
                                             expRun + 'layer occupancy for out-of-time hits;layer',
                                             16, -0.5, 15.5)
        #: histogram of RPC calibrated time in BKLMHit2ds
        self.hist_tRPCCal2d = ROOT.TH1F('tRPCCal2d',
                                        expRun + 'RPC BKLMHit2d time distribution;' +
                                        't - t(trigger) - dt(sector) (ns)',
                                        256, -0.5, 1023.5)
        #: scatterplot of RPC calibrated time in BKLMHit2ds vs sector
        self.hist_tRPCCal2dBySector = ROOT.TH2F('tRPCCal2dBySector',
                                                expRun + 'RPC BKLMHit2d time distribution;' +
                                                'sector # (0-7 = backward, 8-15 = forward);' +
                                                't - t(trigger) - dt(sector) (ns)',
                                                16, -0.5, 15.5, 256, -0.5, 1023.5)
        #: histogram of scint calibrated time in BKLMHit2ds
        self.hist_ctScintCal2d = ROOT.TH1F('ctScintCal2d',
                                           expRun + 'Scint BKLMHit2d ctime distribution;' +
                                           'ct - t(trigger) - dt(sector) (ns)',
                                           128, -0.5, 1023.5)
        #: scatterplot of scint calibrated time in BKLMHit2ds vs sector
        self.hist_ctScintCal2dBySector = ROOT.TH2F('ctScintCal2dBySector',
                                                   expRun + 'Scint BKLMHit2d ctime distribution;' +
                                                   'sector # (0-7 = backward, 8-15 = forward);' +
                                                   'ct - t(trigger) - dt(sector) (ns)',
                                                   16, -0.5, 15.5, 128, -0.5, 1023.5)

        # Open the output PDF file for event displays

        #if self.maxDisplays > 0:
            #: TCanvas on which event displays will be drawn
            #self.eventCanvas = ROOT.TCanvas("eventCanvas", self.eventPdfName, 3200, 1600)
            #title = '{0}['.format(self.eventPdfName)
            #self.eventCanvas.SaveAs(title)
            #self.eventCanvas.Clear()
            #self.eventCanvas.Divide(2, 1)

        # Create the boilerplate for the end- and side-views of the event display

        #: list of line-segment (x,y) points for the BKLM end view
        self.bklmXY = []
        r0 = 201.9 + 0.5 * 4.4  # cm
        dr = 9.1  # cm
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
        g.SetPoint(0, -5.0, 0.0)
        g.SetPoint(1, +5.0, 0.0)
        g.SetPoint(2, 0.0, 0.0)
        g.SetPoint(3, 0.0, +5.0)
        g.SetPoint(4, 0.0, -5.0)
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
        #: list of line-segment (z,y) points for the BKLM side view
        self.bklmZY = []
        rF = r0 + 14 * dr
        x0 = r0 * tan0
        z0 = 47.0  # cm
        zL = 220.0  # cm
        g = ROOT.TGraph()
        g.SetPoint(0, -zL + z0 - 140.0, 0.0)
        g.SetPoint(1, +zL + z0 + 70.0, 0.0)
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
        g.SetPoint(0, -5.0, 0.0)
        g.SetPoint(1, +5.0, 0.0)
        g.SetPoint(2, 0.0, 0.0)
        g.SetPoint(3, 0.0, +5.0)
        g.SetPoint(4, 0.0, -5.0)
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

    def terminate(self):
        """Handle job termination: draw histograms, close output files"""

        #if self.maxDisplays > 0:
         #   pdfNameLast = '{0}]'.format(self.eventPdfName)
          #  self.eventCanvas.Print(pdfNameLast, self.lastTitle)

        for sectorFB in range(0, 16):
            mappedScintSectorOccupancy = self.hist_mappedScintSectorOccupancy.GetBinContent(sectorFB + 1)
            if mappedScintSectorOccupancy > 0:
                for laneAxis in range(0, 42):
                    numerator = self.hist_mappedScintLaneAxisOccupancy.GetBinContent(sectorFB + 1, laneAxis + 1)
                    self.hist_mappedScintLaneAxisOccupancy.SetBinContent(
                        sectorFB + 1, laneAxis + 1, 100.0 * numerator / mappedScintSectorOccupancy)
            mappedRPCSectorOccupancy = self.hist_mappedRPCSectorOccupancy.GetBinContent(sectorFB + 1)
            if mappedRPCSectorOccupancy > 0:
                for laneAxis in range(0, 42):
                    numerator = self.hist_mappedRPCLaneAxisOccupancy.GetBinContent(sectorFB + 1, laneAxis + 1)
                    self.hist_mappedRPCLaneAxisOccupancy.SetBinContent(
                        sectorFB + 1, laneAxis + 1, 100.0 * numerator / mappedRPCSectorOccupancy)
            unmappedScintSectorOccupancy = self.hist_unmappedScintSectorOccupancy.GetBinContent(sectorFB + 1)
            if unmappedScintSectorOccupancy > 0:
                for laneAxis in range(0, 42):
                    numerator = self.hist_unmappedScintLaneAxisOccupancy.GetBinContent(sectorFB + 1, laneAxis + 1)
                    self.hist_unmappedScintLaneAxisOccupancy.SetBinContent(
                        sectorFB + 1, laneAxis + 1, 100.0 * numerator / unmappedScintSectorOccupancy)
            unmappedRPCSectorOccupancy = self.hist_unmappedRPCSectorOccupancy.GetBinContent(sectorFB + 1)
            if unmappedRPCSectorOccupancy > 0:
                for laneAxis in range(0, 42):
                    numerator = self.hist_unmappedRPCLaneAxisOccupancy.GetBinContent(sectorFB + 1, laneAxis + 1)
                    self.hist_unmappedRPCLaneAxisOccupancy.SetBinContent(
                        sectorFB + 1, laneAxis + 1, 100.0 * numerator / unmappedRPCSectorOccupancy)

        self.histogramFile.Write()
        self.histogramFile.Close()
        print('Goodbye')

    def beginRun(self):
        """Handle begin of run: print diagnostic message"""
        EventMetaData = Belle2.PyStoreObj('EventMetaData')
        print('beginRun', EventMetaData.getRun())

    def endRun(self):
        """Handle end of run: print diagnostic message"""
        EventMetaData = Belle2.PyStoreObj('EventMetaData')
        print('endRun', EventMetaData.getRun())

    def event(self):
        """Process one event: fill histograms, (optionally) draw event display"""

        self.eventCounter += 1
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
        count = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
        rawFb = [[], [], [], [], [], [], [], [], [], [], [], [], [], [], [], []]
        rawSector = [[], [], [], [], [], [], [], [], [], [], [], [], [], [], [], []]
        rawLayer = [[], [], [], [], [], [], [], [], [], [], [], [], [], [], [], []]
        rawPlane = [[], [], [], [], [], [], [], [], [], [], [], [], [], [], [], []]
        rawStrip = [[], [], [], [], [], [], [], [], [], [], [], [], [], [], [], []]
        rawCtime = [[], [], [], [], [], [], [], [], [], [], [], [], [], [], [], []]
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
            if (nodeID < 0) or (nodeID > 4):  # skip EKLM nodes
                continue
            trigCtime = (rawklm.GetTTCtime(0) & 0x7ffffff) << 3  # (ns)
            revo9time = trigCtime - 0x3b0
            for finesse in range(0, 4):
                dc = (finesse << 2) + copper
                nWords = rawklm.GetDetectorNwords(0, finesse)
                self.hist_rawKLMsizeByDCMultihit[dc].Fill(nWords)
                if nWords <= 0:
                    continue
                countAllMultihit = countAllMultihit + nWords
                bufSlot = rawklm.GetDetectorBuffer(0, finesse)
                lastWord = bufSlot[nWords - 1]
                if lastWord & 0xffff != 0:
                    print("##1 Event", event, 'copper', copper, 'finesse', finesse, 'n=', nWords, 'lastWord=', hex(lastWord))
                if (nWords % 2) == 0:
                    print("##2 Event", event, 'copper', copper, 'finesse', finesse, 'n=', nWords, 'should be odd -- skipping')
                    continue
                if int(self.exp) != 3:  # revo9time was not stored in the last word of the data-packet list?
                    revo9time = ((lastWord >> 16) << 3) & 0xffff
                dt = (trigCtime - revo9time) & 0x3ff
                if dt >= 0x200:
                    dt -= 0x400
                self.hist_trigCtimeVsTrigRevo9time.Fill(dt)
                countAll += 1
                count[dc] += 1
                sectorFB = self.dcToSectorFB[dc]
                n = nWords >> 1  # number of Data-Concentrator data packets
                channelMultiplicity = {}
                minRPCCtime = 99999
                maxRPCCtime = 0
                minRPCtdc = 99999
                maxRPCtdc = 0
                minScintCtime = 99999
                maxScintCtime = 0
                # first pass over this DC: determine per-channel multiplicities, event time ranges, and
                # fill dictionaries for accessing RawKLM hit information from BLKMHit1ds and BKLMHit2ds
                for j in range(0, n):
                    word0 = bufSlot[j * 2]
                    word1 = bufSlot[j * 2 + 1]
                    ctime = word0 & 0xffff
                    channel = (word0 >> 16) & 0x7f
                    axis = (word0 >> 23) & 0x01
                    lane = (word0 >> 24) & 0x1f  # 1..2 for scints, 8..20 for RPCs (=readout-board slot - 7)
                    flag = (word0 >> 30) & 0x03  # identifies scintillator or RPC hit
                    adc = word1 & 0x0fff
                    tdc = (word1 >> 16) & 0x07ff
                    isRPC = (flag == 1)
                    isScint = (flag == 2)
                    laneAxisChannel = (word0 >> 16) & 0x1fff
                    if laneAxisChannel not in channelMultiplicity:
                        countAll = countAll + 2
                        count[dc] = count[dc] + 2
                        channelMultiplicity[laneAxisChannel] = 0
                    channelMultiplicity[laneAxisChannel] += 1
                    if isRPC:
                        if ctime < minRPCCtime:
                            minRPCCtime = ctime
                        if ctime > maxRPCCtime:
                            maxRPCCtime = ctime
                        if tdc < minRPCtdc:
                            minRPCtdc = tdc
                        if tdc > maxRPCtdc:
                            maxRPCtdc = tdc
                    elif isScint:
                        if int(self.exp) <= 3:  # fix the ctime for old SCROD firmware
                            trigCtx = trigCtime >> 3
                            ctime = trigCtx - ((trigCtx - ctime) << 2)
                        if ctime < minScintCtime:
                            minScintCtime = ctime
                        if ctime > maxScintCtime:
                            maxScintCtime = ctime
                    electId = (channel << 12) | (axis << 11) | (lane << 6) | (finesse << 4) | nodeID
                    if electId in self.electIdToModuleId:
                        moduleId = self.electIdToModuleId[electId]
                        fb = (moduleId & self.BKLM_END_MASK) >> self.BKLM_END_BIT
                        sector = (moduleId & self.BKLM_SECTOR_MASK) >> self.BKLM_SECTOR_BIT
                        layer = (moduleId & self.BKLM_LAYER_MASK) >> self.BKLM_LAYER_BIT
                        plane = (moduleId & self.BKLM_PLANE_MASK) >> self.BKLM_PLANE_BIT
                        strip = (moduleId & self.BKLM_STRIP_MASK) >> self.BKLM_STRIP_BIT
                        rawFb[dc].append(fb)
                        rawSector[dc].append(sector)
                        rawLayer[dc].append(layer)
                        rawPlane[dc].append(plane)
                        rawStrip[dc].append(strip)
                        rawCtime[dc].append(ctime)
                    else:
                        rawFb[dc].append(-1)
                        rawSector[dc].append(-1)
                        rawLayer[dc].append(-1)
                        rawPlane[dc].append(-1)
                        rawStrip[dc].append(-1)
                        rawCtime[dc].append(-1)
                tdcRangeRPC = maxRPCtdc - minRPCtdc  # (ns)
                ctimeRangeRPC = (maxRPCCtime - minRPCCtime) << 3  # (ns)
                ctimeRangeScint = (maxScintCtime - minScintCtime) << 3  # (ns)
                if n > 1:
                    if maxRPCCtime > 0:
                        self.hist_mappedRPCCtimeRangeBySector.Fill(sectorFB, ctimeRangeRPC)
                    if maxScintCtime > 0:
                        self.hist_mappedScintCtimeRange.Fill(ctimeRangeScint)
                        self.hist_mappedScintCtimeRangeBySector.Fill(sectorFB, ctimeRangeScint)
                # second pass over this DC's hits: histogram everything
                for j in range(0, n):
                    word0 = bufSlot[j * 2]
                    word1 = bufSlot[j * 2 + 1]
                    ctime = word0 & 0xffff
                    channel = (word0 >> 16) & 0x7f
                    axis = (word0 >> 23) & 0x01
                    lane = (word0 >> 24) & 0x1f  # 1..2 for scints, 8..20 for RPCs (=readout-board slot - 7)
                    flag = (word0 >> 30) & 0x03  # 1 for RPCs, 2 for scints
                    electId = (channel << 12) | (axis << 11) | (lane << 6) | (finesse << 4) | nodeID
                    adc = word1 & 0x0fff
                    tdc = (word1 >> 16) & 0x07ff
                    tdcExtra = (word1 >> 27) & 0x1f
                    adcExtra = (word1 >> 12) & 0x0f
                    isRPC = (flag == 1)
                    isScint = (flag == 2)
                    laneAxis = axis if ((lane < 1) or (lane > 20)) else ((lane << 1) + axis)
                    laneAxisChannel = (word0 >> 16) & 0x1fff
                    multiplicity = channelMultiplicity[laneAxisChannel]
                    if multiplicity > 1:  # histogram only if 2+ entries in the same channel
                        self.hist_rawKLMchannelMultiplicity[dc].Fill(multiplicity, laneAxis)
                        self.hist_rawKLMchannelMultiplicityFine[dc].Fill(multiplicity, laneAxisChannel)
                    if (self.singleEntry == 1 and multiplicity > 1) or (self.singleEntry == 2 and multiplicity == 1):
                        continue
                    self.hist_rawKLMlaneFlag.Fill(flag, lane)
                    if isRPC:
                        self.hist_rawKLMtdcExtraRPC.Fill(sectorFB, tdcExtra)
                        self.hist_rawKLMadcExtraRPC.Fill(sectorFB, adcExtra)
                    elif isScint:
                        self.hist_rawKLMtdcExtraScint.Fill(sectorFB, tdcExtra)
                        self.hist_rawKLMadcExtraScint.Fill(sectorFB, adcExtra)
                        if int(self.exp) <= 3:  # fix the ctime for old SCROD firmware
                            trigCtx = trigCtime >> 3
                            ctime = trigCtx - ((trigCtx - ctime) << 2)
                    t = (tdc - trigCtime) & 0x03ff  # in ns, range is 0..1023
                    dtIndex = 0.75 * j
                    ct = (ctime << 3) - (trigCtime & 0x7fff8)  # in ns, range is only 8 bits in SCROD (??)
                    ct = ct & 0x3ff
                    if electId in self.electIdToModuleId:  # mapped-channel histograms
                        self.hist_mappedSectorOccupancyMultihit.Fill(sectorFB)
                        if channelMultiplicity[laneAxisChannel] == 1:
                            self.hist_mappedSectorOccupancy.Fill(sectorFB)
                        if isRPC:
                            self.hist_RPCTimeLowBitsBySector.Fill(sectorFB, (tdc & 3))
                            tCal = t - self.t0RPC[sectorFB]
                            if j == 0:
                                self.hist_tdcRangeRPC.Fill(tdcRangeRPC)
                                self.hist_ctimeRangeRPC.Fill(ctimeRangeRPC)
                                self.hist_tdcRangeVsCtimeRangeRPC.Fill(tdcRangeRPC, ctimeRangeRPC)
                            self.hist_tdcRangeVsTimeRPC.Fill(tCal, tdcRangeRPC)
                            self.hist_ctimeRangeVsTimeRPC.Fill(tCal, ctimeRangeRPC)
                            if abs(tCal - self.t0Cal) < 50:
                                self.hist_mappedChannelOccupancyPrompt[sectorFB][axis].Fill(lane, channel)
                                # this code is probably not so useful after the 13x replication of the DC firmware
                                if n > 20:
                                    self.hist_ctimeRPCtCal.Fill(tCal, ctime - minRPCCtime)
                                    self.hist_ctimeRPCtCalCorr.Fill(tCal - dtIndex, ctime - minRPCCtime)
                                    self.hist_jRPCtCal.Fill(tCal, j)
                                    self.hist_jRPCtCalCorr.Fill(tCal - dtIndex, j)
                            else:
                                self.hist_mappedChannelOccupancyBkgd[sectorFB][axis].Fill(lane, channel)
                            self.hist_mappedRPCSectorOccupancy.Fill(sectorFB)
                            self.hist_mappedRPCLaneAxisOccupancy.Fill(sectorFB, laneAxis)
                            self.hist_mappedRPCTime.Fill(t)
                            self.hist_mappedRPCTimeCal.Fill(tCal)
                            self.hist_mappedRPCTimeCal2.Fill(tCal - dtIndex)
                            self.hist_mappedRPCTimeBySector.Fill(sectorFB, t)
                            self.hist_mappedRPCTimeCalBySector.Fill(sectorFB, tCal - dtIndex)
                            self.hist_mappedRPCTimePerSector[sectorFB].Fill(t)
                            self.hist_mappedRPCTimePerLayer[sectorFB][lane - 6].Fill(t)
                        elif isScint:
                            self.hist_ScintTimeLowBitsBySector.Fill(sectorFB, (tdc & 3))
                            ctCal = ct - self.ct0Scint[sectorFB]
                            if abs(ctCal - self.ct0Cal) < 50:
                                self.hist_mappedChannelOccupancyPrompt[sectorFB][1 - axis].Fill(lane, channel)
                            else:
                                self.hist_mappedChannelOccupancyBkgd[sectorFB][1 - axis].Fill(lane, channel)
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
                            self.hist_mappedScintCtimePerLayer[sectorFB][lane - 1].Fill(ct)
                    else:  # unmapped-channel histograms
                        self.hist_unmappedSectorOccupancyMultihit.Fill(sectorFB)
                        if channelMultiplicity[laneAxisChannel] == 1:
                            self.hist_unmappedSectorOccupancy.Fill(sectorFB)
                        if isRPC:
                            self.hist_unmappedChannelOccupancy[sectorFB][axis].Fill(lane, channel)
                            self.hist_RPCTimeLowBitsBySector.Fill(sectorFB, (tdc & 3))
                            self.hist_unmappedRPCSectorOccupancy.Fill(sectorFB)
                            self.hist_unmappedRPCLaneAxisOccupancy.Fill(sectorFB, laneAxis)
                            self.hist_unmappedRPCTime.Fill(t)
                            self.hist_unmappedRPCTimeBySector.Fill(sectorFB, t)
                        elif isScint:
                            self.hist_unmappedChannelOccupancy[sectorFB][1 - axis].Fill(lane, channel)
                            self.hist_ScintTimeLowBitsBySector.Fill(sectorFB, (tdc & 3))
                            self.hist_unmappedScintSectorOccupancy.Fill(sectorFB)
                            self.hist_unmappedScintLaneAxisOccupancy.Fill(sectorFB, laneAxis)
                            self.hist_unmappedScintTime.Fill(t & 0x1f)
                            self.hist_unmappedScintTimeBySector.Fill(sectorFB, t & 0x1f)
                            self.hist_unmappedScintCtime.Fill(ct)
                            self.hist_unmappedScintCtimeBySector.Fill(sectorFB, ct)
                self.hist_rawKLMsizeByDC[dc].Fill(count[dc])
        self.hist_rawKLMsizeMultihit.Fill(countAllMultihit)
        self.hist_rawKLMsize.Fill(countAll)

        # Process the BKLMHit1ds

        cosine = [0, 0, 0, 0, 0, 0, 0, 0]
        sine = [0, 0, 0, 0, 0, 0, 0, 0]
        for sector in range(0, 8):
            phi = math.pi * sector / 4
            cosine[sector] = math.cos(phi)
            sine[sector] = math.sin(phi)
        zyList = [[], [], [], [], [], [], [], []]
        xyList = [[], [], [], [], [], [], [], []]
        r0 = 201.9 + 0.5 * 4.4  # cm
        dr = 9.1  # cm
        z0 = 47.0  # cm
        dzScint = 4.0  # cm
        dzRPC = 4.52  # cm
        nPhiStrips = [37, 42, 36, 36, 36, 36, 48, 48, 48, 48, 48, 48, 48, 48, 48]
        dPhiStrips = [4.0, 4.0, 4.9, 5.11, 5.32, 5.53, 4.3, 4.46, 4.62, 4.77, 4.93, 5.09, 5.25, 5.4, 5.56]
        scintFlip = [[[-1, 1], [-1, 1], [1, 1], [1, -1], [1, -1], [1, -1], [-1, -1], [-1, 1]],
                     [[1, -1], [1, -1], [1, 1], [-1, 1], [-1, 1], [-1, 1], [-1, -1], [1, -1]]]
        promptColor = 3
        bkgdColor = 2
        phiTimes = {}
        zTimes = [{}, {}, {}, {}, {}, {}, {}, {}, {}, {}, {}, {}, {}, {}, {}]
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
            if self.legacyTimes:
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
                    if layer < 2:  # it's a scint layer
                        ctime = rawCtime[dc][j] << 3
                        ct = ctime - trigCtime - self.ct0Scint[sectorFB]  # in ns, range is only 8 bits in SCROD (??)
                        ctTrunc = int(ct) & 0x3ff
                        if abs(ctTrunc - self.ct0Cal) < ctDiffMax:
                            ctDiffMax = int(abs(ctTrunc - self.ct0Cal))
                            tCal = ct
                            if ctDiffMax == 0:
                                break
                    else:  # it's an RPC layer
                        tCal = tCal = hit1d.getTime() - trigCtime - self.t0RPC[sectorFB]
                        break
            else:
                if layer < 2:
                    tCal = hit1d.getTime() - self.ct0Scint[sectorFB]
                else:
                    tCal = hit1d.getTime() - self.t0RPC[sectorFB]
            tCalTrunc = int(tCal) & 0x3ff

            if self.view == 1:
                r = r0 + layer * dr
                yA = r
                zA = 500
                xB = 500
                yB = 500
                stripAverage = (stripMin + stripMax) * 0.5
                isPrompt = False
                if layer < 2:
                    nScint += 1
                    isPrompt = (abs(tCalTrunc - self.ct0Cal1d) < 50)
                    if plane == 0:
                        if fb == 0:
                            zA = z0 - stripAverage * dzScint
                        else:
                            zA = z0 + stripAverage * dzScint
                    else:
                        h = ((stripAverage - 0.5 * nPhiStrips[layer]) * dPhiStrips[layer]) * scintFlip[fb][sector][layer]
                        xB = r * cosine[sector] - h * sine[sector]
                        yB = r * sine[sector] + h * cosine[sector]
                else:
                    isPrompt = (abs(tCalTrunc - self.t0Cal1d) < 50)
                    if plane == 0:
                        if fb == 0:
                            zA = z0 - stripAverage * dzRPC
                        else:
                            zA = z0 + stripAverage * dzRPC
                    else:
                        h = ((stripAverage - 0.5 * nPhiStrips[layer]) * dPhiStrips[layer])  # * rpcFlip[fb][sector]
                        xB = r * cosine[sector] - h * sine[sector]
                        yB = r * sine[sector] + h * cosine[sector]
                    if abs(tCalTrunc - self.t0Cal) < 50:
                        nRPCPrompt += 1
                        if plane == 1:
                            self.hist_multiplicityPhiBySector.Fill(sectorFB, stripMax - stripMin + 1)
                        else:
                            self.hist_multiplicityZBySector.Fill(sectorFB, stripMax - stripMin + 1)
                    else:
                        nRPCBkgd += 1
            if plane == 1:
                nphihits += 1
                phiTimes[key] = tCal
                if layer < 2:
                    self.hist_ctphiScintCal1d.Fill(tCalTrunc)
                else:
                    self.hist_tphiRPCCal1d.Fill(tCalTrunc)
            else:
                nzhits += 1
                zTimes[layer][key] = tCal
                if layer < 2:
                    self.hist_ctzScintCal1d.Fill(tCalTrunc)
                else:
                    self.hist_tzRPCCal1d.Fill(tCalTrunc)
            # Add the hit to the event-display TGraph list (perhaps)
            if (self.view == 1) and (self.eventDisplays < self.maxDisplays):
                if zA != 500:
                    gZY = ROOT.TGraph()
                    gZY.SetPoint(0, zA - 1.0, yA - 1.0)
                    gZY.SetPoint(1, zA - 1.0, yA + 1.0)
                    gZY.SetPoint(2, zA + 1.0, yA + 1.0)
                    gZY.SetPoint(3, zA + 1.0, yA - 1.0)
                    gZY.SetPoint(4, zA - 1.0, yA - 1.0)
                    gZY.SetLineWidth(1)
                    if isPrompt:
                        gZY.SetLineColor(promptColor)
                    else:
                        gZY.SetLineColor(bkgdColor)
                    zyList[sector].append(gZY)
                if xB != 500:
                    gXY = ROOT.TGraph()
                    gXY.SetPoint(0, xB - 1.0, yB - 1.0)
                    gXY.SetPoint(1, xB - 1.0, yB + 1.0)
                    gXY.SetPoint(2, xB + 1.0, yB + 1.0)
                    gXY.SetPoint(3, xB + 1.0, yB - 1.0)
                    gXY.SetPoint(4, xB - 1.0, yB - 1.0)
                    gXY.SetLineWidth(1)
                    if isPrompt:
                        gXY.SetLineColor(promptColor)
                    else:
                        gXY.SetLineColor(bkgdColor)
                    xyList[sector].append(gXY)
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
            tphiTrunc = int(tphi) & 0x3ff
            for zKey in zTimes[layer]:
                mz = zKey & self.BKLM_MODULEID_MASK
                if mphi == mz:
                    tz = zTimes[layer][zKey]
                    tzTrunc = int(tz) & 0x3ff
                    dt = (tphiTrunc - tzTrunc) & 0x3ff
                    if dt >= 0x200:
                        dt -= 0x400
                    t = (tphi + tz) * 0.5
                    tTrunc = int(t) & 0x3ff
                    if layer < 2:
                        self.hist_dtScint1d.Fill(dt)
                    else:
                        self.hist_dtRPC1d.Fill(dt)
                    if abs(dt) < 4000:
                        if layer < 2:
                            self.hist_ctScintCal1d.Fill(tTrunc)
                        else:
                            self.hist_tRPCCal1d.Fill(tTrunc)

        # After processing all of the BKLMHit1ds in the event, draw the event display (perhaps)

        if (self.view == 1) and (self.eventDisplays < self.maxDisplays):
            drawnSectors = 0
            jCanvas = 1
            for sector in range(0, 8):
                if len(zyList[sector]) > self.minRPCHits:
                    drawnSectors += 1
                    self.eventCanvas.cd(jCanvas)
                    title = 'e{0:02d}r{1}: event {2} z-readout hits in S{3}'.format(int(self.exp), int(self.run), event, sector)
                    self.hist_ZY1D[jCanvas - 1].SetTitle(title)
                    self.hist_ZY1D[jCanvas - 1].Draw()
                    for g in self.bklmZY:
                        g.Draw("L")
                    for g in zyList[sector]:
                        g.Draw("L")
                    jCanvas += 1
                    if jCanvas > 2:
                        jCanvas = 1
                        self.lastTitle = "Title:E{0} (#{1})".format(event, self.eventCounter)
                        self.eventCanvas.Print(self.eventPdfName, self.lastTitle)
            enoughXYHits = False
            for sector in range(0, 8):
                if len(xyList[sector]) > self.minRPCHits:
                    enoughXYHits = True
                    break
            if enoughXYHits:
                drawnSectors += 1
                self.eventCanvas.cd(jCanvas)
                jCanvas += 1
                title = 'e{0:02d}r{1}: event {2} phi-readout hits'.format(int(self.exp), int(self.run), event)
                self.hist_XY.SetTitle(title)
                self.hist_XY.Draw()
                for g in self.bklmXY:
                    g.Draw("L")
                for sector in range(0, 8):
                    for g in xyList[sector]:
                        g.Draw("L")
                if jCanvas > 2:
                    jCanvas = 1
                    self.lastTitle = "Title:E{0} (#{1})".format(event, self.eventCounter)
                    self.eventCanvas.Print(self.eventPdfName, self.lastTitle)
            if jCanvas == 2:
                self.eventCanvas.cd(jCanvas)
                ROOT.gPad.Clear()
                self.lastTitle = "Title:E{0} (#{1})".format(event, self.eventCounter)
                self.eventCanvas.Print(self.eventPdfName, self.lastTitle)
            if drawnSectors > 0:
                self.eventDisplays += 1

        # Process the BKLMHit2ds

        xyList = []
        zyList = []
        rpcHits = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
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
                rpcHits[sectorFB] += 1
            if self.legacyTimes:
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
                    if plane == 0:  # it's a z strip
                        if strip < zStripMin:
                            continue
                        if strip > zStripMax:
                            continue
                        ctZ = rawCtime[dc][j] << 3  # in ns, range is only 8 bits in SCROD (??)
                        jZ = j
                    else:  # it's a phi strip
                        if strip < phiStripMin:
                            continue
                        if strip > phiStripMax:
                            continue
                        ctPhi = rawCtime[dc][j] << 3  # in ns, range is only 8 bits in SCROD (??)
                        jPhi = j
                    if (jZ >= 0) and (jPhi >= 0):
                        if layer < 2:  # it's a scint layer
                            if abs(ctZ - ctPhi) > 40:
                                continue
                            ct = int((ctZ + ctPhi) * 0.5 - trigCtime - self.ct0Scint[sectorFB]) & 0x3ff
                            if abs(ct - self.ct0Cal) < ctDiffMax:
                                ctDiffMax = int(abs(ct - self.ct0Cal))
                                tCal = ct
                                if ctDiffMax == 0:
                                    break
                        else:  # it's an RPC layer
                            tCal = hit2d.getTime() - trigCtime - self.t0RPC[sectorFB]
                            break
            else:
                if layer < 2:
                    tCal = hit2d.getTime() - self.ct0Scint[sectorFB]
                else:
                    tCal = hit2d.getTime() - self.t0RPC[sectorFB]
            tCalTrunc = int(tCal) & 0x3ff
            x = hit2d.getGlobalPositionX()
            y = hit2d.getGlobalPositionY()
            z = hit2d.getGlobalPositionZ()
            r = math.sqrt(x * x + y * y)
            isPromptHit = False
            promptColor = 3
            bkgdColor = 2
            #---------- adding by me/ Occupancy per layer--------------------
            #for layers in range(0, layer):
            if layer < 2:
                isPromptHit = True
                if fb == 0:  # backward
                    self.hist_occupancyBackwardXY[layer].Fill(x, y)
                else:  # forward
                    self.hist_occupancyForwardXY[layer].Fill(x, y)

            else:
                isPromptHit = True
                if fb == 0:  # backward
                    self.hist_occupancyBackwardXY[layer].Fill(x, y)
                else:  # forward
                    self.hist_occupancyForwardXY[layer].Fill(x, y)
                    
            #--------------- up to this---------------------------
            
            if layer < 2:
                promptColor = 7
                bkgdColor = 4
                self.hist_ctScintCal2d.Fill(tCalTrunc)
                self.hist_ctScintCal2dBySector.Fill(sectorFB, tCalTrunc)
                
                #------ adding by me ----------------
                isPromptHit = True
                if fb == 0:  # backward
                    self.hist_occupancyBackwardXYPromptBkgd.Fill(x, y)
                else:  # forward
                    self.hist_occupancyForwardXYPromptBkgd.Fill(x, y)
                #----------up to this--------------------
                
                if abs(tCalTrunc - self.ct0Cal2d) < 50:
                    isPromptHit = True
                    if fb == 0:  # backward
                        self.hist_occupancyBackwardXYPrompt.Fill(x, y)
                    else:  # forward
                        self.hist_occupancyForwardXYPrompt.Fill(x, y)
                else:
                    if fb == 0:  # backward
                        self.hist_occupancyBackwardXYBkgd.Fill(x, y)
                    else:  # forward
                        self.hist_occupancyForwardXYBkgd.Fill(x, y)
            else:
                self.hist_tRPCCal2d.Fill(tCalTrunc)
                self.hist_tRPCCal2dBySector.Fill(sectorFB, tCalTrunc)

                #-------- adding by me-------
                isPromptHit = True
                if fb == 0:  # backward
                    self.hist_occupancyBackwardXYPromptBkgd.Fill(x, y)
                else:  # forward
                    self.hist_occupancyForwardXYPromptBkgd.Fill(x, y)
                #-----------up to this------
                
                if abs(tCalTrunc - self.t0Cal2d) < 50:
                    isPromptHit = True
                    self.hist_occupancyRZPrompt.Fill(z, layer)
                    self.hist_occupancyZPrompt.Fill(z)
                    self.hist_occupancyRPrompt.Fill(layer)
                    if fb == 0:  # backward
                        self.hist_occupancyBackwardXYPrompt.Fill(x, y)
                    else:  # forward
                        self.hist_occupancyForwardXYPrompt.Fill(x, y)
                elif abs(tCalTrunc - self.t0Cal2d) >= 50:
                    self.hist_occupancyRZBkgd.Fill(z, layer)
                    self.hist_occupancyZBkgd.Fill(z)
                    self.hist_occupancyRBkgd.Fill(layer)
                    if fb == 0:  # backward
                        self.hist_occupancyBackwardXYBkgd.Fill(x, y)
                    else:  # forward
                        self.hist_occupancyForwardXYBkgd.Fill(x, y)

            # Add the hit to the event-display TGraph list (perhaps)
            if (self.view == 2) and (self.eventDisplays < self.maxDisplays):
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

        # After processing all of the hits in the event, draw the event display (perhaps)

        if (self.view == 2) and (self.eventDisplays < self.maxDisplays):
            hasEnoughRPCHits = False
            for count in rpcHits:
                if count > self.minRPCHits:
                    hasEnoughRPCHits = True
                    break
            if hasEnoughRPCHits:
                self.eventDisplays += 1
                title = 'e{0:02d}r{1}: event {2} z-readout hits'.format(int(self.exp), int(self.run), event)
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
                self.lastTitle = "Title:E{0} (#{1})".format(event, self.eventCounter)
                #self.eventCanvas.Print(self.eventPdfName, self.lastTitle)
                title = 'e{0:02d}r{1}: event {2} phi-readout hits'.format(int(self.exp), int(self.run), event)
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
                self.lastTitle = "Title:E{0} (#{1})".format(event, self.eventCounter)
                #self.eventCanvas.Print(self.eventPdfName, self.lastTitle)
