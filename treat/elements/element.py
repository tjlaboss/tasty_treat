# Element
#
# Module for an abstract element class
#
# TODO: Add PartialElement abilities

#import sys; sys.path.append(".."); import constants
import openmc
import numpy as np

class Element(object):
	"""Abstract class that serves as a wrapper for OpenMC universes,
	built by stacking instances of geometry.Layer axially
	
	Parameters:     (all optional)
	-----------
	manager:        geometry.Manger; manager of the surfaces
	zmin:           float; z-coordinate of the lower bound of the 3D element
	rmax:           float, cm; maximum radius or x/y edge for all layers
	dmax:           float, cm; maximum "corner" midpoint for all layers
	name:           str; name for the element and constituent universe

	Attributes:
	-----------
	zmin
	zmax
	rmax
	dmax
	finalized:      Boolean; whether the element has been completely built
	universe:       openmc.Universe;
	"""
	def __init__(self, manager=None, material_lib=None,
	             zmin=None, rmax=None, dmax=None, name=""):
		self.manager = manager
		self.material_lib = material_lib

		self._rmax = rmax
		self._dmax = dmax
		self._z = zmin
		
		self.name = name
		self.universe = openmc.Universe(name=name)
		self._finalized = False
		self._layer_cells = []
	
	@property
	def rmax(self):
		return self._rmax
	
	@property
	def finalized(self):
		return self._finalized
	
	def finalize(self):
		self.universe.add_cells(self._layer_cells)
		self._finalized = True
	
	def translate_rotate(self, t_vector=None, r_vector=None):
		"""Create a translated and/or version of this universe

		Replaces Element.universe with the translated/rotated one

		Parameter
		---------
		t_vector:         translation vector
		r_vector:         rotation vector

		Returns
		-------
		None
		"""
		assert self.finalized, \
			"This Element must be finalized before translating or rotating."
		assert not all(v is None for v in [t_vector, r_vector]), \
			"You must specify t_vector, r_vector, or both."
		name = self.name[:]
		new_cell = openmc.Cell()
		new_cell.fill = self.universe
		if t_vector:
			name += " [translated]"
			new_cell.translation = t_vector
		if r_vector:
			name += " [rotated]"
			new_cell.rotation = r_vector
		new_cell.name = name
		# new_universe = openmc.Universe(name=new_cell.name, cells=[new_cell])
		# return new_universe
		self.universe = openmc.Universe(name=new_cell.name, cells=[new_cell])
	
	def export_to_xml(self, plotzs=(0.0,), pitch=10.16,
	                  particles = 1000, batches=10, inactive=5):
		"""Export just this element's geometry and materials to XML
		
		Parameters:     (all optional)
		-----------
		plotzs:         Nonetype olattice_idr float, cm; iterable of z-values to plot at
						[Default: tuple of (0.0)]
		pitch:          float, cm; pitch of the lattice the element goes into
						[Default: 10.16]
		particles:      int; number of particles per batch
						[Default: 1000]
		catches:        int; total number of batches
						[Default: 10]
		inactive:       int; number of batches to ignore for statistics
						[Default:3]
		"""
		assert self.finalized, \
			"Cannot export an element which has not been finalized."
		# root universe and geometry
		geom = openmc.Geometry()
		root_universe = openmc.Universe()
		root_cell = openmc.Cell(fill=self.universe, name="root cell")
		hpitch = pitch/2
		xmin = openmc.XPlane(x0=-hpitch, boundary_type="reflective")
		xmax = openmc.XPlane(x0=+hpitch, boundary_type="reflective")
		ymin = openmc.YPlane(y0=-hpitch, boundary_type="reflective")
		ymax = openmc.YPlane(y0=+hpitch, boundary_type="reflective")
		root_universe.add_cell(root_cell)
		root_cell.region = +xmin & -xmax & +ymin & -ymax
		geom.root_universe = root_universe
		geom.export_to_xml()
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
					p.width = [pitch, pitch]
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


class Element3D(Element):
	"""An Element in 3 dimensions
	
	Contains the new method Element3D.add_layer()
	
	Parameters:
	-----------
	manager:        geometry.Manger; manager of the surfaces
	zmin:           float; z-coordinate of the lower bound of the 3D element
	rmax:           float, cm; maximum radius or x/y edge for all layers
	dmax:           float, cm; maximum "corner" midpoint for all layers
	name:           str; name for the element and constituent universe
	
	Attributes:
	-----------
	zmin
	zmax
	rmax
	dmax
	finalized:      Boolean; whether the element has been completely built
	universe:       openmc.Universe;
	"""
	def __init__(self, manager, material_lib,
	             zmin, rmax, dmax=None,
	             name=""):
		super(Element3D, self).__init__(manager, material_lib, zmin, rmax, dmax, name)
		self._bottom = manager.get_zplane(z0=zmin)
		self._last_top = self._bottom
		
	def __str__(self):
		return self.name
	
	@property
	def bottom(self):
		return self._bottom
	
	@property
	def top(self):
		if self.finalized:
			return self._last_top
	
	def add_layer(self, layer, ztop, nomatch=False):
		"""Add a radially infinite layer to the next position in the stack

		Parameters:
		-----------
		layer:      geometry.Layer; axial layer to stack
		ztop:       float, cm; top of the new layer.
					ztop must be below the current zmax.
		nomatch:    Boolean, optional; whether to skip matching the outer
					dimension of the layer to that of the element. Generally,
					you should leave this alone except for the fuel fittings.

		Returns
		-------
		None
		"""
		assert not self._finalized, \
			"Element has already been finalized."
		assert ztop > self._z, \
			"Layer top would be below layer bottom."
		if not nomatch:
			assert np.isclose(layer.rmax, self.rmax, atol=self.manager.tol), \
				"Layer.rmax doesn't match Element.rmax"
		
		new_cell = openmc.Cell(name=layer.name)
		new_cell.fill = layer.universe
		new_top = self.manager.get_zplane(ztop)
		new_cell.region = +self._last_top & -new_top
		self._layer_cells.append(new_cell)
		self._z = ztop
		self._last_top = new_top
	
	
class Element2D(Element):
	@staticmethod
	def fromLayer(layer):
		name = layer.name + " Element (2D)"
		#zmin = layer.manager.zmin
		#zmax = layer.manager.zmax
		elem = Element(layer.manager, layer.material_lib, None, layer.rmax, name=name)
		elem.universe = layer.universe
		#elem.add_layer(layer, zmax)
		elem.finalize()
		return elem

