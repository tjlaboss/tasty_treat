# CMM Correction Factors for crd elements with the graphite follower portion

import numpy as np
from .cumulative import CumulativeMigrationCorrection

# 11-group CMM results
_diffusion_ratios_11 = np.array([
	1.09314,
	1.11817,
	1.03296,
	1.03553,
	1.03126,
	1.03176,
	1.03231,
	1.03535,
	1.03510,
	1.04753,
	1.10179])
_transport_ratios_11 = 1/_diffusion_ratios_11

# 25-group CMM results
_diffusion_ratios_25 = np.array([
	1.04410,
	1.05715,
	1.01776,
	1.01541,
	1.00350,
	1.00375,
	1.02187,
	1.03214,
	1.03055,
	1.03594,
	1.03070,
	1.03188,
	1.03122,
	1.03067,
	1.03045,
	1.03549,
	1.04862,
	1.03125,
	1.03543,
	1.03041,
	1.03329,
	1.03512,
	1.03648,
	1.03865,
	1.08028])
_transport_ratios_25 = 1/_diffusion_ratios_25

# Cumulative Migration Correction objects to be imported
cmm11 = CumulativeMigrationCorrection(11, _transport_ratios_11)
cmm25 = CumulativeMigrationCorrection(25, _transport_ratios_25)
CMMS = {11: cmm11,
        25: cmm25}