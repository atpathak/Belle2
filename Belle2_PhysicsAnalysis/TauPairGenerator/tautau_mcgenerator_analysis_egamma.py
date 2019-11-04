import glob
import basf2 as b2
import modularAnalysis as ma
from variables import variables as var
import variables.collections as vc
import variables.utils as vu
import sys


inputFile = glob.glob('/home/belle2/atpathak/PhysicsAnalysis/work/tau_analysis/kkmc_tautau_4.root')

my_path = b2.create_path()

#tauMinus = sys.argv[1]

ma.inputMdstList(environmentType='default', filelist=inputFile, path=my_path)

######################################################
# create and fill the ParticleLists
######################################################

ma.fillParticleListFromMC('tau-:gen', '', path=my_path)
ma.fillParticleListFromMC('tau+:gen', '', path=my_path)

####################################################
# track cuts
######################################################

var.addAlias('EoverP', 'formula( ifNANgiveX( clusterE, -1 )/p )')

#######################################################
# EventShape and EventKinamatics modules
#######################################################
ma.buildEventShape(['tau-:gen', 'tau+:gen'],
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
ma.buildEventKinematics(['tau-:gen', 'tau+:gen'], path=my_path)

# Get information of the generated decay mode calling labelTauPairMC from modular analysis
ma.labelTauPairMC(path=my_path)

######################################################
# Signal and tag sides
#######################################################

ma.reconstructDecay('vpho:photon_B2SS -> tau+:gen tau-:gen', '', path=my_path)
    

#####################################################
# -- event based variables
##################################################
var.addAlias('nDaug', 'countDaughters(1>0)')
#var.addAlias('InvMass', '')

eventVariables = ['thrust', 'M', 'tauPlusMCMode','tauMinusMCMode', 'nDaug']


tauVariables = ['p','px','py','pz','E','PDG','pt', 'M', 'EoverP'] 

# -- track level variables
#trackVariables = vc.kinematics #+ vc.pid + vc.track + vc.track_hits + vc.vertex
#trackVariables += ['theta','cosTheta','phi', 'charge', 'clusterE','EoverP', 'mcPDG']



variableList = vu.create_aliases_for_selected(list_of_variables=eventVariables,
                                              decay_string='^vpho') + \
               vu.create_aliases_for_selected(list_of_variables=tauVariables + ['charge'],
                                              decay_string='vpho -> ^tau+ ^tau-') #+ \
               #vu.create_aliases_for_selected(list_of_variables=trackVariables,
                                             # decay_string= decay_chain)



ma.variablesToNtuple('vpho:photon_B2SS', variables=variableList, treename ='tree', filename = 'tau_Generator_analysis_4.root', path = my_path)


b2.process(my_path, max_event = 50000)


