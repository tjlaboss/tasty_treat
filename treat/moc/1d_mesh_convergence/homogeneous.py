# Homogeneous
#
# 2-region problem with pure fuel and pure reflector

import openmc
from openmc import mgxs
import openmoc
import openmoc.plotter as plt
from params import *


G = 11
SOLVE_TYPE = "fsr"
PLOT = False
NPROC = 2
N = 5


# Define the OpenMOC materials
def get_material(mid, library):
	m = openmoc.Material()
	m.setNumEnergyGroups(G)
	transport = library.get_mgxs(mid, "nu-transport")
	fission = library.get_mgxs(mid, "fission")
	nufission = library.get_mgxs(mid, "nu-fission")
	nuscatter = library.get_mgxs(mid, "consistent nu-scatter matrix")
	chi = library.get_mgxs(mid, "chi")
	m.setSigmaS(nuscatter.get_xs().flatten())
	m.setSigmaT(transport.get_xs().flatten())
	m.setSigmaF(fission.get_xs().flatten())
	m.setNuSigmaF(nufission.get_xs().flatten())
	m.setChi(chi.get_xs().flatten())
	return m

sp = openmc.StatePoint(STATEPOINT)
lib = mgxs.Library.load_from_file(MATERIAL_LIBS[G], DATA_DIR)
lib.load_from_statepoint(sp)

fuel = get_material(FUEL_ID, lib)
graphite = get_material(REFL_ID, lib)


# Calculate the coordinates
north = openmoc.YPlane(YMAX)
south = openmoc.YPlane(YMIN)
east = openmoc.XPlane(XMAX)
west = openmoc.XPlane(XMIN)
for surf in (north, south, west):
	surf.setBoundaryType(openmoc.REFLECTIVE)
east.setBoundaryType(openmoc.VACUUM)

# Define the OpenMOC geometry
geom = openmoc.Geometry()
root_universe = openmoc.Universe(id=0)
divider = openmoc.XPlane(x=MIDDLE)
# Fuel block
fuel_cell = openmoc.Cell(name="Fuel")
fuel_cell.setFill(fuel)
fuel_cell.addSurface(-1, divider)
fuel_cell.addSurface(+1, west)
fuel_cell.addSurface(+1, south)
fuel_cell.addSurface(-1, north)
#fuel_universe = openmoc.Universe(name="Fuel block")
#fuel_universe.addCell(fuel_cell)
# Reflector block
refl_cell = openmoc.Cell(name="Reflector")
refl_cell.setFill(graphite)
refl_cell.addSurface(+1, divider)
refl_cell.addSurface(-1, east)
refl_cell.addSurface(+1, south)
refl_cell.addSurface(-1, north)
#refl_universe = openmoc.Universe(name="Reflector block")
#refl_universe.addCell(refl_cell)
# Root cell
#root_cell = openmoc.Cell("root cell")
#root_cell.setFill()
root_universe.addCell(fuel_cell)
root_universe.addCell(refl_cell)
geom.setRootUniverse(root_universe)
# Set up CMFD
if N > 0:
	cmfd = openmoc.Cmfd()
	nx = N*(HALF_FUEL + HALF_REFL)
	ny = N
	cmfd.setLatticeStructure(nx, ny)
	print("CMFD set to {}x{}".format(nx, ny))
	cmfd.setSORRelaxationFactor(1.5)
	cmfd.setKNearest(3)
	geom.setCmfd(cmfd)
# Generate tracks
geom.initializeFlatSourceRegions()
track_generator = openmoc.TrackGenerator(
	geom, num_azim=NAZIM, azim_spacing=DAZIM)
track_generator.setNumThreads(NPROC)
track_generator.generateTracks()
print("Tracks generated!")

if PLOT:
	plt.plot_flat_source_regions(geom)

if SOLVE_TYPE in {"flat", "fsr"}:
	solver = openmoc.CPUSolver(track_generator)
elif SOLVE_TYPE in {"linear", "lsr"}:
	solver = openmoc.CPULSSolver(track_generator)
else:
	raise NotImplementedError(SOLVE_TYPE)
solver.setNumThreads(NPROC)
solver.computeEigenvalue(max_iters=200)
solver.printTimerReport()

print("With nazim = {}, spacing = {} cm, and {} energy groups".format(
	track_generator.getNumAzim(),
	track_generator.getDesiredAzimSpacing(),
	G))
keff_moc = solver.getKeff()
print("N =", N)
print('OpenMOC keff: {:1.6f}'.format(keff_moc))
