import glob
import basf2 as b2
import modularAnalysis as ma
from variables import variables as var
import variables.collections as vc
import variables.utils as vu
import sys

inputFile = glob.glob('/home/belle2/atpathak/PhysicsAnalysis/work/skim_thrust_test/taupair/sub00/*.root')

#inputFile = glob.glob('/home/belle2/atpathak/PhysicsAnalysis/work/tau_analysis/kkmc_tautau.root')

my_path = b2.create_path()

tauPlus  = sys.argv[1]
tauMinus = sys.argv[2]

#b2.use_central_database("data_reprocessing_prompt_bucket6")

ma.inputMdstList(environmentType='default', filelist=inputFile, path=my_path)
b2.set_module_parameters(path=my_path,name='RootInput', cacheSize = 100)


######################################################
# create and fill the ParticleLists
######################################################
ma.fillParticleList('e-:all', '', path=my_path)
ma.fillParticleList('mu+:all', '', path=my_path)
ma.fillParticleList('pi-:all', '', path=my_path)

######################################################
# track cuts
######################################################

var.addAlias('EoverP', 'formula( ifNANgiveX( clusterE, -1 )/p )')

cleanTrack = 'abs(z0) < 2.0 and abs(d0) < 0.5 and nCDCHits > 0'

ma.cutAndCopyLists('e-:good', 'e-:all', cleanTrack, path=my_path)

ma.cutAndCopyLists('pi-:good', 'pi-:all', cleanTrack, path=my_path)

ma.cutAndCopyLists('mu+:mugood', 'mu+:all', cleanTrack, path=my_path)

######################################################
# event based cut - ==  2 tracks in event
######################################################

var.addAlias('nCleanedTracks', 'nCleanedTracks(' + cleanTrack + ')')
ma.applyEventCuts(cut='nCleanedTracks == 2', path=my_path)

#######################################################
# EventShape and EventKinamatics modules
#######################################################
ma.buildEventShape(['e-:good', 'mu+:mugood', 'pi-:good'],
                   foxWolfram=False,
                   cleoCones=False,
                   jets=False,
                   harmonicMoments=False,
                   allMoments=False,
                   collisionAxis=False,
                   sphericity=False,
                   thrust=True,
                   path=my_path
                   )
ma.buildEventKinematics(['e-:good', 'pi-:good', 'mu+:mugood'], path=my_path)

# Get information of the generated decay mode calling labelTauPairMC from modular analysis
ma.labelTauPairMC(path=my_path)

######################################################
# Signal and tag sides
#######################################################

ma.reconstructDecay('tau+:signal -> mu+:mugood', '', path=my_path)

if tauMinus == '1':
    ma.reconstructDecay('tau-:tag -> e-:good', 'charge == -1', path=my_path)
    decay_chain = 'vpho -> [^tau+ -> ^mu+] [^tau- -> ^e-]'
    ma.reconstructDecay('vpho:photon_B2SS -> tau+:signal tau-:tag', 'tauPlusMCMode == 2 and tauMinusMCMode == 1', path=my_path)
    
if tauMinus == '3':
    ma.reconstructDecay('tau-:tag -> pi-:good', 'charge == -1', path=my_path)
    decay_chain = 'vpho -> [^tau+ -> ^mu+] [^tau- -> ^pi-]'
    ma.reconstructDecay('vpho:photon_B2SS -> tau+:signal tau-:tag', 'tauPlusMCMode == 2 and tauMinusMCMode == 3', path=my_path)
    

######################################################
# pions and lepton on the opposide sides
######################################################

#ma.applyEventCuts('thrust > 0.8', path=my_path)
#ma.applyEventCuts('thrust < 0.99', path=my_path)

# Read carefully what these aliases mean
#var.addAlias('cosTheta1',
 #                  'formula(daughter(0, daughter(0, cosToThrustOfEvent))*daughter(1, daughter(0,cosToThrustOfEvent)))')


# Now, using the above aliases, select vpho candidates with signal and tag in opposite sides of the event.
#ma.applyCuts('vpho:photon_B2SS', 'cosTheta1 < 0', path=my_path)

######## MC Matching ######
###########################
# Perform MC matching of the tau candidates
ma.matchMCTruth('tau+:signal', path=my_path)
ma.matchMCTruth('tau+:tag', path=my_path)

#####################################################
# select the variables to be stored in the ntuple
#####################################################
# -- event based variables
eventVariables = ['thrust', 'M', 'tauPlusMCMode','tauMinusMCMode']


# -- tau candidate variables
# added vc.kinematics for taus
tauVariables = vc.inv_mass + vc.kinematics + vc.deltae_mbc
tauVariables += ['mcErrors', 'genMotherPDG', 'mcPDG', 'isSignal']


# -- track level variables
trackVariables = vc.kinematics + vc.pid + vc.track + vc.track_hits + vc.vertex
trackVariables += ['theta','cosTheta','phi', 'charge', 'clusterE','EoverP', 'mcPDG']



variableList = vu.create_aliases_for_selected(list_of_variables=eventVariables,
                                              decay_string='^vpho') + \
               vu.create_aliases_for_selected(list_of_variables=tauVariables + ['charge'],
                                              decay_string='vpho -> ^tau+ ^tau-') + \
               vu.create_aliases_for_selected(list_of_variables=trackVariables,
                                              decay_string= decay_chain)



if tauMinus == '1':
    Outputfile = "tautau_mctruthsel_21_test.root"

if tauMinus == '3':
    Outputfile = "tautau_mctruthsel_23_test.root"

ma.variablesToNtuple('vpho:photon_B2SS', variables=variableList, treename ='tree', filename = Outputfile, path = my_path)


b2.process(my_path, max_event = 50000)


