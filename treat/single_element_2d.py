# Single Element 2D
#
# Simplest model to test for OpenMOC compatability

import elements
from common_layers import get_fuel_layer
import materials

man = elements.geometry.Manager()
matlib = materials.get_library("NRL")
fuel_layer = get_fuel_layer(man, matlib)
elem2d = elements.Element2D().fromLayer(fuel_layer)
elem2d.export_to_xml()
