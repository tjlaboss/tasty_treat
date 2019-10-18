# Plot Results
#
# Plotting module for the MC/OpenMC manager

import matplotlib.pyplot as plt
import numpy as np
from plotting import *

EMIN = -1.5
EMAX = +1.5

_MODES = ("show", "save", "return")
_MESHES = ["95x95", "190x190", "285x285", "380x380"]

def _check_params(directory, mesh_shape):
	assert isinstance(mesh_shape, str)
	dims = mesh_shape.split('x')
	array_shape = np.array([int(d) for d in dims])
	if directory[-1] != "/":
		directory += "/"
	return directory, array_shape


def _check_mode(mode):
	assert isinstance(mode, str), "mode must be a string."
	mode = mode.lower()
	assert mode in _MODES, "mode must be in: {}".format(_MODES)
	return mode


def get_normalization_factors(ngroups, mesh_shape, reaction, directory):
	"""Get the factor to re-normalize flux and reaction rates by

	Parameters:
	-----------
	ngroups:        int; number of energy groups
	mesh_shape:     str; name of the mesh shape
	reaction:       str; name of the reaction (e.g., "absorption")
	directory:      str; path to the data

	Returns:
	--------
	montecarlo_norm:    float; normalization factor for OpenMC results
	moc_norm:           float; normalization factor for OpenMOC results
	"""
	directory = _check_params(directory, mesh_shape)[0]
	
	montecarlo_norm = 0.0
	moc_norm = 0.0
	for g in range(ngroups):
		rates_name = "{}_{:02d}-of-{}_{}".format(
			reaction, g + 1, ngroups, mesh_shape)
		fname = directory + "montecarlo_" + rates_name
		montecarlo_reaction_rates = np.loadtxt(fname)
		montecarlo_norm += montecarlo_reaction_rates.sum()
		
		fname = directory + "moc_" + rates_name
		moc_reaction_rates = np.loadtxt(fname)
		moc_norm += moc_reaction_rates.sum()
	return montecarlo_norm, moc_norm


def plot_reaction_rates(ngroups, mesh_shape, reaction, directory, eps=1E-1, norms=(1, 1)):
	"""Plot the OpenMC and OpenMOC reaction rates, as well as
	the relative and absolute error of OpenMOC relative to OpenMC.

	Required Parameters:
	--------------------
	ngroups:        int; number of energy groups
	mesh_shape:     str; name of the mesh shape
	reaction:       str; name of the reaction (e.g., "absorption")
	directory:      str; path to the data

	Optional Parameters:
	--------------------
	eps:            float; fractional reaction rate threshold for cutoff
					Calculated relative to the average over the entire mesh
					tally at that energy group.
					Recommended to be 10-100% for reactions and 0 for flux.
					[Default: 0.1 --> i.e., 10%]

	norms:          iterable of floats with len=2: (norm_openmc, norm_OpenMOC);
					normalization factors for openmc and OpenMOC, respectively.
					The ENTIRE array (across ALL groups) will be divided
					by this factor, which can be gotten from the function
					`get_normalization_factors()` in this same module.
					[Default: (1, 1)]
	"""
	directory, shape = _check_params(directory, mesh_shape)
	montecarlo_norm, moc_norm = norms
	
	for g in range(ngroups):
		rates_name = "{}_{:02d}-of-{}_{}".format(reaction, g + 1, ngroups, mesh_shape)
		
		fname = directory + "montecarlo_" + rates_name
		montecarlo_reaction_rates = np.loadtxt(fname)
		montecarlo_reaction_rates /= montecarlo_norm
		
		scale = montecarlo_reaction_rates/np.nanmean(montecarlo_reaction_rates)
		indices = scale <= eps
		
		fname = directory + "moc_" + rates_name
		moc_reaction_rates = np.loadtxt(fname)
		# moc_reaction_rates = np.flipud(np.fliplr(moc_reaction_rates))
		moc_reaction_rates /= moc_norm
		
		# eventually, we want to load the Monte Carlo uncertainty here, too...
		
		# Then use these normalized arrays to calculate the relative error
		errors = np.divide(moc_reaction_rates - montecarlo_reaction_rates,
		                   montecarlo_reaction_rates/100.0)
		# PCM errors -- absolute error
		pcmerr = (moc_reaction_rates - montecarlo_reaction_rates)*1E5
		
		# Filter out extremely low values
		if eps:
			montecarlo_reaction_rates[indices] = np.NaN
			moc_reaction_rates[indices] = np.NaN
			errors[indices] = np.NaN
			pcmerr[indices] = np.NaN
		
		if reaction == "flux":
			descript = "Flux"
		else:
			descript = "{} Rates".format(reaction.title())
		descript += "\n(group {} of {})".format(g + 1, ngroups)
		
		plt.figure()
		# Plot OpenMC's fission rates in the left subplot
		plt.subplot(221)
		plt.imshow(montecarlo_reaction_rates.squeeze(), interpolation='none', cmap='jet')
		plt.title('OpenMC ' + descript)
		plt.colorbar()
		
		# Plot OpenMOC's fission rates in the right subplot
		plt.subplot(222)
		plt.imshow(moc_reaction_rates.squeeze(), interpolation='none', cmap='jet')
		plt.title('OpenMOC ' + descript)
		plt.colorbar()
		
		plt.subplot(223)
		pct = plt.imshow(errors.squeeze(), interpolation='none', cmap='jet')
		posmax = np.nanmax(errors)
		negmax = np.nanmin(errors)
		cmax = np.ceil(max(abs(posmax), abs(negmax)))
		plt.clim(-cmax, +cmax)
		plt.title('Percent error')
		plt.colorbar(pct)
		
		plt.subplot(224)
		pct = plt.imshow(pcmerr.squeeze(), interpolation='none', cmap='jet')
		posmax = np.nanmax(pcmerr)
		negmax = np.nanmin(pcmerr)
		cmax = np.ceil(max(abs(posmax), abs(negmax)))
		# plt.clim(-cmax, +cmax)
		plt.title('PCM error (absolute)')
		plt.colorbar(pct)
		
		plt.tight_layout()
		fname = directory + rates_name + "-plot.pdf"
		plt.savefig(fname)
		print("Figure saved to:", fname)
	# plt.show()


