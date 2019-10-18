# CRD
#
#

from . import geometry
from . import common_layers
from . import constants as c


def first_crd_ring(manager, material_lib, tube_r, fill):
	if isinstance(fill, str):
		fill = material_lib[fill]
	channel = manager.get_cylinder(tube_r)
	ring0 = geometry.shapes.Circle(channel, fill=fill, innermost=True)
	return ring0


def get_crd_zirc_follower_layer(manager, material_lib):
	air = material_lib["air"]
	graphite = material_lib["graphite"]
	inner_cyl = manager.get_cylinder(c.rcca.active_r)
	# The graphite "meat"
	ring0 = geometry.shapes.Circle(inner_cyl, fill=graphite, innermost=True)
	ring0.name = "graphite follower <ROD>"
	zirc_follower = geometry.Layer(manager, material_lib, ring0, air)
	# Zircaloy-3 clad
	zr3 = material_lib["zirc3"]
	zirc_follower.add_ring(zr3, "circle", c.rcca.clad_thick)
	zirc_follower.finalize()
	return zirc_follower


def get_crd_poision_section_layer(manager, material_lib, new=False):
	"""
	
	Parameters:
	-----------
	manager
	material_lib
	new:            bool, optional; whether to use the denser, post-1967 b4c
	                composition instead of the one from 1960
	                [Default: False]
	"""
	air = material_lib["air"]
	if new:
		b4c = material_lib["b4c rod"]
	else:
		b4c = material_lib["b4c rod old"]
	inner_cyl = manager.get_cylinder(c.rcca.active_r)
	# The active B4C poison section
	ring0 = geometry.shapes.Circle(inner_cyl, fill=b4c, innermost=True)
	ring0.name = "B4C <ROD>"  # <ROD> denotes a cylindrical control rod
	poison_section = geometry.Layer(manager, material_lib, ring0, air)
	# Zircaloy-3 clad
	zr3 = material_lib["zirc3"]
	poison_section.add_ring(zr3, "circle", c.rcca.clad_thick)
	poison_section.finalize()
	return poison_section


def get_crd_fuel_layer(manager, material_lib, rod):
	"""
	
	Parameters:
	-----------
	manager
	material_lib
	rod:            openmc.Universe or openmc.Material;
					what to fill the control rod channel with.
					If nothing, it'll be filled with air.
	"""
	air = material_lib["air"]
	if not rod:
		rod = air
	elif isinstance(rod, geometry.Layer):
		rod = rod.universe
	ring0 = first_crd_ring(manager, material_lib, c.crd.tube_ir, rod)
	crd_fuel_layer = geometry.Layer(manager, material_lib, ring0, air)
	# Guide tube
	zirc = material_lib["zirc3"]
	crd_fuel_layer.add_ring(zirc, "circle", r=c.crd.tube_or)
	# Air gap between the tube and the fuel
	crd_fuel_layer.add_ring(air, "circle", r=c.crd.fuel_channel_r)
	# Fuel
	fuel = material_lib["fuel"]
	crd_fuel_layer.add_ring(fuel, "octagon",
	                        r=c.elements.fuel_or, d=c.elements.fuel_o_diag)
	crd_fuel_layer.add_ring(air, "octagon", thick=c.elements.zr_gap_thick)
	# Can
	crd_fuel_layer.add_ring(zirc, "octagon", thick=c.elements.zr_clad_thick)
	crd_fuel_layer.finalize()
	return crd_fuel_layer
	

def foo():
	pass
