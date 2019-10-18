import pylab


def plot_reaction_rates(eps=1E-6):
	moc_fission_rates = pylab.loadtxt("moc_data/moc_fission_rates")
	fission_rates = pylab.loadtxt("moc_data/montecarlo_fission_rates")
	
	# Filter out values that are essentially zero
	# Objective: Ignore zero fission rates in guide tubes with Matplotlib color scheme
	indices = fission_rates <= eps
	fission_rates[indices] = pylab.NaN
	moc_fission_rates[indices] = pylab.NaN
	
	# Normalize with the nanmean function, which excludes NaNs from the mean
	fission_rates /= pylab.nanmean(fission_rates)
	moc_fission_rates /= pylab.nanmean(moc_fission_rates)
	# Then use these normalized arrays to calculate the relative error
	errors = pylab.divide(moc_fission_rates - fission_rates, fission_rates/100.0)
	errors[indices] = pylab.NaN
	
	pylab.figure()
	# Plot OpenMC's fission rates in the left subplot
	fig = pylab.subplot(221)
	pylab.imshow(fission_rates.squeeze(), interpolation='none', cmap='jet')
	pylab.title('OpenMC Fission Rates')
	pylab.colorbar()
	
	# Plot OpenMOC's fission rates in the right subplot
	fig2 = pylab.subplot(222)
	pylab.imshow(moc_fission_rates.squeeze(), interpolation='none', cmap='jet')
	pylab.title('OpenMOC Fission Rates')
	pylab.colorbar()
	
	fig3 = pylab.subplot(223)
	pct = pylab.imshow(errors.squeeze(), interpolation='none', cmap='jet')
	posmax = pylab.nanmax(errors)
	negmax = pylab.nanmin(errors)
	cmax = pylab.ceil(max(abs(posmax), abs(negmax)))
	#pylab.clim(-100, 100)
	pylab.clim(-cmax, +cmax)
	pylab.title('Percent error')
	pylab.colorbar(pct)
	
	pylab.tight_layout()
	pylab.show()


def plot_montecarlo_results():
	pylab.figure()
	fission_rates = pylab.loadtxt("moc_data/montecarlo_fission_rates")
	indices = fission_rates <= 1E-6
	fission_rates[indices] = pylab.NaN
	fission_rates /= pylab.nanmean(fission_rates)
	pylab.imshow(fission_rates.squeeze(), interpolation='none', cmap='jet')
	pylab.title('OpenMC Fission Rates')
	pylab.colorbar()
	pylab.show()


def plot_moc_results():
	pylab.figure()
	moc_fission_rates = pylab.loadtxt("moc_data/moc_fission_rates")
	indices = moc_fission_rates <= 1E-6
	moc_fission_rates[indices] = pylab.NaN
	moc_fission_rates /= pylab.nanmean(moc_fission_rates)
	pylab.imshow(moc_fission_rates.squeeze(), interpolation='none', cmap='jet')
	pylab.title('OpenMOC Fission Rates')
	pylab.colorbar()
	pylab.show()


if __name__ == "__main__":
	plot_reaction_rates()
	#plot_montecarlo_results()
	#plot_moc_results()
