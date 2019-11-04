# write-html.py
import os
import sys
import time
import subprocess



def findrun(Location):
    lst = []
    file = open(Textfile+'.txt')
    for line in file:
        lst.append([ x for x in line.split()])
    column1 = [ x[0] for x in lst]
    Runtxt = [i[:4] for i in column1]
    Avbklm = os.listdir("/ghi/fs01/belle2/bdata/group/detector/BKLM/Run_Analysis/e0008/bklmroots/")
    Avbklmrun = [i[2:] for i in Avbklm]
    Run = [i for i in Runtxt if i in Avbklmrun]
    #Run.sort()
    return Run

def maketar(Location):
    infile1 = open("maketar_"+Textfile+".sh","w")
    run = findrun(RunLocation)
    for i in run:
        infile1.write("python3 maketar.py -e 8 -r "+i+" \n")


Textfile = sys.argv[1]
RunLocation = "."
maketar(RunLocation)

