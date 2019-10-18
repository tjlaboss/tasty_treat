# MOC Checkerboard
#
# Given the material tally results from OpenMC, take the cross sections
# and plug them into an MOC model

import openmoc
import openmoc.materialize
import openmc.openmoc_compatible
import openmc.mgxs as mgxs
import sys; sys.path.append("../..")

RUN = True
NGROUPS = 11
CMFD = True
FOLDER = "BATMAN/"
SOLVE_TYPE = "lsr"
STATEPOINT = FOLDER + "statepoint.100.h5"
sp = openmc.StatePoint(STATEPOINT)
geom = sp.summary.geometry

# Load the Monte Carlo results
fname = "material_lib_{}".format(NGROUPS)
material_lib = mgxs.Library.load_from_file(filename=fname, directory=FOLDER)
material_lib.load_from_statepoint(sp)

# Make an OpenMOC geometry
root_universe = openmc.openmoc_compatible.get_openmoc_universe(geom.root_universe)
moc_geom = openmoc.Geometry()
moc_geom.setRootUniverse(root_universe)

openmoc_materials = openmoc.materialize.load_openmc_mgxs_lib(material_lib, moc_geom)

if RUN:
	if CMFD:
		cmfd = openmoc.Cmfd()
		cmfd.setSORRelaxationFactor(1.5)
		cmfd.setLatticeStructure(2, 2)
		moc_geom.setCmfd(cmfd)
	
	# Generate tracks for OpenMOC
	moc_geom.initializeFlatSourceRegions()
	track_generator = openmoc.TrackGenerator(moc_geom, num_azim=128, azim_spacing=0.1)
	track_generator.generateTracks()
	print("Tracks generated!")
	
	# Run OpenMOC
	if SOLVE_TYPE == "fsr":
		solver = openmoc.CPUSolver(track_generator)
	elif SOLVE_TYPE == "lsr":
		solver = openmoc.CPULSSolver(track_generator)
	else:
		raise ValueError(SOLVE_TYPE)
	solver.computeEigenvalue()
	
	# Compute eigenvalue bias with OpenMC
	keff_mc = sp.k_combined[0]
	keff_moc = solver.getKeff()
	bias = (keff_moc - keff_mc)*1e5
	
	solver.printTimerReport()
	print("With nazim = {}, spacing = {} cm, and {} energy groups".format(
		track_generator.getNumAzim(), track_generator.getDesiredAzimSpacing(),
		NGROUPS))
	print('OpenMC keff:  {:1.6f} +/- {:1.6f}'.format(keff_mc, sp.k_combined[1]))
	print('OpenMOC keff: {:1.6f}'.format(keff_moc))
	print('OpenMOC bias: {:.0f} [pcm]'.format(bias))
	
