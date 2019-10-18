# Shapes
#
# Useful 2D shapes for TREAT builds

import openmc
from math import sqrt
RT2 = sqrt(2)

SHAPE_TYPES = {"circle", "rectangle", "octagon"}

class Shape(openmc.Cell):
	"""Generic shape, used as a base class for the others
	
	Parameters:
	-----------
	innermost:      Boolean; whether this is the innermost shape in a Layer.
	complement:     openmc.Region for the outside of this shape.
					Can be specified in subclasses for cleanliness; otherwise,
					it will be automatically determined by OpenMC.
	"""
	def __init__(self, innermost,
	             cell_id=None, name='', fill=None):
		super().__init__(cell_id, name, fill)
		self._complement = None
		self.innermost = innermost
		self.shape_type = None
		self.rmin = None
		self.dmin = None
	
	@property
	def complement(self):
		# TODO: Consider removing this. Could cause problems.
		if not self._complement:
			return ~self.region
		else:
			return self._complement

	def punch_hole(self, filler, complement=None):
		"""Intersect this shape's region with something
		entirely contained within it
		
		# TODO: Consider moving this whole method to Layer().
		
		Parameters:
		-----------
		filler:     openmc.Cell to put inside the hole
		"""
		if complement is None:
			complement = ~filler.region
		self.region &= complement
		

class Circle(Shape):
	"""A cell made of a cylinder"""
	def __init__(self, cyl, innermost,
	             cell_id=None, name='', fill=None):
		super().__init__(innermost, cell_id, name, fill)
		self.shape_type = "circle"
		self.region = -cyl
		self._complement = +cyl
		self.rmin = cyl.coefficients['R']

class Rectangle(Shape):
	"""A cell made of 4 planes"""
	def __init__(self, planes, innermost,
	             cell_id=None, name='', fill=None):
		e, w, n, s = planes
		super().__init__(innermost, cell_id, name, fill)
		self.shape_type = "rectangle"
		self.region =      -e & +w & -n & +s
		self._complement = +e | -w | +n | -s
		self.rmin = min(+e.x0, -w.x0, +n.y0, -s.y0)
		xmin = min(+e.x0, -w.x0)
		ymin = min(+n.y0, -s.y0)
		self.dmin = sqrt(xmin**2 + ymin**2)
		

class Octagon(Shape):
	"""A cell made of 8 planes"""
	def __init__(self, planes, innermost,
	             cell_id=None, name='', fill=None):
		e, w, n, s, ne, nw, sw, se = planes
		super().__init__(innermost, cell_id, name, fill)
		self.shape_type = "octagon"
		self.region      = -e & +w & -n & +s & -ne & -nw & +sw & +se
		self._complement = +e | -w | +n | -s | +ne | +nw | -sw | -se
		self.rmin = min(+e.x0, -w.x0, +n.y0, -s.y0)
		self.dmin = min([abs(corner.coefficients['D'])
		                 for corner in (ne, nw, sw, se)])/RT2