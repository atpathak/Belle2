import ROOT
from ROOT import Belle2, TH1, TH2, TCanvas, THistPainter, TPad, gROOT, gStyle, TFile, TDirectory
import os
import sys
import shutil
from optparse import Option, OptionValueError, OptionParser


directory = ['RawKLM', 'SectorOccupancy', 'LayerOccupancy', 'RPCTime', 'ScintTime', 'TimeDistribution', 'ZHit','PhiHit','BKLMXYOccupancy', 'EKLMXYOccupancy']

Raws = ['NDigit','NRawKLM','RawKLMnodeID','NDigitEKLM','NHit1d','NHit2d','NHit2dEKLM']

Sector = ['mappedRPCSectorOccupancy','unmappedRPCSectorOccupancy','mappedScintSectorOccupancy','unmappedScintSectorOccupancy','EKLMBackwardSectorOccupancy','EKLMForwardSectorOccupancy']

Layer = ['EKLMLayeroccupancyBackward','EKLMLayeroccupancyForward']

RPC = ['mappedRPCTime', 'mappedRPCTimeCal', 'mappedRPCTimeBySector']

Scint = [ 'mappedScintCtime', 'mappedScintCtime0', 'mappedScintCtimeBySector']

Time = ['EKLMtime'] #,'EKLMtdc']

Zdisall = ['PlaneZStripBB0', 'PlaneZStripBB1', 'PlaneZStripBB2', 'PlaneZStripBB3', 'PlaneZStripBB4', 'PlaneZStripBB5', 'PlaneZStripBB6', 'PlaneZStripBB7', 'PlaneZStripBF0', 'PlaneZStripBF1', 'PlaneZStripBF2', 'PlaneZStripBF3', 'PlaneZStripBF4', 'PlaneZStripBF5', 'PlaneZStripBF6', 'PlaneZStripBF7']

Zdisincl = ['PlaneZStripBB0', 'PlaneZStripBB1', 'PlaneZStripBB2', 'PlaneZStripBB5', 'PlaneZStripBB6', 'PlaneZStripBF0', 'PlaneZStripBF1', 'PlaneZStripBF2', 'PlaneZStripBF5', 'PlaneZStripBF6']

Phidisall = ['PlanePhiStripBB0', 'PlanePhiStripBB1', 'PlanePhiStripBB2', 'PlanePhiStripBB3', 'PlanePhiStripBB4', 'PlanePhiStripBB5', 'PlanePhiStripBB6', 'PlanePhiStripBB7', 'PlanePhiStripBF0', 'PlanePhiStripBF1', 'PlanePhiStripBF2', 'PlanePhiStripBF3', 'PlanePhiStripBF4', 'PlanePhiStripBF5', 'PlanePhiStripBF6', 'PlanePhiStripBF7']

Phidisincl = ['PlanePhiStripBB0', 'PlanePhiStripBB1', 'PlanePhiStripBB2', 'PlanePhiStripBB5', 'PlanePhiStripBB6', 'PlanePhiStripBF0', 'PlanePhiStripBF1', 'PlanePhiStripBF2', 'PlanePhiStripBF5', 'PlanePhiStripBF6']

XYOcc = ['occupancyBackwardXYPromptBkgd','occupancyForwardXYPromptBkgd']

#['EKLMoccupancyForwardXY','EKLMoccupancyBackwardXY']

EklmXYOcc = ['occupancyBackwardXY_L01', 'occupancyBackwardXY_L02', 'occupancyBackwardXY_L03', 'occupancyBackwardXY_L04', 'occupancyBackwardXY_L05', 'occupancyBackwardXY_L06', 'occupancyBackwardXY_L07', 'occupancyBackwardXY_L08', 'occupancyBackwardXY_L09', 'occupancyBackwardXY_L10', 'occupancyBackwardXY_L11', 'occupancyBackwardXY_L12', 'occupancyForwardXY_L01', 'occupancyForwardXY_L02', 'occupancyForwardXY_L03', 'occupancyForwardXY_L04', 'occupancyForwardXY_L05', 'occupancyForwardXY_L06', 'occupancyForwardXY_L07', 'occupancyForwardXY_L08', 'occupancyForwardXY_L09', 'occupancyForwardXY_L10', 'occupancyForwardXY_L11', 'occupancyForwardXY_L12', 'occupancyForwardXY_L13', 'occupancyForwardXY_L14','EKLMoccupancyForwardXY','EKLMoccupancyBackwardXY']

