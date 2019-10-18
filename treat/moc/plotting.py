# Plotting
#
# A better plotting module for the MC/OpenMC manager

import os
import matplotlib.pyplot as plt
import numpy as np
from .constants import PITCH, HPITCH


def _slashed(directory):
	assert isinstance(directory, str)
	if directory[-1] != "/":
		directory += "/"
	return directory


def _get_mesh_name(mesh_shape, char="x"):
	return char.join(np.array(mesh_shape, dtype=str))


def _get_geneity(homogeneous):
	if homogeneous:
		return "homogeneous"
	else:
		return "heterogeneous"


def load_results(root, homogeneous, ngroups, mesh_shape, solver, rxn, g,
                 monte=False, dir_suffix="", het_suffix="", hom_suffix="", **kwargs):
	"""Load the reaction rates from disk
	
	Parameters:
	-----------
	root:           str; directory containing all the MOC results
	homogeneous:    bool; True: load the hom. results; False: load the het. results
	ngroups:        int; total number of energy groups
	mesh_shape:     tuple; mesh shape written as (nx, ny[, nz])
	solver:         str; "fsr" or "lsr"
	rxn:            str; reaction name (e.g., "fission" or "flux")
	g:              int; group number to return. indexed from 1.
	                To get an array of integrated reaction rates, use `g=0`
	                To get an array of all groups' reaction rates, use `g=-1`
	monte:          bool, optional; whether to load the Monte Carlo (not OpenMOC) results
	                [Default: False]
	dir_suffix:     str, optional; suffix to the directory (not including the underscore)
	het_suffix:     str, optional; suffix after `dir_suffix` to the heterogeneous directory
	                (not including the underscore)
	hom_suffix:     str, optional; suffix after `dir_suffix` to the homogeneous directory
	                (not including the underscore)
	                [Default: "" for all suffixes]
	
	Returns:
	--------
	np.array of the reaction rates --> if g == -1, then the last index is energy groups.
	"""
	assert g <= ngroups, "Group {} of {} does not exist.".format(g, ngroups)
	# Construct the path
	root = _slashed(root)
	solver = solver.lower()
	if solver in ("linear", "lsr"):
		solver = "lsr"
	elif solver in ("flat", "fsr"):
		solver = "fsr"
	else:
		raise NotImplementedError(solver)
	if dir_suffix:
		dir_suffix = "_" + dir_suffix
	if homogeneous and hom_suffix:
		dir_suffix += "_" + hom_suffix
	elif het_suffix:
		dir_suffix += "_" + het_suffix
	geneity = _get_geneity(homogeneous)
	mesh_name = _get_mesh_name(mesh_shape)
	path = root + "{geneity}/{ngroups}groups/cmfd{mesh_name}-{solver}{dir_suffix}/".format(**locals())
	assert os.path.isdir(path), "Path does not exist: {}".format(path)
	# Load and return the arrays
	if monte:
		code = "montecarlo"
	else:
		code = "moc"
	if g == 0:
		# Integrated
		fname = path + "{ngroups}groups_{code}_{rxn}_rates_{mesh_name}".format(**locals())
		return np.loadtxt(fname)
	elif g == -1:
		# All groups in a bigger array
		master_array = np.empty(shape = mesh_shape + (ngroups,))
		fmt = "{code}_{rxn}_{gp:02d}-of-{ngroups:02d}_{mesh_name}"
		for i in range(ngroups):
			gp = i + 1
			fname = path + fmt.format(**locals())
			master_array[..., i] = np.loadtxt(fname)
		return master_array
	else:
		# Single energy group
		fname = path + "{code}_{rxn}_{g:02d}-of-{ngroups:02d}_{mesh_name}".format(**locals())
		return np.loadtxt(fname)


