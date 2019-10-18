"""Tabulated group structures stored as openmc.mgxs.EnergyGroups objects."""

from openmc.mgxs import EnergyGroups
import numpy as np

# Create a global dictionary to store all energy group structures
ALL_GROUP_NUMBERS = (1, 2, 4, 8, 11, 12, 16, 18, 25, 40, 70)
group_structures = dict()

# Create a sub-dictionary for the CASMO energy group structures
casmo = dict()

# 2-group structure
casmo['1-group'] = EnergyGroups()
group_edges = np.array([0., 20.])
casmo['1-group'].group_edges = group_edges

# 2-group structure
casmo['2-group'] = EnergyGroups()
group_edges = np.array([0., 0.625e-6, 20.])
casmo['2-group'].group_edges = group_edges

# 4-group structure
casmo['4-group'] = EnergyGroups()
group_edges = np.array([0., 0.625e-6, 5.53e-3, 821.e-3, 20.])
casmo['4-group'].group_edges = group_edges

# 8-group structure
casmo['8-group'] = EnergyGroups()
group_edges = np.array([0., 0.058e-6, 0.14e-6, 0.28e-6,
                        0.625e-6, 4.e-6, 5.53e-3, 821.e-3, 20.])
casmo['8-group'].group_edges = group_edges

# 12-group structure
casmo['12-group'] = EnergyGroups()
group_edges = np.array([0., 0.03e-6, 0.058e-6, 0.14e-6,
                        0.28e-6, 0.35e-6, 0.625e-6, 4.e-6,
                        48.052e-6, 5.53e-3, 821.e-3, 2.231, 20.])
casmo['12-group'].group_edges = group_edges

# 16-group structure
casmo['16-group'] = EnergyGroups()
group_edges = np.array([0., 0.03e-6, 0.058e-6, 0.14e-6,
                        0.28e-6, 0.35e-6, 0.625e-6, 0.85e-6,
                        0.972e-6, 1.02e-6, 1.097e-6, 1.15e-6,
                        1.3e-6, 4.e-6, 5.53e-3, 821.e-3, 20.])
casmo['16-group'].group_edges = group_edges

# 18-group structure
casmo['18-group'] = EnergyGroups()
group_edges = np.array([0., 0.058e-6, 0.14e-6, 0.28e-6, 0.625e-6,
                        0.972e-6, 1.15e-6, 1.855e-6, 4.e-6, 9.877e-6,
                        15.968e-6, 148.73e-6, 5.53e-3, 9.118e-3,
                        111.e-3, 500.e-3, 821.e-3, 2.231, 20.])
casmo['18-group'].group_edges = group_edges

# 25-group structure
casmo['25-group'] = EnergyGroups()
group_edges = np.array([0., 0.03e-6, 0.058e-6, 0.14e-6, 0.28e-6,
                        0.35e-6, 0.625e-6, 0.972e-6, 1.02e-6,
                        1.097e-6, 1.15e-6, 1.855e-6, 4.e-6,
                        9.877e-6, 15.968e-6, 148.73e-6, 5.53e-3,
                        9.118e-3, 111.e-3, 500.e-3, 821.e-3,
                        1.353, 2.231, 3.679, 6.0655, 20.])
casmo['25-group'].group_edges = group_edges

# 40-group structure
casmo['40-group'] = EnergyGroups()
group_edges = np.array([0., 0.015e-6, 0.03e-6, 0.042e-6,
                        0.058e-6, 0.08e-6, 0.1e-6, 0.14e-6,
                        0.18e-6, 0.22e-6, 0.28e-6, 0.35e-6,
                        0.625e-6, 0.85e-6, 0.95e-6, 0.972e-6,
                        1.02e-6, 1.097e-6, 1.15e-6, 1.3e-6,
                        1.5e-6, 1.855e-6, 2.1e-6, 2.6e-6,
                        3.3e-6, 4.e-6, 9.877e-6, 15.968e-6,
                        27.7e-6, 48.052e-6, 148.73e-6, 5.53e-3,
                        9.118e-3, 111.e-3, 500.e-3, 821.e-3,
                        1.353, 2.231, 3.679, 6.0655, 20.])
casmo['40-group'].group_edges = group_edges

# 70-group structure
casmo['70-group'] = EnergyGroups()
group_edges = np.array([0., 0.005e-6, 0.01e-6, 0.015e-6,
                        0.02e-6, 0.025e-6, 0.03e-6, 0.035e-6,
                        0.042e-6, 0.05e-6, 0.058e-6, 0.067e-6,
                        0.08e-6, 0.1e-6, 0.14e-6, 0.18e-6,
                        0.22e-6, 0.25e-6, 0.28e-6, 0.3e-6,
                        0.32e-6, 0.35e-6, 0.4e-6, 0.5e-6,
                        0.625e-6, 0.78e-6, 0.85e-6, 0.91e-6,
                        0.95e-6, 0.972e-6, 0.996e-6, 1.02e-6,
                        1.045e-6, 1.071e-6, 1.097e-6, 1.123e-6,
                        1.15e-6, 1.3e-6, 1.5e-6, 1.855e-6,
                        2.1e-6, 2.6e-6, 3.3e-6, 4.e-6,
                        9.877e-6, 15.968e-6, 27.7e-6, 48.052e-6,
                        75.501e-6, 148.73e-6, 367.26001e-6,
                        906.90002e-6, 1.4251e-3, 2.2395e-3, 3.5191e-3,
                        5.53e-3, 9.118e-3, 15.03e-3, 24.78e-3, 40.85e-3,
                        67.34e-3, 111.e-3, 183.e-3, 302.5e-3, 500.e-3,
                        821.e-3, 1.353, 2.231, 3.679, 6.0655, 20.])
casmo['70-group'].group_edges = group_edges

# Store the sub-dictionary in the global dictionary
group_structures['CASMO'] = casmo

# 11-group structure used by TREAT
treat = dict()
treat['11-group'] = EnergyGroups()
treat['11-group'].group_edges = np.array(
     [1.000E-11, 2.00100E-08, 4.73020E-08, 7.64970E-08,
      2.09610E-07, 6.25000E-07, 8.100030E-06, 1.32700E-04,
      3.48110E-03, 1.15620E-01, 3.32870E+00, 2.00E+01])
group_structures['TREAT'] = treat
