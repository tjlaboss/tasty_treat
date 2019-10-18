# Build Single Element
#
# Create an OpenMC model of just a single rodded element (graphite follower section)

import numpy
import openmc
import sys; sys.path.append('../..')
import treat
from treat.elements import crd


class SingleCrdFollowerBuilder(treat.CoreBuilder):
	def __init__(self, material_lib, name="Single Crd Element (follower)"):
		super().__init__(material_lib, 1, name)
		self.bc = ["reflective"]*4

	def _populate_core_lattice(self):
		# 2D graphite follower part of the control rod
		crd_graph_rod = crd.get_crd_zirc_follower_layer(self.manager, self.material_lib)
		crd_filled_with_graph = crd.get_crd_fuel_layer(
			self.manager, self.material_lib, rod=crd_graph_rod)
		crdz2d = treat.elements.Element2D.fromLayer(crd_filled_with_graph).universe
		crdz2d.name = "Crd Graphite 2D"
		
		self.lattice.universes = numpy.array([[crdz2d]], dtype=openmc.Universe)
		self._lattice_is_populated = True


if __name__ == "__main__":
	library = treat.materials.get_library("NRL")
	crdz = SingleCrdFollowerBuilder(library)
	crdz.lattice.export_to_xml(crdz.bc, crdz.axially_finite)