def load_sph_results(root, ngroups, mesh_shape, solver, rxn, g, i,
                     monte=False, case_dir="", **kwargs):
	"""Load the reaction rates from disk
	"""
	
	assert g <= ngroups, "Group {} of {} does not exist.".format(g, ngroups)
	# Construct the path
	root = _slashed(root)
	solver = solver.lower()
	if solver in ("linear", "lsr"):
		solver = "lsr"
	elif solver in ("flat", "fsr"):
		solver = "fsr"
	else:
		raise NotImplementedError(solver)

	mesh_name = _get_mesh_name(mesh_shape)
	path = root + "sph_calcs/{ngroups}groups/{case_dir}/" \
	              "cmfd{mesh_name}-{solver}_iter{i:02d}/".format(**locals())
	assert os.path.isdir(path), "Path does not exist: {}".format(path)
	# Load and return the arrays
	if monte:
		code = "montecarlo"
	else:
		code = "moc"
	if g == 0:
		# Integrated
		fname = path + "{ngroups}groups_{code}_{rxn}_rates_{mesh_name}".format(**locals())
		return np.loadtxt(fname)
	elif g == -1:
		# All groups in a bigger array
		master_array = np.empty(shape=mesh_shape + (ngroups,))
		fmt = "{code}_{rxn}_{gp:02d}-of-{ngroups:02d}_{mesh_name}"
		for i in range(ngroups):
			gp = i + 1
			fname = path + fmt.format(**locals())
			master_array[..., i] = np.loadtxt(fname)
		return master_array
	else:
		# Single energy group
		fname = path + "{code}_{rxn}_{g:02d}-of-{ngroups:02d}_{mesh_name}".format(**locals())
		return np.loadtxt(fname)


