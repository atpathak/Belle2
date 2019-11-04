#!/usr/bin/env python3
# -*- coding: utf-8 -*-

########################################################
# Run KKMC to generate tautau events
#
# Example steering file
########################################################

from basf2 import *
import ROOT
from ROOT import Belle2
from beamparameters import add_beamparameters
import sys
import math

set_log_level(LogLevel.INFO)

ndau  = sys.argv[2]

h_E  = ROOT.TH1D('Energy',    'Energy of tau-',    110, 0, 5.5)
h_px = ROOT.TH1D('MomentumX', 'MomentumX of tau-', 110, 0, 5.5)
h_py = ROOT.TH1D('MomentumY', 'MomentumY of tau-', 110, 0, 5.5)
h_pz = ROOT.TH1D('MomentumZ', 'MomentumZ of tau-', 110, 0, 5.5)

h_E_i = []
for i in range(int(ndau)):
    label = 'Hist_E_{0:01d}'.format(i+1)
    title = 'Energy of daughter {0:01d}'.format(i+1)
    h_E_i.append(ROOT.TH1D(label,title,110,0,5.5))

h_m_ij = []
for idau in range(int(ndau)):
    for jdau in range(idau):
        label = 'Hist_InvMass_{0:01d}{1:01d}'.format(jdau+1,idau+1)
        title = 'InvMass for daughter pair {0:01d}{1:01d} '.format(jdau+1,idau+1)
        h_m_ij.append(ROOT.TH1D(label,title,100,0,2))


class ShowMCParticles(Module):

    """Simple module to collect some information about MCParticles"""

    def event(self):
        """Fill the histograms with the values of the MCParticle collection"""

        T=Belle2.PCmsLabTransform()
        mcParticles = Belle2.PyStoreArray('MCParticles')
        nMCParticles = mcParticles.getEntries()
        for i in range(nMCParticles):
            mc = mcParticles[i]
            if (mc.getPDG() == 15):
                plab = mc.get4Vector()
                pcms = T.rotateLabToCms() * plab
                h_E.Fill(pcms.E())
                h_px.Fill(pcms.Px())
                h_py.Fill(pcms.Py())
                h_pz.Fill(pcms.Pz())
#                print (mc.getNDaughters())
                vec_p4 = []
                for idau in range(int(ndau)):
                    dau = mc.getDaughters()[idau]
                    p4lab  = dau.get4Vector()
                    p4cms  = T.rotateLabToCms() * p4lab
                    vec_p4.append(p4cms)
                    h_E_i[idau].Fill(p4cms.E())
#                    print (idau, dau.getPDG(), p4cms.E(), p4cms.M())
                ij=0
                for idau in range(int(ndau)):
                    for jdau in range(idau):
                        mij=(vec_p4[idau]+vec_p4[jdau]).M()
                        h_m_ij[ij].Fill(mij)
#                        print(idau, jdau, ij, mij)
                        ij = ij+1
              

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
kkgeninput.param('taudecaytableFile', 'my_tau_decaytable_tauenubar.dat')
kkgeninput.param('kkmcoutputfilename', 'kkmc_tautau.txt')

# run
main.add_module("Progress")
main.add_module(kkgeninput)
main.add_module("RootOutput", outputFileName="kkmc_tautau_tauenubar.root")
#main.add_module("PrintTauTauMCParticles", logLevel=LogLevel.INFO, onlyPrimaries=False)
main.add_module("PrintMCParticles", logLevel=LogLevel.INFO, onlyPrimaries=False)

#
showMCPart = ShowMCParticles()
main.add_module(showMCPart)

# generate events
process(main)

# show call statistics
print(statistics)

infile = ROOT.TFile("kkmc_tautau_tauenubar.root","update")

# Create a Canvas to show histograms
c = ROOT.TCanvas('Canvas', 'Canvas')
c.Divide(2, 2, 1e-5, 1e-5)

# Draw all histograms
histograms = [
    h_px,
    h_py,
    h_pz,
    h_E
]
for (i, h) in enumerate(histograms):
    c.cd(i + 1)
    h.SetMinimum(0)
    h.Draw()
    h.Write()
    
for i in range(int(ndau)):
    h_E_i[i].Write()

def nCr(n,r):
    f = math.factorial
    return f(n) / f(r) / f(n-r)

nInvM = nCr(int(ndau),2)

for ij in range(int(nInvM)):
    h_m_ij[ij].Write()

c.Update()
c.SaveAs("kkmc_tautau_tauenubar.pdf")

infile.Write()
infile.Close()