def plot_power(ngroups, mesh_shape, directory, mode="show"):
	"""Plot the integrated fission rates from OpenMC and OpenMOC, as well as
	the relative and absolute error of OpenMOC relative to OpenMC.

	Parameters:
	-----------
	ngroups:        int; number of energy groups
	mesh_shape:     str; name of the mesh shape
	directory:      str; path to the data
	"""
	mode = _check_mode(mode)
	directory, shape = _check_params(directory, mesh_shape)
	montecarlo_power = np.zeros(shape)
	moc_power = np.zeros(shape)
	
	# Integrate over all energy groups
	for g in range(ngroups):
		rates_name = "fission_{:02d}-of-{}_{}".format(g+1, ngroups, mesh_shape)
		
		fname = directory + "montecarlo_" + rates_name
		montecarlo_group_rates = np.loadtxt(fname)
		montecarlo_power += montecarlo_group_rates
		
		fname = directory + "moc_" + rates_name
		moc_group_rates = np.loadtxt(fname)
		moc_power += moc_group_rates
	
	# Filter out results that are essentially zero
	mc_mean = np.nanmean(montecarlo_power)*0.1
	indices = (montecarlo_power < mc_mean) + (moc_power < mc_mean)
	montecarlo_power[indices] = np.nan
	moc_power[indices] = np.nan
	# Normalize
	montecarlo_power /= np.nanmean(montecarlo_power)
	moc_power /= np.nanmean(moc_power)
	# Find the errors in the normalized distributions
	errors = np.divide(moc_power - montecarlo_power, montecarlo_power/100)
	pcmerr = (moc_power - montecarlo_power)*100
	
	if mode == "return":
		return montecarlo_power, moc_power, errors, pcmerr
	
	# Plot OpenMC's fission rates in the upper left subplot
	plt.subplot(231)
	plt.imshow(montecarlo_power.squeeze(), interpolation='none', cmap='jet')
	plt.title('OpenMC Power Distribution\n{} groups'.format(ngroups))
	cmin = min(np.nanmin(montecarlo_power), np.nanmin(moc_power))
	cmax = max(np.nanmax(montecarlo_power), np.nanmax(moc_power))
	plt.clim(cmin, cmax)
	plt.colorbar()
	
	# Plot OpenMOC's fission rates in the upper right subplot
	plt.subplot(232)
	plt.imshow(moc_power.squeeze(), interpolation='none', cmap='jet')
	plt.title('OpenMOC Power Distribution\n{} groups'.format(ngroups))
	plt.clim(cmin, cmax)
	plt.colorbar()
	
	# Plot the relative error in the lower left subplot
	plt.subplot(233)
	pct = plt.imshow(errors.squeeze(), interpolation='none', cmap='jet')
	posmax = np.nanmax(errors)
	negmax = np.nanmin(errors)
	cmax = np.ceil(max(abs(posmax), abs(negmax)))
	plt.clim(-cmax, +cmax)
	plt.title('Relative error (%)')
	plt.colorbar(pct)
	
	# Plot the absolute error in the lower right subplot
	plt.subplot(234)
	pct = plt.imshow(pcmerr.squeeze(), interpolation='none', cmap='jet')
	posmax = np.nanmax(pcmerr)
	negmax = np.nanmin(pcmerr)
	cmax = np.ceil(max(abs(posmax), abs(negmax)))
	plt.clim(-cmax, +cmax)
	plt.title('Absolute error (%)')
	plt.colorbar(pct)
	
	if mode == "show":
		plt.show()
	elif mode == "save":
		# Save and/or show the plot
		plt.tight_layout()
		fname = directory + "power_{}-groups.pdf".format(ngroups)
		plt.savefig(fname)
		print("Figure saved to:", fname)
	return montecarlo_power, moc_power, errors, pcmerr


