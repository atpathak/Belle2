import ROOT
from ROOT import Belle2, TH1, TH2, TCanvas, THistPainter, TPad, gROOT, gStyle, TFile  
import os
import sys
import shutil
from optparse import Option, OptionValueError, OptionParser

Box = ["RawKLMnodeID","rawKLMlaneFlag","rawKLMtdcExtraRPC","rawKLMadcExtraRPC","rawKLMtdcExtraScint","rawKLMadcExtraScint","rawKLMsizeMultihit","rawKLM_S00_channelMultiplicity","rawKLM_S00_channelMultiplicityFine","rawKLM_S01_channelMultiplicity","rawKLM_S01_channelMultiplicityFine","rawKLM_S02_channelMultiplicity","rawKLM_S02_channelMultiplicityFine","rawKLM_S03_channelMultiplicity","rawKLM_S03_channelMultiplicityFine","rawKLM_S04_channelMultiplicity","rawKLM_S04_channelMultiplicityFine","rawKLM_S05_channelMultiplicity","rawKLM_S05_channelMultiplicityFine","rawKLM_S06_channelMultiplicity","rawKLM_S06_channelMultiplicityFine","rawKLM_S07_channelMultiplicity","rawKLM_S07_channelMultiplicityFine","rawKLM_S08_channelMultiplicity","rawKLM_S08_channelMultiplicityFine","rawKLM_S09_channelMultiplicity","rawKLM_S09_channelMultiplicityFine","rawKLM_S10_channelMultiplicity","rawKLM_S10_channelMultiplicityFine","rawKLM_S11_channelMultiplicity","rawKLM_S11_channelMultiplicityFine","rawKLM_S12_channelMultiplicity","rawKLM_S12_channelMultiplicityFine","rawKLM_S13_channelMultiplicity","rawKLM_S13_channelMultiplicityFine","rawKLM_S14_channelMultiplicity","rawKLM_S14_channelMultiplicityFine","rawKLM_S15_channelMultiplicity","rawKLM_S15_channelMultiplicityFine","mappedRPCCtimeRangeBySector","mappedScintCtimeRangeBySector"]

#Colz = ["",]

def recurPlot(tree):
    pathname=os.path.join(*path)
    #if not os.path.exists(pathname):
    shutil.rmtree(pathname)
    os.mkdir(pathname)
    for key in tree.GetListOfKeys():
        thisObject=tree.Get(key.GetName())
        thisObject.GetYaxis().SetTitleOffset(1)
        if isinstance(thisObject,TH2):
            if key.GetName() in Box:
                thisObject.Draw("box")
            else:
                thisObject.Draw("colz")
        elif isinstance(thisObject, TH1):
            thisObject.Draw()
        c.SaveAs(os.path.join(pathname,key.GetName()+".png"))
    
def makehtml(pngdir,indexfile):
    ListOfPng = os.listdir(pngdir)
    Namehtml = open(indexfile,'w')
    for i in ListOfPng:
        if i.endswith('.png'):
            Namehtml.write("<img src='"+i+"' width='25%'></img>")
            #Namehtml.write("<img src='"+pngdir+"/"+i+"' width='25%'></img>")
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

inputName = '/ghi/fs01/belle2/bdata/group/detector/BKLM/Run_Analysis/e{0}/bklmroots/r{1}/bklmHists-e{0}r{1}_corrected.root'.format(exp, run)
#inputName = 'bklmHists-e{0}r{1}_corrected.root'.format(exp, run)
#outputpng = './png-e{0}r{1}'.format(exp, run)
outputpng = '/ghi/fs01/belle2/bdata/group/detector/BKLM/Run_Analysis/e{0}/bklmroots/r{1}/png-e{0}r{1}'.format(exp, run)
#htmlindex = '/ghi/fs01/belle2/bdata/group/detector/BKLM/Run_Analysis/e{0}/bklmroots/r{1}/png-e{0}r{1}/index.html'.format(exp, run)


gROOT.SetBatch()
gStyle.SetOptStat(10)
infile1 = TFile(inputName)
#infile2 = TFile(inputhitName)
c=TCanvas()
path=[outputpng]
recurPlot(infile1)
###recurPlot(infile2)
##makehtml(outputpng,htmlindex)

