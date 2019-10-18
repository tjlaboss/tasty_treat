# Params

NGROUPS = (11, 25)
PITCH = 10.14
NLAT = 19
HALF_FUEL = 6
HALF_REFL = 4
MIDDLE = 0.0
XMIN = -HALF_FUEL * PITCH
XMAX = +HALF_FUEL * PITCH
YMAX = +PITCH / 2.0
YMIN = -PITCH / 2.0
REFL_ID = 8
FUEL_ID = 9
DATA_DIR = "../inl_mcfuel/heterogeneous/same/"
#STATEPOINT = DATA_DIR + "statepoint.100.h5"
STATEPOINT = DATA_DIR + "statepoint_same.h5"
CELL_LIBS = {11: "cell_lib_11",
             25: "cell_lib_25"}
MATERIAL_LIBS = {11: "material_lib_11",
                 25: "material_lib_25"}
NAZIM = 32
DAZIM = 0.1
