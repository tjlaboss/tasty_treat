# MCM 2D
#
# New 2D Minimum Critical Mass core builder
# Uses 4 types of elements:
# fuel, control rod fuel (with zircaloy-clad graphite follower),
# aluminum-clad dummies, and zirc-clad dummies

import numpy
import openmc
import elements
import constants
import common_layers
import crd
import treat_lattice
import materials


def get_core_lattice(manager, material_lib):
	# Must do this first to avoid using the reserved ID
	lat = treat_lattice.TreatLattice(constants.LATTICE_SIZE, material_lib)
	
	# 2D active fuel element
	fuel_layer = common_layers.get_fuel_layer(manager, material_lib)
	fuel2d = elements.Element2D().fromLayer(fuel_layer).universe
	# 2D zirc-clad reflector element
	zr_dummy_layer = common_layers.get_zr_dummy_layer(manager, material_lib)
	zirc2d = elements.Element2D().fromLayer(zr_dummy_layer).universe
	# 2D aluminum-clad dummy element
	al_dummy_layer = common_layers.get_al_dummy_layer(manager, material_lib)
	alum2d = elements.Element2D().fromLayer(al_dummy_layer).universe
	# 2D zirc follower part of the control rod
	crd_zirc_rod = crd.get_crd_zirc_follower_layer(manager, material_lib)
	crd_filled_with_zirc = crd.get_crd_fuel_layer(manager, material_lib, rod=crd_zirc_rod)
	crdz2d = elements.Element2D().fromLayer(crd_filled_with_zirc).universe
	
	lat.universes = numpy.array(
		 [[alum2d, alum2d, alum2d, alum2d, alum2d, alum2d, alum2d, alum2d, alum2d, alum2d, alum2d, alum2d, alum2d, alum2d, alum2d, alum2d, alum2d, alum2d, alum2d],
	      [alum2d, alum2d, alum2d, alum2d, alum2d, alum2d, alum2d, alum2d, alum2d, alum2d, alum2d, alum2d, alum2d, alum2d, alum2d, alum2d, alum2d, alum2d, alum2d],
	      [alum2d, alum2d, alum2d, alum2d, alum2d, alum2d, alum2d, alum2d, zirc2d, alum2d, zirc2d, alum2d, alum2d, alum2d, alum2d, alum2d, alum2d, alum2d, alum2d],
	      [alum2d, alum2d, alum2d, alum2d, alum2d, alum2d, fuel2d, fuel2d, fuel2d, zirc2d, fuel2d, fuel2d, fuel2d, alum2d, alum2d, alum2d, alum2d, alum2d, alum2d],
	      [alum2d, alum2d, alum2d, alum2d, zirc2d, fuel2d, fuel2d, fuel2d, fuel2d, fuel2d, fuel2d, fuel2d, fuel2d, fuel2d, zirc2d, alum2d, alum2d, alum2d, alum2d],
	      [alum2d, alum2d, alum2d, alum2d, fuel2d, fuel2d, fuel2d, crdz2d, fuel2d, fuel2d, fuel2d, crdz2d, fuel2d, fuel2d, fuel2d, alum2d, alum2d, alum2d, alum2d],
	      [alum2d, alum2d, alum2d, fuel2d, fuel2d, fuel2d, fuel2d, fuel2d, fuel2d, fuel2d, fuel2d, fuel2d, fuel2d, fuel2d, fuel2d, fuel2d, alum2d, alum2d, alum2d],
	      [alum2d, alum2d, alum2d, fuel2d, fuel2d, crdz2d, fuel2d, fuel2d, fuel2d, fuel2d, fuel2d, fuel2d, fuel2d, crdz2d, fuel2d, fuel2d, alum2d, alum2d, alum2d],
	      [alum2d, alum2d, zirc2d, fuel2d, fuel2d, fuel2d, fuel2d, fuel2d, fuel2d, fuel2d, fuel2d, fuel2d, fuel2d, fuel2d, fuel2d, fuel2d, zirc2d, alum2d, alum2d],
	      [alum2d, alum2d, alum2d, zirc2d, fuel2d, fuel2d, fuel2d, fuel2d, fuel2d, fuel2d, fuel2d, fuel2d, fuel2d, fuel2d, fuel2d, zirc2d, alum2d, alum2d, alum2d],
	      [alum2d, alum2d, zirc2d, fuel2d, fuel2d, fuel2d, fuel2d, fuel2d, fuel2d, fuel2d, fuel2d, fuel2d, fuel2d, fuel2d, fuel2d, fuel2d, zirc2d, alum2d, alum2d],
	      [alum2d, alum2d, alum2d, fuel2d, fuel2d, crdz2d, fuel2d, fuel2d, fuel2d, fuel2d, fuel2d, fuel2d, fuel2d, crdz2d, fuel2d, fuel2d, alum2d, alum2d, alum2d],
	      [alum2d, alum2d, alum2d, fuel2d, fuel2d, fuel2d, fuel2d, fuel2d, fuel2d, fuel2d, fuel2d, fuel2d, fuel2d, fuel2d, fuel2d, fuel2d, alum2d, alum2d, alum2d],
	      [alum2d, alum2d, alum2d, alum2d, fuel2d, fuel2d, fuel2d, crdz2d, fuel2d, fuel2d, fuel2d, crdz2d, fuel2d, fuel2d, fuel2d, alum2d, alum2d, alum2d, alum2d],
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
	mcm.export_to_xml()
