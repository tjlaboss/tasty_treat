# Serpent Materials
#
# Material definitions for TREAT taken from the Idaho National Laboratory (INL)
# Serpent II models.

import os
import xml.etree.ElementTree as ET
from collections import OrderedDict
from .material_lib import MaterialLib
from .treat_material import TreatMaterial

_DIRNAME = os.path.dirname(os.path.realpath(__file__))
_FILENAME = _DIRNAME + "/nrl_materials.xml"
_KEYS = {
	20000 : "air",
	10002 : "b4c rod",
	10003 : "b4c rod old",
	20005 : "zirc",
	20008 : "aluminum",
	20009 : "steel",
	20010 : "concrete",
	20012 : "graphite",
	90000 : "fuel"
}

def get_nrl_library(materials_xml=_FILENAME):
	"""Generate a library of materials based on the MIT
	Nuclear Reactor Lab's model of TREAT.
	
	Note that the materials used in the Minimum Critical Mass model
	do not represent a complete set of all the possible materials in a
	TREAT model. Some more will be need to be added to 'nrl_materials.xml'
	and the _KEYS dictionary. Others are accessible by including the
	"backup" materials library.
	
	Parameter:
	----------
	materials_xml:  str, optional; absolute path to the materials.xml
					[Default: "materials/nrl_materials.xml"]

	Returns:
	--------
	MaterialLib()
	"""
	mats = OrderedDict()
	# Read the XML and extract the materials
	tree = ET.parse(materials_xml)
	for melem in tree.findall("material"):
		key = _KEYS[int(melem.attrib["id"])]
		new_mat = TreatMaterial(name=melem.attrib["name"], key=key)
		dens = melem.find("density")
		new_mat.set_density(dens.attrib["units"], float(dens.attrib["value"]))
		for nuc in melem.findall("nuclide"):
			a = float(nuc.attrib["ao"])
			new_mat.add_nuclide(nuc.attrib["name"], a, 'ao')
		for sab in melem.findall("sab"):
			frac = 1.0
			if "fraction" in sab.attrib:
				frac = float(sab.attrib["fraction"])
			new_mat.add_s_alpha_beta(sab.attrib['name'], frac)
		mats[key] = new_mat
	
	# Fill in the missing special materials
	for al in ("al1100", "al6061", "al6063"):
		mats[al] = mats["aluminum"]
	for zirc in range(2,4+1):
		mats["zirc{}".format(zirc)] = mats["zirc"]
	for boron in (5.9, 7.6):
		mats["graphite {} ppm".format(boron)] = mats["graphite"]
		mats["fuel {} ppm".format(boron)] = mats["fuel"]
	for steel in ("mild steel", "boron steel", "ss304"):
		mats[steel] = mats["steel"]
	
	
	# The product of this module is the object `nrl_materials`
	nrl_library = MaterialLib()
	for _key, _mat in mats.items():
		nrl_library.add_material(_mat, _key.lower())
	
	return nrl_library