def compare_moc_rates(mesh_shape, montecarlo_coarse, moc_coarse, moc1, moc2,
                      compare_against_mc=False, ebars=False):
	"""Compare a reaction rate with the coarsest MOC tally  (or OpenMC tally)
	
	Designed for the comparison of the 190x190 and 285x285 with the 95x95.
	The two finer distributions (moc1 and moc2) are projected onto an array
	in the shape of `moc_coarse`
	
	Parameters:
	-----------
	mesh_shape:         str; name of the shape of the mesh
	montecarlo_coarse:  array of floats; coarse mesh openmc  solution
	moc_coarse:         array of floats; coarse mesh OpenMOC solution
	moc1:               array of floats;  finer mesh OpenMOC solution
	moc2:               array of floats; finest mesh OpenMOC solution
	
	Optional parameters:
	(all False by default)
	--------------------
	compare_against_mc: Boolean; whether to compare against montecarlo_coarse
						instead of against the coarsest MOC tally
	ebars:              Boolean; whether to use the global color scheme for
						plotting errors. Useful for consistency across plots.
	
	"""
	shape = _check_params("none/", mesh_shape)[1]
	assert (montecarlo_coarse.shape == moc_coarse.shape == shape).all(), \
		"Reference shapes do not match."
	coarse_mocs = [np.zeros(shape), np.zeros(shape)]
	for k, moc_array in enumerate((moc1, moc2)):
		if moc_array is None:
			continue
		elif moc_array.shape == moc_coarse:
			coarse_mocs[k][:,:] = moc1
		else:
			# project
			coarse_mocs[k][:,:] = project_array(moc_array, moc_coarse)
			coarse_mocs[k][:,:] /= np.nanmean(coarse_mocs[k][:,:])
	
	# Plot stuff
	plt.figure()
	# Plot OpenMOC's fission rates in the upper left subplot
	plt.subplot(231)
	a = plt.imshow(moc_coarse.squeeze(), interpolation='none', cmap='jet')
	plt.title('OpenMOC Power Distribution\n{}'.format(moc_coarse.shape))
	cmin = min(np.nanmin(montecarlo_coarse), np.nanmin(moc_coarse),
	           np.nanmin(coarse_mocs[0]),    np.nanmin(coarse_mocs[1]))
	cmax = max(np.nanmax(montecarlo_coarse), np.nanmax(moc_coarse),
	           np.nanmax(coarse_mocs[0]),    np.nanmin(coarse_mocs[1]))
	plt.clim(cmin, cmax)
	plt.colorbar(a)
	
	# Plot OpenMC's fission rates in the lower left subplot
	plt.subplot(234)
	b = plt.imshow(montecarlo_coarse.squeeze(), interpolation='none', cmap='jet')
	plt.title('OpenMC Power Distribution\n{}'.format(mesh_shape))
	plt.clim(cmin, cmax)
	plt.colorbar(b)
	
	# Get errors and their colorbars
	if compare_against_mc:
		reference = montecarlo_coarse
		against = "OpenMC"
	else:
		reference = moc_coarse
		against = "MOC"
	error1 = np.divide(coarse_mocs[0] - reference, reference/100)
	error2 = np.divide(coarse_mocs[1] - reference, reference/100)
	if ebars:
		emin = EMIN
		emax = EMAX
	else:
		emin = min(np.nanmin(error1), np.nanmin(error2))
		emax = max(np.nanmax(error1), np.nanmax(error2))
		
	# projection of moc1 (190x190 I think)
	plt.subplot(232)
	c = plt.imshow(coarse_mocs[0].squeeze(), interpolation='none', cmap='jet')
	plt.title('OpenMOC {}'.format(moc1.shape))
	plt.clim(cmin, cmax)
	plt.colorbar(c)
	# Plot the relative error in the projection of the finer mesh
	plt.subplot(235)
	d = plt.imshow(error1.squeeze(), interpolation='none', cmap='rainbow')
	plt.title('% Relative error of {}\nvs {} {}'.format(moc1.shape, against, moc_coarse.shape))
	plt.clim(emin, emax)
	plt.colorbar(d)
	
	# projection of moc2 (285x285 I think)
	plt.subplot(233)
	e = plt.imshow(coarse_mocs[1].squeeze(), interpolation='none', cmap='jet')
	plt.title('OpenMOC {}'.format(moc2.shape))
	plt.clim(cmin, cmax)
	plt.colorbar(e)
	# Plot the relative error in the projection of the finest mesh
	plt.subplot(236)
	f = plt.imshow(error2.squeeze(), interpolation='none', cmap='rainbow')
	plt.title('% Relative error of {}\nvs {} {}'.format(moc2.shape, against, moc_coarse.shape))
	plt.clim(emin, emax)
	plt.colorbar(f)
	
	# implement mode and the rest
	plt.show()
	
	
def compare_moc_across_groups(mc, moc11, moc25, mesh_name, ebar=False):
	assert (mc.shape == moc11.shape == moc25.shape)
	mc /= np.nanmean(mc)
	moc11 /= np.nanmean(moc11)
	moc25 /= np.nanmean(moc25)
	cmin = min(np.nanmin(mc), np.nanmin(moc11), np.nanmin(moc25))
	cmax = max(np.nanmax(mc), np.nanmax(moc11), np.nanmax(moc25))
	
	# Plot stuff
	plt.figure()
	
	# Plot OpenMOC's 11-group fission rates in the upper left subplot
	plt.subplot(231)
	a = plt.imshow(moc11.squeeze(), interpolation='none', cmap='jet')
	plt.title('OpenMOC Power Distribution\n11 Groups {}'.format(mesh_name))
	plt.clim(cmin, cmax)
	plt.colorbar(a)
	# Plot OpenMOC's 25-group fission rates in the upper center subplot
	plt.subplot(232)
	b = plt.imshow(moc25.squeeze(), interpolation='none', cmap='jet')
	plt.title('OpenMOC Power Distribution\n25 groups {}'.format(mesh_name))
	plt.clim(cmin, cmax)
	plt.colorbar(b)
	# Plot OpenMC's continuous-energy fission rates in the upper right subplot
	plt.subplot(233)
	c = plt.imshow(mc.squeeze(), interpolation='none', cmap='jet')
	plt.title('OpenMC Power Distribution\n{}'.format(mesh_name))
	plt.clim(cmin, cmax)
	plt.colorbar(c)
	
	# Get errors and their colorbars
	error11 = np.divide(moc11 - mc, mc/100)
	error25 = np.divide(moc25 - mc, mc/100)
	errorvs = np.divide(moc11 - moc25, moc25/100)
	if ebar:
		emin = EMIN
		emax = EMAX
	else:
		_emin, _emax = get_min_and_max((error11, error25, errorvs))
		emin = min(_emin, -_emax)
		emax = max(_emax, -_emin)
	
	# Plot (11-group vs. Monte Carlo) error in the lower left
	plt.subplot(234)
	b = plt.imshow(moc11.squeeze(), interpolation='none', cmap='rainbow')
	plt.title('% Relative error of 11-group\nvs openmc')
	plt.clim(emin, emax)
	plt.colorbar(b)
	# Plot (25-group vs. Monte Carlo) error in the lower center
	plt.subplot(235)
	e = plt.imshow(moc25.squeeze(), interpolation='none', cmap='rainbow')
	plt.title('% Relative error of 25-group\nvs openmc')
	plt.clim(emin, emax)
	plt.colorbar(e)
	# Plot (11-group vs. 25-group) error in the lower right
	plt.subplot(236)
	f = plt.imshow(moc25.squeeze(), interpolation='none', cmap='rainbow')
	plt.title('% Relative error of 11-group\nvs 25-group')
	plt.clim(emin, emax)
	plt.colorbar(f)
	
	# implement mode and the rest later
	plt.show()


