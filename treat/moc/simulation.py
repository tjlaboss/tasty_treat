# Simulation Manager

import os
import numpy as np
from .standard import *


class Simulation:
	"""Class to automate the management of simulations
	
	Required Parameters:
	--------------------
	case:           moc.Case
	ngroups:        int; number of energy groups to run this simulation in
	solve_type:     str; type of Solver to use. Can be flat ("fsr") or linear ("lsr")
	mesh_shape:     tuple of (nx, ny); CMFD mesh shape to use
	homogeneous:    bool; whether to do homogeneous ("universe" domain + CMM),
	                or heterogeneous ("cell" domain). No way to do "material" domain right now.
	
	Optional Parameters:
	--------------------
	nazim:          int; number of azimuthal angles to use.
					[Default: NAZIM --> 32]
	dazim:          float, cm; desired azimuthal ray spacing
	                [Default: DAZIM --> 0.1]
	
	Attributes:
	-----------
	stabilize:      float; damping factor for transport stabilization.
	                The higher the number, the more damping will be applied.
	                Guillaume recommends a value on (0, 1).
	                [Default: 0 --> no damping.]
	fsrsects:       int; number of source region azimuthal sectors to use in b4c control rods
					TODO: Consider whether to repurpose this argument for all cells.
	                [Default: 0 --> no azimuthal discretization]
	crdrings:       bool; whether to apply radial rings in b4c control rods
	                [Default: False]
	calculate_sph:  list; element key(s) to calculate SPH factors on
	save_results:   bool; whether to save all the reaction rate results after the simulation
	                [Default: True]
	save_suffix:    str; string to add to the save directory, after the solver.
	                If one is specified, it will be separated with an underscore '_'.
	                [Default: None]
	save_uncert:    bool; if saving results, whether to save the OpenMC uncertainties as well
	                [Default: False]
	plot:           bool; whether to make plots of the source regions,
	                materials, cells, and spatial fluxes
	                [Default: False]
	"""
	def __init__(self, case, ngroups, solve_type, mesh_shape, homogeneous,
	             use_sph=False, nazim=NAZIM, dazim=DAZIM):
		# Check that the selected options correspond to the MOC case
		assert ngroups in case.energy_groups, \
			"Available group structures are: {}".format(case.energy_groups.keys())
		assert mesh_shape in case.meshes, \
			"Available mesh shapes are: {}".format(tuple(case.meshes.keys()))
		self._case = case
		self.ngroups = ngroups
		self.gen = GENEOUS[homogeneous]
		self.solve_type = SOLVERS[solve_type.lower()]
		self.domain = DOMAINS[self.gen]
		self.use_cmm = bool(homogeneous)
		self.use_sph = use_sph
		self.nazim = nazim
		self.dazim = dazim
		self.cmfd_mesh = mesh_shape
		self.mesh_str = "x".join(np.array(mesh_shape, dtype=str))
		self.stabilize = 0.0
		self.fsrsects = 0
		self.crdrings = False
		self.elements = {}
		self._calculate_sph = []
		self._sph_keys = None
		self.save_results = True
		self.save_suffix = None
		self.save_uncert = False
		self.plot = False
		self._path = None
	
	@property
	def calculate_sph(self):
		return self._calculate_sph
	
	@calculate_sph.setter
	def calculate_sph(self, input_list):
		sph_keys = []
		for key_or_elem in input_list:
			if not isinstance(key_or_elem, str):
				key_or_elem = key_or_elem.key
			sph_keys.append(key_or_elem)
		self._calculate_sph = sph_keys
	
	@property
	def path(self):
		return self._path
	
	@path.setter
	def path(self, path):
		if path is None:
			self._path = None
		else:
			self._set_path(path)
	
	def _set_path(self, path=None, overwrite=False):
		if path is None:
			path = self._get_default_path(self.save_suffix)
		if os.path.exists(path):
			if not overwrite:
				# Only raise the warning if the folder isn't empty
				if tuple(os.scandir(path)):
					raise FileExistsError("Path {} already exists.".format(path))
		else:
			os.makedirs(path)
		self._path = path
	
	def _get_default_path(self, suffix=None):
		if self.domain == "material":
			prefix = "material"
		else:
			prefix = "{gen}"
		struct = prefix + "/{ngroups}groups/cmfd{mesh_str}-{solve_type}"
		if suffix:
			struct += "_" + suffix
		struct += '/'
		return struct.format(**vars(self))
	
	def _set_sph_keys(self):
		test_set = set(self._calculate_sph)
		assert test_set <= self.elements.keys(), \
			"Unknown elements: {}".format(test_set - self.elements.keys())
		self._sph_keys = self._calculate_sph
	
	def get_report(self):
		base = """
MOC simulation for:
	Energy groups:  {ngroups} groups
	Domain:         {domain}
	Geneity:        {gen}
	Mesh:           {mesh_str}
	Solver:         {solve_type}
	CMM:            {use_cmm}
	SPH:            {use_sph}
	Calculate SPH:  {sph_elements}
	Num_azim:       {nazim} angles
	delta_azim:     {dazim} cm
	path:           {PATH}
"""
		vardict = vars(self)
		if self._path:
			vardict["PATH"] = self._path
		else:
			vardict["PATH"] = "(not set)"
		if self.calculate_sph:
			vardict["sph_elements"] = self.calculate_sph
		else:
			vardict["sph_elements"] = False
		return base.format(**vardict)
	
	
	def run(self, nproc=4):
		if self.save_results and not self._path:
			self._set_path()
		if self.calculate_sph:
			self._set_sph_keys()
		print("Running", self.get_report())
		self._case.run_openmoc(
			nproc=nproc,
			export_path=self._path,
			calculate_sph=self._sph_keys,
			**vars(self))
	
	
	def write_xs(self):
		"""TODO implement"""
		pass
		
