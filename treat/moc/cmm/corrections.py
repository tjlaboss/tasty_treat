# Corrections
#
# Correction factors for the transport and scattering cross sections by group

from . import fuel, crd_follower, crd_poison

CORRECTIONS = {
	# The 3 foundational CMM corrections
	"Fuel"             : fuel.CMMS,
	"Crd Follower"     : crd_follower.CMMS,
	"Crd Poison"       : crd_poison.CMMS,
	# Connect the remaining keys to the appropriate tally
	"Reflector"        : fuel.CMMS,
	"Fuel 2D"          : fuel.CMMS,
	"Zircaloy Dummy 2D": fuel.CMMS,
	"Aluminum Dummy 2D": fuel.CMMS,
	"Crd B4C 2D"       : crd_poison.CMMS,
	"Crd Graphite 2D"  : crd_follower.CMMS
}


