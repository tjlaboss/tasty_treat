# CMM Correction Factors for plain fuel elements

import numpy as np
from .cumulative import CumulativeMigrationCorrection

# 11-group CMM results
_diffusion_ratios_11 = np.array([
	1.11499,
	1.11897,
	1.02546,
	1.03141,
	1.03291,
	1.03104,
	1.03133,
	1.03229,
	1.03543,
	1.04577,
	1.11985])
_transport_ratios_11 = 1/_diffusion_ratios_11

# 25-group CMM results
_diffusion_ratios_25 = np.array([
	1.06448,
	1.06876,
	1.02020,
	1.01679,
	0.99973,
	1.00372,
	1.02078,
	1.02389,
	1.02942,
	1.03104,
	1.03332,
	1.03205,
	1.03001,
	1.02798,
	1.03292,
	1.04388,
	1.02530,
	1.03698,
	1.03376,
	1.02964,
	1.03102,
	1.03596,
	1.03299,
	1.04040,
	1.08603])
_transport_ratios_25 = 1/_diffusion_ratios_25

# Cumulative Migration Correction objects to be imported
cmm11 = CumulativeMigrationCorrection(11, _transport_ratios_11)
cmm25 = CumulativeMigrationCorrection(25, _transport_ratios_25)
CMMS = {11: cmm11,
        25: cmm25}