def compare_geneity(ngroups, mesh_shape, solve_type, core,
                    condense=True, ebar=False):
	solve_type = solve_type.lower()
	core = core.lower()
	assert core in {"same", "interface"}
	suffix = "moc_fission_rates_{}".format(mesh_shape)
	hom_folder = "inl_mcfuel/homogeneous/{}/{}groups/universe_{}_{}/".\
		format(core, ngroups, mesh_shape, solve_type)
	hom_file = hom_folder + suffix
	het_folder = "inl_mcfuel/heterogeneous/{}/{}groups/cell_{}_{}/".\
		format(core, ngroups, mesh_shape, solve_type)
	het_file = het_folder + suffix
	#fold = "_{}_{}/moc_fission_rates_{}".format(mesh_shape, SOLVE_TYPE, mesh_shape)
	
	if condense:
		fname = "inl_mcfuel/montecarlo_19x19"
	else:
		fname = "inl_mcfuel/montecarlo_{}".format(mesh_shape)
	montecarlo = normalize_rates(np.loadtxt(fname))
	indices = np.isnan(montecarlo)
	
	if condense:
		moc_hom = project_array(np.loadtxt(hom_file), montecarlo)
		moc_het = project_array(np.loadtxt(het_file), montecarlo)
	else:
		moc_hom = np.loadtxt(hom_file)
		moc_het = np.loadtxt(het_file)
		
	moc_hom[indices] = np.nan
	moc_het[indices] = np.nan
	moc_hom /= np.nanmean(moc_hom)
	moc_het /= np.nanmean(moc_het)
	
	# Get color schemes
	cmin = min(np.nanmin(montecarlo), np.nanmin(moc_hom), np.nanmin(moc_het))
	cmax = max(np.nanmax(montecarlo), np.nanmax(moc_hom), np.nanmax(moc_het))
	error_hom = np.divide(moc_hom - montecarlo, montecarlo/100)
	error_het = np.divide(moc_het - montecarlo, montecarlo/100)
	error_moc = np.divide(moc_hom - moc_het, moc_het/100)
	if ebar:
		emin = EMIN
		emax = EMAX
	else:
		emin, emax = get_min_and_max((error_hom, error_het, error_moc))
	
	plt.figure()
	# Plot OpenMC's power distribution in the
	plt.subplot(231)
	a = plt.imshow(montecarlo.squeeze(), interpolation='none', cmap='jet')
	plt.title('OpenMC Power Distribution\nReference')
	plt.clim(cmin, cmax)
	plt.colorbar(a)
	# Plot OpenMOC's heterogeneous fission rates in the upper center subplot
	plt.subplot(232)
	b = plt.imshow(moc_het.squeeze(), interpolation='none', cmap='jet')
	plt.title('OpenMOC, Heterogeneous, {}\n{} groups {}'.format(solve_type, ngroups, mesh_shape))
	plt.clim(cmin, cmax)
	plt.colorbar(b)
	# Plot OpenMOC's homogeneous fission rates in the upper right subplot
	plt.subplot(233)
	c = plt.imshow(moc_hom.squeeze(), interpolation='none', cmap='jet')
	plt.title('OpenMOC, Homogeneous, {}\n{} groups {}'.format(solve_type, ngroups, mesh_shape))
	plt.clim(cmin, cmax)
	plt.colorbar(c)

	# Plot (homogeneous vs heterogeneous) error in the lower left
	plt.subplot(234)
	b = plt.imshow(error_moc.squeeze(), interpolation='none', cmap='rainbow')
	plt.title('% Relative error of Homogeneous\nvs Heterogeneous')
	plt.clim(emin, emax)
	plt.colorbar(b)
	# Plot (heterogeneous vs. Monte Carlo) error in the lower center
	plt.subplot(235)
	e = plt.imshow(error_het.squeeze(), interpolation='none', cmap='rainbow')
	plt.title('% Relative error of Heterogeneous\nvs openmc')
	plt.clim(emin, emax)
	plt.colorbar(e)
	# Plot (homogeneous vs Monte Carlo) error in the lower right
	plt.subplot(236)
	f = plt.imshow(error_hom.squeeze(), interpolation='none', cmap='rainbow')
	plt.title('% Relative error of Homogeneous\nvs openmc')
	plt.clim(emin, emax)
	plt.colorbar(f)
	
	# implement mode and the rest later...
	plt.show()


