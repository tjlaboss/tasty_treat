# TREAT Materials
#
# Module containing classes for material libraries and wrappers
# for the TREAT builder

import openmc
from collections import OrderedDict
from warnings import warn
from .treat_material import TreatMaterial
from .colors import DEFAULT_COLORS

class MaterialLib(object):
	"""Container for sets of materials.
	
	This class is intended to be paired with a TREAT model builder,
	dispensing materials as needed. This avoids unnecessarily exporting
	materials not used in the model to the XML inputs. Once the model is
	completed, the user should run MaterialLib.toOpenmcMaterials()

	Parameters:
	-----------
	None
	
	Attributes:
	-----------
	backup_lib:         MaterialLib; library to use if materials are not found in this one.
	materials:          dictionary of all defined materials; {"key", TreatMaterial}
	openmc_materials:   dictionary of all used materials; {"key", TreatMaterial}
	"""
	
	def __init__(self):
		self._materials = {}
		self._openmc_materials = OrderedDict()
		self._backup_lib = None
		self.color_mapping = {}
	
	def __str__(self):
		rep = """MaterialLib
	Defined materials: {}
	OpenMC  materials: {}""".format(
			len(self._materials), len(self._openmc_materials))
		return rep
	
	def __getitem__(self, item):
		# Consider having this just run self.get_material(item)
		#return self._openmc_materials[item]
		return self.get_material(item.lower())
	
	def __iter__(self):
		for mat in self._openmc_materials.values():
			yield mat
	
	@property
	def materials(self):
		return self._materials
	
	@property
	def openmc_materials(self):
		return self._openmc_materials
	
	@property
	def backup_lib(self):
		return self._backup_lib
	
	@backup_lib.setter
	def backup_lib(self, lib):
		if lib:
			assert lib.backup_lib is not self
		self._backup_lib = lib
	
	def add_material(self, material, key=None):
		errstr = "Must be a TreatMaterial, not a {}."
		assert isinstance(material, TreatMaterial), \
			errstr.format(type(material))
		if not key:
			key = material.key
		if key not in self._materials:
			self._materials[key] = material
		else:
			errstr = "Material already exists: {}"
			raise KeyError(errstr.format(key))
	
	def get_material(self, key):
		if key not in self._openmc_materials:
			if key in self._materials:
				self._openmc_materials[key] = self._materials[key]
			else:
				if self._backup_lib:
					errstr = "Material {} not found; checking backup library."
					warn(errstr.format(key))
					self._openmc_materials[key] = self._backup_lib.get_material(key)
				else:
					errstr = "Undefined Material: {}"
					raise KeyError(errstr.format(key))
		mat = self._openmc_materials[key]
		# Handle color schemes for plotting
		if mat.color:
			self.color_mapping[mat] = mat.color
		elif key in DEFAULT_COLORS:
			self.color_mapping[mat] = DEFAULT_COLORS[key]
		return mat
	
	def toOpenmcMaterials(self):
		"""Once all of the materials needed in the model have been gotten,
		create the Materials() collection, ready to be exported to XML.
		
		Returns:
		--------
		Materials() instance populated with all of self.openmc_materials
		"""
		assert len(self.openmc_materials), \
			"MaterialLib is empty!"
		treatmats = openmc.Materials()
		for mat in self.openmc_materials.values():
			if mat not in treatmats:
				treatmats.append(mat)
		return treatmats

