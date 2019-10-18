# Builder
#
# Class to standardize the building of a TREAT lattice geometry

from .treat_lattice import TreatLattice
from .elements.geometry import Manager


DEFAULT_BC = bc=["vacuum"]*4


class CoreBuilder:
	"""TREAT Core Lattice Builder
	
	Derived classes must implement the _populate_core_lattice() method.
	
	Parameters:
	-----------
	material_lib:   treat.materials.MaterialLib
	n:              int; number of elements on one side of the square core
	name:           str, optional; name to give the TreatLattice
	
	Attributes:
	-----------
	material_lib
	n
	lattice:        treat.TreatLattice; will be set up by self._populate_core_lattice()
	bc:             list of str in {"reflective", "vacuum", "periodic"}, length=4;
	                boundary conditions in the order (e, w, n, s)
	
	"""
	def __init__(self, material_lib, n, name=""):
		self.material_lib = material_lib
		self.manager = Manager()
		self.lattice = TreatLattice(n, material_lib, name)
		self.axially_finite = False
		self.bc = DEFAULT_BC
		# TODO: Remove _lattice_is_populated OR _populate_core_lattice()
		self._lattice_is_populated = False
		self._populate_core_lattice()
	
	@property
	def n(self):
		return self.lattice.n
	
	def _populate_core_lattice(self):
		"""Implement in derived classes!"""
		raise NotImplementedError("Derived classes must implement the "
		                          "_populate_core_lattice() method.")
	
	def get_core_geometry(self):
		if not self._lattice_is_populated:
			raise ValueError("You must set the core lattice universes first!")
		return self.lattice.get_openmc_geometry(self.bc, self.axially_finite)
		
		