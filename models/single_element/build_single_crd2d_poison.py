# Build Single Element
#
# Create an OpenMC model of just a single rodded element (old B4C section)

import numpy
import openmc
import sys; sys.path.append('../..')
import treat
from treat.elements import crd


class SingleCrdPoisonBuilder(treat.CoreBuilder):
	def __init__(self, material_lib, name="Single Crd Element (poison)"):
		super().__init__(material_lib, 1, name)
		self.bc = ["reflective"]*4
	
	def _populate_core_lattice(self):
		# 2D b4c poison part of the control rod
		crd_b4c_rod = crd.get_crd_poision_section_layer(
			self.manager, self.material_lib, False)
		crd_filled_with_b4c = crd.get_crd_fuel_layer(
			self.manager, self.material_lib, rod=crd_b4c_rod)
		crdb2d = treat.elements.Element2D.fromLayer(crd_filled_with_b4c).universe
		crdb2d.name = "Crd B4C 2D"
		
		self.lattice.universes = numpy.array([[crdb2d]], dtype=openmc.Universe)
		self._lattice_is_populated = True


if __name__ == "__main__":
	library = treat.materials.get_library("NRL")
	crdb = SingleCrdPoisonBuilder(library)
	crdb.lattice.export_to_xml(crdb.bc, crdb.axially_finite)
