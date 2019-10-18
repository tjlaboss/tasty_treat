# Manager
#
# Keep track of surfaces with equivalent dimensions

from math import sqrt
import openmc
from numpy import isclose
_rt2 = sqrt(2.0)
from . import shapes


class Manager(object):
	def __init__(self, tol=5):
		self.tol = tol
		self._zplanes = {}
		self._xplanes = {}
		self._yplanes = {}
		self._xyplanes1 = {}  #  45 (and 225) degrees
		self._xyplanes2 = {}  # 135 (and 315) degrees
		self._zcylinders = {}
	
	def isclose(self, a, b):
		return isclose(a, b, atol=10**-self.tol)
	
	def get_cylinder(self, r0, bound="transmission"):
		r0 = round(r0, self.tol)
		if r0 not in self._zcylinders:
			self._zcylinders[r0] = openmc.ZCylinder(R=r0, boundary_type=bound)
		return self._zcylinders[r0]
	
	def get_zplane(self, z0, bound="transmission"):
		z0 = round(z0, self.tol)
		if z0 not in self._zplanes:
			self._zplanes[z0] = openmc.ZPlane(z0=z0, boundary_type=bound)
		return self._zplanes[z0]
	
	def get_xplane(self, x0, bound="transmission"):
		x0 = round(x0, self.tol)
		if x0 not in self._xplanes:
			self._xplanes[x0] = openmc.XPlane(x0=x0, boundary_type=bound)
		return self._xplanes[x0]
	
	def get_yplane(self, y0, bound="transmission"):
		y0 = round(y0, self.tol)
		if y0 not in self._yplanes:
			self._yplanes[y0] = openmc.YPlane(y0=y0, boundary_type=bound)
		return self._yplanes[y0]
	
	def get_xyplane1(self, diag, bound="transmission"):
		"""ne (+d) and sw (-d)"""
		d = round(diag*_rt2, self.tol)
		if d not in self._xyplanes1:
			self._xyplanes1[d] = openmc.Plane(A=-1, B=1, D=d, boundary_type=bound)
		return self._xyplanes1[d]
	
	def get_xyplane2(self, diag, bound="transmission"):
		"""nw (+d) and se (-d)"""
		d = round(diag*_rt2, self.tol)
		if d not in self._xyplanes2:
			self._xyplanes2[d] = openmc.Plane(A=+1, B=1, D=d, boundary_type=bound)
		return self._xyplanes2[d]
	
	def get_octagon(self, r0, diag, innermost=False):
		r0 = round(r0, self.tol)
		#d = round(diag*_rt2, self.tol)
		d = round(diag, self.tol)
		w = self.get_xplane(-r0)
		e = self.get_xplane(+r0)
		s = self.get_yplane(-r0)
		n = self.get_yplane(+r0)
		ne = self.get_xyplane1(+d)
		nw = self.get_xyplane2(+d)
		sw = self.get_xyplane1(-d)
		se = self.get_xyplane2(-d)
		return shapes.Octagon((e, w, n, s, ne, nw, sw, se), innermost)
	
	def get_rectangle(self, r0, innermost=False):
		r0 = round(r0, self.tol)
		w = self.get_xplane(-r0)
		e = self.get_xplane(+r0)
		s = self.get_yplane(-r0)
		n = self.get_yplane(+r0)
		return shapes.Rectangle((e, w, n, s), innermost)
	
	def get_circle(self, r0, innermost=False):
		r0 = round(r0, self.tol)
		cyl = openmc.ZCylinder(R=r0)
		return shapes.Circle(cyl, innermost)
