# Cumulative
#
# Class for applying a correction using the Cumulative Migration Method (CMM)

import numpy as np


class CumulativeMigrationCorrection(object):
	"""Class for managing correction factors for the Transport and
	in-group Scatter MGXS, from the Cumulative Migration Method (CMM).
	
	Energy groups are "descending"; i.e., group 0 is the fastest.
	
	Many thanks to Zhaoyuan "Johnny" Liu for this research.
	
	
	Parameters:
	-----------
	ngroups:        int; number of energy groups
	corrections:    array of floats of length=len(ngroups), optional;
					correction factors sorted by energy group
	
	"""
	def __init__(self, ngroups, corrections=None):
		self.ngroups = ngroups
		if corrections is not None:
			self.corrections = corrections
		else:
			self._corrections = None
		
	@property
	def corrections(self):
		return self._corrections
	
	@corrections.setter
	def corrections(self, list_of_corrections):
		g = len(list_of_corrections)
		errstr = "Cannot assign {} corrections to {} energy groups"
		assert g == self.ngroups, errstr.format(g, self.ngroups)
		self._corrections = np.array(list_of_corrections)
	
	def _check_correction(self, g):
		assert self._corrections is not None, \
			"You must set the corrections first!"
		return self._corrections[g]
	
	def get_corrected_transport(self, g, old_transport):
		"""Get \Sigma_{tr,g}^{new}
		
		Parameters:
		-----------
		g:              int; energy group
		old_transport:  float, cm^-1; original (un-corrected) value of
						the transport-corrected macroscopic cross section
		
		Returns:
		--------
		float, cm^-1; transport-corrected cross section corrected by CMM
		"""
		
		r = self._check_correction(g)
		return r*old_transport
	
	def get_corrected_scatter(self, g, old_scatter, old_transport=None,
	                          new_transport=None, delta_transport=None):
		"""Get \Sigma_{g -> g}^{new}
		
		This corrects only the in-group scatter cross section.
		
		Required Parameters:
		--------------------
		g:                  int; enrgy group
		old_scatter:        float, cm^-1; original (un-corrected) value of
							the in-group macroscopic scatter cross section
		-----and one of-----
		old_transport:      float, cm^-1; original (un-corrected) value of
							the transport-corrected macroscopic cross section
		new_transport:      float, cm^-1; CMM-corrected value of
							the transport-corrected macroscopic cross section
		delta_transport:    float, cm^-1; (new_transport - old_transport)
		
		Returns:
		--------
		float, cm^-1; in-group scatter cross section corrected by CMM
		"""
		r = self._check_correction(g)
		opts = (old_transport, new_transport, delta_transport)
		errstr = "You must specify one (and exactly 1) of: \n\t" \
		         "old_transport, new_transport, delta_transport"
		c = 0
		for o in opts:
			if o is not None:
				c += 1
		assert c == 1, errstr
		
		if new_transport:
			delta_transport = (1 - 1/r)*new_transport
		elif old_transport:
			delta_transport = (r - 1)*old_transport
		return old_scatter + delta_transport
	
	def get_corrected_transport_mgxs(self, transport_xs):
		"""Get an array of CMM-corrected transport cross sections
		
		Parameters:
		-------------
		transport_xs:       array; openmc.mgxs.TransportXS.get_xs()
		
		Returns:
		--------
		array; same thing times the respective correction factors
		"""
		assert len(transport_xs) == self.ngroups, \
			"Wrong number of energy groups."
		new_transport = np.zeros(self.ngroups)
		for g, xs in enumerate(transport_xs.flatten()):
			new_transport[g] = self.get_corrected_transport(g, xs)
		return new_transport.flatten()
	
	def get_corrected_scatter_mgxs(self, scatter_matrix_xs, transport_xs):
		"""Get a CMM-corrected scatter matrix

		Parameters:
		-------------
		scatter_matrix_xs:  array; openmc.mgxs.ScatterMattrixXS.get_xs()
		transport_xs:       array; openmc.mgxs.TransportXS.get_xs()

		Returns:
		--------
		array; scatter matrix with the in-group scatter term corrected for CMM
		"""
		assert scatter_matrix_xs.shape == (self.ngroups, self.ngroups), \
			"Wrong number of energy groups."
		assert len(transport_xs) == self.ngroups, \
			"Wrong number of energy groups."
		new_scatter = np.array(scatter_matrix_xs)
		for g, xs in enumerate(transport_xs.flatten()):
			new_scatter[g, g] = self.get_corrected_scatter(
				g, scatter_matrix_xs[g, g], old_transport=xs)
		return new_scatter
	