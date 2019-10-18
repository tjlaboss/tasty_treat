# Single Element 2D
#
# Simplest model to test for OpenMOC compatability

import openmc
import openmc.mgxs as mgxs
import energy_groups

ISOTROPIC = False

# Extract the geometry from an existing summary
summ = openmc.Summary("summary.h5")
geom = summ.geometry

mats = geom.get_all_materials().values()
materials_file = openmc.Materials(mats)
if ISOTROPIC:
	materials_file.make_isotropic_in_lab()
materials_file.export_to_xml()
#m = openmc.Material()
#m.get_nuclide_atom_densities()

material_11group_lib = mgxs.Library(geom)
material_25group_lib = mgxs.Library(geom)
material_70group_lib = mgxs.Library(geom)

# MGXS group structure
groups11 = mgxs.EnergyGroups()
groups25 = mgxs.EnergyGroups()
groups70 = mgxs.EnergyGroups()
# Convert from MeV to eV
groups11.group_edges = energy_groups.treat["11-group"].group_edges*1E6
groups25.group_edges = energy_groups.casmo["25-group"].group_edges*1E6
groups70.group_edges = energy_groups.casmo["70-group"].group_edges*1E6
material_11group_lib.energy_groups = groups11
material_25group_lib.energy_groups = groups25
material_70group_lib.energy_groups = groups70
all_group_libs = (material_11group_lib, material_25group_lib, material_70group_lib)

# Make the libraries
for group_lib in all_group_libs:
	if ISOTROPIC:
		group_lib.mgxs_types = ['total', 'fission', 'nu-fission', 'capture', 'chi', 'consistent nu-scatter matrix']
		group_lib.correction = False
	else:
		group_lib.mgxs_types = ['transport', 'fission', 'nu-fission', 'capture', 'chi', 'consistent nu-scatter matrix']
		group_lib.correction = "P0"
	group_lib.domain_type = "material"
	group_lib.domains = mats
	group_lib.by_nuclide = False
	group_lib.build_library()
	fname = "material_lib_{}".format(group_lib.num_groups)
	group_lib.dump_to_file(fname)

# We also want to tally the fission rates for comparison
lat = geom.get_all_lattices()[10]
mesh = openmc.Mesh()
mesh.lower_left  = +lat.lower_left
mesh.upper_right = -lat.lower_left
mesh.dimension = lat.shape
mesh_filter = openmc.MeshFilter(mesh)
fission_tally = openmc.Tally(name='mesh tally')
fission_tally.filters = [mesh_filter]
fission_tally.scores = ["fission"]

# Finish up
tallies_file = openmc.Tallies()
tallies_file.extend([fission_tally])
for group_lib in all_group_libs:
	group_lib.add_to_tallies_file(tallies_file)
tallies_file.export_to_xml()
