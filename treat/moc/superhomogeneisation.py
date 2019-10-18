# SuPerHomogeneisation
#
# Class for applying correction factors via SuPerHomogeneisation (SPH)

import numpy as np


class SuperhomogeneisationFactors:
	"""Class for managing SPH factors in MGXS

	Energy groups are "descending"; i.e., group 0 is the fastest.


	Parameters:
	-----------
	ngroups:        int; number of energy groups
	factors:        array of floats of length=len(ngroups), optional;
					SPH factors sorted by energy group

	"""
	def __init__(self, ngroups, factors=None):
		self._ngroups = ngroups
		if factors is not None:
			self.factors = factors
		else:
			self._factors = None
	
	@property
	def ngroups(self):
		return self._ngroups
	
	@property
	def factors(self):
		return self._factors
	
	@factors.setter
	def factors(self, list_of_factors):
		g = len(list_of_factors)
		errstr = "Cannot assign {} factors to {} energy groups"
		assert g == self.ngroups, errstr.format(g, self.ngroups)
		self._factors = np.array(list_of_factors)
	
	def _get_corrected_scatter_mgxs(self, scatter_matrix):
		# TODO: Confirm with Ben that this is how SPH is applied
		new_scatter = np.zeros(scatter_matrix.shape)
		for g in range(self._ngroups):
			new_scatter[g, :] = self._factors * scatter_matrix[g, :]
		return new_scatter
			
	
	def get_corrected_mgxs(self, reaction_xs):
		assert self._factors is not None, \
			"You must set the SPH factors first!"
		if reaction_xs.size == self._ngroups:
			return self._factors * reaction_xs
		elif reaction_xs.size == self._ngroups**2:
			# This must be the scatter matrix
			return self._get_corrected_scatter_mgxs(reaction_xs)
		else:
			raise AssertionError("Wrong number of energy groups.")
		
	