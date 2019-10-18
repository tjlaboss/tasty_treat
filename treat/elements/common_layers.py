# Common layers
#
# Layers that are common to multiple types of elements

from . import geometry
from .constants import elements as c

# Common octagons
def get_fuel_meat_octagon(manag, innermost=False):
	"""Octagon used in both fuel and control elements"""
	fo = manag.get_octagon(r0=c.fuel_or, diag=c.fuel_o_diag,
	                       innermost=innermost)
	return fo

def get_plug_refl_octagon(manag, innermost=False):
	"""Octagon used in upper & lower fuel plugs and aluminum dummies"""
	po = manag.get_octagon(r0=c.plug_or, diag=c.plug_o_diag,
	                       innermost=innermost)
	return po

def get_fuel_layer(manager, material_lib):
	air = material_lib["air"]
	# Fuel meat
	ring0 = get_fuel_meat_octagon(manager, innermost=True)
	ring0.fill = material_lib["fuel"]
	fuel_layer = geometry.Layer(manager, material_lib, ring0, outer_mat=air)
	# Gap
	fuel_layer.add_ring(air, "octagon", thick=c.zr_gap_thick)
	# Can
	zirc = material_lib["zirc3"]
	fuel_layer.add_ring(zirc, "octagon", thick=c.zr_clad_thick)
	fuel_layer.finalize()
	return fuel_layer

def get_plug_layer(manager, material_lib):
	"""Upper & lower fuel plugs"""
	air = material_lib["air"]
	# Inner graphite plug
	ring0 = get_plug_refl_octagon(manager, innermost=True)
	ring0.fill = material_lib["graphite"]
	plug_layer = geometry.Layer(manager, material_lib, ring0, outer_mat=air)
	# Gap
	plug_layer.add_ring(air, "octagon", thick=c.plug_gap_thick)
	# Can
	al = material_lib["al6063"]
	plug_layer.add_ring(al, "octagon", thick=c.plug_clad_thick)
	plug_layer.finalize()
	return plug_layer

def get_al_dummy_layer(manager, material_lib):
	"""Aluminum-Clad Dummy Assembly"""
	air = material_lib["air"]
	# Inner graphite plug
	ring0 = get_plug_refl_octagon(manager, innermost=True)
	ring0.fill = material_lib["graphite"]
	dummy_layer = geometry.Layer(manager, material_lib, ring0, outer_mat=air)
	# Gap
	dummy_layer.add_ring(air, "octagon", thick=c.plug_gap_thick)
	# Can - yes, this is a different aluminum than the plug
	al = material_lib["al1100"]
	dummy_layer.add_ring(al, "octagon", thick=c.al_clad_thick)
	dummy_layer.finalize()
	return dummy_layer

def get_zr_dummy_layer(manager, material_lib):
	"""Zircaloy-Clad Dummy Assembly"""
	air = material_lib["air"]
	# Graphite is of same dimensinos as fuel meat
	ring0 = get_fuel_meat_octagon(manager, innermost=True)
	ring0.fill = material_lib["graphite"]
	dummy_layer = geometry.Layer(manager, material_lib, ring0, outer_mat=air)
	# Gap
	dummy_layer.add_ring(air, "octagon", thick=c.zr_gap_thick)
	# Can
	zirc = material_lib["zirc3"]
	dummy_layer.add_ring(zirc, "octagon", thick=c.zr_clad_thick)
	dummy_layer.finalize()
	return dummy_layer


# test
if __name__ == "__main__":
	man = geometry.Manager()
	
	import materials
	matlib = materials.get_library("NRL")
	fl = get_fuel_layer(man, matlib)
	
	# 2d fuel element
	import element
	fe = element.Element2D().fromLayer(fl)
	fe.finalize()
	
	fe.export_to_xml()

