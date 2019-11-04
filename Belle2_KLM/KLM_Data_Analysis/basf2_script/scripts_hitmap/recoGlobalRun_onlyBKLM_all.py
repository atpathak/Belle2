#!/usr/bin/env python3
# -*- coding: utf-8 -*-

##############################################
#
# Simple script to reconstruct global runs 
#
##############################################

import sys
if len(sys.argv) != 5:
    print('You must enter 5 arguments!')
    print('Usage: basf2 recoGloballRun_onlyBKLM.py <inputPath> <outputPath> <date> <useSroot> <HLT>')
    sys.exit()

inputPath = sys.argv[1]
outputPath = sys.argv[2]
date = sys.argv[3]
useSroot = int(sys.argv[4])
#HLT = sys.argv[5]

if (useSroot != 0) and (useSroot != 1):
    print('<useSroot> must be 1 when sroot files are used and 0 when root files are used as input!')
    print('Different values are not accepted!')
    sys.exit()

# import the right things
import glob
import basf2 as b2
import mdst as mdst
import reconstruction as re
import modularAnalysis as ma
from ROOT import Belle2

# module to skim out the random-triggered events
class skimRandomTriggerModule(b2.Module):
    def event(self):
        rawFTSW = Belle2.PyStoreArray('RawFTSWs')
        if not rawFTSW.isValid():
            b2.B2ERROR('No RawFTSW available - event ignored')
            self.return_value(0)
            return
        # unknown meaning of this number
        unknownInt = 0
        if rawFTSW[0].GetTRGType(unknownInt) != Belle2.TRGSummary.TTYP_RAND:
            self.return_value(1)
        else:
            self.return_value(0)

# set the global log level
ma.set_log_level(ma.LogLevel.INFO)

# set the correct GT
ma.reset_database()
ma.use_database_chain()
#ma.use_central_database("staging_data_reprocessing", ma.LogLevel.WARNING)
#ma.use_central_database('data_reprocessing_prompt_bucket6', ma.LogLevel.INFO)

ma.use_central_database('data_reprocessing_prompt_snapshot_02182019', ma.LogLevel.INFO)

# create the main path and also an empty path
main_path = b2.create_path()
empty_path = b2.create_path()

# add input and the progress bar
if useSroot:
    inputFileName = glob.glob(inputPath + '*.*.*.*.*.sroot')
    main_path.add_module('SeqRootInput', inputFileNames=inputFileName)
else:
    inputFileName = glob.glob(inputPath + '*.*.*.*.*.root')
    main_path.add_module('RootInput', inputFileNames=inputFileName)
main_path.add_module('Progress')
main_path.add_module('ProgressBar')

# set geometry w/o the magnetic field
main_path.add_module('Gearbox')
main_path.add_module('Geometry', 
                     useDB=True)

# skim out the random-triggered events
#skimRandomTrigger = skimRandomTriggerModule()
#main_path.add_module(skimRandomTrigger)
#skimRandomTrigger.if_false(empty_path)

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
                     outputName=outputPath+'bklmEfficiency_day' + date + '.root')

# process the path
b2.print_path(main_path)
b2.process(main_path)
print(b2.statistics)
