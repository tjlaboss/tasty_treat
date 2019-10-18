"""core.py

Provides a container class for TREAT core lattice

"""

import common_files.treat.constants as c
from common_files.treat.corebuilder import TemplatedLattice

class Core(object):

  #################################################################################################################################################
  # The core lattice template list contains all of the spots in the core grid. This provides the shape of the lattice to corebuilder, and
  # should always be completely full
  core_lattice_template = [
    ['E___1', 'D___1', 'C___1', 'B___1', 'A___1'],
    ['E___2', 'D___2', 'C___2', 'B___2', 'A___2'],
    ['E___3', 'D___3', 'C___3', 'B___3', 'A___3'],
    ['E___4', 'D___4', 'C___4', 'B___4', 'A___4'],
    ['E___5', 'D___5', 'C___5', 'B___5', 'A___5'],
  ]

  # Positions that have standard elements we wish to autofill from the elements file. In most cases, this will look very similar to the 
  # core_lattice_template, but as a single list instead of an ordered lattice. Element locations would be left empty here if there was a 
  # lattice position that we did not want to autofill (e.g. a gap with pure air from an assebly being left out, or an experimental test position)
  core_positions = [
    'E___1', 'D___1', 'C___1', 'B___1', 'A___1',
    'E___2', 'D___2', 'C___2', 'B___2', 'A___2',
    'E___3', 'D___3', 'C___3', 'B___3', 'A___3',
    'E___4', 'D___4', 'C___4', 'B___4', 'A___4',
    'E___5', 'D___5', 'C___5', 'B___5', 'A___5'
  ]
  #################################################################################################################################################

  def __init__(self, elements, has_experiment=False):
    """ Creates TREAT core lattice universe """
    
    self.elements = elements
    self.has_experiment = has_experiment
    
    self._set_weight_percent_positions()
    self._set_boron_ppm_positions()
    self._set_slot_positions()
    self._make_core_universe()
    
  def _set_weight_percent_positions(self):
    """ Sets the specification for TREAT assembly fuel weight percent positions """
    
  #################################################################################################################################################
  # Sets the fuel weight percent in each autofilled element position. At the moment, 0.211% is the only option.
    self.fuel_wgt_positions ={
    'E___1':'0.211%', 'D___1':'0.211%',                   'B___1':'0.211%', 'A___1':'0.211%',
    'E___2':'0.211%', 'D___2':'0.211%',                   'B___2':'0.211%', 'A___2':'0.211%',
    'E___3':'0.211%', 'D___3':'0.211%',                   'B___3':'0.211%', 'A___3':'0.211%',
    'E___4':'0.211%', 'D___4':'0.211%', 'C___4':'0.211%', 'B___4':'0.211%', 'A___4':'0.211%',
    'E___5':'0.211%', 'D___5':'0.211%', 'C___5':'0.211%', 'B___5':'0.211%', 'A___5':'0.211%',
    }
  #################################################################################################################################################

  def _set_boron_ppm_positions(self):
    """ Sets the specification for TREAT assembly boron ppm positions """
    
  #################################################################################################################################################
  # Sets the boron impurity values in the active fuel region in each autofilled element position
    self.fuel_ppm_positions ={
    'E___1':'5.9 ppm', 'D___1':'5.9 ppm',                    'B___1':'5.9 ppm', 'A___1':'5.9 ppm',
    'E___2':'5.9 ppm', 'D___2':'5.9 ppm',                    'B___2':'5.9 ppm', 'A___2':'5.9 ppm',
    'E___3':'5.9 ppm', 'D___3':'5.9 ppm',                    'B___3':'5.9 ppm', 'A___3':'5.9 ppm',
    'E___4':'5.9 ppm', 'D___4':'5.9 ppm', 'C___4':'5.9 ppm', 'B___4':'5.9 ppm', 'A___4':'5.9 ppm',
    'E___5':'5.9 ppm', 'D___5':'5.9 ppm', 'C___5':'5.9 ppm', 'B___5':'5.9 ppm', 'A___5':'5.9 ppm',
    }
  # Sets the boron impurity values in the dummy elements in each autofilled element position
    self.refl_ppm_positions ={
                                          'C___1':'CP2',                                      
                                          'C___2':'CP2',                                      
                                          'C___3':'CP2',                                      
                                                                                                  
                                                                                                  
    }
  #################################################################################################################################################

  def _set_slot_positions(self):
    """ Sets the specifications for the slotted dummy element positions """
    
  #################################################################################################################################################
  # What the heights are for each of the slotted dummy element positions
    self.slot_height_positions ={
                                          'C___1':'48 inch',                                      
                                          'C___2':'48 inch',                                      
                                          'C___3':'48 inch',                                      
                                                                                                  
                                                                                                  
    }

  #################################################################################################################################################

  def _make_core_universe(self):
    # Goes through and actually autofills the positions
    """ Creates the TREAT core lattice universe """

    lattice = TemplatedLattice(c.ROOT_LATTICE, name='Core Lattice')
    lattice.setTemplate(self.core_lattice_template)
    lattice.pitch = [c.latticePitch, c.latticePitch]
    lattice.lower_left = [-5.0 * c.latticePitch / 2.0, -5.0 * c.latticePitch / 2.0]
    for pos in self.core_positions:
      # Do the fueled elements first
      if pos in self.fuel_wgt_positions:
        # First set the fuel weight percent and the boron ppm concentration for this position
        wgt = self.fuel_wgt_positions[pos]
        boron = self.fuel_ppm_positions[pos]
        lattice.setPosition(pos, self.elements.u_fuel_p[wgt,boron])
      # Now do the access hole dummy elements
      if pos in self.refl_ppm_positions:
        boron = self.refl_ppm_positions[pos]
        height = self.slot_height_positions[pos]
        # We have a position with a control rod element
        lattice.setPosition(pos, self.elements.u_access_dummy_p[height,boron])
    lattice.finalize()
    
    self.u_coreLattice = lattice

