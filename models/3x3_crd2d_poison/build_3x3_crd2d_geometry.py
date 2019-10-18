# 3x3 CRD (2D) Geometry
#
# Build a simple 3x3 geometry with a crd (B4C poison section) in the middle

import numpy
import openmc
import sys; sys.path.append('../..')
import treat


class Crd2dPoisonBuilder(treat.CoreBuilder):
	def __init__(self, material_lib, name=""):
		super().__init__(material_lib, 3, name)
		self.bc = ["reflective"]*4

	def _populate_core_lattice(self):
		# 2D active fuel element
		fuel_layer = treat.elements.common_layers.get_fuel_layer(
			self.manager, self.material_lib)
		fuel2d = treat.elements.Element2D.fromLayer(fuel_layer).universe
		fuel2d.name = "Fuel 2D"
		# 2D b4c poison part of the control rod
		crd_b4c_rod = treat.elements.crd.get_crd_poision_section_layer(
			self.manager, self.material_lib, new=False)
		crd_filled_with_b4c = treat.elements.crd.get_crd_fuel_layer(
			self.manager, self.material_lib, rod=crd_b4c_rod)
		crdb2d = treat.elements.Element2D.fromLayer(crd_filled_with_b4c).universe
		crdb2d.name = "Crd B4C 2D"
		
		self.lattice.universes = numpy.array(
			[[fuel2d, fuel2d, fuel2d],
			 [fuel2d, crdb2d, fuel2d],
			 [fuel2d, fuel2d, fuel2d]
			 ], dtype=openmc.Universe)
		self._lattice_is_populated = True


if __name__ == "__main__":
	library = treat.materials.get_library("NRL")
	builder = Crd2dPoisonBuilder(library)
	builder.lattice.export_to_xml(builder.bc, builder.axially_finite)

