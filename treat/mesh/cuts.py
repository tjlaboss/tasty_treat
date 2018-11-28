# Mesh Cuts
#
# Replicate the mesh cuts from the Serpent model

import sys; sys.path.append("..")
import numpy as np

# Height of layers (cm)
layers = np.array(
	[3.486, 27, 22.68875, 8.89, 0.762, 20, 31.59375, 5, 5, 39.37375, 20, 0.762, 22.06625, 13.64, 27, 8.02675])
# Number of axial slices per layer
n_cuts = np.array([1, 5, 4, 2, 1, 4, 5, 1, 1, 7, 4, 1, 4, 3, 5, 2])
# delta-z for each layer's slices
dzs = layers/n_cuts

# Where tallies start:
#Z0 = c.struct_CoreGuide_top  # cm; z-position of the bottom of the element
#Z0 = c.struct_LowerZrSpace_top - 62.8267500
Z0 = 122.99# + 3.486
n = len(layers)
heights = np.zeros(n)
for i in range(n):
	heights[i] = layers[:i+1].sum()
heights += Z0

NX = 1
NY = 1
NZ = n_cuts.sum()
