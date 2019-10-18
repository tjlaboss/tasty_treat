# Standard
#
# Streamline the case creation process with some parameters that I never really change


from .base_case import BaseCase


NAZIM = 32
DAZIM = 0.1
NGROUPS = (1, 11, 25)
GENEOUS = {True: "homogeneous", False: "heterogeneous"}
DOMAINS = {"homogeneous": "universe", "heterogeneous": "cell"}
SOLVERS = {"linear": "lsr", "lsr": "lsr", "flat": "fsr", "fsr": "fsr"}


class StandardCase(BaseCase):
	"""Wrapper for the Case class to reduce repitition

	Parameters:
	-----------
	geometry:           openmc.Geometry; the model's geometry, populated with materials
	mesh_shapes:        list of mesh shapes to tally OpenMC results on
	summary_file:       str, optional; summary file to load geometry from
	                    [Default: "summary.h5"]
	isotropic:          bool, optional; whether to use isotropic elastic
	                    scattering in the lab frame
	                    [Default: False]
	"""
	
	def __init__(self, geometry, mesh_shapes, isotropic=False):
		super().__init__(geometry, NGROUPS, tuple(DOMAINS.values()),
		                 mesh_shapes, isotropic)
