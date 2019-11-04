#!/usr/bin/env python3
# -*- coding: utf-8 -*-

##############################################
#
# Simple script to reconstruct local runs 
#
##############################################

import sys

if len(sys.argv) != 4:
    print('You must enter 3 arguments!')
    print('Usage: basf2 recoLocalRun_onlyBKLM.py <inputPath> <outputPath> <date>')
    sys.exit()

inputPath = sys.argv[1]
outputPath = sys.argv[2]
date = sys.argv[3]

# import the right things
import glob
import basf2 as b2
import mdst as mdst
import reconstruction as re
import modularAnalysis as ma
from ROOT import Belle2

# set the log level
ma.set_log_level(ma.LogLevel.INFO)

# set the correct GT, not needed for local runs taken with PocketDAQ
ma.reset_database()
ma.use_database_chain()
ma.use_central_database('data_reprocessing_prompt_snapshot_01252019', ma.LogLevel.INFO)

# create the main path and also an empty path
main_path = b2.create_path()

# add input and the progress bar
inputFileName = glob.glob(inputPath + '*.sroot*')
main_path.add_module('SeqRootInput', inputFileNames=inputFileName)
main_path.add_module('Progress')
main_path.add_module('ProgressBar')

# set the geometry
main_path.add_module('Gearbox')
main_path.add_module('Geometry', 
                     useDB=True)

# unpack bklm raw dawa
main_path.add_module('BKLMUnpacker')

# analyze bklm digits
main_path.add_module('BKLMDigitAnalyzer',
                     outputRootName=outputPath+'bklmHitmap')

# reconstruct bklm 2d hits
reco = ma.register_module('BKLMReconstructor')
reco.param('Prompt window (ns)', 2000)
main_path.add_module(reco)

# add bklm stand-alone tracking
main_path.add_module('BKLMTracking',
                     StudyEffiMode=True,
                     outputName=outputPath+'bklmEfficiency_' + date + '.root')

# process the path
b2.print_path(main_path)
b2.process(main_path, 100000)
print(b2.statistics)