def compare_source_order(ngroups, gen, mesh_shape, condense=False, ebar=True):
	gen = gen.lower()
	domain = {"homogeneous"  : "universe",
	          "heterogeneous": "cell"}[gen]
	
	prefix = "inl_mcfuel/{gen}/same/{ngroups}groups/" \
	         "{domain}_{mesh_shape}_".format(**locals())
	suffix = "/moc_fission_rates_{}".format(mesh_shape)
	
	fsr_file = prefix + "fsr" + suffix
	lsr_file = prefix + "linear" + suffix
	
	if condense:
		fname = "inl_mcfuel/montecarlo_19x19"
	else:
		fname = "inl_mcfuel/montecarlo_{}".format(mesh_shape)
	montecarlo = normalize_rates(np.loadtxt(fname))
	indices = np.isnan(montecarlo)
	
	if condense:
		moc_fsr = project_array(np.loadtxt(fsr_file), montecarlo)
		moc_lsr = project_array(np.loadtxt(lsr_file), montecarlo)
	else:
		moc_fsr = np.loadtxt(fsr_file)
		moc_lsr = np.loadtxt(lsr_file)
		
	moc_fsr[indices] = np.nan
	moc_lsr[indices] = np.nan
	moc_fsr /= np.nanmean(moc_fsr)
	moc_lsr /= np.nanmean(moc_lsr)
	
	# Get color schemes
	cmin, cmax = get_min_and_max((montecarlo, moc_lsr, moc_fsr))
	error_fsr = np.divide(moc_fsr - montecarlo, montecarlo/100)
	error_lsr = np.divide(moc_lsr - montecarlo, montecarlo/100)
	error_moc = np.divide(moc_fsr - moc_lsr, moc_lsr/100)
	if ebar:
		emin = EMIN
		emax = EMAX
	else:
		emin, emax = get_min_and_max((error_fsr, error_lsr, error_moc))
	
	plt.figure()
	# Plot OpenMC's power distribution in the
	plt.subplot(231)
	a = plt.imshow(montecarlo.squeeze(), interpolation='none', cmap='jet')
	plt.title('OpenMC Power Distribution\nReference')
	plt.clim(cmin, cmax)
	plt.colorbar(a)
	# Plot OpenMOC's FSR fission rates in the upper center subplot
	plt.subplot(232)
	b = plt.imshow(moc_fsr.squeeze(), interpolation='none', cmap='jet')
	plt.title('OpenMOC, {}, FSR\n{} groups {}'.format(gen, ngroups, mesh_shape))
	plt.clim(cmin, cmax)
	plt.colorbar(b)
	# Plot OpenMOC's homogeneous fission rates in the upper right subplot
	plt.subplot(233)
	c = plt.imshow(moc_lsr.squeeze(), interpolation='none', cmap='jet')
	plt.title('OpenMOC, {}, LSR\n{} groups {}'.format(gen, ngroups, mesh_shape))
	plt.clim(cmin, cmax)
	plt.colorbar(c)
	
	# Plot (FSR vs LSR) error in the lower left
	plt.subplot(234)
	d = plt.imshow(error_moc.squeeze(), interpolation='none', cmap='rainbow')
	plt.title('% Relative error of FSR\nvs LSR')
	plt.clim(emin, emax)
	plt.colorbar(d)
	# Plot (heterogeneous vs. Monte Carlo) error in the lower center
	plt.subplot(235)
	e = plt.imshow(error_fsr.squeeze(), interpolation='none', cmap='rainbow')
	plt.title('% Relative error of FSR\nvs openmc')
	plt.clim(emin, emax)
	plt.colorbar(e)
	# Plot (homogeneous vs Monte Carlo) error in the lower right
	plt.subplot(236)
	f = plt.imshow(error_fsr.squeeze(), interpolation='none', cmap='rainbow')
	plt.title('% Relative error of LSR\nvs openmc')
	plt.clim(emin, emax)
	plt.colorbar(f)
	
	# implement mode and the rest later...
	plt.show()


def compare_mesh_convergence(ngroups, gen, solve_type, condense_to=None, ebar=True):
	solve_type = solve_type.lower()
	domain = {"homogeneous"  : "universe",
	          "heterogeneous": "cell"}[gen]
	
	if condense_to:
		assert condense_to in ["19x19"] + meshes, \
			"Unknown shape to condense to"
		monte_condense = np.loadtxt("inl_mcfuel/montecarlo_{}".\
		                            format(condense_to))
		monte_condense = normalize_rates(monte_condense)
		indices = np.isnan(monte_condense)
	else:
		monte_condense = None
	
	n = len(meshes)
	monte_rates = [None]*n
	moc_rates = [None]*n
	moc_errs = [None]*n
	
	for i, mesh_shape in enumerate(meshes):
		if condense_to is None:
			fname = "inl_mcfuel/montecarlo_{}".format(mesh_shape)
			monte_arr = normalize_rates(np.loadtxt(fname))
			indices = np.isnan(monte_arr)
			monte_rates[i] = monte_arr
		else:
			monte_rates[i] = monte_condense
		
		# OpenMOC solution to compare
		prefix = "inl_mcfuel/{gen}/same/{ngroups}groups/" \
	             "{domain}_{mesh_shape}_".format(**locals())
		suffix = "/moc_fission_rates_{}".format(mesh_shape)
		gname = prefix + solve_type + suffix
		moc_arr = np.loadtxt(gname)
		if condense_to:
			moc_arr = project_array(moc_arr, monte_condense)
		moc_arr[indices] = np.nan
		moc_arr /= np.nanmean(moc_arr)
		moc_rates[i] = moc_arr
		
		if condense_to:
			errs = np.divide(moc_arr - monte_rates[0], monte_condense/100)
		else:
			errs = np.divide(moc_arr - monte_arr, monte_arr/100)
		moc_errs[i] = errs
		
	# Get color schemes
	cmin, cmax = get_min_and_max(monte_rates + moc_rates)
	if ebar:
		emin = EMIN
		emax = EMAX
	else:
		emin, emax = get_min_and_max(moc_errs)
	
	pids = ((241, 245), (242, 246), (243, 247), (244, 248))
	# OK, now generate 1 plots
	plt.figure()
	for i, mesh_shape in enumerate(meshes):
		top, bot = pids[i]
		# Top plot: OpenMOC fission rate
		plt.subplot(top)
		a = plt.imshow(moc_rates[i].squeeze(), interpolation='none', cmap='jet')
		plt.title('OpenMOC, {}, {}\n{} groups {}'.format(gen, solve_type, ngroups, mesh_shape))
		plt.clim(cmin, cmax)
		plt.colorbar(a)
		# Bottom plot: OpenMOC vs. OpenMC relative error
		plt.subplot(bot)
		b = plt.imshow(moc_errs[i].squeeze(), interpolation='none', cmap='rainbow')
		plt.title('Percent Relative error of {}\nvs openmc'.format(mesh_shape))
		plt.clim(emin, emax)
		plt.colorbar(b)
	
	# implement mode and the rest later...
	plt.show()


