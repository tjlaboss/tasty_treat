# MOC 3x3 Crd 2D, follower
#
# Control rods use the zirc-clad graphite follower section

from build_3x3_crd2d_geometry import Crd2DFollowerBuilder
import sys; sys.path.append('../..')
import treat

NRINGS = 3
LAT = 3
G = 25
SOLVE_TYPE = "fsr"
HOMOGENEOUS = True
MESHES = [(n*LAT, n*LAT) for n in treat.constants.DEFAULT_DIVISIONS]
MESH = MESHES[-1]
FUEL_DIV = (10, 10)
CRDZ_DIV = (20, 20)
ONLY_MAKE_XML = False
RUN_MOC = True
SAVE_RESULTS = True
PLOT = False


# Build fresh instead of loading from summary
library = treat.materials.get_library("NRL")
builder = Crd2DFollowerBuilder(library)
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
ecrdz = treat.moc.Element2D("Crd Graphite 2D")
ecrdz.division = CRDZ_DIV
ecrdz.crdrings = NRINGS
ecrdz.add_cmm_corrections(treat.moc.cmm.CORRECTIONS[ecrdz.key][G])
special_elements[ecrdz.key] = ecrdz


if RUN_MOC:
	sim = treat.moc.Simulation(follower3x3, G, SOLVE_TYPE, MESH, HOMOGENEOUS)
	sim.elements = special_elements
	sim.save_results = SAVE_RESULTS
	sim.plot = PLOT
	sim.run(nproc=4)
