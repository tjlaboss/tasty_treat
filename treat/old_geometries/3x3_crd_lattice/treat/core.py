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
    ['C___1', 'B___1', 'A___1'],
    ['C___2', 'B___2', 'A___2'],
    ['C___3', 'B___3', 'A___3'],
  ]

  # Positions that have standard elements we wish to autofill from the elements file. In most cases, this will look very similar to the 
  # core_lattice_template, but as a single list instead of an ordered lattice. Element locations would be left empty here if there was a 
  # lattice position that we did not want to autofill (e.g. a gap with pure air from an assebly being left out, or an experimental test position)
  core_positions = [
    'C___1', 'B___1', 'A___1',
    'C___2', 'B___2', 'A___2',
    'C___3', 'B___3', 'A___3'
  ]
  #################################################################################################################################################

  def __init__(self, elements):
    """ Creates TREAT core lattice universe """
    
    self.elements = elements
    self.has_experiment = False
    
    self._set_weight_percent_positions()
    self._set_boron_ppm_positions()
    self._set_rcca_positions()
    self._make_core_universe()
    
  def _set_weight_percent_positions(self):
    """ Sets the specification for TREAT assembly fuel weight percent positions """
    
  #################################################################################################################################################
  # Sets the fuel weight percent in each autofilled element position. At the moment, 0.211% is the only option.
    self.fuel_wgt_positions ={
    'C___1':'0.211%', 'B___1':'0.211%', 'A___1':'0.211%',
    'C___2':'0.211%', 'B___2':'0.211%', 'A___2':'0.211%',
    'C___3':'0.211%', 'B___3':'0.211%', 'A___3':'0.211%',
    }
  #################################################################################################################################################

  def _set_boron_ppm_positions(self):
    """ Sets the specification for TREAT assembly boron ppm positions """
    
  #################################################################################################################################################
  # Sets the boron impurity values in the active fuel region in each autofilled element position
    self.fuel_ppm_positions ={
    'C___1':'7.6 ppm', 'B___1':'7.6 ppm', 'A___1':'7.6 ppm',
    'C___2':'7.6 ppm', 'B___2':'7.6 ppm', 'A___2':'7.6 ppm',
    'C___3':'7.6 ppm', 'B___3':'7.6 ppm', 'A___3':'7.6 ppm',
    }
  #################################################################################################################################################

  def _set_rcca_positions(self):
    """ Sets the specifications for the control rod element positions """
    
  #################################################################################################################################################
  # Positions that have the physical possibility (i.e. whether there are drive mechanisms below the floor at that position for the 
  # TREAT reactor) to contain a control rod are listed here, along with a logical flag indicating whether that position actually
  # does contain a rodded element (1 : contains a rodded element, 0 : is a regular fuel or dummy element)
    self.rcca_positions = {
      'B___2' : 1,
    }

  # Sets the control rod bank to be associated with each position that has a control rod. The bank determines the insertion level
  # of the relevant control rod
    self.rcca_bank_locations = {
      'B___2' : 'Benchmark_Withdrawn',
    }

  # Sets the type of control rod that will be placed in the position (transient vs shutdown, Type I old design vs Type II new design)
    self.rcca_bank_types = {
      'B___2' : 'Shutdown Type II',
    }
  #################################################################################################################################################

  def _make_core_universe(self):
    # Goes through and actually autofills the positions
    """ Creates the TREAT core lattice universe """

    lattice = TemplatedLattice(c.ROOT_LATTICE, name='Core Lattice')
    lattice.setTemplate(self.core_lattice_template)
    lattice.pitch = [c.latticePitch, c.latticePitch]
    lattice.lower_left = [-3.0 * c.latticePitch / 2.0, -3.0 * c.latticePitch / 2.0]
    for pos in self.core_positions:
      # First set the fuel weight percent and the boron ppm concentration for this position
      wgt = self.fuel_wgt_positions[pos]
      boron = self.fuel_ppm_positions[pos]
      # Now figure out if this is a regular fuel element or a control rod fuel element
      if pos in self.rcca_positions:
        bank = self.rcca_bank_locations[pos]
        rod_type = self.rcca_bank_types[pos]
        # We have a position with a control rod element
        lattice.setPosition(pos, self.elements.u_rcca[bank,rod_type,wgt,boron])
      else:
        # We have a position with a regular fuel element
        lattice.setPosition(pos, self.elements.u_fuel_p[wgt,boron])
    lattice.finalize()
    
    self.u_coreLattice = lattice