def compare_new_inl_plots(ngroups, gen, mesh_shape, solve_type,
                          ebar=False):
	gen = gen.lower()
	solve_type = solve_type.lower()
	domain = {"homogeneous"  : "universe",
	          "heterogeneous": "cell"}[gen]
	
	folder = "inl_mcfuel/{gen}/same/{ngroups}groups/" \
	         "{domain}_{mesh_shape}_{solve_type}/".format(**locals())
	folder, shape = _check_params(folder, mesh_shape)
	basename = "{}{}_fission_rates_{}"
	mocfname = basename.format(folder, "moc", mesh_shape)
	moc_rates = np.loadtxt(mocfname)

	if gen == "homogeneous":
		# load the 19x19 OpenMC and project the MOC
		mcfname = "inl_mcfuel/montecarlo_19x19"
		montecarlo_rates = normalize_rates(np.loadtxt(mcfname))
		moc_rates = project_array(moc_rates, montecarlo_rates)
	else:
		mcfname = basename.format(folder, "montecarlo", mesh_shape)
		montecarlo_rates = normalize_rates(np.loadtxt(mcfname))
	
	# Normalize the integrated fission rates
	moc_rates[np.isnan(montecarlo_rates)] = np.nan
	moc_rates /= np.nanmean(moc_rates)
	
	# Errors and color schemes
	cmin = min(np.nanmin(montecarlo_rates), np.nanmin(moc_rates))
	cmax = max(np.nanmax(montecarlo_rates), np.nanmax(moc_rates))
	err1 = np.divide(moc_rates - montecarlo_rates, montecarlo_rates/100)
	pcmerr = (moc_rates - montecarlo_rates)*1E5
	if ebar:
		emin = EMIN
		emax = EMAX
	else:
		dmin = abs(np.nanmin(err1))
		dmax = np.nanmax(err1)
		elim = max(dmin, dmax)
		emin = -elim
		emax = +elim
	
	plt.figure()
	
	# Top left: OpenMC solution
	plt.subplot(221)
	a = plt.imshow(montecarlo_rates.squeeze(), interpolation='none', cmap='jet')
	plt.title('OpenMC Power Distribution\n(Reference)')
	plt.clim(cmin, cmax)
	plt.colorbar(a)
	# Top right: OpenMOC solution
	plt.subplot(222)
	b = plt.imshow(moc_rates.squeeze(), interpolation='none', cmap='jet')
	plt.title('OpenMOC {}, {}\n{} Groups {}'.format(gen, solve_type, ngroups, mesh_shape))
	plt.clim(cmin, cmax)
	plt.colorbar(b)
	# Bottom left: relative error
	plt.subplot(223)
	c = plt.imshow(err1.squeeze(), interpolation='none', cmap='rainbow')
	plt.title('Percent relative error vs. MC\n{}'.format(mesh_shape))
	plt.clim(emin, emax)
	plt.colorbar(c)
	# Bottom right: absolute error
	plt.subplot(224)
	d = plt.imshow(pcmerr.squeeze(), interpolation='none', cmap='rainbow')
	plt.title('PCM absolute error vs. MC\n{}'.format(mesh_shape))
	#plt.clim(emin, emax)
	plt.colorbar(d)
	
	plt.tight_layout()
	plt.show()

def effect_of_cmm(ngroups, gen, mesh_shape, solve_type, core,
                  condense_to=None, ebar=True):
	solve_type = solve_type.lower()
	core = core.lower()
	assert core in {"same", "interface"}
	domain = {"homogeneous"  : "universe",
	          "heterogeneous": "cell"}[gen]
	#suffix = "moc_fission_rates_{}".format(mesh_shape)
	prefix = "inl_mcfuel/{gen}/{core}/{ngroups}groups/{domain}_{mesh_shape}_".format(**locals())
	if solve_type in {"fsr", "flat"}:
		raw_folder = prefix + "fsr"
		cmm_folder = prefix + "fsr-cmm"
	elif solve_type in {"lsr", "linear"}:
		raw_folder = prefix + "linear"
		cmm_folder = prefix + "lsr-cmm"
	else:
		raise TypeError("SOLVE_TYPE = " + solve_type)
	
	if condense_to:
		assert condense_to in ["19x19"] + _MESHES, \
			"Unknown shape to condense to"
		montecarlo_rates = np.loadtxt("inl_mcfuel/montecarlo_{}". \
		                            format(condense_to))
		montecarlo_rates = normalize_rates(montecarlo_rates)
		fname = "/{}groups_moc_fission_rates_{}".format(ngroups, mesh_shape)
		moc_raw = project_array(np.loadtxt(raw_folder + fname), montecarlo_rates)
		moc_cmm = project_array(np.loadtxt(cmm_folder + fname), montecarlo_rates)
	else:
		montecarlo_rates = np.loadtxt("inl_mcfuel/montecarlo_{}".format(mesh_shape))
		montecarlo_rates = normalize_rates(montecarlo_rates)
		fname = "/{}groups_moc_fission_rates_{}".format(ngroups, mesh_shape)
		moc_raw = project_array(np.loadtxt(raw_folder + fname), montecarlo_rates)
		moc_cmm = project_array(np.loadtxt(cmm_folder + fname), montecarlo_rates)
	indices = np.isnan(montecarlo_rates)
	moc_raw[indices] = np.nan
	moc_raw /= np.nanmean(moc_raw)
	moc_cmm[indices] = np.nan
	moc_cmm /= np.nanmean(moc_cmm)
	
	# Get color schemes
	cmin, cmax = get_min_and_max((montecarlo_rates, moc_raw, moc_cmm))
	error_cmm = np.divide(moc_cmm - montecarlo_rates, montecarlo_rates/100)
	error_raw = np.divide(moc_raw - montecarlo_rates, montecarlo_rates/100)
	error_moc = np.divide(moc_cmm - moc_raw, moc_raw/100)
	if ebar:
		emin = EMIN
		emax = EMAX
	else:
		emin, emax = get_min_and_max((error_cmm, error_raw, error_moc))
	
	plt.figure()
	# Plot OpenMC's power distribution in the
	plt.subplot(231)
	a = plt.imshow(montecarlo_rates.squeeze(), interpolation='none', cmap='jet')
	plt.title('OpenMC Power Distribution\nReference')
	plt.clim(cmin, cmax)
	plt.colorbar(a)
	# Plot OpenMOC's raw, uncorrected fission rates in the upper center subplot
	plt.subplot(232)
	b = plt.imshow(moc_raw.squeeze(), interpolation='none', cmap='jet')
	plt.title('OpenMOC, Uncorrected, {}\n{} groups {}'.format(solve_type, ngroups, mesh_shape))
	plt.clim(cmin, cmax)
	plt.colorbar(b)
	# Plot OpenMOC's CMM-corrected fission rates in the upper right subplot
	plt.subplot(233)
	c = plt.imshow(moc_cmm.squeeze(), interpolation='none', cmap='jet')
	plt.title('OpenMOC, CMM-Corrected, {}\n{} groups {}'.format(solve_type, ngroups, mesh_shape))
	plt.clim(cmin, cmax)
	plt.colorbar(c)
	
	# Plot (homogeneous vs heterogeneous) error in the lower left
	plt.subplot(234)
	b = plt.imshow(error_moc.squeeze(), interpolation='none', cmap='rainbow')
	plt.title('% Relative difference of CMM\nvs Uncorrected')
	plt.clim(emin, emax)
	plt.colorbar(b)
	# Plot (heterogeneous vs. Monte Carlo) error in the lower center
	plt.subplot(235)
	e = plt.imshow(error_raw.squeeze(), interpolation='none', cmap='rainbow')
	plt.title('% Relative error of Uncorrected\nvs openmc')
	plt.clim(emin, emax)
	plt.colorbar(e)
	# Plot (homogeneous vs Monte Carlo) error in the lower right
	plt.subplot(236)
	f = plt.imshow(error_cmm.squeeze(), interpolation='none', cmap='rainbow')
	plt.title('% Relative error of CMM-Corrected\nvs openmc')
	plt.clim(emin, emax)
	plt.colorbar(f)
	
	# implement mode and the rest later...
	plt.show()


