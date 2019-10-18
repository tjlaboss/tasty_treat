# Simple 3x3 2D
#
# Simple lattice with one fuel element surrounded by 8 reflector elements
# The four courners are aluminum dummpy plugs, and the rest are zirc clad

import numpy
import openmc
import elements
import common_layers
import crd
import treat_lattice
import materials


man = elements.geometry.Manager()
matlib = materials.get_library("NRL")
# Must do this first to avoid using the reserved ID
lat = treat_lattice.TreatLattice(3, matlib)

# 2D active fuel element
fuel_layer = common_layers.get_fuel_layer(man, matlib)
fuel2d = elements.Element2D().fromLayer(fuel_layer).universe
# 2D zirc-clad reflector element
zr_dummy_layer = common_layers.get_zr_dummy_layer(man, matlib)
zr2d = elements.Element2D().fromLayer(zr_dummy_layer).universe
# 2D aluminum-clad dummy element
al_dummy_layer = common_layers.get_al_dummy_layer(man, matlib)
al2d = elements.Element2D().fromLayer(al_dummy_layer).universe
# 2D empty control rod layer
crd_empty_layer = crd.get_crd_fuel_layer(man, matlib, rod=None)
crd2d = elements.Element2D().fromLayer(crd_empty_layer).universe
# 2D zirc follower part of the control rod
crd_zirc_rod = crd.get_crd_zirc_follower_layer(man, matlib)
crd_filled_with_zirc = crd.get_crd_fuel_layer(man, matlib, rod=crd_zirc_rod)
zrfol = elements.Element2D().fromLayer(crd_filled_with_zirc).universe

lat.universes = numpy.array(
	[[al2d,   zr2d,  al2d],
	 [zr2d, fuel2d,  zr2d],
	 [al2d,  zrfol, crd2d]
	 ], dtype=openmc.Universe
)

lat.export_to_xml()

