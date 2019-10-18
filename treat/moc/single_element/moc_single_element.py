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

PLOT = True
RUN = True
CMFD = True
STATEPOINT = "statepoint_good.h5"
sp = openmc.StatePoint(STATEPOINT)

# Load in the element's geometry
geom = sp.summary.geometry
matcells = geom.get_all_material_cells()

# Load the Monte Carlo results
material_lib = mgxs.Library.load_from_file(filename="material_lib")
material_lib.load_from_statepoint(sp)

# Try to make an OpenMOC geometry
#root_universe = openmc.openmoc_compatible.get_openmoc_universe(geom.root_universe)
moc_element = openmoc.Universe(name="Fuel Element")

openmoc_materials = OrderedDict()
for dom in material_lib.domains:
	m = openmoc.Material()
	m.setNumEnergyGroups(material_lib.num_groups)
	m.setSigmaT(material_lib.get_mgxs(domain=dom, mgxs_type="total").get_pandas_dataframe()['mean'])
	m.setChi(material_lib.get_mgxs(domain=dom, mgxs_type="chi").get_pandas_dataframe()['mean'])
	m.setSigmaS(material_lib.get_mgxs(domain=dom, mgxs_type="consistent nu-scatter matrix").get_pandas_dataframe()['mean'])
	m.setNuSigmaF(material_lib.get_mgxs(domain=dom, mgxs_type="nu-fission").get_pandas_dataframe()['mean'])
	m.setSigmaF(material_lib.get_mgxs(domain=dom, mgxs_type="fission").get_pandas_dataframe()['mean'])
	openmoc_materials[dom.name] = m

for cid, matc in matcells.items():
	#c = openmoc.Cell()
	c = openmc.openmoc_compatible.get_openmoc_cell(matc)
	m = openmoc_materials[matc.fill.name]
	c.setFill(m)
	moc_element.addCell(c)

root_cell = openmoc.Cell(name="root cell")
root_cell.setFill(moc_element)

# fix this later
HPITCH = 10.16/2
min_x = openmoc.XPlane(x=-HPITCH)
max_x = openmoc.XPlane(x=+HPITCH)
min_y = openmoc.YPlane(y=-HPITCH)
max_y = openmoc.YPlane(y=+HPITCH)
surfs = [min_x, max_x, min_y, max_y]
for s in surfs:
	s.setBoundaryType(openmoc.REFLECTIVE)
root_cell.addSurface(+1, min_x)
root_cell.addSurface(-1, max_x)
root_cell.addSurface(+1, min_y)
root_cell.addSurface(-1, max_y)

# Build the root universe & geometry
root_universe = openmoc.Universe(name="root universe")
root_universe.addCell(root_cell)
moc_geom = openmoc.Geometry()
moc_geom.setRootUniverse(root_universe)

print(moc_geom.getAllMaterialCells())

# View FSRs
# Spatial discretization
cells = moc_geom.getAllMaterialCells()
#for c in cells:
#	cells[c].setNumSectors(8)
if PLOT:
	plt.plot_cells(moc_geom)
	plt.plot_materials(moc_geom)
if RUN:
	if CMFD:
		cmfd = openmoc.Cmfd()
		cmfd.setSORRelaxationFactor(1.5)
		#cmfd.setLatticeStructure(mesh.dimension[0], mesh.dimension[1])
		#cmfd.setGroupStructure([[1, 2, 3], [4, 5, 6, 7]])
		#cmfd.setGroupStructure((range(1,6), range(6,12)))
		#cmfd.setKNearest(3)
		moc_geom.setCmfd(cmfd)
	# Generate tracks for OpenMOC
	# note: increase num_azim and decrease azim_spacing for actual results (as for TREAT)
	#
	# good run:
	track_generator = openmoc.TrackGenerator(moc_geom, num_azim = 128, azim_spacing = 0.01)
	# quick run:
	#track_generator = openmoc.TrackGenerator(moc_geom, num_azim=16, azim_spacing=1)
	track_generator.generateTracks()
	print("Tracks generated!")
	
	if PLOT:
		plt.plot_flat_source_regions(moc_geom)
	# Run OpenMOC
	solver = openmoc.CPUSolver(track_generator)
	solver.computeEigenvalue()
	
	# Compute eigenvalue bias with OpenMC
	keff_mc = sp.k_combined[0]
	keff_moc = solver.getKeff()
	bias = (keff_moc - keff_mc)*1e5
	
	print('OpenMC keff:  {:1.6f} +/- {:1.6f}'.format(keff_mc, sp.k_combined[1]))
	print('OpenMOC keff: {:1.6f}'.format(keff_moc))
	print('OpenMOC bias: {:.0f} [pcm]'.format(bias))
