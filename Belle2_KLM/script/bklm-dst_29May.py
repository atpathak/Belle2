#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# Purpose:
#   Analyze a DST ROOT file or an SROOT file and write resulting histograms/scatterplots to
#   ROOT and PDF files. This script cannot analyze MDST files because they don't contain RawKLMs.
#
# Prerequisite (on kekcc):
#   Before running this script, type
#     source /cvmfs/belle.cern.ch/tools/b2setup release-02-01-00 <or higher release>
#   then verify that the corresponding proper global tag is used near the end of this script.
#   (Global tags are tabulated at https://confluence.desy.de/display/BI/Global+Tag+%28GT%29+page)
#   The external python script bklmDB.py must be in the same folder as this script.
#
# Usage:
#   basf2 bklm-dst.py -- -e # -r # -i infilename -n # -d # -m # -t tagname
#      You need the '--' before these options to tell basf2 that these are options to this script.
#   Required arguments:
#      either -i infilename or -e # -r # (can supply all three)
#      -i infilename  to specify the full pathname of the input ROOT DST file (no default)
#      -e #   to specify the experiment number (no default)
#      -r #   to specify the run number (no default)
# Optional arguments:
#      -s #   to select events with all (0) or exactly one (1) or two or more (2) entries/channel (default is 0)
#      -n #   to specify the maximum number of events to analyze (no default -> all events)
#      -d #   to specify the maximum number of event displays (default is 0)
#      -m #   to specify the minimum number of RPC BKLMHit2ds in any one sector (default is 4)
#      -t tagName   to specify the name of conditions-database global tag (no default)
#      -l #   to specify whether to use legacy time calculations (1) or not (0) (default is 0)
#
# Input:
#   ROOT DST file written by basf2 (may include multiple folios for one expt/run). For example,
#   /ghi/fs01/belle2/bdata/Data/Raw/e0003/r04794/sub00/physics.0003.r04794.HLT1.f*.root
#   /ghi/fs01/belle2/bdata/Data/Raw/e0004/r06380/sub00/cosmic.0004.r06380.HLT1.f00000.root
#   /ghi/fs01/belle2/bdata/Data/Raw/e0007/r01650/sub00/cosmic.0007.r01650.HLT1.f*.root
#
# Output:
#   ROOT histogram file named bklmHists-e#r#.root, using the experiment number and run number
#   PDF file named bklmHists-e#r#.pdf, using the experiment number and run number
#

import basf2
from basf2 import *
import EventInspector
from EventInspector import *
import simulation
import reconstruction
import rawdata
from optparse import Option, OptionValueError, OptionParser
import glob

parser = OptionParser()
parser.add_option('-e', '--experiment',
                  dest='eNumber', default='',
                  help='Experiment number [no default]')
parser.add_option('-r', '--run',
                  dest='rNumber', default='',
                  help='Run number [no default]')
parser.add_option('-t', '--hlt', dest='tHLT',
                  default='HLT1',
                  help='HLT number [default=HLT1]')
parser.add_option('-n', '--nEvents',
                  dest='nEvents', default='',
                  help='Max # of analyzed events [no default]')
parser.add_option('-s', '--singleEntry',
                  dest='singleEntry', default='0',
                  help='Select events with any (0) or exactly one (1) or more than one (2) entries/channel [0]')
parser.add_option('-d', '--displays',
                  dest='displays', default='0',
                  help='Max # of displayed events [0]')
parser.add_option('-v', '--view',
                  dest='view', default='2',
                  help='View event displays using one-dimensional (1) or two-dimensional (2) hits [2]')
parser.add_option('-m', '--minRPCHits',
                  dest='minRPCHits', default='4',
                  help='Min # of RPC hits in any one sector to display the event [4]')
parser.add_option('-l', '--legacyTimes',
                  dest='legacyTimes', default='0',
                  help='Perform legacy time calculations (1) or not (0) for BKLMHit1ds,2ds [0]')
#parser.add_option('-t', '--tagName',
 #                 dest='tagName', default='data_reprocessing_prompt',
  #                help='Conditions-database global-tag name [data_reprocessing_prompt]')
(options, args) = parser.parse_args()

singleEntry = int(options.singleEntry)
if singleEntry < 0 or singleEntry > 2:
    singleEntry = 0

maxCount = -1
if options.nEvents != '':
    maxCount = int(options.nEvents)
    if maxCount <= 0:
        print("Maximum number of events to analyze is", maxCount, " - nothing to do.")
        sys.exit()

view = int(options.view)

maxDisplays = int(options.displays)

minRPCHits = int(options.minRPCHits)

legacyTimes = int(options.legacyTimes)

tagName = 'data_reprocessing_prompt'

exp = '{0:04d}'.format(int(options.eNumber))
run = '{0:05d}'.format(int(options.rNumber))
HLT = options.tHLT

inputName = '/ghi/fs01/belle2/bdata/Data/Raw/e{0}/r{1}/sub00/*.{0}.{1}.{2}.f*.root'.format(exp, run, HLT)

suffix = '' if singleEntry == 0 else '-singleEntry' if singleEntry == 1 else '-multipleEntries'
histName = 'bklmHists-e{0}r{1}{2}.root'.format(exp, run, suffix)
pdfName = 'bklmPlots-e{0}r{1}{2}.pdf'.format(exp, run, suffix)
eventPdfName = 'bklmEvents{3}D-e{0}r{1}{2}.pdf'.format(exp, run, suffix, view)

if maxCount >= 0:
    print('bklm-dst: exp=' + exp + ' run=' + run + ' input=' + inputName + '. Analyze', maxCount, 'events using ' + tagName)
else:
    print('bklm-dst: exp=' + exp + ' run=' + run + ' input=' + inputName + '. Analyze all events using ' + tagName)

reset_database()
use_database_chain()
use_central_database('data_reprocessing_prompt')

main = create_path()
main.add_module('RootInput', inputFileName=inputName)
main.add_module('ProgressBar')

eventInspector = EventInspector(exp, run, histName, pdfName, eventPdfName, maxDisplays, minRPCHits, legacyTimes, singleEntry, view)
rawdata.add_unpackers(main, components=['BKLM'])
main.add_module('BKLMReconstructor')
main.add_module(eventInspector)

process(main, max_event=maxCount)
print(statistics)
