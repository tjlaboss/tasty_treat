# MOC Single Fuel Element
#
# One lonely little standard fuel element

from build_single_fuel2d import SingleFuelElementBuilder
import sys; sys.path.append('../..')
import treat.moc.simulation

LAT = 1
G = 25
SOLVE_TYPE = "fsr"
HOMOGENEOUS = True
MESHES = [(n*LAT, n*LAT) for n in treat.constants.DEFAULT_DIVISIONS]
MESH = MESHES[1]
FUEL_DIV = (10, 10)
ONLY_MAKE_XML = True
RUN_MOC = True
SAVE_RESULTS = False
PLOT = False


# Build fresh instead of loading from summary
library = treat.materials.get_library("NRL")
builder = SingleFuelElementBuilder(library)
geom = builder.get_core_geometry()

fuel2d = treat.moc.StandardCase(geom, MESHES)
fuel2d.make_montecarlo_tallies(reactions=["fission"])

if ONLY_MAKE_XML:
	fuel2d.export_to_xml()
	print("OpenMC XML exported; exiting.")
	raise SystemExit

fuel2d.load_openmc_statepoint("statepoint.50.h5")

# Set individual element parameters
efuel = treat.moc.Element2D("Fuel 2D")
efuel.division = FUEL_DIV
efuel.add_cmm_corrections(treat.moc.cmm.CORRECTIONS[efuel.key][G])
special_elements = {efuel.key : efuel}

if RUN_MOC:
	sim = treat.moc.Simulation(fuel2d, G, SOLVE_TYPE, MESH, HOMOGENEOUS)
	sim.elements = special_elements
	sim.save_results = SAVE_RESULTS
	sim.plot = PLOT
	sim.run(nproc=4)
