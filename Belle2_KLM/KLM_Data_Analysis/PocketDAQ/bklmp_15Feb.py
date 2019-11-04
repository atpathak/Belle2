#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# Prerequisite (on kekcc): type
# source /cvmfs/belle.cern.ch/tools/b2setup release-02-01-00
#
# basf2-pocketdaq bklm.py -- -i infilename -e # -r #
# Required argument:
#    -i infilename  to specify the full pathname of the input ROOT file; for example,
#    -i /home/belle2/dbiswas/Documents/PocketDAQ/klm_offline_entpacker/build/klm_unpacker/brandon_data/dblpls_30k_fine_20190109.root
# Optional arguments:
#    -e #   to specify the experiment number, e.g., -e 1 (default is 1)
#    -r #   to specify the run number, e.g., -r 0109 (default is 0000)
#    You need the '--' before these options to tell basf2 that these are options to this script.
#

from basf2 import *
import simulation
import reconstruction
import rawdata
import math
import ctypes
import ROOT
from ROOT import Belle2, TH1F, TH2F, TCanvas, THistPainter, TPad, TFile
from optparse import Option, OptionValueError, OptionParser

#=========================================================================
#
#   EventInspectorBKLM class (must be defined before use)
#
#=========================================================================

class EventInspectorBKLM:

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
        if maxEventCounter > 0:
            self.eventCanvas = ROOT.TCanvas("eventCanvas", eventPdfName, 3200, 1600)
            title = '{0}['.format(eventPdfName)
            self.eventCanvas.SaveAs(title)
            self.eventCanvas.Clear()
            self.eventCanvas.Divide(2,1)
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
        self.histogramFile = ROOT.TFile.Open(histName, "RECREATE")
        # create the rawKLM histograms
        self.hist_rawKLMlane = ROOT.TH1F('rawKLMlane', expRun+'RawKLM lane;Lane (scint: 1..7, RPC: 8..20)', 21, -0.5, 20.5)
        self.hist_rawKLMsizeMultihit = ROOT.TH1F('rawKLMsizeMultihit', expRun+'RawKLM word count (N/channel)', 200, -0.5, 199.5)
        self.hist_rawKLMsize = ROOT.TH1F('rawKLMsize', expRun+'RawKLM word count (1/channel)', 200, -0.5, 199.5)
        self.hist_rawKLMchannelMultiplicity = []
        self.hist_PerChannelMultiplicity = ROOT.TH2F('PerChannelMultiplicity', expRun+'Per-channel multiplicity (N/channel > 1);Per-channel multiplicity;(Lane #) * 2 + (Axis #)', 30, -0.5, 29.5, 42, -0.5, 41.5)
        self.hist_RPCLaneAxisOccupancy = ROOT.TH2F('RPCLaneAxisOccupancy', expRun+'Lane/axis occupancy of RPC channels (1/channel);Sector # (always 0);(Lane #) * 2 + (Axis #)', 3, -1.5, 1.5, 42, -0.5, 41.5)
        self.hist_ScintLaneAxisOccupancy = ROOT.TH2F('ScintLaneAxisOccupancy', expRun+'Lane/axis occupancy of scint channels (1/channel);Sector # (always 0);(Lane #) * 2 + (Axis #)', 3, -1.5, 1.5, 42, -0.5, 41.5)
        self.hist_ChannelOccupancy = [ 0, 0 ]
        self.hist_ChannelOccupancy[0] = ROOT.TH2F('ChannelOccupancy_a0', expRun+'Channel occupancy for axis 0;lane;channel', 42, -0.25, 20.75, 128, -0.25, 63.75)
        self.hist_ChannelOccupancy[1] = ROOT.TH2F('ChannelOccupancy_a1', expRun+'Channel occupancy for axis 1;lane;channel', 42, -0.25, 20.75, 128, -0.25, 63.75)
        self.hist_ChannelOccupancyAL = [ [0, 0], [0, 0], [0, 0], [0, 0], [0, 0], [0, 0], [0, 0], [0, 0], [0, 0], [0, 0], [0, 0], [0, 0], [0, 0], [0, 0], [0, 0], [0, 0], [0, 0], [0, 0], [0, 0], [0, 0], [0, 0] ]
        for lane in range(0, 21):
            nChannels = 64 if (lane > 2) else 128
            label = 'ChannelOccupancy_a0l{0}'.format(lane)
            title = '{0}Channel occupancy for axis 0 lane {1};channel'.format(expRun, lane)
            self.hist_ChannelOccupancyAL[lane][0] = ROOT.TH1F(label, title, nChannels, -0.5, nChannels-0.5)
            label = 'ChannelOccupancy_a1l{0}'.format(lane)
            title = '{0}Channel occupancy for axis 1 lane {1};channel'.format(expRun, lane)
            self.hist_ChannelOccupancyAL[lane][1] = ROOT.TH1F(label, title, nChannels, -0.5, nChannels-0.5)
        self.hist_RPCTimeLowBitsBySector = ROOT.TH2F('RPCTimeLowBitsBySector', expRun+'RPC TDC lowest-order bits;Sector # (always 0);TDC % 4 (ns) [should be 0]', 3, -1.5, 1.5, 4, -0.5, 3.5)
        self.hist_RPCTime = ROOT.TH1F('RPCTime', expRun+'RPC tdc distribution;tdc - triggerTime (ns)', 256, -0.5, 1023.5)
        self.hist_RPCTimePerLayerA0 = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
        for lane in range(0, 21):
            label = 'RPCTimeL{0:02d}A0'.format(lane)
            title = '{0}RPC axis 0 lane {1} time distribution;t - triggerTime (ns)'.format(expRun, lane)
            self.hist_RPCTimePerLayerA0[lane] = ROOT.TH1F(label, title, 256, -0.5, 1023.5)
        self.hist_RPCTimePerLayerA1 = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
        for lane in range(0, 21):
            label = 'RPCTimeL{0:02d}A1'.format(lane)
            title = '{0}RPC axis 0 lane {1} time distribution;t - triggerTime (ns)'.format(expRun, lane)
            self.hist_RPCTimePerLayerA1[lane] = ROOT.TH1F(label, title, 256, -0.5, 1023.5)
        self.hist_ScintTimeLowBitsBySector = ROOT.TH2F('ScintTimeLowBitsBySector', expRun+'Scint TDC lowest-order bits;Sector # (always 0);TDC % 4 (ns) [should be 0]', 3, -1.5, 1.5, 4, -0.5, 3.5)
        self.hist_ScintTime = ROOT.TH1F('ScintTime', expRun+'Scint tdc distribution;tdc - triggerTime (ns)', 256, -0.5, 1023.5)
        self.hist_ScintCtime = ROOT.TH1F('ScintCtime', expRun+'Scint ctime distribution;ctime - triggerCtime (ns)', 32, -0.5, 1023.5)
        self.hist_ScintCtime0 = ROOT.TH1F('ScintCtime0', expRun+'Scint ctime distribution;ctime - triggerTime (ns)', 32, -0.5, 1023.5)
        self.hist_ctimeRPCtdc = ROOT.TH2F('ctimeRPCtdc', expRun+'RPC TDC vs ctime;tdc (ns);ctime - minCtime', 16, 281.5, 345.5, 16, -0.5, 255.5)
        self.hist_ctimeRPCtdc2 = ROOT.TH2F('ctimeRPCtdc2', expRun+'RPC TDC vs ctime;tdc - dt(index) (ns);ctime - minCtime', 16, 281.5, 345.5, 16, -0.5, 255.5)
        self.hist_jRPCtdc = ROOT.TH2F('jRPCtdc', expRun+'RPC TDC vs hit index;tdc (ns);Hit index', 16, 281.5, 345.5, 50, -0.5, 49.5)
        self.hist_jRPCtdc2 = ROOT.TH2F('jRPCtdc2', expRun+'RPC TDC vs hit index;tdc - dt(index) (ns);Hit index', 16, 281.5, 345.5, 50, -0.5, 49.5)
        self.hist_ttCtime = ROOT.TH1F('ttCtime', expRun+'tt_ctime distribution;tt_ctime (ns)', 10, -0.5, 1023.5)
        self.hist_deltaCtime = ROOT.TH1F('deltaCtime', expRun+'delta Ctime distribution;Maxctime-MinCtime (ns)', 128, -0.5, 1023.5)

    def terminate(self):
        if maxEventCounter > 0:
            self.eventCanvas.Clear()
            self.eventCanvas.SaveAs(eventPdfName)
            title = '{0}]'.format(eventPdfName)
            self.eventCanvas.SaveAs(title)
        canvas = ROOT.TCanvas("canvas", pdfName, 1600, 1600)
        title = '{0}['.format(pdfName)
        canvas.SaveAs(title)
        canvas.Clear()
        canvas.GetPad(0).SetGrid(1, 1)
        canvas.GetPad(0).Update()
        self.hist_rawKLMlane.Draw()
        canvas.Print(pdfName, "Title:{0}".format(self.hist_rawKLMlane.GetName()))
        self.hist_rawKLMsizeMultihit.Draw()
        canvas.Print(pdfName, "Title:{0}".format(self.hist_rawKLMsizeMultihit.GetName()))
        self.hist_rawKLMsize.Draw()
        canvas.Print(pdfName, "Title:{0}".format(self.hist_rawKLMsize.GetName()))
        self.hist_PerChannelMultiplicity.Draw("box")
        canvas.Print(pdfName, "Title:{0}".format(self.hist_PerChannelMultiplicity.GetName()))
        canvas.Clear()
        canvas.Divide(2, 1)
        canvas.GetPad(0).SetGrid(1, 1)
        canvas.GetPad(1).SetGrid(1, 1)
        canvas.GetPad(2).SetGrid(1, 1)
        #borderRPC0x = [7.5, 20.5, 20.5, 7.5, 7.5]
        #borderRPC0y = [0.5, 0.5, 48.5, 48.5, 0.5]
        #borderRPC0yChimney = [0.5, 0.5, 34.5, 34.5, 0.5]
        #borderScint0x = [0.5, 1.5, 1.5, 2.5, 2.5, 1.5, 1.5, 0.5, 0.5]
        #borderScint0y = [4.5, 4.5, 2.5, 2.5, 44.5, 44.5, 41.5, 41.5, 4.5]
        #borderRPC1x = [7.5, 20.5, 20.5, 11.5, 11.5, 7.5, 7.5]
        #borderRPC1y = [0.5, 0.5, 48.5, 48.5, 36.5, 36.5, 0.5]
        #borderScint1x = [0.5, 2.5, 2.5, 0.5, 0.5]
        #borderScint1ay = [0.5, 0.5, 9.5, 9.5, 0.5]
        #borderScint1by = [15.5, 15.5, 60.5, 60.5, 15.5]
        #borderScint1xChimney = [0.5, 1.5, 1.5, 2.5, 2.5, 1.5, 1.5, 0.5, 0.5]
        #borderScint1ayChimney = [0.5, 0.5, 0.5, 0.5, 9.5, 9.5, 8.5, 8.5, 0.5]
        #borderScint1byChimney = [15.5, 15.5, 16.5, 16.5, 45.5, 45.5, 45.5, 45.5, 15.5]
        #graphRPC0 = self.makeGraph(borderRPC0x, borderRPC0y)
        #graphRPC0Chimney = self.makeGraph(borderRPC0x, borderRPC0yChimney)
        #graphScint0 = self.makeGraph(borderScint0x, borderScint0y)
        #graphRPC1 = self.makeGraph(borderRPC1x, borderRPC1y)
        #graphScint1a = self.makeGraph(borderScint1x, borderScint1ay)
        #graphScint1b = self.makeGraph(borderScint1x, borderScint1by)
        #graphScint1aChimney = self.makeGraph(borderScint1xChimney, borderScint1ayChimney)
        #graphScint1bChimney = self.makeGraph(borderScint1xChimney, borderScint1byChimney)
        #textRPC0 = self.makeText(6.8, 25.0, "RPC z")
        #textScint0 = self.makeText(3.2, 25.0, "Scint #phi")
        #textRPC1 = self.makeText(6.8, 25.0, "RPC #phi")
        #textScint1 = self.makeText(3.2, 25.0, "Scint z")
        for sectorFB in range(0, 1):
            canvas.cd(1)
            self.hist_ChannelOccupancy[0].Draw("colz")
            #graphRPC0.Draw("L")
            #graphScint0.Draw("L")
            #textRPC0.Draw()
            #textScint0.Draw()
            canvas.cd(2)
            self.hist_ChannelOccupancy[1].Draw("colz")
            #graphRPC1.Draw("L")
            #graphScint1a.Draw("L")
            #graphScint1b.Draw("L")
            #textRPC1.Draw()
            #textScint1.Draw()
            canvas.Print(pdfName, "Title:{0}".format(self.hist_ChannelOccupancy[0].GetName()))
        for lane in range(0, 21):
            n0 = self.hist_ChannelOccupancyAL[lane][0].GetEntries()
            n1 = self.hist_ChannelOccupancyAL[lane][1].GetEntries()
            if n0 + n1 > 0:
                canvas.cd(1)
                self.hist_ChannelOccupancyAL[lane][0].Draw()
                canvas.cd(2)
                self.hist_ChannelOccupancyAL[lane][1].Draw()
                canvas.Print(pdfName, "Title:{0}".format(self.hist_ChannelOccupancyAL[lane][0].GetName()))
        canvas.Clear()
        canvas.Divide(1, 1)
        self.hist_RPCTimeLowBitsBySector.Draw("box")
        canvas.Print(pdfName, "Title:{0}".format(self.hist_RPCTimeLowBitsBySector.GetName()))
        self.hist_RPCTime.Draw()
        canvas.Print(pdfName, "Title:{0}".format(self.hist_RPCTime.GetName()))
        for lane in range(0, 21):
            if self.hist_RPCTimePerLayerA0[lane].GetEntries() > 0:
                self.hist_RPCTimePerLayerA0[lane].Draw()
                canvas.Print(pdfName, "Title:{0}".format(self.hist_RPCTimePerLayerA0[lane].GetName()))
        for lane in range(0, 21):
            if self.hist_RPCTimePerLayerA1[lane].GetEntries() > 0:
                self.hist_RPCTimePerLayerA1[lane].Draw()
                canvas.Print(pdfName, "Title:{0}".format(self.hist_RPCTimePerLayerA1[lane].GetName()))
        self.hist_ScintTimeLowBitsBySector.Draw("box")
        canvas.Print(pdfName, "Title:{0}".format(self.hist_ScintTimeLowBitsBySector.GetName()))
        self.hist_ScintTime.Draw()
        canvas.Print(pdfName, "Title:{0}".format(self.hist_ScintTime.GetName()))
        self.hist_ScintCtime.Draw()
        canvas.Print(pdfName, "Title:{0}".format(self.hist_ScintCtime.GetName()))
        self.hist_ttCtime.Draw()
        canvas.Print(pdfName, "Title:{0}".format(self.hist_ttCtime.GetName()))
        self.hist_deltaCtime.Draw()
        canvas.Print(pdfName, "Title:{0}".format(self.hist_deltaCtime.GetName()))
        self.hist_ScintCtime0.Draw()
        canvas.Print(pdfName, "Title:{0}".format(self.hist_ScintCtime0.GetName()))
        self.hist_ctimeRPCtdc.Draw("colz")
        canvas.Print(pdfName, "Title:{0}".format(self.hist_ctimeRPCtdc.GetName()))
        self.hist_ctimeRPCtdc2.Draw("colz")
        canvas.Print(pdfName, "Title:{0}".format(self.hist_ctimeRPCtdc2.GetName()))
        self.hist_jRPCtdc.Draw("colz")
        canvas.Print(pdfName, "Title:{0}".format(self.hist_jRPCtdc.GetName()))
        self.hist_jRPCtdc2.Draw("colz")
        canvas.Print(pdfName, "Title:{0}".format(self.hist_jRPCtdc2.GetName()))
        canvas.Clear()
        canvas.Print(pdfName)
        title = '{0}]'.format(pdfName)
        canvas.SaveAs(title)
        self.histogramFile.Write()
        self.histogramFile.Close()
        print('Goodbye')

    def beginRun(self):
        print('beginRun', run)

    def endRun(self):
        print('endRun', run)

    def event(self):
        sectorFB = 0
        n = len(eventHits)
        countAllMultihit = 2 * n + 1 if (n > 0) else 0
        countAll = 1
        channelMultiplicity = { }
        minCtime = 99999
        maxCtime = 0
        for j in range(0, n):
            items = eventHits[j]
            lane = items[0]
            channel = items[1]
            axis = items[2]
            ctime = items[3]
            flag = 1 if (lane > 2) else 2
            isRPC = (flag == 1)
            isScint = (flag == 2)
            laneAxisChannel = (((lane << 1) + axis) << 7) + channel
            if laneAxisChannel not in channelMultiplicity:
                countAll = countAll + 2
                channelMultiplicity[laneAxisChannel] = 0
            channelMultiplicity[laneAxisChannel] = channelMultiplicity[laneAxisChannel] + 1
            if ctime < minCtime:
                minCtime = ctime
            if ctime > maxCtime:
                maxCtime = ctime
            self.hist_rawKLMlane.Fill(lane)
        self.hist_ttCtime.Fill((tt_ctime_only << 3) & 0x3ff)
        self.hist_deltaCtime.Fill(maxCtime-minCtime)
        for j in range(0, n):
            items = eventHits[j]
            lane = items[0]
            channel = items[1]
            axis = items[2]
            ctime = items[3]
            tdc = items[4]
            charge = items[5]
            flag = 1 if (lane > 2) else 2
            isRPC = (flag == 1)
            isScint = (flag == 2)
            laneAxisChannel = (((lane << 1) + axis) << 7) + channel
            laneAxis = axis if ((lane < 1) or (lane > 20)) else ((lane << 1) + axis)
            if laneAxisChannel in channelMultiplicity:
                if channelMultiplicity[laneAxisChannel] > 1:
                    self.hist_PerChannelMultiplicity.Fill(channelMultiplicity[laneAxisChannel], laneAxis)
                ### DIVOT del channelMultiplicity[laneAxisChannel] # consider only first hit in the channel/axis/lane of this dc
                t   = (tdc - raw_time) & 0x03ff # in ns, range is 0..1023
                ct  = ((ctime << 3) - tt_ctime) & 0x3ff
                if isRPC:
                    self.hist_RPCTimeLowBitsBySector.Fill(sectorFB, (tdc & 3))
                    self.hist_RPCLaneAxisOccupancy.Fill(sectorFB, laneAxis)
                    self.hist_RPCTime.Fill(t)
                    if axis == 0:
                        self.hist_RPCTimePerLayerA0[lane].Fill(t)
                    else:
                        self.hist_RPCTimePerLayerA1[lane].Fill(t)
                    if n > 60:
                        t0j = 0.75 * j
                        self.hist_ctimeRPCtdc.Fill(t, ctime - minCtime)
                        self.hist_ctimeRPCtdc2.Fill(t - t0j, ctime - minCtime)
                        self.hist_jRPCtdc.Fill(t, j)
                        self.hist_jRPCtdc2.Fill(t - t0j, j)
                else:
                    self.hist_ScintTimeLowBitsBySector.Fill(sectorFB, (tdc & 3))
                    self.hist_ScintLaneAxisOccupancy.Fill(sectorFB, laneAxis)
                    self.hist_ScintTime.Fill(t)
                    self.hist_ScintCtime.Fill(ct)
                    self.hist_ScintCtime0.Fill(((ctime << 3) - raw_time) & 0x3ff)
                self.hist_ChannelOccupancy[axis].Fill(lane, channel)
                self.hist_ChannelOccupancyAL[lane][axis].Fill(channel)
        self.hist_rawKLMsizeMultihit.Fill(countAllMultihit)
        self.hist_rawKLMsize.Fill(countAll)

        #xyList = []
        #zyList = []
        #rpcHits = [ 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0 ]
        #for j in range(0, n):
        #    if lane > 2:
        #        x = 201.9 + 0.5 * 4.4 + 9.1 * (lane - 6)
        #    else:
        #        x = 201.9 + 0.5 * 4.4 + 9.1 * (lane - 1)
        #    y = channel * 4.0 ## nominal strip width in cm
        #    z = 0
        #    promptColor = 3
        #    if self.eventDisplayCounter >= maxEventCounter:
        #        continue
        #    gXY = ROOT.TGraph()
        #    gXY.SetPoint(0, x - 1.0, y - 1.0)
        #    gXY.SetPoint(1, x - 1.0, y + 1.0)
        #    gXY.SetPoint(2, x + 1.0, y + 1.0)
        #    gXY.SetPoint(3, x + 1.0, y - 1.0)
        #    gXY.SetPoint(4, x - 1.0, y - 1.0)
        #    gXY.SetLineWidth(1)
        #    gZY = ROOT.TGraph()
        #    gZY.SetPoint(0, z - 1.0, y - 1.0)
        #    gZY.SetPoint(1, z - 1.0, y + 1.0)
        #    gZY.SetPoint(2, z + 1.0, y + 1.0)
        #    gZY.SetPoint(3, z + 1.0, y - 1.0)
        #    gZY.SetPoint(4, z - 1.0, y - 1.0)
        #    gZY.SetLineWidth(1)
        #    gXY.SetLineColor(promptColor)
        #    gZY.SetLineColor(promptColor)
        #    xyList.append(gXY)
        #    zyList.append(gZY)
        #if self.eventDisplayCounter < maxEventCounter:
        #    hasManyRPCHits = False
        #    for count in rpcHits:
        #        if count > 5:
        #            hasManyRPCHits = True
        #            break
        #    if hasManyRPCHits:
        #        self.eventDisplayCounter = self.eventDisplayCounter + 1
        #        title = 'e{0:02d}r{1}: event {2}'.format(int(exp), int(run), eventNumber)
        #        self.hist_XY.SetTitle(title)
        #        self.hist_ZY.SetTitle(title)
        #        self.eventCanvas.cd(1)
        #        self.hist_XY.Draw()
        #        for g in self.bklmXY:
        #            g.Draw("L")
        #        for g in xyList:
        #            g.Draw("L")
        #        self.eventCanvas.cd(2)
        #        self.hist_ZY.Draw()
        #        for g in self.bklmZY:
        #            g.Draw("L")
        #        for g in zyList:
        #            g.Draw("L")
        #        self.eventCanvas.Print(eventPdfName, "Title:{0}".format(eventNumber))

