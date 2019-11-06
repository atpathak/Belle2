from ROOT import *
import os
import sys
from optparse import Option, OptionValueError, OptionParser

Box = ["RawKLMnodeID","rawKLMlaneFlag","rawKLMtExtraRPC","rawKLMqExtraRPC","rawKLMtExtraScint","rawKLMqExtraScint","rawKLMsizeMultihit","rawKLM00channelMultiplicity","rawKLM00channelMultiplicityFine","rawKLM10channelMultiplicity","rawKLM10channelMultiplicityFine","rawKLM20channelMultiplicity","rawKLM20channelMultiplicityFine","rawKLM30channelMultiplicity","rawKLM30channelMultiplicityFine","rawKLM01channelMultiplicity","rawKLM01channelMultiplicityFine","rawKLM11channelMultiplicity","rawKLM11channelMultiplicityFine","rawKLM21channelMultiplicity","rawKLM21channelMultiplicityFine","rawKLM31channelMultiplicity","rawKLM31channelMultiplicityFine","rawKLM02channelMultiplicity","rawKLM02channelMultiplicityFine","rawKLM12channelMultiplicity","rawKLM12channelMultiplicityFine","rawKLM22channelMultiplicity","rawKLM22channelMultiplicityFine","rawKLM32channelMultiplicity","rawKLM32channelMultiplicityFine","rawKLM03channelMultiplicity","rawKLM03channelMultiplicityFine","rawKLM13channelMultiplicity","rawKLM13channelMultiplicityFine","rawKLM23channelMultiplicity","rawKLM23channelMultiplicityFine","rawKLM33channelMultiplicity","rawKLM33channelMultiplicityFine"]

#Colz = ["",]

def recurPlot(tree):
    pathname=os.path.join(*path)
    if not os.path.exists(pathname):
        os.mkdir(pathname)
    for key in tree.GetListOfKeys():
        thisObject=tree.Get(key.GetName())
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
                  default='7',
                  help='Experiment number [default=7]')
parser.add_option('-r', '--run', dest='rNumber',
                  default='1505',
                  help='Run number [default=0604]')
(options, args) = parser.parse_args()
exp = '{0:04d}'.format(int(options.eNumber))
run = '{0:05d}'.format(int(options.rNumber))
runhit = '{0:04d}'.format(int(options.rNumber))

inputName = '/ghi/fs01/belle2/bdata/group/detector/BKLM/Run_Analysis/e0007/bklmroots/bklmHists-e{0}r{1}.root'.format(exp, run)
#inputhitName = 'bklmHitmap_run{0}.root'.format(runhit)
outputpng = '/ghi/fs01/belle2/bdata/group/detector/BKLM/Run_Analysis/e0007/bklmroots/png-e{0}r{1}'.format(exp, run)
#htmlindex = 'png-e{0}r{1}/index.html'.format(exp, run)


gROOT.SetBatch()
gStyle.SetOptStat(10)
infile1 = TFile(inputName)
#infile2 = TFile(inputhitName)
c=TCanvas()
path=[outputpng]
recurPlot(infile1)
#recurPlot(infile2)
#makehtml(outputpng,htmlindex)
