# Layer
#
# Take 2D regions and coalesce them into an axially infinite universe

from copy import deepcopy
import openmc
from . import shapes
from .error import *

class Layer(object):
	"""
	
	Parameters:
	-----------
	ring0:      Shape; cell for the innermost ring.
	manager:    Manager; surface manager from the geometry builder.
	(pitch:      float, cm; not implemented)
	outer_mat:  openmc.Material; the material for the gap on the outside
	
	Attributes:
	-----------
	finalized:  Boolean; whether the Layer has been fully completed.
	region:     openmc.Region; inside the current outermost ring
	outside:    openmc.Region; outside the current outermost, infinite ring.
				Is not created until the Layer is finalized.
	universe:   openmc.Universe;
	
	"""
	def __init__(self, manager, material_lib, ring0, outer_mat, name=""):
		#self.pitch = pitch
		# actually, that may not be necessary
		assert ring0.innermost, "ring0 must be an `innermost` shape."
		self._shapes = [ring0]
		self._rmin = ring0.rmin
		self._rmax = None
		self._dmin = ring0.dmin
		self._region = ring0.region
		self._outside = ring0.complement
		self._universe = None
		self.manager = manager
		self.material_lib = material_lib
		if isinstance(outer_mat, openmc.Material):
			self.outer_mat = outer_mat
		elif isinstance(outer_mat, str):
			self.outer_mat = material_lib[outer_mat]
		else:
			errstr = "outer_mat must be an openmc.Material or " + \
					 "a key in the material library"
			raise TypeError(errstr)
		self.name = name
		self.finalized = False
	
	def __len__(self):
		return len(self._shapes)
	
	@property
	def outside(self):
		return self._outside
	
	@property
	def region(self):
		return self._region
	
	@property
	def universe(self):
		return self._universe
	
	@property
	def rmax(self):
		return self._rmax
	
	@property
	def dmax(self):
		return self.dmax
	
	def add_ring(self, fill, shape, thick=None, r=None, d=None):
		"""Add another 2D ring outside the last one.
		
		Parameters:
		-----------
		fill:       openmc.{Material, Universe, or "void"};
					  what to fill the new ring with
		shape:      str; name of the shape
		thick:      float, cm;
		"""
		if self.finalized:
			raise FinalizedError("Cannot add ring to finalized Layer.")
		shape = shape.lower()
		if isinstance(fill, str):
			fill = self.material_lib[fill]
		
		# Make sure enough parameters have been given
		if thick is not None:
			assert r is None
			r = self._rmin + thick
		elif r is not None:
			assert r > self._rmin, \
				"New ring (r={} cm) would be inside old one".format(shape.rmin)
		else:
			raise ValueError("add_ring() requires either `thick` or `r`")
		
		if shape == "circle":
			ring = self.manager.get_circle(r)
		elif shape == "rectangle":
			ring = self.manager.get_rectangle(r)
		elif shape == "octagon":
			if d is None:
				try:
					d = self._dmin + thick
				except TypeError:
					errstr = "You must specify diagonal `d` unless " + \
					"the last ring was also an octagon."
					raise ValueError(errstr)
			ring = self.manager.get_octagon(r, d)
		else:
			raise NotImplementedError(shape)
		
		ring.fill = fill
		self._rmin = ring.rmin
		self._dmin = ring.dmin
		self._region = deepcopy(ring.region)
		ring.region &= self._outside
		self._outside = deepcopy(ring.complement)
		self._shapes.append(ring)
	
	def finalize(self):
		"""Set the outside cell (TBD?) and set self.universe"""
		if not self.finalized:
			# do we need the next two lines?
			self._rmax = self._rmin
			last = self._shapes[-1]
			self._outside = last.complement
			# the infinite outer gap outside the element clad
			outer_gap = openmc.Cell()
			outer_gap.fill = self.outer_mat
			outer_gap.region = self._outside
			# Zip it all up in a nice universe
			self._universe = openmc.Universe()
			self._universe.add_cells(self._shapes)
			self._universe.add_cell(outer_gap)
			self.finalized = True
		

