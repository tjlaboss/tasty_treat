# TREAT 2D
#
# 2D models of treat

import openmc
import elements
import constants
import materials

MODELS = {"MCM", "M8CAL"}

class Treat2D(object):
	"""Two-dimentional model of TREAT
	
	Parameters:
	-----------
	matlib:             str; name of the MaterialLib to use
	
	Attributes:
	-----------
	matlib
	material_lib:       materials.MaterialLib; library to get materials from
	empty:              openmc.{Material, Universe} (or "void");
						what goes outside the core. currently uses air.
	manager:            geometry.Manager; surface manager for the builder
	finalized:          Boolean; whether the model is finished and ready to go
	"""
	def __init__(self, matlib):
		self.matlib = matlib
		self.material_lib = materials.get_library(matlib)
		self.empty = self.material_lib["air"]
		self.manager = elements.geometry.Manager()
		self._core_lat = None
		self._root_cell = openmc.Cell(name="Root Cell")
		self._root_universe = openmc.Universe(universe_id=0, name="Root Universe")
		self._edges = []
		self._finalized = False
	
	@property
	def finalized(self):
		return self._finalized
	
	@property
	def universe(self):
		return self._root_universe
	
	def set_core_lattice(self, model):
		model = model.upper()
		if model == "MCM":
			import mcm2d as core
		elif model in MODELS:
			raise NotImplementedError(model)
		else:
			errstr = "{} is not a valid model."
			raise ValueError(errstr.format(model))
		self._core_lat = core.get_core_lattice(self.manager, self.material_lib)
	
	def build_excore(self, simple):
		"""Build the stuff outside the core
		
		Parameter:
		----------
		simple:     Boolean; whether to use the simplified geometry,
					as used by NRL, instead of the complicated geometry.
		"""
		assert self._core_lat, \
			"You must select a core lattice before adding the excore features."
		if simple is True:
			x, y = self._core_lat.width/2.0
			core_w = self.manager.get_xplane(-x)
			core_e = self.manager.get_xplane(+x)
			core_s = self.manager.get_yplane(-y)
			core_n = self.manager.get_yplane(+y)
			core_planes = (core_e, core_w, core_n, core_s)  # Order matters!
			core_square = elements.geometry.shapes.Rectangle(core_planes, innermost=True)
			core_square.fill = self._core_lat
			# The core itself
			model = elements.geometry.Layer(self.manager, self.material_lib,
			                                core_square, self.empty)
			# air box
			model.add_ring("air", "rectangle", constants.excore.nrl_gap)
			# Permanent reflector liner
			model.add_ring("aluminum", "rectangle", constants.excore.nrl_liner_thick)
			# Permanent excore reflector
			# FIXME: This is a different graphite than used inside the core (not CP-2)
			model.add_ring("graphite", "rectangle", constants.excore.nrl_graphite_thick)
			# And then it's all just air past that
			model.finalize()
			self._root_cell.fill = model.universe
			#void_cell = openmc.Cell(fill="void")
			#void_verse = openmc.Universe(cells=[void_cell])
			self._edges = model.region.get_surfaces()
		else:
			raise NotImplementedError("simple={}".format(simple))
	
	def finalize(self):
		"""Check if all of the essential parts of the model have been built.
		Set a few OpenMC parameters. Switch Treat2D.finalized to True. """
		if self._finalized:
			return
		assert self._core_lat
		assert self._root_cell.fill
		assert len(self._edges) == 4
		
		# more to do
		self._finalized = True
	
	def export_to_xml(self, plotzs=(0.0,),
	                  particles=1000, batches=10, inactive=5):
		"""Export just this lattice's geometry and materials to XML

		Parameters:     (all optional)
		-----------
		plotzs:         Nonetype olattice_idr float, cm; iterable of z-values to plot at
						[Default: tuple of (0.0)]
		particles:      int; number of particles per batch
						[Default: 1000]
		catches:        int; total number of batches
						[Default: 10]
		inactive:       int; number of batches to ignore for statistics
						[Default:3]
		"""
		assert self._finalized, \
			"Model must be finalized before exporting to XML."
		# root universe and geometry
		geom = openmc.Geometry()
		bounds = [None]*4
		for i, old_surf in enumerate(self._edges.values()):
			new_surf = old_surf.clone()
			new_surf.boundary_type = "vacuum"
			bounds[i] = new_surf
		# Order matters! E, W, N, S
		xmax, xmin, ymax, ymin = bounds
		xwidth = xmax.x0 - xmin.x0
		ywidth = ymax.y0 - ymin.y0
		self._root_cell.region = +xmin & -xmax & +ymin & -ymax
		self._root_universe.add_cell(self._root_cell)
		geom.root_universe = self._root_universe
		geom.export_to_xml()
		# plots
		if plotzs:
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
					p.width = (xwidth, ywidth)
					lots.append(p)
			lots.export_to_xml()
		# essential settings
		s = openmc.Settings()
		s.particles = particles
		s.batches = batches
		s.inactive = inactive
		s.export_to_xml()
		# materials
		mats = geom.root_universe.get_all_materials().values()
		openmc.Materials(mats).export_to_xml()
	

# test it out!
if __name__ == "__main__":
	mcm = Treat2D("NRL")
	mcm.set_core_lattice("MCM")
	mcm.build_excore(simple=True)
	mcm.finalize()
	mcm.export_to_xml()
