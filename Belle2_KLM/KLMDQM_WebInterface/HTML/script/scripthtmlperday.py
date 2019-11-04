import os
import sys

run = ["%.2d" % i for i in range(9,32)]
infile1 = open("makehtmlperday_May.sh","w")
#infile2 = open("maketarperday.sh","w")
#infile3 = open("makingtarforallrun.sh","w")
for i in run:
    infile1.write("python3 makehtmlforeachday.py 2019_06_"+i+"_1M \n")
    #infile2.write("python3 Selecttar.py 2019_05_"+i+"_1M \n")
    #infile3.write("source maketar_2019_05_"+i+"_1M.sh \n")

