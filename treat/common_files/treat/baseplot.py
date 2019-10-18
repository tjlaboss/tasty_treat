# Base plot
#
# Base class for the individual models' plot classes

from collections import OrderedDict, Iterable
import openmc
import common_files.treat.constants as c
import sys; sys.path.append("../..")
from constants.colors import DEFAULT_COLORS


class BasePlot(object):
	""" Base class for TREAT plots
  
	Parameters:
	----------
	mats:       dictionary of instances of openmc.Material
	xwidth:     float; width of the plot in the x-direction
	ywidth:     float; width of the plot in the y-direction
	H:          float; total plottable height of the model
	"""
	
	def __init__(self, mats, xwidth, ywidth, H):
		self.lib = mats
		self._xwidth = xwidth
		self._ywidth = ywidth
		self._H = H
		
		print('Setting up the plots file. Note that the default resolution for rapid plot generation'
		      ' is insufficient to see all of the fine details of the fuel elements')
		
		self.plots = []
		self.color_mat = {}
		self._set_color()
		
		self.default_xy = OrderedDict({
			"midFuel"               : (c.fuel_ActiveFuel_bot + c.fuel_ActiveFuel_top)/2.0,
			"upperZrSpacer"         : (c.struct_UpperZrSpace_bot + c.struct_UpperZrSpace_top)/2.0,
			"upperGapSpacer"        : (c.struct_UpperZrSpace_top + c.struct_UpperGap_top)/2.0,
			"upperAlSpacer"         : (c.struct_UpperGap_top + c.struct_UpperAlSpace_top)/2.0,
			"upperOffgasSP"         : (c.struct_UpperAlSpace_top + c.struct_OffGas_top)/2.0,
			"upperCrimpSP"          : (c.struct_OffGas_top + c.struct_UpperCrimp_top)/2.0,
			"upperMachinedSP"       : (c.struct_UpperCrimp_top + c.struct_UpperShortPlug_mid)/2.0,
			"upperSP"               : (c.struct_UpperShortPlug_mid + c.struct_UpperShortPlug_top)/2.0,
			"upperLP"               : (c.struct_UpperShortPlug_top + c.struct_UpperLongPlug_top)/2.0,
			"upperStructuralGap"    : (c.struct_UpperLongPlug_top + c.struct_UpperReflec_top)/2.0,
			"upperStructuralFitting": (c.struct_UpperReflec_top + c.struct_upper_head_top)/2.0,
			"lowerZrSpacer"         : (c.struct_LowerGap_top + c.struct_LowerZrSpace_top)/2.0,
			"lowerGapSpacer"        : (c.struct_LowerAlSpace_top + c.struct_LowerGap_top)/2.0,
			"lowerAlSpacer"         : (c.struct_LowerShortPlug_top + c.struct_LowerAlSpace_top)/2.0,
			"lowerMachinedSP"       : (c.struct_LowerShortPlug_top + c.struct_LowerShortPlug_mid)/2.0,
			"lowerSP"               : (c.struct_LowerShortPlug_mid + c.struct_LowerLongPlug_top)/2.0,
			"lowerLP"               : (c.struct_LowerReflec_bot + c.struct_LowerLongPlug_top)/2.0,
			"lowerStructuralSupport": (c.struct_Support_bot + c.struct_LowerReflec_bot)/2.0,
		})
		
		self.default_xz = OrderedDict({})
		self.default_yz = OrderedDict({})
	
	def _set_color(self):
		"""If a material has a specified color, use it.
		Otherwise, apply the default color from constants.colors."""
		for key, mat in self.lib.openmc_materials.items():
			if mat.color:
				self.color_mat[mat] = mat.color
			elif key in DEFAULT_COLORS:
				self.color_mat[mat] = DEFAULT_COLORS[key]
	
	def _add_plots(self, xy_dict=None, xz_dict=None, yz_dict=None, res=1000):
		"""Add the plots that are common to most of the models.
	
		Parameters:
		-----------
		extra_radials:    dictionary of {name, height} for any additional radial plots
						  [Default: None]
		extra_axials:     dictionary of {name, height} for any additional axial plots
						  [Default: None]
		res:              int; plot resolution
						  [Default: 1000]
		"""
		xys = OrderedDict(self.default_xy)
		xzs = OrderedDict(self.default_xz)
		yzs = OrderedDict(self.default_yz)
		
		if isinstance(xy_dict, dict):
			xys.update(xy_dict)
		if isinstance(xz_dict, dict):
			xzs.update(xz_dict)
		if isinstance(yz_dict, dict):
			yzs.update(yz_dict)
		
		### Radial slice of the fuel region
		
		for name, z in xys.items():
			for plot_type in ("cell", "material"):
				p = openmc.Plot()
				p.color_by = plot_type
				p.filename = 'radial_{}s_{}'.format(plot_type, name)
				p.width = [self._xwidth, self._ywidth]
				p.pixels = [res, res]
				p.basis = 'xy'
				p.origin = _get_origin(z)
				if p.color_by == 'material':
					p.colors = self.color_mat
				self.plots.append(p)
		
		### Axial Slices
		# XZ
		for name, origin in xzs.items():
			for plot_type in ("cell", "material"):
				for stretch in ("", "_radially_stretched"):
					p = openmc.Plot()
					p.color_by = plot_type
					p.filename = 'axial_{}s_{}{}'.format(plot_type, name, stretch)
					if stretch:
						p.width = [self._xwidth, self._H]
					else:
						p.width = [self._H, self._H]
					p.pixels = [res, res]
					p.basis = 'xz'
					p.origin = _get_origin(origin)
					if p.color_by == 'material':
						p.colors = self.color_mat
					self.plots.append(p)
		# YZ
		for name, origin in yzs.items():
			for plot_type in ("cell", "material"):
				for stretch in ("", "_radially_stretched"):
					p = openmc.Plot()
					p.color_by = plot_type
					p.filename = 'axial_{}s_{}{}'.format(plot_type, name, stretch)
					if stretch:
						p.width = [self._ywidth, self._H]
					else:
						p.width = [self._H, self._H]
					p.pixels = [res, res]
					p.basis = 'yz'
					p.origin = _get_origin(origin)
					if p.color_by == 'material':
						p.colors = self.color_mat
					self.plots.append(p)


def _get_origin(value):
	"""Set the origin of a plot"""
	if isinstance(value, Iterable):
		return value
	else:
		return (0, 0, value)
