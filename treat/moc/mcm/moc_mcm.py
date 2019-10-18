# MOC Checkerboard
#
# Given the material tally results from OpenMC, take the cross sections
# and plug them into an MOC model

import openmoc
import openmoc.materialize
import openmc.openmoc_compatible
import openmoc.plotter as plt
import openmc.mgxs as mgxs
from collections import OrderedDict
import numpy as np

PLOT = True
RUN = True
CMFD = True
GRIDSIZE = 640*2
NGROUPS = 11
ISOTROPIC = True
# TODO: Re-generate these
if ISOTROPIC:
	STATEPOINT = "statepoint_iso_lab.h5"
else:
	STATEPOINT = "statepoint_aniso_lab.h5"
sp = openmc.StatePoint(STATEPOINT)

# Load in the element's geometry
geom = sp.summary.geometry
treat_lattice = geom.get_all_lattices()[10]
matcells = geom.get_all_material_cells()

# Load the Monte Carlo results
fname = "material_lib_{}".format(NGROUPS)
material_lib = mgxs.Library.load_from_file(filename=fname)
material_lib.load_from_statepoint(sp)

# Make an OpenMOC geometry
root_universe = openmc.openmoc_compatible.get_openmoc_universe(geom.root_universe)
moc_geom = openmoc.Geometry()
moc_geom.setRootUniverse(root_universe)

openmoc_materials = openmoc.materialize.load_openmc_mgxs_lib(material_lib, moc_geom)

# View FSRs
# Spatial discretization
cells = moc_geom.getAllMaterialCells()
for cid, cell in cells.items():
	#mkey = cell.getFillMaterial().getName() #.getId()
	#cell.setFill(openmoc_materials[mkey])
	# TODO: Make this discriminate by cell type/name, not fill
	if ("fuel" in cell.getFillMaterial().getName()) or ("graphite" in cell.getFillMaterial().getName()):
		cell.setNumSectors(8)
if PLOT:
	plt.plot_cells(moc_geom)
	plt.plot_materials(moc_geom, gridsize=GRIDSIZE)
if RUN:
	# TODO: Change OpenMC geometry such that entire geometry is a divisible me too
	# number of elemnent pitches
	NXY = 97
	if CMFD:
		cmfd = openmoc.Cmfd()
		cmfd.setSORRelaxationFactor(1.5)
		#cmfd.setLatticeStructure(mesh.dimension[0], mesh.dimension[1])
		cmfd.setLatticeStructure(NXY, NXY)
		#cmfd.setGroupStructure([[1, 2, 3], [4, 5, 6, 7]])
		#cmfd.setGroupStructure((range(1,7), range(7,12)))
		#cmfd.setKNearest(3)
		moc_geom.setCmfd(cmfd)
	
	# Create OpenMOC Mesh on which to tally fission rates
	moc_mesh = openmoc.process.Mesh()
	moc_mesh.dimension = treat_lattice.shape
	moc_mesh.lower_left  =  treat_lattice.lower_left
	moc_mesh.upper_right = -treat_lattice.lower_left
	moc_mesh.width = (moc_mesh.upper_right - moc_mesh.lower_left)/moc_mesh.dimension
	
	# Generate tracks for OpenMOC
	# note: increase num_azim and decrease azim_spacing for actual results (as for TREAT)
	#
	# good run:
	#track_generator = openmoc.TrackGenerator(moc_geom, num_azim=128, azim_spacing=0.1)
	# quick but less crappy run:
	track_generator = openmoc.TrackGenerator(moc_geom, num_azim=32, azim_spacing=0.1)
	# quick run:
	#track_generator = openmoc.TrackGenerator(moc_geom, num_azim=16, azim_spacing=1)
	track_generator.generateTracks()
	print("Tracks generated!")
	
	if PLOT:
		plt.plot_flat_source_regions(moc_geom, gridsize=GRIDSIZE)
		plt.plot_cells(moc_geom, gridsize=GRIDSIZE)
	# Run OpenMOC
	solver = openmoc.CPUSolver(track_generator)
	solver.computeEigenvalue()
	
	
	# Tally OpenMOC fission rates on the Mesh
	moc_fission_rates = np.array(moc_mesh.tally_fission_rates(solver))
	moc_fission_rates.shape = moc_mesh.dimension
	moc_fission_rates = np.fliplr(moc_fission_rates)
	# Save results
	np.savetxt("moc_data/moc_fission_rates", moc_fission_rates)
	
	# Also output your OpenMC fission rates for comparison
	fission_tally = sp.get_tally(name="mesh tally")
	vals = fission_tally.get_values(scores=["fission"])
	fission_rates = vals[:, 0, 0]
	fission_rates[fission_rates == 0] = np.nan
	fission_rates.shape = moc_mesh.dimension
	fission_rates /= np.nanmean(fission_rates)
	np.savetxt("moc_data/montecarlo_fission_rates", fission_rates)
	
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
	
	if PLOT:
		openmoc.plotter.plot_spatial_fluxes(solver, energy_groups=range(1,NGROUPS+1))
		openmoc.plotter.plot_energy_fluxes(solver, range(1,10+1))
