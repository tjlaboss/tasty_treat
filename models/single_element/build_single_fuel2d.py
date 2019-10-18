# Build Single Element
#
# Create an OpenMC model of just a single lonely fuel element

import numpy
import openmc
import sys; sys.path.append('../..')
import treat


class SingleFuelElementBuilder(treat.CoreBuilder):
	def __init__(self, material_lib, name="Single Fuel Element"):
		super().__init__(material_lib, 1, name)
		self.bc = ["reflective"]*4
	
	def _populate_core_lattice(self):
		# 2D active fuel element
		fuel_layer = treat.elements.common_layers.get_fuel_layer(
			self.manager, self.material_lib)
		fuel2d = treat.elements.Element2D.fromLayer(fuel_layer).universe
		fuel2d.name = "Fuel 2D"
		
		self.lattice.universes = numpy.array([[fuel2d]], dtype=openmc.Universe)
		self._lattice_is_populated = True


if __name__ == "__main__":
	library = treat.materials.get_library("NRL")
	elem = SingleFuelElementBuilder(library)
	elem.lattice.export_to_xml(elem.bc, elem.axially_finite)
