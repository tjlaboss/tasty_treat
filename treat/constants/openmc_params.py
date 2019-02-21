# OpenMC Parameters
#
# Reserved IDs and other special parameters for OpenMC

ROOT_LATTICE = 10

ZMIN2D = -1.0
ZMAX2D = +1.0

# MGXS rxn types
ISO_TYPES = ('total', 'fission', 'nu-fission', 'capture', 'chi', 'consistent nu-scatter matrix')
ANISO_TYPES = ISO_TYPES + ("nu-transport", "transport")
MOC_TYPES = ('nu-transport', 'fission', 'nu-fission', 'chi', 'consistent nu-scatter matrix')

# Numbers of mesh divisions per core element for the default simulation meshes
DEFAULT_DIVISIONS = (1, 2, 4, 5)

# File names
IDS_PICKLE = "ids_to_keys.pkl"
