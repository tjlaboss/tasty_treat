# Element
#
# Class for data about MOC representation of TREAT elements

from .cmm.cumulative import CumulativeMigrationCorrection
from .superhomogeneisation import SuperhomogeneisationFactors


class Element:
	def __init__(self, key, ndim):
		self._key = key
		self.ndim = ndim
		self._sph = {}
		self._cmm = {}
		self.crdrings = 0
		self.crdsectors = 0
		self._division = None

	@property
	def key(self):
		return self._key
	
	@property
	def division(self):
		return self._division
	
	@division.setter
	def division(self, subdivision_shape):
		if subdivision_shape is not None:
			assert len(subdivision_shape) == self.ndim
			self._division = subdivision_shape
	
	@property
	def cmm(self):
		return self._cmm
	
	@property
	def sph(self):
		return self._sph
	
	def add_cmm_corrections(self, cumulative_migration_correction):
		"""Add a treat.moc.cmm.CumulativeMigrationCorrection instance"""
		ngroups = cumulative_migration_correction.ngroups
		self._cmm[ngroups] = cumulative_migration_correction
	
	def add_cmm_corrections_from_array(self, corrections):
		"""Use an array to create and add a new CumulativeMigrationCorrection instance"""
		ngroups = len(corrections)
		self._cmm[ngroups] = CumulativeMigrationCorrection(ngroups, corrections)
	
	def add_sph_factors(self, super_homogenization_factors):
		"""Add a treat.moc.SuperhomogeneisationFactors instance"""
		ngroups = super_homogenization_factors.ngroups
		self._sph[ngroups] = super_homogenization_factors
		
	def add_sph_factors_from_array(self, factors):
		"""Use an array to create and add a new SuperhomogeneisationFactors instance"""
		ngroups = len(factors)
		self._sph[ngroups] = SuperhomogeneisationFactors(ngroups, factors)


class Element2D(Element):
	def __init__(self, key):
		super().__init__(key, 2)


class Element3D(Element):
	def __init__(self, key):
		super().__init__(key, 3)
