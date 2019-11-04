#!/usr/bin/env python3
# -*- coding: utf-8 -*-

######################################################
# This steering file shows how to run the framework
# for different experiment, run and event numbers.
#
# In the example below, basf2 will run on and display
# the following experiment, run and event numbers:
#
# Experiment 71, Run  3, 4 Events
# Experiment 71, Run  4, 6 Events
# Experiment 73, Run 10, 2 Events
# Experiment 73, Run 20, 5 Events
# Experiment 73, Run 30, 3 Events
#
# Example steering file - 2011 Belle II Collaboration
# useage basf2 readDataFile.py -i srootfilename -o outputfilename
######################################################

from basf2 import *

#inputName = '/home/belle2/atpathak/ppcc2018/work/KLM_5Feb2019/190209-poisson-50kHz-1M-0001-nobeam.sroot'
#outputName = '190209.poisson.50kHz.1M.0001.00001.nobeam.root'

inputName = '19feb2019_poisson_5KHz_5M_AllbutBF2.sroot'
outputName = '19Feb2019.poisson.5kHz.5M.0001.00001.nobeam_AllbutBF2.root'



# Create main path
reset_database()
use_database_chain()
use_central_database('data_reprocessing_prod6')  # use proper global tag for data

main = create_path()
main.add_module('SeqRootInput', inputFileName=inputName)

output = main.add_module('RootOutput')
output.param('outputFileName', outputName)

#main.add_module('SeqRootInput',inputFileName='/hsm/belle2/bdata/Data/sRaw/e0002/r03744/sub00/cosmic.0002.03744.HLT4.f00001.sroot')
#main.add_module('RootOutput',outputFileName='cosmic.0002.03744.HLT4.f00001.root')
#main.add_module('SeqRootInput',inputFileName='190209-poisson-50kHz-1M-nobeam.sroot')
#main.add_module('RootOutput',outputFileName='190209-poisson-50kHz-1M-nobeam.root')





# Process all events
process(main)
