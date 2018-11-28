# Libraries

from .serpent_materials import get_serpent_materials
from .batman_materials import get_batman_materials
from .nrl_materials import get_nrl_library
from .backup_materials import get_backup_library


LIBRARIES = {
	"SERPENT": get_serpent_materials,
	"INL"    : get_serpent_materials,
	"NRL"    : get_nrl_library,
	"KAICHAO": get_nrl_library,
	"BATMAN" : get_batman_materials,
	"HAUGEN" : get_batman_materials,
	"BACKUP" : get_backup_library,
}

def get_library(name, *args):
	if name is not None:
		return LIBRARIES[name.upper()](*args)
