import basf2 as b2
import modularAnalysis as ma
import variables.collections as vc
import variables.utils as vu
from variables import variables as var
import os

# create path
my_path = b2.create_path()

# load input ROOT file
ma.inputMdst(environmentType='default', filename='kkmc_tautau_3.root', path=my_path)

ma.printDataStore(path=my_path)

photons = ('gamma:gen', '')
electrons = ('e-:gen', 'charge == -1')
muons = ('mu-:gen', '')
taus = ('tau-:gen', '')
pions = ('pi-:gen', '')
nue = ('nu_e:gen','')
numu = ('nu_mu:gen','')
nutau = ('nu_tau:gen','')
#anti_nu_mu = ('anti-nu_mu:gen','')
#anti_nu_e = ('anti-nu_me:gen','')


ma.fillParticleListsFromMC([photons, electrons, muons, taus, pions, nue, numu, nutau], path=my_path)


#ma.fillParticleListFromMC(decayString='e-:gen', cut='', path=my_path)
#ma.fillParticleListFromMC(decayString='e+:gen', cut='', path=my_path)
#ma.fillParticleListFromMC(decayString='p+:gen', cut='', path=my_path)

ma.printDataStore(path=my_path)

ma.printList(list_name='gamma:gen', full=False, path=my_path)
ma.printList(list_name='e-:gen', full=False, path=my_path)
ma.printList(list_name='mu-:gen', full=False, path=my_path)
ma.printList(list_name='pi-:gen', full=False, path=my_path)
ma.printList(list_name='nu_e:gen', full=False, path=my_path)
ma.printList(list_name='nu_mu:gen', full=False, path=my_path)
#ma.printList(list_name='anti-nu_mu:gen', full=False, path=my_path)
#ma.printList(list_name='anti-nu_me:gen', full=False, path=my_path)

#ma.reconstructDecay('tau-:gen -> e-:gen anti-nu_e:gen nu_tau:gen', '', path=my_path)

var.addAlias('invMS1', 'invMassInLists(e-:gen, anti-nu_e:gen, nu_tau:gen)')
var.addAlias('invMS2', 'invMassInLists(e-:gen, nu_tau:gen)')
var.addAlias('invMS3', 'invMassInLists(anti-nu_e:gen, nu_tau:gen)')

mcVariables = ['p','px','py','pz','E','PDG','pt','invMS1', 'invMS2', 'invMS3']



#tauVariables = vc.inv_mass

variableList = vu.create_aliases_for_selected(list_of_variables=mcVariables,
                                              decay_string='^e-')#+ #\
               #vu.create_aliases_for_selected(list_of_variables=tauVariables,
                                              #decay_string='^tau- -> ^e- ^anti-nu_e ^nu_tau')
#output_file = 'mcparticles.root'
#ma.variablesToNtuple(decayString='e+:gen',
 #                    variables=mcVariables,
  #                   treename='electron',
   #                  filename=output_file,
    #                 path=my_path)
    
    
output_file = 'GeneratorLevel-MCparticles.root'

ma.variablesToNtuple(decayString='e-:gen', variables=variableList, treename='electron', filename=output_file, path=my_path)
#ma.variablesToNtuple(decayString='mu-:gen', variables=variableList, treename='tree2', filename=output_file, path=my_path)


b2.process(my_path)

# print out the summary
print(b2.statistics)