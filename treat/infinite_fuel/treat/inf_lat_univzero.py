"""univzero.py

Provides a container class for the TREAT main universe cells

"""

import common_files.treat.constants as c

import openmc

class UniverseZero(openmc.Universe):

  def __init__(self, core, mats):
    """ Creates TREAT infinite lattice of basic fuel assemblies """
    
    super(UniverseZero, self).__init__(name='Main TREAT lattice universe', universe_id=0)
    
    self.core = core # Here, the "core" is just a single element that will be surrounded by reflective surfaces
                     # Leaving the term core because that will become more appropriate when going to larger lattices
    self.mats = mats
    self.zmid = round((c.struct_UpperAir_top - c.struct_CoreFloor_top)/2 + c.struct_CoreFloor_top)


    self._add_outer_universe()
    self._add_core()
    self._create_main_universe()


  def _add_outer_universe(self):
    """ Adds TREAT air between element and reflective surfaces """

    self.s_upperBound = openmc.ZPlane(name='Highest Extent', z0=self.zmid+1, boundary_type='reflective')
    self.s_lowerBound = openmc.ZPlane(name='Lowest Extent', z0=self.zmid-1, boundary_type='reflective')
    hpitch = c.latticePitch/2.0
    self.s_radialBound_N = openmc.YPlane(name='N Radial Universe Bound', y0= hpitch, boundary_type='reflective')
    self.s_radialBound_S = openmc.YPlane(name='S Radial Universe Bound', y0=-hpitch, boundary_type='reflective')
    self.s_radialBound_E = openmc.XPlane(name='E Radial Universe Bound', x0= hpitch, boundary_type='reflective')
    self.s_radialBound_W = openmc.XPlane(name='W Radial Universe Bound', x0=-hpitch, boundary_type='reflective')
    

  def _add_core(self):
    """ Adds TREAT single fuel element """
    # Core lattice
    self.c_core = openmc.Cell(name="Single fuel element", fill=self.core.u_fuel_p['0.211%', '5.9 ppm'])
    self.c_core.region = +self.s_radialBound_W & -self.s_radialBound_E & \
                         +self.s_radialBound_S & -self.s_radialBound_N & \
                         +self.s_lowerBound    & -self.s_upperBound


  def _create_main_universe(self):
    """ Creates the main TREAT infinite lattice universe """
    self.add_cell(self.c_core)