#=========================================================================
#
#   Main routine
#
#=========================================================================

parser = OptionParser()
parser.add_option('-i', '--inputfile', dest='infilename',
                  default='',
                  help='Input ROOT filename [no default]')
parser.add_option('-e', '--experiment', dest='eNumber',
                  default='0',
                  help='Experiment number [default=0]')
parser.add_option('-r', '--run', dest='rNumber',
                  default='0000',
                  help='Run number [default=0000]')
parser.add_option('-c', '--count', dest='counter',
                  default='1000',
                  help='Max # of event displays [default=1000]')
(options, args) = parser.parse_args()
exp = '{0:04d}'.format(int(options.eNumber))
run = '{0:05d}'.format(int(options.rNumber))
inputRoot = options.infilename
maxEventCounter = int(options.counter)
if len(options.infilename.strip()) == 0:
    print("Missing input filename (required parameter)")
else:
    infile = TFile(options.infilename + '.root')

    #print(infile)
    histName = 'bklmHists-'+ inputRoot +'-e{0}r{1}.root'.format(exp, run)
    pdfName = 'bklmPlots-'+ inputRoot +'-e{0}r{1}.pdf'.format(exp, run)
    eventPdfName = 'bklmEvents-'+ inputRoot +'-e{0}r{1}.pdf'.format(exp, run)
    
    #main.add_module(EventInspectorBKLM())
    inspector = EventInspectorBKLM()
    inspector.initialize()
    inspector.beginRun()
    eventNumber = -1
    eventHits = []
    for row in infile.Get('KLM_raw_hits'):
        if row.eventNr > 20000:
            break
        items = (row.lane,row.channel,row.axis,row.ctime,row.tdc,row.charge)
        tt_ctime_only = row.tt_ctime
        newEventNumber = row.eventNr 
        if newEventNumber == eventNumber:
            eventHits.append(items)
        else:
            if eventNumber >= 0:
                inspector.event()
            eventNumber = newEventNumber
            if row.broken != 0:
                print("*** Event {0} is broken!".format(eventNumber))
            eventHits.clear()
            eventHits.append(items)
            tt_ctime = row.tt_ctime << 3
            raw_time = (row.raw_time >> 16) << 3
    if eventNumber >= 0:
        inspector.event()
    inspector.endRun()
    inspector.terminate()
