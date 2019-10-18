# TREAT Lattice
#
# A lattice template to speed up making simple cores

import pickle
from warnings import warn
from numpy import array
import openmc
from . import constants

class TreatLattice(openmc.RectLattice):
	def __init__(self, n, material_lib, name=''):
		super().__init__(lattice_id=constants.ROOT_LATTICE, name=name)
		self.material_lib = material_lib
		self.n = n
		self.dimension = array([n, n])
		self._pitch = array([constants.PITCH, constants.PITCH])
		self.width = self.dimension*self.pitch
		self._lower_left = -self.width/2.0
		
	
	def export_key_pickle(self, fname=constants.IDS_PICKLE):
		ids_to_keys = {}
		all_keys = set()
		for u, universe in self.get_unique_universes().items():
			name = universe.name
			if name:
				if name in all_keys:
					warnstr = 'key "{}" is not unique!'.format(name)
					warn(warnstr)
				else:
					all_keys.add(name)
			else:
				warnstr = "Universe {} has no key.".format(u)
				warn(warnstr)
			ids_to_keys[u] = name
		with open(fname, 'wb') as pickle_file:
			pickle.dump(ids_to_keys, pickle_file)
	
	
	def get_openmc_geometry(self, bc, axially_finite):
		geom = openmc.Geometry()
		root_universe = openmc.Universe(universe_id=0)
		root_cell = openmc.Cell(name="root cell")
		hwidth = self.width[0]/2.0
		bce, bcw, bcs, bcn = bc
		xmin = openmc.XPlane(x0=-hwidth, boundary_type=bce)
		xmax = openmc.XPlane(x0=+hwidth, boundary_type=bcw)
		ymin = openmc.YPlane(y0=-hwidth, boundary_type=bcs)
		ymax = openmc.YPlane(y0=+hwidth, boundary_type=bcn)
		root_universe.add_cell(root_cell)
		root_cell.region = +xmin & -xmax & +ymin & -ymax
		if axially_finite:
			zmin = openmc.ZPlane(z0=constants.ZMIN2D, boundary_type="reflective")
			zmax = openmc.ZPlane(z0=constants.ZMAX2D, boundary_type="reflective")
			root_cell.region &= +zmin & -zmax
		root_cell.fill = self
		geom.root_universe = root_universe
		return geom
	
	
	def export_to_xml(self, bc, axially_finite, plotzs=(0.0,), entropy=0,
	                  particles=1000, batches=10, inactive=5):
		"""Export just this lattice's geometry and materials to XML

		Parameters:     (all optional)
		-----------
		bc:             str; boundary condition for the edges of the lattice.
						BC order: (e, w, n, s)
						[Default: "vacuum" on all 4 edges]
		
		plotzs:         Nonetype or float, cm; iterable of z-values to plot at
						[Default: tuple of (0.0)]
		
		entropy:        int, optional; number of divisions per lattice element
						to tally Shannon entropy on.
						Anything Falsey disables this tally.
						[Default: 0]
						
		particles:      int; number of particles per batch
						[Default: 1000]
		
		batches:        int; total number of batches
						[Default: 10]
		
		inactive:       int; number of batches to ignore for statistics
						[Default: 5]
		
		axially_finite: bool; whether to bound the top and bottom with reflective ZPlanes.
		                [Default: False]
		
		"""
		geom = self.get_openmc_geometry(bc, axially_finite)
		geom.export_to_xml()
		self.export_key_pickle()
		# plots
		if len(plotzs):
			lots = openmc.Plots()
			for z in plotzs:
				for scheme in ("cell", "material"):
					p = openmc.Plot()
					p.name = "Plot_{:.3f}_{}s".format(z, scheme)
					p.filename = p.name
					p.basis = 'xy'
					p.color_by = scheme
					if scheme == "material":
						p.colors = self.material_lib.color_mapping
					p.origin = (0, 0, z)
					#p.width = [self.plot_width, self.plot_width]
					p.width = self.width
					lots.append(p)
			lots.export_to_xml()
		# essential settings
		s = openmc.Settings()
		s.particles = particles
		s.batches = batches
		s.inactive = inactive
		if entropy:
			raise NotImplementedError("Shannon Entropy")
			emesh = openmc.Mesh.from_rect_lattice(self, division=entropy)
			s.entropy_mesh = emesh
		s.export_to_xml()
		# materials
		mats = geom.root_universe.get_all_materials().values()
		openmc.Materials(mats).export_to_xml()

