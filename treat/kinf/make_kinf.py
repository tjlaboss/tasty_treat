# Make kinf
#
# Analyze the fuel materials from different libraries

import numpy as np
import openmc
import os
import sys; sys.path.append("..")
import materials


def _get_fuel(library):
	try:
		fuel = library.get_material("fuel")
	except KeyError:
		fuel = library.get_material("fuel 7.6 ppm")
	return fuel

def get_geometry(fuel):
	root_cell = openmc.Cell(name="root cell")
	root_cell.fill = fuel
	w = openmc.XPlane(x0=-10, boundary_type="periodic")
	e = openmc.XPlane(x0=+10, boundary_type="periodic")
	s = openmc.YPlane(y0=-10, boundary_type="periodic")
	n = openmc.YPlane(y0=+10, boundary_type="periodic")
	b = openmc.ZPlane(z0=-10, boundary_type="periodic")
	t = openmc.ZPlane(z0=+10, boundary_type="periodic")
	root_cell.region = +w & -e & +s & -n & +b & -t
	root_universe = openmc.Universe(0, "root universe", [root_cell])
	g = openmc.Geometry()
	g.root_universe = root_universe
	return g

def get_materials(library):
	openmc_mats = library.toOpenmcMaterials()
	return openmc_mats

def get_settings():
	s = openmc.Settings()
	s.particles = int(1E6)
	s.batches = 100
	s.inactive = 25
	return s

def get_tallies(fuel):
	tallies = openmc.Tallies()
	tal1 = openmc.Tally()
	tal1.scores = ["absorption"]
	nucs = list(np.array(fuel.nuclides)[:,0])
	tal1.nuclides = nucs
	tallies.extend([tal1])
	return tallies
	

def export_to_xml(export_path, s, g, m, t=None):
	assert isinstance(s, openmc.Settings)
	assert isinstance(g, openmc.Geometry)
	assert isinstance(m, openmc.Materials)
	if t is not None:
		assert isinstance(t, openmc.Tallies)
		t.export_to_xml(export_path + "/tallies.xml")
	
	s.export_to_xml(export_path + "/settings.xml")
	g.export_to_xml(export_path + "/geometry.xml")
	m.export_to_xml(export_path + "/materials.xml")

def build_model(lib):
	matlib = materials.get_library(lib)
	if not os.path.isdir(lib):
		# Standard PermissionError is exactly what we want
		os.mkdir(lib)
	print("Exporting to:", lib)
	fuel = _get_fuel(matlib)
	
	# replace natural elements to nuclides
	# Note: I think this can be done with "fuel.get_nuclide_densities()"
	all_elements = fuel.elements[:]
	for el in all_elements:
		elem, etype, efrac = el[0:3]
		for nuc, nfrac, ntype in elem.expand(etype, efrac):
			fuel.add_nuclide(nuc, nfrac, ntype)
		fuel.remove_element(elem)
	
	mats = get_materials(matlib)
	sets = get_settings()
	geom = get_geometry(fuel)
	tals = get_tallies(fuel)

	export_to_xml(lib, sets, geom, mats, tals)
	
	# Extract the nuclide number densities
	fuel_atoms = fuel.get_nuclide_atom_densities()
	nuclide_results = np.array(list(fuel_atoms.values()))
	nuclides = np.array([n.name for n in nuclide_results[:, 0]])
	np.savetxt(lib + "/nuclides.txt", nuclides, fmt='%s')
	atom_dens = nuclide_results[:, 1]
	np.savetxt(lib + "/atom_dens.txt", atom_dens)
	atom_frac = atom_dens / atom_dens.sum()
	np.savetxt(lib + "/atom_frac.txt", atom_frac)
	

if __name__ == "__main__":
	build_model("Serpent")
