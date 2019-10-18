# MOC Case
#
# Container to facilitate the conversion of models from OpenMC to OpenMOC

import openmc
from openmc import mgxs
from openmc import openmoc_compatible
import openmoc
import openmoc.plotter as moc_plt
import openmoc.checkvalue as cv
import numpy as np
import os
from warnings import warn
from . import energy_groups
from . import constants
from . import Core
from .plotting import project_array


class BaseCase(object):
	"""Container for the parameters for the OpenMC and OpenMOC models
	
	Parameters:
	-----------
	geometry:       openmc.Geometry; the model's geometry, populated with materials
	
	nums_groups:    iterable of ints; numbers of energy groups to use
	
	domains:        iterable of str in {"cell", "material", "universe"};
					which domains to tally MGXS on
	
	mesh_shape:     list of arrays of ints; shapes of meshes for two purposes:
					  1) Tallying reaction rates in OpenMC
					  2) Running CMFD in OpenMOC (required for OpenMOC to tally on the mesh)
	
	isotropic:      bool; whether to use isotropic_in_lab mode
					[Default: False]
	
	Attributes:
	-----------
	domains
	geometry
	isotropic
	lattice:        openmc.RectLattice; the core lattice
	materials:      dict.values() of the openmc.Geometry's constituent materials
	materials_xml:  openmc.Materials
	energy_groups:  dict of {int: openmc.EnergyGroups}
					used to tally cross sections over
	"""
	def __init__(self, geometry, nums_groups, domains, mesh_shapes=None, isotropic=False):
		cv.check_type("geometry", geometry, openmc.Geometry)
		cv.check_iterable_type("nums_groups", nums_groups, int)
		self._domains = domains
		self.geometry = geometry
		self.isotropic = isotropic
		self.lattice = None
		lats = self.geometry.get_all_lattices()
		if lats:
			if constants.ROOT_LATTICE in lats:
				self.lattice = lats[constants.ROOT_LATTICE]
		self.materials = self.geometry.get_all_materials().values()
		self.materials_xml = openmc.Materials(self.materials)
		if isotropic:
			self.materials_xml.make_isotropic_in_lab()
		
		self.energy_groups = {}
		self.energy_filters = {}
		self._material_libraries = {}
		self._cell_libraries = {}
		self._mesh_libraries = {}
		self._universe_libraries = {}
		self._lib_dict = \
			{"mesh"    : self._mesh_libraries,
			 "cell"    : self._cell_libraries,
			 "material": self._material_libraries,
			 "universe": self._universe_libraries}
		
		for g in nums_groups:
			assert g in energy_groups.ALL_GROUP_NUMBERS
			if g == 11:
				eg = energy_groups.treat["11-group"]
			else:
				key = "{}-group".format(g)
				eg = energy_groups.casmo[key]
			eg.group_edges *= 1E6
			self.energy_groups[g] = eg
			self.energy_filters[g] = openmc.EnergyFilter(eg.group_edges)
			
			if "material" in domains:
				lib = mgxs.Library(self.geometry)
				lib.energy_groups = eg
				self._material_libraries[g] = lib
			if "universe" in domains:
				lib = mgxs.Library(self.geometry)
				lib.energy_groups = eg
				self._universe_libraries[g] = lib
			if "cell" in domains:
				lib = mgxs.Library(self.geometry)
				lib.energy_groups = eg
				self._cell_libraries[g] = lib
			if "mesh" in domains:
				lib = mgxs.Library(self.geometry)
				lib.energy_groups = eg
				self._mesh_libraries[g] = lib
	
		self._moc_meshes = {}
		self._meshes = {}
		self._mesh_filters = {}
		self._mesh_names = {}
		if mesh_shapes is None:
			if self.lattice:
				latshape = self.lattice.shape
				mesh_shapes = [latshape]
				warnstr = "No mesh shapes provided; defaulting to: {}"
				warn(warnstr.format(latshape))
			else:
				raise AttributeError("No mesh shapes provided and "
				                     "no lattice shape to default to.")
				
		for shape in mesh_shapes:
			(self._meshes[shape], self._mesh_filters[shape]) = \
				self._get_mesh_and_filter(shape, False)
			self._mesh_names[shape] = self.shape_to_string(shape)
		self._mesh_shapes = mesh_shapes
		
		self._tallies = openmc.Tallies()
		self._reaction_tallies = {}
		self._sph_ids = None
		self._sp = None
		self._moc_geom = None
		self._solver = None
		self._prepped = False
		self._run = False
	
	
	def _get_mesh_and_filter(self, mesh_shape, symmetry):
		mesh = openmc.Mesh()
		if self.lattice:
			if not symmetry:
				dx = 0
				dy = 0
			elif symmetry == 2:
				dx = self.lattice.pitch[0]/ 2.0
				dy = 0
			elif symmetry == 4:
				dx, dy = self.lattice.pitch/2.0
			else:
				raise NotImplementedError("Symmetry: {}".format(symmetry))
			mesh.lower_left  = self.lattice.lower_left + np.array([dx, dy])
			width = self.lattice.pitch*self.lattice.shape
			mesh.upper_right = self.lattice.lower_left + width
		else:
			warn("No lattice present; using entire geometry with no symmetry.")
			lleft, uright = self.geometry.bounding_box
			mesh.lower_left = lleft[0:2]
			mesh.upper_right = uright[0:2]
		mesh.dimension = np.array(mesh_shape)
		mesh_filter = openmc.MeshFilter(mesh)
		return mesh, mesh_filter
	
	
	@property
	def sp(self):
		return self._sp
	
	@property
	def domains(self):
		return self._domains
	
	@property
	def material_libraries(self):
		return self._material_libraries
	
	@property
	def cell_libraries(self):
		return self._cell_libraries
	
	@property
	def universe_libraries(self):
		return self._universe_libraries
	
	@property
	def mesh_libraries(self):
		return self._mesh_libraries
	
	@property
	def meshes(self):
		return self._meshes
	
	def _assert_statepoint(self):
		assert self._sp is not None, \
			"You need to load a StatePoint first!"
	
	@staticmethod
	def shape_to_string(shape):
		"""Given an array shape, return it as a nice string
		
		e.g., np.array([5, 5, 2]) would become "5x5x2"
		
		this should probably be an external static method
		"""
		string = ""
		for d, n in enumerate(shape):
			if d:
				string += "x"
			string += str(n)
		return string
	
	def add_montecarlo_tally(self, tally):
		"""Add a custom tally to the mix.
		
		Parameter:
		----------
		tally:      openmc.Tally
		"""
		assert isinstance(tally, openmc.Tally)
		self._tallies.append(tally)
	
	def add_mgxs_library(self, library):
		"""Add a custom MGXS library to the mix.
		
		Parameters:
		-----------
		tally:      openmc.mgxs.Library
		"""
		assert isinstance(library, mgxs.Library)
		ngroups = library.energy_groups.num_groups
		self._lib_dict[library.domain_type][ngroups] = library
		try:
			library.add_to_tallies_file(self._tallies)
		except KeyError:
			library.build_library()
			library.add_to_tallies_file(self._tallies)
	
	def make_montecarlo_tallies(self, reactions=None, mesh_name=None,
            fuel_nuclides=False, graph_nuclides=False, zirc_nuclides=False):
		"""Add the default tallies and select optional tallies
		
		All tallies in the parameters are disabled by default.
		
		Parameters:
		-----------
		reactions:          iterable of str, optional;
							which reaction types to tally on each mesh scale
							and energy grup structure. Will always tally flux.
		mesh_name:          str, optional;
							if tallying MGXS on a 'mesh' domain, name of
							the mesh to use (see: `Case.shape_to_str()`)
		fuel_nuclides:      Boolean, optional;
							whether to tally absorption per fuel nuclide
		graph_nuclides:     Boolean, optional;
							whether to tally absorption per graphite nuclide
		zirc_nuclides:      Boolean, optional;
							whether to tally absorption per zircaloy nuclide
		"""
		if "mesh" in self.domains:
			if len(self.meshes) == 1:
				mesh_domain = list(self.meshes.values())
			else:
				assert mesh_name is not None, \
					"Multiple meshes are available. You must specify one."
				assert mesh_name in self.meshes, \
					"Could not find mesh: {}".format(mesh_name)
				mesh_domain = [self.meshes[mesh_name]]
		else:
			mesh_domain = None
		if "universe" in self.domains:
			if self.lattice is not None:
				universe_domain = list(self.lattice.get_all_universes().values())
			else:
				universe_domain = []
				for uid, universe in self.geometry.get_all_universes():
					if universe != self.geometry.root_universe:
						universe_domain.append(universe)
		else:
			universe_domain = None
		
		# gross hack for the next 3; fix...
		fuel = None
		graph = None
		zirc = None
		for m in self.materials:
			if m.name[0:4].lower() == "fuel":
				fuel = m
			elif m.name[0:8].lower() == "graphite":
				graph = m
			elif m.name[0:4].lower() == "Zr3" or m.name[0:3] == 'zr3' or \
					("zirc" in m.name.lower() and "3" in m.name.lower):
				zirc = m
		
		if fuel_nuclides:
			assert fuel is not None, "Could not find fuel!"
			fuel_tally = openmc.Tally(name='fuel tally')
			fuel_tally.scores = ["absorption"]
			fuel_filter = openmc.MaterialFilter([fuel])  # heh, fuel filter
			fuel_tally.filters = [fuel_filter]
			fuel_tally.nuclides = list(np.array(fuel.nuclides)[:, 0])
			self._tallies.append(fuel_tally)
		if graph_nuclides:
			assert graph is not None, "Could not find graphite!"
			graph_tally = openmc.Tally(name='graphite tally')
			graph_tally.scores = ["absorption"]
			graph_filter = openmc.MaterialFilter([graph])
			graph_tally.filters = [graph_filter]
			graph_tally.nuclides = list(np.array(graph.nuclides)[:, 0])
			self._tallies.append(graph_tally)
		if zirc_nuclides:
			assert zirc is not None, "Could not find zircaloy-3!"
			zirc_tally = openmc.Tally(name='zircaloy tally')
			zirc_tally.scores = ["absorption"]
			zirc_filter = openmc.MaterialFilter([zirc])
			zirc_tally.filters = [zirc_filter]
			zirc_tally.nuclides = list(np.array(zirc.nuclides)[:, 0])
			self._tallies.append(zirc_tally)
		
		# Power distribution (fission) tallies
		for mesh_shape, mesh_filter in self._mesh_filters.items():
			name = "{} mesh tally".format(self._mesh_names[mesh_shape])
			power_tally = openmc.Tally(name=name)
			power_tally.filters = [mesh_filter]
			power_tally.scores = ["fission"]
			self._tallies.append(power_tally)
			
		# Multigroup tallies
		if reactions is None:
			reactions = ['flux']
		elif 'flux' not in reactions:
			reactions.append('flux')
		for ngroups, energy_filter in self.energy_filters.items():
			# Reaction rate (and flux) tallies
			self._reaction_tallies[ngroups] = {}
			for rxn_type in reactions:
				self._reaction_tallies[ngroups][rxn_type] = {}
				for mesh_shape, mesh_filter in self._mesh_filters.items():
					shape_name = self._mesh_names[mesh_shape]
					name = "{} {} mesh tally {}".format(
						rxn_type, shape_name, ngroups)
					tally = openmc.Tally(name=name)
					tally.filters = [mesh_filter, energy_filter]
					tally.scores = [rxn_type]
					self._reaction_tallies[ngroups][rxn_type][shape_name] = tally
					self._tallies.append(tally)
			
			# Flux tallies for SPH -- only valid on "universe" domain.
			if "universe" in self.domains:
				utally = openmc.Tally(name="SPH tally {}".format(ngroups))
				utally.scores = ['flux']
				unique = tuple(self.lattice.get_unique_universes().keys())
				ufilt = openmc.UniverseFilter(unique)
				utally.filters = [ufilt, energy_filter]
				self._tallies.append(utally)
				
			# MGXS tallies
			dom_dict = {"cell"    : self.geometry.get_all_material_cells().values(),
			            "material": self.materials,
			            "universe": universe_domain,
			            "mesh"    : mesh_domain}
			for dom in self.domains:
				if dom == "mesh":
					warnstr = "Due to a bug in OpenMC, Mesh {} will be " \
					          "exported multiple times. You will have to " \
							  "manually remove it.".format(mesh_domain[0].id)
					warn(warnstr)
				group_lib = self._lib_dict[dom][ngroups]
				if self.isotropic:
					group_lib.mgxs_types = constants.ISO_TYPES
					group_lib.correction = None
				else:
					group_lib.mgxs_types = constants.ANISO_TYPES
					group_lib.correction = "P0"
				group_lib.domain_type = dom
				group_lib.domains = dom_dict[dom]
				group_lib.by_nuclide = False
				group_lib.build_library()
				group_lib.add_to_tallies_file(self._tallies)
	
	def export_to_xml(self, path="./"):
		"""Export the geometry, materials, and tallies for this model to XML.
		
		Parameters:
		-----------
		path:           str, optional; directory to export the XML files to
						[Default: "./"]
		"""
		# Make sure the slash is there for easy appending
		if path[-1] != "/":
			path += "/"
		for ngroups, structure in self.energy_groups.items():
			if ngroups in self._material_libraries:
				group_lib = self._material_libraries[ngroups]
				fname = "material_lib_{}".format(ngroups)
				group_lib.dump_to_file(fname, path)
			if ngroups in self._cell_libraries:
				group_lib = self._cell_libraries[ngroups]
				fname = "cell_lib_{}".format(ngroups)
				group_lib.dump_to_file(fname, path)
			if ngroups in self._mesh_libraries:
				group_lib = self._mesh_libraries[ngroups]
				fname = "mesh_lib_{}".format(ngroups)
				group_lib.dump_to_file(fname, path)
			if ngroups in self._universe_libraries:
				group_lib = self._universe_libraries[ngroups]
				fname = "universe_lib_{}".format(ngroups)
				group_lib.dump_to_file(fname, path)
		self.geometry.export_to_xml(path + "geometry.xml")
		self.materials_xml.export_to_xml(path + "materials.xml")
		# Todo: export settings and plots to XML
		if self._tallies:
			self._tallies.export_to_xml(path + "tallies.xml")
	
	def load_openmc_statepoint(self, statepoint, path="./"):
		"""Load an HDF5 statepoint
		
		Parameters:
		-----------
		statepoint:     str; file name, e.g., "statepoint.100.h5"
		path:           str, optional; path to the folder the statepoint is in.
		                [Default: "./" <-- the current directory]
		"""
		if path[-1] != "/":
			path += "/"
		try:
			self._sp = openmc.StatePoint(path + statepoint)
		except OSError as err:
			warn("Could not load statepoint:" + str(err))
			raise
		else:
			for n in self.energy_groups.keys():
				if "material" in self.domains:
					fname = "material_lib_{}".format(n)
					material_lib = mgxs.Library.load_from_file(
						filename=fname, directory=path)
					material_lib.load_from_statepoint(self._sp)
					self._material_libraries[n] = material_lib
				if "universe" in self.domains:
					fname = "universe_lib_{}".format(n)
					universe_lib = mgxs.Library.load_from_file(
						filename=fname, directory=path)
					universe_lib.load_from_statepoint(self._sp)
					self._universe_libraries[n] = universe_lib
				if "cell" in self.domains:
					fname = "cell_lib_{}".format(n)
					cell_lib = mgxs.Library.load_from_file(
						filename=fname, directory=path)
					cell_lib.load_from_statepoint(self._sp)
					self._cell_libraries[n] = cell_lib
				if "mesh" in self.domains:
					fname = "mesh_lib_{}".format(n)
					mesh_lib = mgxs.Library.load_from_file(
						filename=fname, directory=path)
					mesh_lib.load_from_statepoint(self._sp)
					self._mesh_libraries[n] = mesh_lib
	
	
	def _get_reference_fluxes(self, ngroups, universe_ids):
		"""Load the groupwise scalar fluxes from the OpenMC statepoint.
		
		This is only appropriate for an OpenMC simulation with the "universe" domain.
		A statepoint must have been loaded first. The reference fluxes for this group
		structure will be loaded from the SPH tally. If there are multiple universe ids,
		they will be summed at the end (so that SPH factors can be shared).
		
		Parameters:
		-----------
		ngroups:        int; number of energy groups to load the tally for
		universe_ids:   iterable of int; universe IDs to include in this tally
		
		"""
		assert self._sp, "You need to load a StatePoint first."
		assert "universe" in self.domains, "No homogenized data was tallied."
		cv.check_iterable_type("universe_ids", universe_ids, int)
		bins = [tuple(universe_ids)]
		tal = self._sp.get_tally(name="SPH tally {}".format(ngroups))
		sli = tal.get_slice(filters=[openmc.UniverseFilter], filter_bins=bins)
		fluxes = np.flip(sli.mean.reshape((len(universe_ids), ngroups)).sum(axis=0))
		# Normalize by the total flux.
		fluxes /= tal.mean.sum()
		return fluxes
	
	def _get_simulation_fluxes(self, ngroups, universe_ids, flux_mesh):
		"""Load the groupwise scalar fluxes from the OpenMOC run
		
		Parameters:
		-----------
		ngroups:        int; number of energy groups for the MOC simulation
		universe_ids:   iterable of int; which universes the flux tally should consider
		flux_mesh:      openmoc.process.Mesh on which the flux may be tallied
		
		Returns:
		--------
		"""
		flux_array = flux_mesh.tally_reaction_rates_on_mesh(self._solver, "flux", energy="by_group")
		indices = []
		for index, u in np.ndenumerate(self.lattice.universes):
			if u.id in universe_ids:
				indices.append(index)
		shape = self.lattice.shape + (ngroups,)
		# If the CMFD mesh isn't the core shape, project it onto the lattice mesh.
		if flux_array.shape != shape:
			new_flux_array = np.zeros(shape)
			template_array = np.zeros(self.lattice.shape, dtype=int)
			for g in range(ngroups):
				new_flux_array[:, :, g] = project_array(fine=flux_array[:, :, g],
				                                        coarse=template_array)
			flux_array = new_flux_array
			del template_array
		# Tally the appropriate universe fluxes
		uflux = np.zeros(ngroups)
		for i, j in indices:
			uflux += flux_array[i, j, :]
		uflux /= flux_array.sum()
		return uflux
	
	
	def _save_simulation_results(self, ngroups, export_path, save_uncertainty):
		"""Save the results of a recently completed simulation
		
		Parameters:
		-----------
		ngroups:            int; the number of energy groups used for the simulation
		export_path:        str; directory to save the results to
		save_uncertainty:   bool; whether to save Monte Carlo uncertainties as well
		"""
		if not self._run:
			warn("You must run a simulation to save its results.")
			return
		# Also output your OpenMC fission rates for comparison
		for mesh_shape, moc_mesh in self._moc_meshes.items():
			if moc_mesh is None:
				continue
			mname = self._mesh_names[mesh_shape]
			tal_name = "{} mesh tally".format(mname)
			try:
				# Total fission rate tally
				fission_tally = self._sp.get_tally(name=tal_name)
				vals = fission_tally.get_values(scores=["fission"])
				fission_rates = vals[:, 0, 0]
				fission_rates[fission_rates == 0] = np.NaN
				fission_rates.shape = moc_mesh.dimension
				fission_rates /= np.nanmean(fission_rates)
				fission_rates = np.flipud(fission_rates)
				fname = export_path + \
				        "{}groups_montecarlo_fission_rates_{}".format(ngroups, mname)
				np.savetxt(fname, fission_rates)
				print("OpenMC {} mesh tally exported to {}".format(mname, fname))
			except (LookupError, ValueError) as err:
				warnstr = "{} : {}".format(str(err), tal_name)
				warn(warnstr)
			# Groupwise reaction tallies
			for rxn_type in self._reaction_tallies[ngroups]:
				try:
					self._save_groupwise_mesh_tally(
						ngroups, rxn_type, moc_mesh, mname, export_path, save_uncertainty)
				except (LookupError, KeyError) as err:
					warnstr = "{} : self._reaction_tallies[{}][{}][{}]".\
						format(str(err), ngroups, rxn_type, mname)
					warn(warnstr)
	
	
	def _save_groupwise_mesh_tally(self, ngroups, rxn_type, moc_mesh, mesh_name,
	                               export_path, save_uncertainty):
		"""Save the reaction rate tallies from the OpenMC and OpenMOC meshes
		
		Parameters:
		-----------
		ngroups:            int; the number of energy groups used for the simulation
		rxn_type:           str; the reaction whose rates we are saving
		moc_mesh:           openmoc.process.Mesh; the mesh reaction rates were tallied on
		mesh_name:          str; the mesh name in the format {NX}x{NY}, e.g., "3x3"
		export_path:        str; directory to save the results to
		save_uncertainty:   bool; whether to save Monte Carlo uncertainties as well
		"""
		if not self._run:
			warn("You must run a simulation to save its results.")
			return
		# Monte Carlo
		rxn_tally = self._reaction_tallies[ngroups][rxn_type][mesh_name]
		# I think I have to do this instead because some tallies may merge...
		vals = self._sp.get_tally(name=rxn_tally.name).get_values(scores=[rxn_type])
		vals[vals == 0] = np.NaN
		rxn_rates = vals[:, 0, 0]
		if save_uncertainty:
			vals = self._sp.tallies[rxn_tally.id].get_values(scores=[rxn_type])
			uncertain = vals[:, 0, 1]
		rxn_rates.shape = np.append(moc_mesh.dimension, ngroups)
		# And then for the MOC results
		moc_rates = moc_mesh.tally_reaction_rates_on_mesh(
			self._solver, rxn_type, energy="by_group")
		for g in range(ngroups):
			# Monte Carlo. OpenMC groups are in the opposite order!!
			group_rates = rxn_rates[:, :, ngroups - (g + 1)]
			group_rates = np.flipud(group_rates)
			fname = export_path + "montecarlo_{}_{:02d}-of-{}_{}". \
				format(rxn_type, g + 1, ngroups, mesh_name)
			np.savetxt(fname, group_rates)
			if save_uncertainty:
				group_uncert = uncertain[:, :, ngroups - (g + 1)]
				group_uncert = np.flipud(group_uncert)
				gname = export_path + "montecarlo_{}_uncert_{:02d}-of-{}". \
					format(rxn_type, g + 1, ngroups)
				np.savetxt(gname, group_uncert)
				print(rxn_type, "rates exported to", fname, gname)
			# MOC
			moc_group_rates = moc_rates[:, :, g]
			moc_group_rates = np.flipud(moc_group_rates)
			hname = export_path + "moc_{}_{:02d}-of-{}_{}". \
				format(rxn_type, g + 1, ngroups, mesh_name)
			np.savetxt(hname, moc_group_rates)
			if g == 0:
				print("MOC {} rates exported to {} ...".format(rxn_type, hname))
	
	
	def _prep_openmoc(self, ngroups, domain_type, cmfd_mesh, calculate_sph=None, **kwargs):
		"""Prepare the OpenMOC core model for the run
		
		Parameters:
		-----------
		ngroups:            int; number of energy groups for the multigroup run
		domain_type:        str; {"universe", "cell", "material", "mesh" (not implemented)}
		cmfd_mesh:          tuple (int, int); (nx, ny) of the mesh to use for CMFD discretization
		calculate_sph:      list of str, optional; keys for the elements to calculate SPH
		                    factors on. If not provided, no SPH factors will calculated.
		                    [Default: None]
		"""
		if self._prepped:
			return
		domain_type = domain_type.lower()
		assert domain_type in self.domains
		assert self._sp is not None, "You need to load a StatePoint first!"
		
		self._moc_geom = openmoc.Geometry()
		mglib = self._lib_dict[domain_type][ngroups]
		core = Core(self.lattice, mglib, domain_type, **kwargs)
		if calculate_sph:
			self._sph_ids = core.get_universe_ids(calculate_sph)
		openmc_root_cell = self.geometry.get_cells_by_name(name="root cell")[0]
		moc_root_region = openmc.openmoc_compatible.get_openmoc_region(openmc_root_cell.region)
		moc_lat = core.get_moc_lattice()
		
		root_cell = openmoc.Cell(name="root cell")
		root_cell.setFill(moc_lat)
		root_cell.setRegion(moc_root_region)
		root_universe = openmoc.Universe(name="root universe")
		root_universe.addCell(root_cell)
		self._moc_geom.setRootUniverse(root_universe)
		
		if cmfd_mesh:
			cmfd = openmoc.Cmfd()
			cmfd.setSORRelaxationFactor(1.5)
			# Assumes 2D; will break on 3D.
			nx, ny = cmfd_mesh
			print("CMFD set to {}x{}".format(nx, ny))
			cmfd.setLatticeStructure(nx, ny)
			cmfd.setKNearest(3)
			self._moc_geom.setCmfd(cmfd)
			# Use the CMFD mesh to create an OpenMOC Mesh on which to tally reaction rates
			mesh = self._meshes[cmfd_mesh]
			m = openmoc.process.Mesh()
			m.dimension = np.array(cmfd_mesh)
			m.lower_left = mesh.lower_left
			m.upper_right = mesh.upper_right
			m.width = (m.upper_right - m.lower_left)/m.dimension
			self._moc_meshes[cmfd_mesh] = m
		else:
			warnstr="No CMFD mesh given. OpenMOC may be very slow,\n" \
			        "and you may encounter errors when tallying reactions."
			warn(warnstr)
			
		self._prepped = True
	
	
	def run_openmoc(self, ngroups, domain, nazim, dazim, solve_type,
	                cmfd_mesh, nproc=4, stabilize=0.0,
	                plot=False, save_results=True, save_uncert=False,
	                calculate_sph=None,
	                export_path="moc_data/", **kwargs):
		"""Run a Method Of Characteristics eigenvalue calculation using OpenMOC
		
		Parameters:
		-----------
		ngroups:        int; number of energy groups to use
		domain:         str, in {"cell", "material"};
		                which domain type to use the MGXS Library for
		nazim:          int; number of azimuthal angles (multiple of 4)
		dazim:          float, cm; desired azimuthal ray spacing
		solve_type:     str; use "flat" (or "fsr") for flat source regions,
		                or "linear" (or "lsr") to use linear sources
		cmm             cumulative.CumulativeMigrationCorrection, optional;
		                a CMM correction for transport and scattering MGXS
		                [Default: None]
		cmfd_mesh:      tuple of (int, int); mesh shape to use for CMFD.
		                [Default: None].
		nproc:          int; number of threads for the MOC solver to use
		                [Default: 4]
		plot:           bool, optional; whether to generate default plots.
		                Cells, materials, FSRs, fission rate, and mg flux plots
		                [Default: False]
		save_results:   bool, optional; whether to export the OpenMC and OpenMOC tally
		                results to the export_path.
		save_uncert:    bool, optional; whether to export the OpenMC tally
		                standard deviations to the export_path.
		calculate_sph:  list of str, optional; keys for the elements to calculate SPH
		                factors on. If not provided, no SPH factors will calculated.
		                [Default: None]
		export_path:    str, optional; directory to export data to.
		                [Default: "moc_data/"]
		
		kwargs:
		-------
		subdivide:          bool; whether to subdivide Elements that request it
		use_sph:            bool; whether to apply SPH factors to Elements that request it
		use_cmm:            bool; whether to apply CMM corrections to Elements that request it
		                    Only valid in the "universe" domain. IDK if it can be used with SPH.
		crdrings:           bool; whether to apply azimuthal rings to crds in Elements that request it
		fsrsects:           bool; whether to apply azimuthal sectors to crds in Elements that request it
		elements:           dict of {key : treat.moc.Element}; Elements requesting the features above
		ids_fname:          str; file name of ids_to_keys pickle
		                    [Default: consants.IDS_PICKLE --> "ids_to_keys.pkl"]
		"""
		if save_results:
			if export_path[-1] != "/":
				export_path += "/"
			if not os.path.isdir(export_path):
				os.mkdir(export_path)
		solve_type = solve_type.lower()
		assert solve_type in ("fsr", "flat", "lsr", "linear"), \
			"Unknown solve type: {}".format(solve_type)
		if not self._prepped:
			self._prep_openmoc(ngroups, domain, cmfd_mesh, calculate_sph, **kwargs)
		
		self._moc_geom.initializeFlatSourceRegions()
		track_generator = openmoc.TrackGenerator(self._moc_geom, num_azim=nazim, azim_spacing=dazim)
		
		#track_generator.setZCoord(0.0)
		track_generator.setNumThreads(nproc)
		track_generator.generateTracks()
		print("Tracks generated!")
		if plot:
			moc_plt.plot_flat_source_regions(self._moc_geom)
			moc_plt.plot_materials(self._moc_geom)
			moc_plt.plot_cells(self._moc_geom)
			if plot < 0:
				return
		# Run OpenMOC
		if solve_type in ("flat", "fsr"):
			self._solver = openmoc.CPUSolver(track_generator)
		elif solve_type in ("linear", "lsr"):
			self._solver = openmoc.CPULSSolver(track_generator)
		else:
			raise NotImplementedError(solve_type)
		if stabilize:
			self._solver.stabilizeTransport(stabilize)
		self._solver.setNumThreads(nproc)
		self._solver.computeEigenvalue(max_iters=500)
		self._solver.printTimerReport()
		self._run = True
		
		print("With nazim = {}, spacing = {} cm, and {} energy groups".format(
			track_generator.getNumAzim(),
			track_generator.getDesiredAzimSpacing(),
			ngroups))
		keff_moc = self._solver.getKeff()
		print('OpenMOC keff: {:8.6f}'.format(keff_moc))
		
		# OpenMOC fission rates from the meshes
		moc_mesh = self._moc_meshes[cmfd_mesh]
		mname = self._mesh_names[cmfd_mesh]
		if save_results:
			moc_fission_rates = \
				np.array(moc_mesh.tally_fission_rates(self._solver))
			moc_fission_rates.shape = moc_mesh.dimension
			moc_fission_rates = np.fliplr(moc_fission_rates).T  # WHY :(
			fname = export_path + "{}groups_moc_fission_rates_{}".\
				format(ngroups, mname)
			np.savetxt(fname, moc_fission_rates)
			print("MOC {} mesh tally exported to {}\n".format(mname, fname))
		if self._sp:
			keff_mc, uncert_mc = self._sp.k_combined
			bias = (keff_moc - keff_mc)*1E5
			eigenreport = """\
OpenMC keff:  {keff_mc:8.6f} +/- {uncert_mc:8.6f}
OpenMOC keff: {keff_moc:8.6f}
OpenMOC bias: {bias:.0f} [pcm]
""".format(**locals())
			print(eigenreport)
			if save_results:
				fname = export_path + "RESULTS.txt"
				with open(fname, 'w') as results_file:
					results_file.write(eigenreport)
			if calculate_sph:
				# Get the flux tallies
				mcflux = self._get_reference_fluxes(ngroups, self._sph_ids)
				simflux = self._get_simulation_fluxes(ngroups, self._sph_ids, moc_mesh)
				sph_factors = mcflux/simflux
				if save_results:
					fname = export_path + constants.SPH_ARRAY
					np.savetxt(fname, sph_factors)
					print("SPH factors saved to", fname)
				else:
					print("\nSPH factors:\n", sph_factors)
			if save_results:
				self._save_simulation_results(ngroups, export_path, save_uncert)
		elif not self._sp:
			print("(No OpenMC tally to compare results against.)")
		elif not save_results:
			print("Results not saved.")
		else:
			print("I forgot an error message for this case.")
			print("save_results: {};  self._sp: {}".format(save_results, bool(self._sp)))
		
		if plot:
			openmoc.plotter.plot_spatial_fluxes(self._solver, energy_groups=range(1, ngroups+1))
	

	def reset(self):
		"""Reset the variables that were changed when calling Case.run()"""
		self._moc_geom = None
		self._sph_ids = None
		self._moc_meshes = {}
		self._solver = None
		self._prepped = False
		self._run = False