#my_file = TFile.Open("klmHists-e0008r03123.root",'recreate')
#my_file1 = TFile.Open("bklmHists-e0008r03123_corrected.root")
#my_file2 = TFile.Open("eklmHists-e0008r03123.root")
#my_file3 = TFile.Open("bklmHitmap_run3123.root")

def combDict(my_file,my_file1,my_file2,my_file3):
    for i in directory:
        TDirectory.dircd = my_file.mkdir(i)

    my_file.cd("RawKLM")
    for i in Raws:
        if i in my_file1.GetListOfKeys():
            if (str(i) is not 'RawKLMnodeID'):
                thisObject = my_file1.Get(i)
            if (str(i)=='RawKLMnodeID'):
                thisObject = my_file2.Get(i)
                #print('Atanu')
                #stats1 = thisObject.GetListOfFunctions().FindObject("stats")
                #stats1.SetX1NDC(.4)
                #stats1.SetX2NDC(.6)
                #stats1.SetY1NDC(.7)
                #stats1.SetY2NDC(.9)
                #thisObject.GetXaxis().SetRange(0,500)
                #thisObject.GetYaxis().SetRangeUser(0.,30.)
        else:
            thisObject = my_file2.Get(i)
        thisObject.GetYaxis().SetTitleOffset(1)
        thisObject.Write()

    my_file.cd("SectorOccupancy")
    for i in Sector:
        if i in my_file1.GetListOfKeys():
            thisObject = my_file1.Get(i)
            thisObject.SetTitle(str(i))
        else:
            thisObject = my_file2.Get(i)
            thisObject.SetTitle(str(i))
            thisObject.SetMinimum(0)
            thisObject.SetMaximum(2*thisObject.GetMaximum())
        thisObject.GetYaxis().SetTitleOffset(1)
        thisObject.Write()

    my_file.cd("LayerOccupancy")
    for i in Layer:
        if i in my_file1.GetListOfKeys():
            thisObject = my_file1.Get(i)
        else:
            thisObject = my_file2.Get(i)
            if (str(i)=='EKLMLayeroccupancyBackward'):
                thisObject.SetTitle("Backward LayerOccupancy")
            else:
                thisObject.SetTitle("Forward LayerOccupancy")
        thisObject.GetYaxis().SetTitleOffset(1)
        thisObject.Write()

    my_file.cd("RPCTime")
    for i in RPC:
        if i in my_file1.GetListOfKeys():
            thisObject = my_file1.Get(i)
            thisObject.SetTitle(str(i))
        else:
            thisObject = my_file2.Get(i)
        thisObject.GetYaxis().SetTitleOffset(1.4)
        thisObject.Write()

    my_file.cd("ScintTime")
    for i in Scint:
        if i in my_file1.GetListOfKeys():
            thisObject = my_file1.Get(i)
            thisObject.SetTitle(str(i))
        else:
            thisObject = my_file2.Get(i)
        thisObject.GetYaxis().SetTitleOffset(1.4)
        thisObject.Write()

    my_file.cd("TimeDistribution")
    for i in Time:
        if i in my_file1.GetListOfKeys():
            thisObject = my_file1.Get(i)
        else:
            thisObject = my_file2.Get(i)
        thisObject.GetYaxis().SetTitleOffset(1)
        thisObject.Write()

    my_file.cd("BKLMXYOccupancy")
    for i in XYOcc:
        thisObject = my_file1.Get(i)
        thisObject.GetYaxis().SetTitleOffset(1.4)
        if (str(i) == 'occupancyBackwardXYPromptBkgd'):
            thisObject.SetTitle("Backward")
        else:
            thisObject.SetTitle("Forward")
        thisObject.Write()
    
    my_file.cd("EKLMXYOccupancy")
    for i in EklmXYOcc:
        thisObject = my_file2.Get(i)
        if ( str(i)[9:12] == 'For'):
            thisObject.SetTitle("Forward "+str(i[-3:]))
        else:
            thisObject.SetTitle("Backward "+str(i[-3:]))
        thisObject.GetYaxis().SetTitleOffset(1.4)
        thisObject.Write()

    my_file.cd("ZHit")
    for i in Zdisall:
        if (i in Zdisincl):
            thisObject = my_file3.Get(i)
        else:
            thisObject = ROOT.TH2F(i, str(i[-3:]) +';Layer (0-based);strip', 31, -0.5, 15., 130, -0.5, 64.5,)
        thisObject.SetTitle(str(i[-3:]))
        thisObject.GetYaxis().SetTitleOffset(1)
        thisObject.Write() 

    my_file.cd("PhiHit")
    for i in Phidisall:
        if (i in Phidisincl):
            thisObject = my_file3.Get(i)
        else:
            thisObject = ROOT.TH2F(i, str(i[-3:]) +';Layer (0-based);strip', 31, -0.5, 15., 130, -0.5, 64.5,)
        thisObject.SetTitle(str(i[-3:]))
        thisObject.GetYaxis().SetTitleOffset(1)
        thisObject.Write() 
    
    my_file.Write()

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
runhit1 = '{0:04d}'.format(int(options.rNumber))
runhit2 = '{0:03d}'.format(int(options.rNumber))
runhit3 = '{0:02d}'.format(int(options.rNumber))

