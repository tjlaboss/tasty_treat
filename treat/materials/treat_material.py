# Treat Material
#
# Module for the TreatMaterial on its own.

import openmc

class TreatMaterial(openmc.Material):
	"""Wrapper for OpenMC Material with two additional attributes,
	`key` and `color`

	This class exists for two reasons:

		First, to deal with compatability of more specific materials in some
		models than others. For instance, the INL Serpent model uses only
		a single Zircaloy composition for fuel elements, whereas the model
		built faithfully from the BATMAN report features both Zircaloy-3 and
		Zircaloy-4. One of these would appear under the key "zirc".
		This is also used for materials with long names, e.g.,
		"lead" will refer to "Lead that is actually Bismuth" from the Serpent deck.

		Second, to [...]
			--> TBD; may use indexing for different material impurities.

	Additional Attributes:
	----------------------
	key:        str, optional; key in the MaterialLib dictionary
	color:      list, optional; [R, G, B] color scheme for this material
	            in plots. Not yet implemented.
	"""
	def __init__(self, material_id=None, name='', temperature=None,
	             key="", color=None):
		if key:
			self.key = key.lower()
		else:
			self.key = name.lower()
		self.color = color
		super().__init__(material_id, name, temperature)
	
	# def __getitem__(self, item):
	#	return self.key + str(item)
	
	def __str__(self):
		return self.key
	
	def is_equivalent_to(self, other):
		"""Check if one material has the same key as another"""
		return self.key == other.key
