# CMM Correction Factors for crd elements with the B4C posion portion

import numpy as np
from .cumulative import CumulativeMigrationCorrection

# 11-group CMM results
_diffusion_ratios_11 = np.array([
	1.07111,
	1.11400,
	1.03268,
	1.02436,
	0.99089,
	0.97956,
	0.97954,
	0.96031,
	1.05272,
	0.89645,
	1.00701])
_transport_ratios_11 = 1/_diffusion_ratios_11

# 25-group CMM results
_diffusion_ratios_25 = np.array([
	1.02570,
	1.04130,
	1.00688,
	1.01368,
	0.99983,
	1.00507,
	1.02053,
	1.03221,
	1.02990,
	1.02743,
	0.99224,
	0.98231,
	0.98852,
	0.97503,
	0.96227,
	0.98541,
	0.93173,
	0.93325,
	0.95877,
	0.98000,
	0.98888,
	0.96869,
	0.98709,
	0.90881,
	0.95543])
_transport_ratios_25 = 1/_diffusion_ratios_25

# Cumulative Migration Correction objects to be imported
cmm11 = CumulativeMigrationCorrection(11, _transport_ratios_11)
cmm25 = CumulativeMigrationCorrection(25, _transport_ratios_25)
CMMS = {11: cmm11,
        25: cmm25}