def het25_hom25_hom11(mesh_shape, solve_type, condense_to=None, ebar=False):
	solve_type = solve_type.lower()
	
	if solve_type in {"fsr", "flat"}:
		raw = "fsr"
		cmm = "fsr-cmm"
	elif solve_type in {"lsr", "linear"}:
		raw = "linear"
		cmm = "lsr-cmm"
	else:
		raise TypeError("SOLVE_TYPE = " + solve_type)
	
	# suffix = "moc_fission_rates_{}".format(mesh_shape)
	het25_folder = "inl_mcfuel/heterogeneous/same/25groups/cell_{}_{}".format(mesh_shape, raw)
	hom25_folder = "inl_mcfuel/homogeneous/same/25groups/universe_{}_{}".format(mesh_shape, cmm)
	hom11_folder = "inl_mcfuel/homogeneous/same/11groups/universe_{}_{}".format(mesh_shape, cmm)
	
	# 25-group heterogeneous
	fpath_het25 = "{}/25groups_moc_fission_rates_{}".format(het25_folder, mesh_shape)
	het25 = np.loadtxt(fpath_het25)
	# 25-group homogeneous+CMM
	fpath_hom25 = "{}/25groups_moc_fission_rates_{}".format(hom25_folder, mesh_shape)
	hom25 = np.loadtxt(fpath_hom25)
	# 11-group homogeneous+CMM
	fpath_hom11 = "{}/11groups_moc_fission_rates_{}".format(hom11_folder, mesh_shape)
	hom11 = np.loadtxt(fpath_hom11)

	if condense_to:
		assert condense_to in ["19x19"] + _MESHES, \
			"Unknown shape to condense to"
		shape = np.array(condense_to.split('x'), dtype=int)
		blank_array = np.empty(shape)
		het25 = project_array(het25, blank_array)
		hom25 = project_array(hom25, blank_array)
		hom11 = project_array(hom11, blank_array)
		del blank_array
	#indices = np.isnan(montecarlo_rates)
	het25[het25 < het25.mean()] = np.nan
	indices = np.isnan(het25)
	het25 /= np.nanmean(het25)
	hom25[indices] = np.nan
	hom25 /= np.nanmean(hom25)
	hom11[indices] = np.nan
	hom11 /= np.nanmean(hom11)
	
	# Get color schemes
	cmin, cmax = get_min_and_max((het25, hom25, hom11))
	error_hom25 = np.divide(hom25 - het25, het25 / 100)
	error_hom11 = np.divide(hom11 - het25, het25 / 100)
	error_11_25 = np.divide(hom11 - hom25, hom25 / 100)
	if ebar:
		emin = EMIN
		emax = EMAX
	else:
		emin, emax = get_min_and_max((error_hom25, error_hom11), absolute_magnitude=True)
		print(emin, emax)
	
	plt.figure()
	# Plot OpenMOC's 25-group heterogeneous fission rates in the upper left
	plt.subplot(231)
	a = plt.imshow(het25.squeeze(), interpolation='none', cmap='jet')
	plt.title('OpenMOC, Heterogeneous {}\n{} groups {}'.format(raw, 25, mesh_shape))
	plt.clim(cmin, cmax)
	plt.colorbar(a)
	# Plot OpenMOC's 25-group CMM-corrected homogeneous fission rates in the upper center
	plt.subplot(232)
	b = plt.imshow(hom25.squeeze(), interpolation='none', cmap='jet')
	plt.title('OpenMOC, Homogeneous, {}\n{} groups {}'.format(cmm, 25, mesh_shape))
	plt.clim(cmin, cmax)
	plt.colorbar(b)
	# Plot OpenMOC's 11-group CMM-corrected homogeneous fission rates in the upper right
	plt.subplot(233)
	c = plt.imshow(hom11.squeeze(), interpolation='none', cmap='jet')
	plt.title('OpenMOC, Homogeneous, {}\n{} groups {}'.format(cmm, 11, mesh_shape))
	plt.clim(cmin, cmax)
	plt.colorbar(c)
	
	# Plot (11-group homogeneous vs 25-group homogeneous) error in the lower left
	plt.subplot(234)
	b = plt.imshow(error_11_25.squeeze(), interpolation='none', cmap='rainbow')
	plt.title('% Relative difference of 11-group Homogeneous\nvs 25-group Homogeneous')
	plt.clim(emin, emax)
	plt.colorbar(b)
	# Plot (25-group homogeneous vs. 25-group heterogeneous) error in the lower center
	plt.subplot(235)
	e = plt.imshow(error_hom25.squeeze(), interpolation='none', cmap='rainbow')
	plt.title('% Relative error of 25-group Homogeneous\nvs 25-group Heterogeneous')
	plt.clim(emin, emax)
	plt.colorbar(e)
	# Plot (11-group homogeneous vs 25-group heterogeneous) error in the lower right
	plt.subplot(236)
	f = plt.imshow(error_hom25.squeeze(), interpolation='none', cmap='rainbow')
	plt.title('% Relative error of 11-group Homogeneous\nvs 25-group Heterogeneous')
	plt.clim(emin, emax)
	plt.colorbar(f)
	
	plt.show()
	
		
