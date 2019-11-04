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

inputName = '/ghi/fs01/belle2/bdata/group/detector/BKLM/2019_10/0x40FF/klm.0010.01936.HLT1.f00001.sroot'
outputName = 'e0010/r01936/klm.0010.01936.HLT1.f00001.root'


# Create main path
reset_database()
use_database_chain()
use_central_database('data_reprocessing_prompt')  # use proper global tag for data

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