expRun = 'e{0:02d}r{1}: '.format(int(options.eNumber), int(options.rNumber))
print(expRun)

'''
outputName = '/ghi/fs01/belle2/bdata/group/detector/BKLM/Run_Analysis/e{0}/bklmroots/r{1}/klmHists-e{0}r{1}.root'.format(exp, run)
inputName1 = '/ghi/fs01/belle2/bdata/group/detector/BKLM/Run_Analysis/e{0}/bklmroots/r{1}/bklmHists-e{0}r{1}_corrected.root'.format(exp, run)
inputName2 = '/ghi/fs01/belle2/bdata/group/detector/BKLM/Run_Analysis/e{0}/bklmroots/r{1}/eklmHists-e{0}r{1}.root'.format(exp, run)
input1 = '/ghi/fs01/belle2/bdata/group/detector/BKLM/Run_Analysis/e{0}/bklmroots/r{1}/bklmHitmap_run{2}.root'.format(exp, run, runhit1)
input2 = '/ghi/fs01/belle2/bdata/group/detector/BKLM/Run_Analysis/e{0}/bklmroots/r{1}/bklmHitmap_run{2}.root'.format(exp, run, runhit2)
input3 = '/ghi/fs01/belle2/bdata/group/detector/BKLM/Run_Analysis/e{0}/bklmroots/r{1}/bklmHitmap_run{2}.root'.format(exp, run, runhit3)
'''
outputName = './klmHistsE-e{0}r{1}.root'.format(exp, run)
inputName1 = './bklmHists-e{0}r{1}_corrected.root'.format(exp, run)
inputName2 = './eklmHists-e{0}r{1}.root'.format(exp, run)
input1 = './bklmHitmap_run{2}.root'.format(exp, run, runhit1)
input2 = './bklmHitmap_run{2}.root'.format(exp, run, runhit2)
input3 = './bklmHitmap_run{2}.root'.format(exp, run, runhit3)


if os.path.exists(input1):
    inputName3 = input1

if os.path.exists(input2):
    inputName3 = input2
    
if os.path.exists(input3):
    inputName3 = input3

print(inputName3)

outfile = TFile.Open(outputName,'recreate')
infile1 = TFile.Open(inputName1)
infile2 = TFile.Open(inputName2)
infile3 = TFile.Open(inputName3)

combDict(outfile,infile1,infile2,infile3)