if __name__ == "__main__":
	GROUPS = 11
	NDIV = 380
	MESH = "{}x{}".format(NDIV, NDIV)
	#DOMAIN = "cell"
	GEN = "homogeneous"
	#FOLDER = "mcfuel/moc_data/{}groups/{}_{}".format(GROUPS, DOMAIN, MESH)
	#base_eps = 1/(NDIV**2*GROUPS)
	
	if True:
		#compare_new_inl_plots(GROUPS, GEN, MESH, "fsr", ebar=True)
		#compare_geneity(GROUPS, MESH, "linear", "interface", condense=True, ebar=True)
		#compare_geneity(GROUPS, MESH, "linear", "interface", condense=False, ebar=False)
		#compare_mesh_convergence(GROUPS, GEN, "linear", condense_to="19x19", ebar=True)
		#compare_mesh_convergence(GROUPS, GEN, "linear", condense_to=None, ebar=True)
		#compare_mesh_convergence(GROUPS, GEN, "linear", condense_to=None, ebar=False)
		#effect_of_cmm(GROUPS, GEN, MESH, "linear", "interface", condense_to="19x19", ebar=True)
		#het25_hom25_hom11(MESH, "linear", condense_to="19x19")
		het25_hom25_hom11(MESH, "linear", condense_to=None, ebar=True)
		raise SystemExit
	
	
	#RXN_EPS = {"fission"   : 1.5,  # less than 150% of avg. group rxn rate
	#           "absorption": 0.9,  # less than 90% of avg. group reaction rate
	#           "total"     : 0,
	#           "flux"      : 0}
	
	#normalizations = get_normalization_factors(GROUPS, MESH, "absorption", FOLDER)
	#for rxn, e in RXN_EPS.items():
	#	plot_reaction_rates(GROUPS, MESH, rxn, FOLDER, e, normalizations)
	
	#plot_power(GROUPS, MESH, FOLDER, mode="show")
	
	meshes = ["95x95", "190x190", "285x285", "380x380"]
	n = len(meshes)
	folders = [None]*n
	mcs = [None]*n
	mocs = [None]*n
	
	#mesh0, mesh1, mesh2, mesh3 = meshes
	for i, meshi in enumerate(meshes):
		folder = "mcfuel/moc_data/{}groups/{}_{}".format(GROUPS, DOMAIN, meshi)
		folders[i] = folder
		mcs[i], mocs[i] = plot_power(GROUPS, meshi, folder, mode="return")[0:2]
		'''
		#mesh1 = "190x190"
		folder1 = "mcfuel/moc_data/{}groups/{}_{}".format(GROUPS, DOMAIN, mesh1)
		mc1, moc1 = plot_power(GROUPS, mesh1, folder1, mode="return")[0:2]
		#mesh2 = "285x285"
		folder2 = "mcfuel/moc_data/{}groups/{}_{}".format(GROUPS, DOMAIN, mesh2)
		mc2, moc2 = plot_power(GROUPS, mesh2, folder2, mode="return")[0:2]
		'''
		# ok, and then compare them
	compare_moc_rates(meshes[0], mcs[0], mocs[0], mocs[1], mocs[2])
	exit()
	
	if NDIV == 285:
		if GROUPS == 25:
			moc25 = moc2
			folder11 = "mcfuel/moc_data/{}groups/{}_{}".format(11, DOMAIN, mesh2)
			moc11 = plot_power(11, mesh2, folder11, mode="return")[1]
		else:
			moc11 = moc2
			folder25 = "mcfuel/moc_data/{}groups/{}_{}".format(25, DOMAIN, mesh2)
			moc25 = plot_power(25, mesh2, folder25, mode="return")[1]
		compare_moc_across_groups(mc2, moc11, moc25, mesh2)
	elif NDIV == 190:
		if GROUPS == 25:
			moc25 = moc1
			folder11 = "mcfuel/moc_data/{}groups/{}_{}".format(11, DOMAIN, mesh1)
			moc11 = plot_power(11, mesh1, folder11, mode="return")[1]
		else:
			moc11 = moc1
			folder25 = "mcfuel/moc_data/{}groups/{}_{}".format(25, DOMAIN, mesh1)
			moc25 = plot_power(25, mesh1, folder25, mode="return")[1]
		compare_moc_across_groups(mc1, moc11, moc25, mesh1)
	elif NDIV == 95:
		if GROUPS == 25:
			moc25 = moc0
			folder11 = "mcfuel/moc_data/{}groups/{}_{}".format(11, DOMAIN, mesh0)
			moc11 = plot_power(11, mesh0, folder11, mode="return")[1]
		else:
			moc11 = moc0
			folder25 = "mcfuel/moc_data/{}groups/{}_{}".format(25, DOMAIN, mesh0)
			moc25 = plot_power(25, mesh0, folder25, mode="return")[1]
		compare_moc_across_groups(mc0, moc11, moc25, mesh0)
	
	

