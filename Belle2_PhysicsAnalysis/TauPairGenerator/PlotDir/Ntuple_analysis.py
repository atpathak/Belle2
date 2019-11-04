import math
import ROOT
from ROOT import Belle2, TH1F, TH2F, TCanvas, THistPainter, TPad, TFile
from optparse import Option, OptionValueError, OptionParser


def tauMode(rootFile,hist,var):
    
    infile = TFile(rootFile)
    myTree = infile.Get("tree")
    hist = ROOT.TH1F("hist", "", 100,0,50);
    hist_tauMinus = ROOT.TH1F("hist_tauMinus", "tau Minus Decays", 100,0,50);
    for entry in myTree:
        tauPlus = entry.tauPlusMCMode
        tauMinus = entry.tauMinusMCMode
        hist_tauPlus.Fill(tauPlus)
        hist_tauMinus.Fill(tauMinus)
    
        
        
    
    






#=========================================================================
#
#   Main routine
#
#=========================================================================

parser = OptionParser()
parser.add_option('-i', '--inputfile', dest='infilename',
                  default='',
                  help='Input ROOT filename [no default]')


inputRoot = options.infilename

        

        
    

