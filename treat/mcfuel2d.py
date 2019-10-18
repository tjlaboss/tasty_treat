# MC Fuel 2D
#
# 2D Minimum Critical Mass core builder, with fuel instead of crd channels
# Uses 4 types of elements:
# fuel, control rod fuel (with zircaloy-clad graphite follower),
# aluminum-clad dummies, and zirc-clad dummies

import numpy
import openmc
import elements
import constants
import common_layers
import treat_lattice
import materials


def get_core_lattice(manager, material_lib):
	# Must do this first to avoid using the reserved ID
	lat = treat_lattice.TreatLattice(constants.LATTICE_SIZE, material_lib)
	
	# TODO: Implement "edge fuel" and "edge reflector" --> subdivided element for cell tally
	
	# 2D active fuel element
	fuel_layer = common_layers.get_fuel_layer(manager, material_lib)
	fuel2d = elements.Element2D().fromLayer(fuel_layer).universe
	# 2D zirc-clad reflector element
	zr_dummy_layer = common_layers.get_zr_dummy_layer(manager, material_lib)
	zirc2d = elements.Element2D().fromLayer(zr_dummy_layer).universe
	# 2D aluminum-clad dummy element
	al_dummy_layer = common_layers.get_al_dummy_layer(manager, material_lib)
	alum2d = elements.Element2D().fromLayer(al_dummy_layer).universe
	
	lat.universes = numpy.array(
		 [[alum2d, alum2d, alum2d, alum2d, alum2d, alum2d, alum2d, alum2d, alum2d, alum2d, alum2d, alum2d, alum2d, alum2d, alum2d, alum2d, alum2d, alum2d, alum2d],
	      [alum2d, alum2d, alum2d, alum2d, alum2d, alum2d, alum2d, alum2d, alum2d, alum2d, alum2d, alum2d, alum2d, alum2d, alum2d, alum2d, alum2d, alum2d, alum2d],
	      [alum2d, alum2d, alum2d, alum2d, alum2d, alum2d, alum2d, alum2d, zirc2d, alum2d, zirc2d, alum2d, alum2d, alum2d, alum2d, alum2d, alum2d, alum2d, alum2d],
	      [alum2d, alum2d, alum2d, alum2d, alum2d, alum2d, fuel2d, fuel2d, fuel2d, zirc2d, fuel2d, fuel2d, fuel2d, alum2d, alum2d, alum2d, alum2d, alum2d, alum2d],
	      [alum2d, alum2d, alum2d, alum2d, zirc2d, fuel2d, fuel2d, fuel2d, fuel2d, fuel2d, fuel2d, fuel2d, fuel2d, fuel2d, zirc2d, alum2d, alum2d, alum2d, alum2d],
	      [alum2d, alum2d, alum2d, alum2d, fuel2d, fuel2d, fuel2d, fuel2d, fuel2d, fuel2d, fuel2d, fuel2d, fuel2d, fuel2d, fuel2d, alum2d, alum2d, alum2d, alum2d],
	      [alum2d, alum2d, alum2d, fuel2d, fuel2d, fuel2d, fuel2d, fuel2d, fuel2d, fuel2d, fuel2d, fuel2d, fuel2d, fuel2d, fuel2d, fuel2d, alum2d, alum2d, alum2d],
	      [alum2d, alum2d, alum2d, fuel2d, fuel2d, fuel2d, fuel2d, fuel2d, fuel2d, fuel2d, fuel2d, fuel2d, fuel2d, fuel2d, fuel2d, fuel2d, alum2d, alum2d, alum2d],
	      [alum2d, alum2d, zirc2d, fuel2d, fuel2d, fuel2d, fuel2d, fuel2d, fuel2d, fuel2d, fuel2d, fuel2d, fuel2d, fuel2d, fuel2d, fuel2d, zirc2d, alum2d, alum2d],
	      [alum2d, alum2d, alum2d, zirc2d, fuel2d, fuel2d, fuel2d, fuel2d, fuel2d, fuel2d, fuel2d, fuel2d, fuel2d, fuel2d, fuel2d, zirc2d, alum2d, alum2d, alum2d],
	      [alum2d, alum2d, zirc2d, fuel2d, fuel2d, fuel2d, fuel2d, fuel2d, fuel2d, fuel2d, fuel2d, fuel2d, fuel2d, fuel2d, fuel2d, fuel2d, zirc2d, alum2d, alum2d],
	      [alum2d, alum2d, alum2d, fuel2d, fuel2d, fuel2d, fuel2d, fuel2d, fuel2d, fuel2d, fuel2d, fuel2d, fuel2d, fuel2d, fuel2d, fuel2d, alum2d, alum2d, alum2d],
	      [alum2d, alum2d, alum2d, fuel2d, fuel2d, fuel2d, fuel2d, fuel2d, fuel2d, fuel2d, fuel2d, fuel2d, fuel2d, fuel2d, fuel2d, fuel2d, alum2d, alum2d, alum2d],
	      [alum2d, alum2d, alum2d, alum2d, fuel2d, fuel2d, fuel2d, fuel2d, fuel2d, fuel2d, fuel2d, fuel2d, fuel2d, fuel2d, fuel2d, alum2d, alum2d, alum2d, alum2d],
	      [alum2d, alum2d, alum2d, alum2d, zirc2d, fuel2d, fuel2d, fuel2d, fuel2d, fuel2d, fuel2d, fuel2d, fuel2d, fuel2d, zirc2d, alum2d, alum2d, alum2d, alum2d],
	      [alum2d, alum2d, alum2d, alum2d, alum2d, alum2d, fuel2d, fuel2d, fuel2d, zirc2d, fuel2d, fuel2d, fuel2d, alum2d, alum2d, alum2d, alum2d, alum2d, alum2d],
	      [alum2d, alum2d, alum2d, alum2d, alum2d, alum2d, alum2d, alum2d, zirc2d, alum2d, zirc2d, alum2d, alum2d, alum2d, alum2d, alum2d, alum2d, alum2d, alum2d],
	      [alum2d, alum2d, alum2d, alum2d, alum2d, alum2d, alum2d, alum2d, alum2d, alum2d, alum2d, alum2d, alum2d, alum2d, alum2d, alum2d, alum2d, alum2d, alum2d],
	      [alum2d, alum2d, alum2d, alum2d, alum2d, alum2d, alum2d, alum2d, alum2d, alum2d, alum2d, alum2d, alum2d, alum2d, alum2d, alum2d, alum2d, alum2d, alum2d]
		 ], dtype=openmc.Universe
	)
	return lat

if __name__ == "__main__":
	manager = elements.geometry.Manager()
	library = materials.get_library("NRL")
	mcm = get_core_lattice(manager, library)
	mcm.export_to_xml(bc="vacuum")
