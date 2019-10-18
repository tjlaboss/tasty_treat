# Base class for TREAT

import openmc
from treat.plots import Plots
import materials
import constants
from mesh import build_tallies


class BaseTREAT(object):
	"""Base class for all TREAT builders
	
	Parameters:
	-----------
	material_lib:   str; name of the material library to use.
	nndc_xs:        Boolean; I have no idea what this is for.
	
	Attributes:
	-----------
	mats:           MaterialLib;
	nndc_xs:        Boolean
	"""
	def __init__(self, material_lib, backup_lib=None, nndc_xs=False):
		self.mats = materials.get_library(material_lib)
		self.mats.backup_lib = materials.get_library(backup_lib)
		self.nndc_xs = nndc_xs
		
	
	def write_openmc_geometry(self):
		self.openmc_geometry.export_to_xml()
	
	def write_openmc_materials(self):
		materials_file = self.mats.toOpenmcMaterials()
		materials_file.export_to_xml()
	
	def write_openmc_plots(self):
		self.plots = Plots(self.mats)
		plot_file = openmc.Plots(self.plots.plots)
		plot_file.export_to_xml()
	
	def write_openmc_tallies(self):
		build_tallies(constants.ROOT_LATTICE, self.openmc_geometry)
