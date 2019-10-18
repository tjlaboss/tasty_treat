# Single Element 2D
#
# Simplest model to test for OpenMOC compatability

import openmc
import openmc.mgxs as mgxs
import energy_groups
import elements
import materials
from common_layers import get_fuel_layer

man = elements.geometry.Manager()
matlib = materials.get_library("NRL")
fuel_layer = get_fuel_layer(man, matlib)
elem2d = elements.Element2D().fromLayer(fuel_layer)
elem2d.export_to_xml()

# Extract the geometry from an existing summary
summ = openmc.Summary("summary.h5")
geom = summ.geometry
material_lib = mgxs.Library(geom)

# MGXS group structure
groups = mgxs.EnergyGroups()
# Convert from MeV to eV
groups.group_edges = energy_groups.treat["11-group"].group_edges*1E6
material_lib.energy_groups = groups

# Make the library
mats = geom.get_all_materials()
material_lib.energy_groups = groups
material_lib.mgxs_types = ['total', 'fission', 'nu-fission', 'capture', 'chi', 'consistent nu-scatter matrix']
material_lib.domain_type = "material"
material_lib.domains = mats.values()
material_lib.by_nuclide = False
material_lib.correction = None

# Finish up
material_lib.build_library()
material_lib.dump_to_file("material_lib")
tallies_file = openmc.Tallies()
material_lib.add_to_tallies_file(tallies_file, merge=True)
tallies_file.export_to_xml()