def project_array(fine, coarse):
	"""Projects a coarse array on a finer array.
	The shapes of the two must be evenly divisible.
	Mesh must be uniform (i.e., have equal volumes/weights)

	Tested on:
	 * OpenMC fission rates 285 -> 95
	 * OpenMC fission rates 190 -> 95
	 * Arbitrary floating point matrix 4x4 -> 2x2

	Parameters:
	-----------
	fine:       array of floats; the array to project.
				Its shape must be an integer*(coarse.shape)
	coarse:     array of floats; the template array to project upon.
				Anyplace `coarse` has a NaN, one will be placed in the output.

	Returns:
	--------
	array of floats; values of `fine` projected down to the shape of `coarse`
	"""
	f = np.array(fine.shape)
	c = np.array(coarse.shape)
	assert (f // c == f / c).all(), "Meshes do not line up!"
	new = np.zeros(c)
	xratio, yratio = f // c
	for i in range(c[0]):
		for j in range(c[1]):
			tot = 0
			if np.isnan(coarse[i, j]):
				new[i, j] = np.nan
			else:
				for cmi in range(xratio):
					fmi = xratio * i + cmi
					for cmj in range(yratio):
						fmj = yratio * j + cmj
						add = fine[fmi, fmj]
						if not np.isnan(add):
							tot += add
				new[i, j] = tot
	new /= (xratio * yratio)
	return new


def get_min_and_max(list_of_arrays, absolute_magnitude=False, positive=False):
	all_nanmin = [np.nanmin(a) for a in list_of_arrays]
	all_nanmax = [np.nanmax(a) for a in list_of_arrays]
	emin = min(all_nanmin)
	emax = max(all_nanmax)
	if absolute_magnitude:
		emin, emax = min(emin, -emax), max(emax, -emin)
	if positive and emin < 0:
		emin = 0
	return emin, emax


def normalize_rates(arr, *args, eps=None) -> tuple:
	if eps is None:
		eps = np.nanmean(arr)
	scale = arr / np.nanmean(arr)
	indices = scale <= eps
	arr[indices] = np.nan
	arr /= np.nanmean(arr)
	for arg in args:
		arg[indices] = np.nan
		arg[arg <= eps] = np.nan
		arg /= np.nanmean(arg)
	return (arr,) + args


def make_many_plots(list_of_axes):
	'''
	if n == 2:
		axes = fig.subplots(1, 2)
	elif n < 5:
		axes = fig.subplots(2, 2)
	elif n < 7:
		axes = fig.subplots(2, 3)
	else:
		raise NotImplementedError("Number of plots: {}".format(n))
	'''
	fig = plt.figure()
	for ax in list_of_axes:
		print(type(ax))
		fig.add_subplot(ax)


def make_six_plots(mc, moc1, moc2, moc1name, moc2name, rxn,
                   cmin=None, cmax=None, emin=None, emax=None, **kwargs):
	"""Compare two MOC reaction rate distributions to OpenMC
	
	Plots will be laid out
	 ________________________________
	|          |          |          |
	|    mc    |   moc1   |   moc2   |
	|__________|__________|__________|
	|%err moc1 |%err moc1 |%err moc2 |
	| vs. moc2 |  vs. mc  |  vs. mc  |
	|__________|__________|__________|
	
	Parameters:
	-----------
	mc:         array; Monte Carlo reference reaction rates
	moc1:       array; MOC reaction rates, version 1
	moc2:       array; MOC reaction rates, version 2
	moc1name:   str;   brief title of MOC 1 (e.g., "11-group" or "homogeneous")
	moc2name:   str;   brief title of MOC 2 (e.g., "25-group" or "heterogeneous")
	rxn:        str;   reaction type (e.g., "Power" or "Group 2 Flux")
	
	cmin:       float, optional; minimum reaction rate for scale
	            [Default: None --> determine automatically]
	cmax:       float, optional; maximum reaction rate for scale
	            [Default: None --> determine automatically]
	emin:       float, optional; minimum error bar for scale
	            [Default: None --> determine automatically]
	emax:       float, optional; maximum error bar for scale
	            [Default: None --> determine automatically]
	
	Returns:
	--------
	fig:        matplotlib Figure
	six_axes:   tuple of the 6 matplotlib.axis.Axes instances
	"""
	# Get reaction rate colorbars
	_cmin, _cmax = get_min_and_max((mc, moc1, moc2), positive=True)
	if cmin is None:
		cmin = max(1 - max(1 - _cmin, _cmax - 1), 0)
	if cmax is None:
		cmax = 1 + max(_cmax - 1, 1 - _cmin)
	
	fig = plt.figure()
	# Plot the OpenMC reference solution in the upper left subplot
	axa = fig.add_subplot(231)
	a = plt.imshow(mc.squeeze(), interpolation="none", cmap="jet")
	plt.title("OpenMC {} Distribution".format(rxn))
	plt.clim(cmin, cmax)
	plt.colorbar(a)
	# Plot OpenMOC"s fission rates in the upper center subplot
	axb = fig.add_subplot(232)
	b = plt.imshow(moc1.squeeze(), interpolation="none", cmap="jet")
	plt.title("OpenMOC {} Distribution\n{}".format(rxn, moc1name))
	plt.clim(cmin, cmax)
	plt.colorbar(b)
	# Plot different OpenMOC fission rates in the upper right subplot
	axc = fig.add_subplot(233)
	c = plt.imshow(moc2.squeeze(), interpolation="none", cmap="jet")
	plt.title("OpenMOC {} Distribution\n{}".format(rxn, moc2name))
	plt.clim(cmin, cmax)
	plt.colorbar(c)
	
	# Get errors and their colorbars
	error11 = np.divide(moc1 - mc, mc / 100)
	error25 = np.divide(moc2 - mc, mc / 100)
	errorvs = np.divide(moc1 - moc2, moc2 / 100)
	
	_emin, _emax = get_min_and_max((error11, error25, errorvs))
	if emin is None:
		emin = min(_emin, -_emax)
	if emax is None:
		emax = max(_emax, -_emin)
		
	# Plot (MOC #1 vs. MOC #2) error in the lower left
	axd = fig.add_subplot(234)
	d = plt.imshow(errorvs.squeeze(), interpolation="none", cmap="rainbow")
	plt.title("% Relative error of {}\nvs {}".format(moc1name, moc2name))
	plt.clim(emin, emax)
	plt.colorbar(d)
	# Plot (MOC #1 vs. Monte Carlo) error in the lower center
	axe = fig.add_subplot(235)
	e = plt.imshow(error11.squeeze(), interpolation="none", cmap="rainbow")
	plt.title("% Relative error of {}\nvs openmc".format(moc1name))
	plt.clim(emin, emax)
	plt.colorbar(e)
	# Plot (MOC #2 vs. Monte Carlo) error in the lower right
	axf = fig.add_subplot(236)
	f = plt.imshow(error25.squeeze(), interpolation="none", cmap="rainbow")
	plt.title("% Relative error of {}\nvs openmc".format(moc2name))
	plt.clim(emin, emax)
	plt.colorbar(f)
	
	# implement mode and the rest later
	six_axes = (axa, axb, axc, axd, axe, axf)
	return fig, six_axes


def make_four_plots(img_file, mc, moc1, moc2, moc1name, moc2name, rxn, img_name,
                    lat=None, cmin=None, cmax=None, emin=None, emax=None, **kwargs):
	# Get reaction rate colorbars
	_cmin, _cmax = get_min_and_max((mc, moc1, moc2), positive=True)
	if cmin is None:
		cmin = max(1 - max(1 - _cmin, _cmax - 1), 0)
	if cmax is None:
		cmax = 1 + max(_cmax - 1, 1 - _cmin)
		
	# Get errors and their colorbars
	error11 = np.divide(moc1 - mc, mc/100)
	error25 = np.divide(moc2 - mc, mc/100)
	
	_emin, _emax = get_min_and_max((error11, error25))
	if emin is None:
		emin = min(_emin, -_emax)
	if emax is None:
		emax = max(_emax, -_emin)
	
	fig = plt.figure()
	# Show the geometry in the upper left
	axnw = fig.add_subplot(221)
	img_data = plt.imread(img_file)
	nw = plt.imshow(img_data)
	plt.title(img_name, fontsize=8)
	plt.xticks([], []); plt.yticks([], [])
	# Plot the OpenMC solution in the upper right
	axne = fig.add_subplot(222)
	ne = plt.imshow(mc.squeeze(), interpolation="none", cmap="jet")
	plt.title("OpenMC {} Distribution".format(rxn.title()), fontsize=8)
	plt.clim(cmin, cmax)
	plt.colorbar(ne)
	plt.xticks([], []); plt.yticks([], [])
	# Plot (MOC #1 vs. Monte Carlo) in the lower left
	axsw = fig.add_subplot(223)
	sw = plt.imshow(error11.squeeze(), interpolation="none", cmap="rainbow")
	plt.clim(emin, emax)
	plt.title("% Relative error of {}\nvs openmc".format(moc1name), fontsize=8)
	# Plot (MOC #2 vs. Monte Carlo) error in the lower right
	axse = fig.add_subplot(224)
	se = plt.imshow(error25.squeeze(), interpolation="none", cmap="rainbow")
	plt.title("% Relative error of {}\nvs openmc".format(moc2name), fontsize=8)
	plt.clim(emin, emax)
	plt.colorbar(se)
	
	# implement mode and the rest later
	four_axes = (axnw, axne, axsw, axse)
	plt.tight_layout()
	return fig, four_axes


def compare_group_structures(root, ngroups1, ngroups2, rxn, homogeneous, mesh_shape, solver,
                             normalize=False, eps=None, **kwargs):
	mc = load_results(root, homogeneous, ngroups1, mesh_shape, solver, rxn, 0,
	                  monte=True, **kwargs)
	moc1 = load_results(root, homogeneous, ngroups1, mesh_shape, solver, rxn, 0, **kwargs)
	moc2 = load_results(root, homogeneous, ngroups2, mesh_shape, solver, rxn, 0, **kwargs)
	if normalize:
		mc, moc1, moc2 = normalize_rates(mc, moc1, moc2, eps=eps)
	name1 = "{} groups".format(ngroups1)
	name2 = "{} groups".format(ngroups2)
	return make_six_plots(mc, moc1, moc2, name1, name2, rxn, **kwargs)


def compare_homogeneous_heterogeneous(root, ngroups, rxn, mesh_shape, solver, g,
                                      normalize=False, eps=None, **kwargs):
	assert g >= 0, "You may only plot a single energy group profile."
	mc      = load_results(root, False, ngroups, mesh_shape, solver, rxn, g,
	                       monte=True, **kwargs)
	moc_hom = load_results(root, True,  ngroups, mesh_shape, solver, rxn, g, **kwargs)
	moc_het = load_results(root, False, ngroups, mesh_shape, solver, rxn, g, **kwargs)
	if normalize:
		mc, moc_hom, moc_het = normalize_rates(mc, moc_hom, moc_het, eps=eps)
	hom_name = "homogeneous"
	het_name = "heterogeneous"
	if g > 0:
		suffix = " (group {})".format(g)
		hom_name += suffix
		het_name += suffix
	return make_six_plots(mc, moc_hom, moc_het, hom_name, het_name, rxn, **kwargs)


def compare_source_order(root, ngroups, rxn, homogeneous, mesh_shape, g,
                         normalize=False, eps=None, **kwargs):
	assert g >= 0, "You may only plot a single energy group profile."
	mc      = load_results(root, homogeneous, ngroups, mesh_shape, "fsr", rxn, g,
	                       monte=True, **kwargs)
	moc_fsr = load_results(root, homogeneous, ngroups, mesh_shape, "fsr", rxn, g, **kwargs)
	moc_lsr = load_results(root, homogeneous, ngroups, mesh_shape, "lsr", rxn, g, **kwargs)
	if normalize:
		mc, moc_fsr, moc_lsr = normalize_rates(mc, moc_fsr, moc_lsr, eps=eps)
	fsr_name = "FSR"
	lsr_name = "LSR"
	if g > 0:
		suffix = " (group {})".format(g)
		fsr_name += suffix
		lsr_name += suffix
	return make_six_plots(mc, moc_fsr, moc_lsr, fsr_name, lsr_name, rxn, **kwargs)


def compare_mesh_shapes(root, coarse_shape, fine_shape, homogeneous, ngroups, rxn, solver, g,
                        normalize=False, eps=None, **kwargs):
	assert g >= 0, "You may only plot a single energy group profile."
	mc     = load_results(root, homogeneous, ngroups, coarse_shape, solver, rxn, g,
	                      monte=True, **kwargs)
	fine   = load_results(root, homogeneous, ngroups,   fine_shape, solver, rxn, g, **kwargs)
	coarse = load_results(root, homogeneous, ngroups, coarse_shape, solver, rxn, g, **kwargs)
	fine = project_array(fine, coarse)
	if normalize:
		mc, fine, coarse = normalize_rates(mc, fine, coarse, eps=eps)
	name1 = _get_mesh_name(fine_shape)
	name2 = _get_mesh_name(coarse_shape)
	return make_six_plots(mc, fine, coarse, name1, name2, rxn, **kwargs)


def compare_sph_results(root, ngroups, solver, rxn, mesh_shape, g, case_dir, i, i0=0,
                        normalize=False, eps=None, **kwargs):
	assert g >= 0, "You may only plot a single energy group profile."
	mc   = load_sph_results(root, ngroups, mesh_shape, solver, rxn, g, i0,
	                        monte=True, case_dir=case_dir)
	sph0 = load_sph_results(root, ngroups, mesh_shape, solver, rxn, g, i0, case_dir=case_dir)
	sph1 = load_sph_results(root, ngroups, mesh_shape, solver, rxn, g, i,  case_dir=case_dir)
	if normalize:
		mc, sph0, sph1 = normalize_rates(mc, sph0, sph1, eps=eps)
	if i0 == 0:
		name0 = "(no SPH)"
	else:
		name0 = "(SPH iter {:02d})".format(i0)
	name1 = "(SPH iter {:02d})".format(i)
	if g > 0:
		suffix = " (group {})".format(g)
		name0 += suffix
		name1 += suffix
	return make_six_plots(mc, sph0, sph1, name0, name1, rxn, **kwargs)


def compare_sph_case_dirs(root, ngroups, solver, rxn, mesh_shape, g, case_dir1, case_dir2, i,
                          normalize=False, eps=None, **kwargs):
	assert g >= 0, "You may only plot a single energy group profile."
	mc   = load_sph_results(root, ngroups, mesh_shape, solver, rxn, g, i,
	                      monte=True, case_dir=case_dir1)
	sph1 = load_sph_results(root, ngroups, mesh_shape, solver, rxn, g, i, case_dir=case_dir1)
	sph2 = load_sph_results(root, ngroups, mesh_shape, solver, rxn, g, i, case_dir=case_dir2)
	if normalize:
		mc, sph1, sph2 = normalize_rates(mc, sph1, sph2, eps=eps)
	name1 = case_dir1
	name2 = case_dir2
	if g > 0:
		suffix = " (group {})".format(g)
		name1 += suffix
		name2 += suffix
	return make_six_plots(mc, sph1, sph2, name1, name2, rxn, **kwargs)


def compare_sph_group_structures(root, ngroups1, ngroups2, solver, rxn, mesh_shape, case_dir, i,
                                 normalize=False, eps=None, **kwargs):
	mc   = load_sph_results(root, ngroups1, mesh_shape, solver, rxn, 0, i,
	                      monte=True, case_dir=case_dir)
	sph1 = load_sph_results(root, ngroups1, mesh_shape, solver, rxn, 0, i, case_dir=case_dir)
	sph2 = load_sph_results(root, ngroups2, mesh_shape, solver, rxn, 0, i, case_dir=case_dir)
	if normalize:
		mc, sph1, sph2 = normalize_rates(mc, sph1, sph2, eps=eps)
	name1 = "{} groups".format(ngroups1)
	name2 = "{} groups".format(ngroups2)
	return make_six_plots(mc, sph1, sph2, name1, name2, rxn, **kwargs)


def compare_dir_suffix(root, suff1, suff2, homogeneous, ngroups, rxn, mesh_shape, solver, g,
                       normalize=False, eps=None, **kwargs):
	assert g >= 0, "You may only plot a single energy group profile."
	mc   = load_results(root, homogeneous, ngroups, mesh_shape, solver, rxn, g,
	                    monte=True, dir_suffix=suff1)
	moc1 = load_results(root, homogeneous, ngroups, mesh_shape, solver, rxn, g, dir_suffix=suff1)
	moc2 = load_results(root, homogeneous, ngroups, mesh_shape, solver, rxn, g, dir_suffix=suff2)
	if normalize:
		mc, moc1, moc2 = normalize_rates(mc, moc1, moc2, eps=eps)
	if g > 0:
		# suffix to the suffix :)
		suffix = " (group {})".format(g)
		suff1 += suffix
		suff2 += suffix
	return make_six_plots(mc, moc1, moc2, suff1, suff2, rxn, **kwargs)


def compare_hom_het_for_thesis(root, ngroups, rxn, mesh_shape, solver, g, img_file,
                               img_name="Geometry", normalize=False, eps=None, **kwargs):
	assert g >= 0, "You may only plot a single energy group profile."
	mc      = load_results(root, False, ngroups, mesh_shape, solver, rxn, g, monte=True, **kwargs)
	moc_hom = load_results(root, True,  ngroups, mesh_shape, solver, rxn, g, **kwargs)
	moc_het = load_results(root, False, ngroups, mesh_shape, solver, rxn, g, **kwargs)
	if normalize:
		mc, moc_hom, moc_het = normalize_rates(mc, moc_hom, moc_het, eps=eps)
	hom_name = "homogeneous"
	het_name = "heterogeneous"
	if g > 0:
		suffix = " (group {})".format(g)
		hom_name += suffix
		het_name += suffix
	fig, four_plots = make_four_plots(
		img_file, mc, moc_het, moc_hom, het_name, hom_name, rxn, img_name, **kwargs)
	plt.tight_layout()
	return fig, four_plots


def show():
	return plt.show()

