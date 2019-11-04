import ROOT
from ROOT import Belle2, TH1, TH2, TCanvas, THistPainter, TPad, gROOT, gStyle, TFile  
import os
import sys
import shutil
from optparse import Option, OptionValueError, OptionParser

Important = ["FoundEff_Endcap_1_Layer_1","FoundEff_Endcap_1_Layer_2","FoundEff_Endcap_1_Layer_3","FoundEff_Endcap_1_Layer_4","FoundEff_Endcap_1_Layer_5","FoundEff_Endcap_1_Layer_6","FoundEff_Endcap_1_Layer_7","FoundEff_Endcap_1_Layer_8","FoundEff_Endcap_1_Layer_9","FoundEff_Endcap_1_Layer_10","FoundEff_Endcap_1_Layer_11","FoundEff_Endcap_1_Layer_12","FoundEff_Endcap_2_Layer_1","FoundEff_Endcap_2_Layer_2","FoundEff_Endcap_2_Layer_3","FoundEff_Endcap_2_Layer_4","FoundEff_Endcap_2_Layer_5","FoundEff_Endcap_2_Layer_6","FoundEff_Endcap_2_Layer_7","FoundEff_Endcap_2_Layer_8","FoundEff_Endcap_2_Layer_9","FoundEff_Endcap_2_Layer_10","FoundEff_Endcap_2_Layer_11","FoundEff_Endcap_2_Layer_12","FoundEff_Endcap_2_Layer_13","FoundEff_Endcap_2_Layer_14"]


#Colz = ["",]

def recurPlot(tree1,tree2):
    #pathname=os.path.join(*path)
    #if not os.path.exists(pathname):
    #shutil.rmtree(pathname)
    #os.mkdir(pathname)
    for key in tree1.GetListOfKeys():
        thisObject=tree1.Get(key.GetName())
        #thisObject.GetYaxis().SetTitleOffset(1)
        #if isinstance(thisObject,TH2):
        if key.GetName() in Important:
            thisObject.Write()

    tree2.Write()
    tree2.Close()
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

#inputName = '/ghi/fs01/belle2/bdata/group/detector/BKLM/Run_Analysis/e{0}/bklmroots/r{1}/bklmHists-e{0}r{1}_corrected.root'.format(exp, run)
inputName = 'testEffPlots_exp8_3115.root'
#inputName = 'bklmHists-e{0}r{1}_corrected.root'.format(exp, run)

gROOT.SetBatch()
gStyle.SetOptStat(10)
infile1 = TFile(inputName)
infile2 = TFile("eklm-e8r03115.root","recreate")
recurPlot(infile1,infile2)

