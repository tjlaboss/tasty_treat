# Common
#
# Some constants common to many parts of the model

import math
RT2 = math.sqrt(2.0)
TANPI8 = math.tan(math.pi/8)

# Remember that surfaces must go in this order!
ORDER = ("E", "W", "N", "S", "NE", "NW", "SW", "SE")

# Unit conversion
IN = 2.54               # inches to centimeters

# Lattice parameters
ROOT_LATTICE = 10
PITCH = 10.16           # Proper assembly / lattice pitch
HPITCH = PITCH / 2.0
LATTICE_SIZE = 19       # number of element positions across the lattice
LATTICE_WIDTH = PITCH*LATTICE_SIZE

# Upper and lower bounds for 2D models. Doesn"t really matter much.
ZMIN2D = -1.0
ZMAX2D = +1.0

# MGXS reaction types
ISO_TYPES = ("total", "fission", "nu-fission", "capture", "chi", "consistent nu-scatter matrix")
ANISO_TYPES = ISO_TYPES + ("nu-transport", "transport")

