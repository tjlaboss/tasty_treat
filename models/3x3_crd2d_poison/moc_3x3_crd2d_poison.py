# MOC 3x3 Crd 2D, follower
#
# Control rods use the (old) B4C poison section

from build_3x3_crd2d_geometry import Crd2dPoisonBuilder
import sys; sys.path.append('../..')
import treat.moc.simulation

NRINGS = 3
LAT = 3
G = 25
SOLVE_TYPE = "fsr"
HOMOGENEOUS = False
MESHES = [(n*LAT, n*LAT) for n in treat.constants.DEFAULT_DIVISIONS]
MESH = MESHES[-1]
FUEL_DIV = (10, 10)
CRDB_DIV = (80, 80)
ONLY_MAKE_XML = False
RUN_MOC = True
SAVE_RESULTS = False
PLOT = False


# Build fresh instead of loading from summary
library = treat.materials.get_library("NRL")
builder = Crd2dPoisonBuilder(library)
geom = builder.get_core_geometry()

follower3x3 = treat.moc.StandardCase(geom, MESHES)
follower3x3.make_montecarlo_tallies(reactions=["fission"])

if ONLY_MAKE_XML:
	follower3x3.export_to_xml()
	print("OpenMC XML exported; exiting.")
	raise SystemExit

follower3x3.load_openmc_statepoint("statepoint.50.h5")

# Set individual element parameters
special_elements = {}
# Regular fuel
efuel = treat.moc.Element2D("Fuel 2D")
efuel.division = FUEL_DIV
efuel.add_cmm_corrections(treat.moc.cmm.CORRECTIONS[efuel.key][G])
special_elements[efuel.key] = efuel
# Crd element with follower
ecrdb = treat.moc.Element2D("Crd B4C 2D")
ecrdb.division = CRDB_DIV
ecrdb.crdrings = NRINGS
ecrdb.add_cmm_corrections(treat.moc.cmm.CORRECTIONS[ecrdb.key][G])
special_elements[ecrdb.key] = ecrdb

if RUN_MOC:
	sim = treat.moc.Simulation(follower3x3, G, SOLVE_TYPE, MESH, HOMOGENEOUS)
	sim.elements = special_elements
	sim.save_results = SAVE_RESULTS
	sim.plot = PLOT
	sim.run(nproc=4)

