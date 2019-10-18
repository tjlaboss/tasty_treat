# OpenMC MGXS
#
# Run OpenMC in MGXS mode to test the 2-region problem

import openmc
import openmc.stats
import openmc.mgxs as mgxs
import numpy as np
from params import *

G = 25
MGFILE = "MGXS.h5"

groups11 = openmc.mgxs.EnergyGroups()
groups11.group_edges = np.array(
     [1.000E-11, 2.00100E-08, 4.73020E-08, 7.64970E-08,
      2.09610E-07, 6.25000E-07, 8.100030E-06, 1.32700E-04,
      3.48110E-03, 1.15620E-01, 3.32870E+00, 2.00E+01])
groups25 = openmc.mgxs.EnergyGroups()
groups25.group_edges = np.array(
	[0., 0.03e-6, 0.058e-6, 0.14e-6, 0.28e-6,
	 0.35e-6, 0.625e-6, 0.972e-6, 1.02e-6,
	 1.097e-6, 1.15e-6, 1.855e-6, 4.e-6,
	 9.877e-6, 15.968e-6, 148.73e-6, 5.53e-3,
	 9.118e-3, 111.e-3, 500.e-3, 821.e-3,
	 1.353, 2.231, 3.679, 6.0655, 20.])
GROUPS = {11: groups11, 25: groups25}
energy_groups = GROUPS[G]


sp = openmc.StatePoint(STATEPOINT)
lib = mgxs.Library.load_from_file(MATERIAL_LIBS[G], DATA_DIR)
lib.load_from_statepoint(sp)

mg_library = openmc.MGXSLibrary(energy_groups)

def get_material(id, name, library):
	m = openmc.Material(id, name=name)
	data = openmc.XSdata(name, energy_groups)
	data.order = 0
	transport = library.get_mgxs(id, "nu-transport").get_xs()
	capture = library.get_mgxs(id, "capture").get_xs()
	fission = library.get_mgxs(id, "fission").get_xs()
	nufission = library.get_mgxs(id, "nu-fission").get_xs()
	nuscatter = library.get_mgxs(id, "consistent nu-scatter matrix").get_xs()
	nuscatter.shape = (G, G, 1)
	chi = library.get_mgxs(id, "chi").get_xs()
	absorption = capture + fission
	data.set_total(transport.squeeze())
	data.set_scatter_matrix(nuscatter)
	data.set_absorption(absorption.squeeze())
	data.set_fission(fission.squeeze())
	data.set_nu_fission(nufission.squeeze())
	data.set_chi(chi.squeeze())
	mg_library.add_xsdata(data)
	
	m.set_density('macro', 1)
	m.add_macroscopic(data.name)
	return m

# Create the materials xml
fuel = get_material(FUEL_ID, "fuel", lib)
graphite = get_material(REFL_ID, "graphite", lib)
mg_library.export_to_hdf5(MGFILE)
mats = openmc.Materials()
mats.append(fuel)
mats.append(graphite)
mats.cross_sections = MGFILE
mats.export_to_xml("multigroup/materials.xml")
# Create the geometry
geom = openmc.Geometry()
root_universe = openmc.Universe()
west = openmc.XPlane(x0=XMIN, boundary_type="reflective")
east = openmc.XPlane(x0=XMAX, boundary_type="vacuum")
north = openmc.YPlane(y0=YMAX, boundary_type="reflective")
south = openmc.YPlane(y0=YMIN, boundary_type="reflective")
top = openmc.ZPlane(z0=+5, boundary_type="reflective")
bot = openmc.ZPlane(z0=-5, boundary_type="reflective")
mid = openmc.XPlane(x0=MIDDLE)
# Fuel cell
fuel_block = openmc.Cell(name="Fuel")
fuel_block.fill = fuel
fuel_block.region = +west & +south & -north & -mid & +bot & -top
root_universe.add_cell(fuel_block)
# Reflector cell
graphite_block = openmc.Cell(name="Reflector")
graphite_block.fill = graphite
graphite_block.region = +mid & +south & -north & -east & +bot & -top
root_universe.add_cell(graphite_block)
# tie the geometry together
geom.root_universe = root_universe
geom.export_to_xml("multigroup/geometry.xml")
# Create the settings
s = openmc.Settings()
s.energy_mode = "multi-group"
s.particles = int(1E7)
s.batches = 50
s.inactive = 10
distribution = openmc.stats.Box(
	[XMIN, YMIN, -5], [MIDDLE, YMAX, +5], only_fissionable=True)
src = openmc.Source(space=distribution)
s.source = src
s.run_mode = "eigenvalue"
s.export_to_xml("multigroup/settings.xml")
