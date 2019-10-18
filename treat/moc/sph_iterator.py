# SPH Iterator
#
# Iteratively sovle for SPH factors

import numpy as np
from .simulation import Simulation
from .constants import SPH_ARRAY


def _fmt_iter(i):
	return "iter{:02d}".format(i)


class SphIterator(Simulation):
	def __init__(self, case, ngroups, solve_type, mesh_shape, last_iter=None, **kwargs):
		super().__init__(case, ngroups, solve_type, mesh_shape,
		                 homogeneous=True, use_sph=True, **kwargs)
		if last_iter is None:
			last_iter = -1
		self._last_iter = last_iter
	
	
	def _load_factors(self):
		if self._last_iter < 0:
			return np.ones(self.ngroups)
		else:
			path = self._get_default_path(suffix=_fmt_iter(self._last_iter))
			fname = path + SPH_ARRAY
			factors = np.loadtxt(fname)
			num = len(factors)
			errstr = "SPH factors from '{}' contain {} energy groups, not {}."
			assert num == self.ngroups, errstr.format(fname, num, self.ngroups)
			return factors
	
	
	def _apply_factors(self, factors):
		for ekey in self._calculate_sph:
			elem = self.elements[ekey]
			elem.add_sph_factors_from_array(factors)
	
	
	def solve_for_sph_factors(self, max_iter, eps, nproc=4, overwrite=False):
		self._set_sph_keys()
		mu = self._load_factors()
		diff = eps + 1
		for i in range(self._last_iter + 1, max_iter + 1):
			header = "SPH ITERATION {}:".format(i)
			header += '\n' + '-'*len(header)
			print("\n\n" + header)
			self._case.reset()
			self._apply_factors(mu)
			self.save_suffix = _fmt_iter(i)
			self._set_path(overwrite=overwrite)
			print("Running", self.get_report())
			self._case.run_openmoc(
				nproc=nproc,
				export_path=self._path,
				calculate_sph=self._sph_keys,
				**vars(self))
			self._last_iter = i
			last_mu = mu
			mu = self._load_factors()
			diff = np.divide(abs(mu - last_mu), mu).max()
			print("SPH max eps: {:8.6f}".format(diff))
			if diff <= eps:
				print("SPH factors converged in", i, "iterations.")
				break
		if diff > eps:
			print("SPH factors did not converge in", max_iter, "iterations.")
			print("{}-group factors:\n{}".format(self.ngroups, mu))
		print("...finished.")
			
