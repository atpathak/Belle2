#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Descriptor:
#############################################################
# Steering file for official MC production of phase 3
# 'taupair' samples with beam backgrounds (BGx1).
#
# April 2019 - Belle II Collaboration
#############################################################

from basf2 import *
import ROOT
from ROOT import Belle2
from beamparameters import add_beamparameters
import sys
import math

# reenable GUI thread for our canvas
from ROOT import PyConfig
PyConfig.StartGuiThread = True



#set_log_level(LogLevel.INFO)
set_log_level(LogLevel.DEBUG)

# Create some histograms to be filled
h_nMCParticles = ROOT.TH1D('nMCParticles', 'Number of MCParticles per Event;#', 20, 0, 20)
h_pdg = ROOT.TH1D('pid', 'Particle code of particles', 500, -250, 250)      #100, -50, 50)
h_momentum = ROOT.TH1D('momentum', 'Momentum of particles', 200, 0, 8)
h_pt = ROOT.TH1D('pt', 'Transverse Momentum of particles', 200, 0, 6)
h_phi = ROOT.TH1D('phi', 'Azimuth angle of particles', 200, -180, 180)
h_theta = ROOT.TH1D('theta', 'Polar angle of particles', 200, 0, 180)
h_costheta = ROOT.TH1D('costheta', 'Cosinus of the polar angle of particles', 200, -1, 1)
h_E = ROOT.TH1D('Energy', 'Energy of particles', 200, 0, 8)
h_px = ROOT.TH1D('Xmomentum', 'X axis Momentum of particles', 200, 0, 8)
h_py = ROOT.TH1D('Ymomentum', 'Y axis Momentum of particles', 200, 0, 8)
h_pz = ROOT.TH1D('Zmomentum', 'Z axis Momentum of particles', 200, 0, 8)

h_vertex = ROOT.TH2D(
    'xyvertex',
    'XY Vertex of particles',
    200,
    -10,
    10,
    200,
    -10,
    10,
)

class ShowMCParticles(Module):

    """Simple module to collect some information about MCParticles"""

    def event(self):
        """Fill the histograms with the values of the MCParticle collection"""

        mcParticles = Belle2.PyStoreArray('MCParticles')
        nMCParticles = mcParticles.getEntries()
        h_nMCParticles.Fill(nMCParticles)
        for i in range(nMCParticles):
            mc = mcParticles[i]
            if mc.hasStatus(Belle2.MCParticle.c_PrimaryParticle):
                p = mc.getMomentum()
                t = mc.get4Vector()
                
                h_momentum.Fill(p.Mag())
                h_px.Fill(p.Px())
                h_py.Fill(p.Py())
                h_pz.Fill(p.Pz())
                h_E.Fill(t.E())
                h_pt.Fill(p.Perp())
                h_phi.Fill(p.Phi() / math.pi * 180)
                h_theta.Fill(p.Theta() / math.pi * 180)
                h_costheta.Fill(math.cos(p.Theta()))
                h_pdg.Fill(mc.getPDG())
                h_vertex.Fill(mc.getProductionVertex().X(),
                              mc.getProductionVertex().Y())
                


# main path
main = create_path()

# event info setter
main.add_module("EventInfoSetter", expList=0, runList=1, evtNumList=1000)

# beam parameters
beamparameters = add_beamparameters(main, "Y4S")
# beamparameters.param("generateCMS", True)
# beamparameters.param("smearVertex", False)

# to run the framework the used modules need to be registered
kkgeninput = register_module('KKGenInput')
kkgeninput.param('tauinputFile', Belle2.FileSystem.findFile('data/generators/kkmc/tau.input.dat'))
kkgeninput.param('KKdefaultFile', Belle2.FileSystem.findFile('data/generators/kkmc/KK2f_defaults.dat'))
#kkgeninput.param('taudecaytableFile', Belle2.FileSystem.findFile('data/generators/kkmc/tau_decaytable.dat'))
kkgeninput.param('taudecaytableFile', './my_tau_decaytable_4.dat')
kkgeninput.param('kkmcoutputfilename', 'kkmc_tautau_4.txt')

# run
main.add_module("Progress")
main.add_module(kkgeninput)
main.add_module("RootOutput", outputFileName="kkmc_tautau_4.root")
# main.add_module("PrintTauTauMCParticles", logLevel=LogLevel.INFO, onlyPrimaries=False)
main.add_module("PrintMCParticles", logLevel=LogLevel.INFO, onlyPrimaries=False)

showMCPart = ShowMCParticles()

main.add_module(showMCPart)

# generate events
process(main)


# show call statistics
print(statistics)

# Create a Canvas to show histograms
#c = ROOT.TCanvas('Canvas', 'Canvas', 1536, 768)
#c.Divide(4, 3, 1e-5, 1e-5)

infile = ROOT.TFile("Generator_4.root","recreate")

# Draw all histograms
histograms = [
    h_nMCParticles,
    h_pdg,
    h_momentum,
    h_pt,
    h_theta,
    h_costheta,
    h_phi,
    h_px,
    h_py,
    h_pz,
    h_E
]
for (i, h) in enumerate(histograms):
    #c.cd(i + 1)
    h.SetMinimum(0)
    #h.Draw()
    h.Write()
#c.cd(i + 2)
#h_vertex.Draw('colz')
h_vertex.Write()
#c.Update()
#c.SaveAs("mcparticle_4_test.pdf")
infile.Write()
infile.Close()

# Wait for enter to be pressed
sys.stdin.readline()