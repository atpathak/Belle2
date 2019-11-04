import ROOT
from ROOT import Belle2, TH1, TH2, TCanvas, THistPainter, TPad, gROOT, gStyle, TFile  
import os
import sys
import subprocess
from optparse import Option, OptionValueError, OptionParser


RunNameList = os.listdir("/ghi/fs01/belle2/bdata/group/detector/BKLM/Run_Analysis/e0008/bklmroots/")

notrunning = []

for i in RunNameList:
    RootLocation = "/ghi/fs01/belle2/bdata/group/detector/BKLM/Run_Analysis/e0008/bklmroots/"+i+"/bklmHists-e0008"+i+"_corrected.root"
    if not os.path.exists(RootLocation):
        notrunning.append(i)

print (notrunning)

notrunning = ['r00057', 'r00115', 'r00194', 'r00198', 'r00211', 'r00212', 'r00213', 'r00214', 'r00217', 'r00218', 'r00219', 'r00220', 'r00222', 'r00223', 'r00224', 'r00225', 'r00226', 'r00227', 'r00228', 'r00230', 'r00231', 'r00232', 'r00235', 'r00236', 'r00237', 'r00238', 'r00240', 'r00241', 'r00243', 'r00244', 'r00245', 'r00246', 'r00248', 'r00249', 'r00276', 'r00277', 'r00278', 'r00280', 'r00282', 'r00287', 'r00295', 'r00296', 'r00300', 'r00301', 'r00303', 'r00305', 'r00317', 'r00328', 'r00332', 'r00333', 'r00339', 'r00340', 'r00341', 'r00343', 'r00344', 'r00345', 'r00347', 'r00348', 'r00349', 'r00351', 'r00352', 'r00357', 'r00359', 'r00361', 'r00363', 'r00364', 'r00366', 'r00367', 'r00369', 'r00372', 'r00377', 'r00548', 'r00550', 'r00554', 'r00556', 'r00557', 'r00569', 'r00623', 'r00624', 'r00625', 'r00654', 'r00659', 'r00660', 'r00784', 'r00786', 'r00787', 'r00788', 'r00790', 'r00791', 'r00792', 'r00795', 'r00798', 'r00799', 'r00825', 'r00826', 'r00827', 'r00828', 'r00831', 'r00833', 'r00834', 'r00836', 'r00838', 'r00839', 'r00840', 'r00841', 'r00843', 'r00845', 'r00846', 'r00847', 'r00848', 'r01001', 'r01005', 'r01006', 'r01008', 'r01012', 'r01019', 'r01020', 'r01021', 'r01023', 'r01025', 'r01026', 'r01027', 'r01029', 'r01030', 'r01031', 'r01036', 'r01038', 'r01039', 'r01050', 'r01053', 'r01054', 'r01055', 'r01056', 'r01058', 'r01059', 'r01060', 'r01065', 'r01068', 'r01070', 'r01096', 'r01098', 'r01103', 'r01104', 'r01105', 'r01122', 'r01123', 'r01126', 'r01131', 'r01135', 'r01136', 'r01137', 'r01144', 'r01145', 'r01150', 'r01158', 'r01163', 'r01168', 'r01170', 'r01174', 'r01175', 'r01190', 'r01201', 'r01202', 'r01204', 'r01207', 'r01208', 'r01212', 'r01213', 'r01215', 'r01216', 'r01217', 'r01221', 'r01226', 'r01230', 'r01233', 'r01237', 'r01238', 'r01239', 'r01240', 'r01242', 'r01263', 'r01265', 'r01275', 'r01287', 'r01288', 'r01289', 'r01291', 'r01292', 'r01293', 'r01295', 'r01296', 'r01306', 'r01307', 'r01308', 'r01309', 'r01315', 'r01700', 'r01701']

We will think about that later

hitmap  = ['0115', '0248', '1023', '1055', '1056', '1058', '1059', '1060', '1064', '1065', '1068', '1163', '1175', '1190', '1213', '1217', '1238', '1240', '1288', '1289', '1291', '1295', '1296', '1307', '1309', '1315', '1700', '1701']

find: `./r01700': Permission denied
find: `./r02045': Permission denied
find: `./r01931': Permission denied
find: `./r00115': Permission denied
find: `./r01023': Permission denied
find: `./e0008': Permission denied
find: `./r02160': Permission denied
find: `./r00248': Permission denied
find: `./r01701': Permission denied
find: `./r02183': Permission denied
