# Serpent Materials
#
# Material definitions for TREAT taken from the Idaho National Laboratory (INL)
# Serpent II models.

from collections import OrderedDict
from .material_lib import MaterialLib
from .treat_material import TreatMaterial

# S(a,b) fractions for the graphite
# INL uses 59% graphitization for both fuel and reflector
GRAPHITE_SAB = 0.59     # Reflector
FUEL_SAB = 0.59         # Fuel


def _add_nuclides(nucdict, material):
	"""Add a dictionary of nuclides to a material using the 'sum' mode.

	Parameters:
	-----------
	:param nucdict:     dictionary of {"nuclide name", nuclide number}
	:param material:    openmc.Material to add the nuclides to
	"""
	for nuc, frac in nucdict.items():
		material.add_nuclide(nuc, frac)
	material.set_density("sum")


def get_serpent_materials(graphite_sab=GRAPHITE_SAB, fuel_sab=FUEL_SAB):
	"""Generate a library of materials using compositions from Serpent models

	Note that not all of the materials specified in the BATMAN report are
	present in the Serpent models from INL. There are others which may have
	been used by the various OpenMC models. These are accessible in the
	"backup" materials library.

	Parameters:
	-----------
	serpent_only:   Boolean; whether to only create the materials which are actually
					present in the Serpent deck.
					[Default: False]
	graphite_sab:   float; partial S(a,b) fraction to use for Graphite materials.
					[Default: 0.59]
	fuel_sab:       float; partial S(a,b) fraction to use for Fuel materials.
					[Default: 0.59]

	Returns:
	--------
	MaterialLib()
	"""
	mats = OrderedDict()
	
	# Normal air, one of many air compositions in the Serpent deck
	air = TreatMaterial(name="Air")
	air_nuclides = {
		"C0" : 7.5811E-09,
		"N14": 3.9484E-05,
		"O16": 1.0608E-05,
	}
	_add_nuclides(air_nuclides, air)
	mats[air.name] = air
	
	# Old boron control rod: Original pre 1960 material (low packing density)
	b4c_old = TreatMaterial(name="Pre 1960 B4C Control Rods",
	                        key="b4c")
	b4c_old_nuclides = {
		"B10": 1.3881E-02,
		"B11": 5.5872E-02,
		"C0" : 1.7438E-02,
	}
	_add_nuclides(b4c_old_nuclides, b4c_old)
	mats["B4C Rod Old"] = b4c_old
	
	# New boron control rod: post 1967 material (high packing density)
	b4c_new = TreatMaterial(name="Post 1967 B4C Control Rods",
	                        key="b4c")
	b4c_new_nuclides = {
		"B10": 1.5616E-02,
		"B11": 6.2854E-02,
		"C0" : 2.3562E-01,
	}
	_add_nuclides(b4c_new_nuclides, b4c_new)
	mats["B4C Rod"] = b4c_new
	
	
	# Zircaloy. Only one composition given; used for Zr3 and Zr4
	# Note that the Serpent deck also defines Zr2 tubing for some models,
	# which is not featured in the OpenMC models to date.
	zirc = TreatMaterial(name="Zircaloy",
	                     key="zirc")
	zirc_nuclides = {
		"B10"  : 1.3751E-07,
		"B11"  : 5.9006E-07,
		"Cr50" : 9.8706E-08,
		"Cr52" : 1.9013E-06,
		"Cr53" : 2.1556E-07,
		"Cr54" : 5.3551E-08,
		"Fe54" : 1.1659E-05,
		"Fe56" : 1.8285E-04,
		"Fe57" : 4.2252E-06,
		"Fe58" : 5.5804E-07,
		"Ni58" : 2.2803E-07,
		"Ni60" : 8.7821E-08,
		"Ni61" : 3.8183E-09,
		"Ni62" : 2.2207E-08,
		"Ni64" : 3.1149E-09,
		"Zr90" : 2.2054E-02,
		"Zr91" : 4.8095E-03,
		"Zr92" : 7.3513E-03,
		"Zr94" : 7.4499E-03,
		"Zr96" : 1.2002E-03,
		"Cd106": 8.7468E-11,
		"Cd108": 6.2277E-11,
		"Cd110": 8.7398E-10,
		"Cd111": 8.9567E-10,
		"Cd112": 1.6885E-09,
		"Cd113": 8.5508E-10,
		"Cd114": 2.0104E-09,
		"Cd116": 5.2411E-10,
		"Sn112": 8.9997E-07,
		"Sn114": 6.1235E-07,
		"Sn115": 3.1545E-07,
		"Sn116": 1.3490E-05,
		"Sn117": 7.1255E-06,
		"Sn118": 2.2471E-05,
		"Sn119": 7.9698E-06,
		"Sn120": 3.0228E-05,
		"Sn122": 4.2957E-06,
		"Sn124": 5.3720E-06,
		"Hf174": 3.5695E-09,
		"Hf176": 1.1471E-07,
		"Hf177": 4.0996E-07,
		"Hf178": 6.0146E-07,
		"Hf179": 3.0030E-07,
		"Hf180": 7.7339E-07,
	}
	_add_nuclides(zirc_nuclides, zirc)
	mats[zirc.key] = zirc
	mats["Zirc3"] = zirc
	mats["Zirc4"] = zirc
	
	# Lead
	##  Note: The Serpent deck mistakenly uses Bismuth instead of lead!! ##
	lead = TreatMaterial(name="Lead that is actually Bismuth",
	                     key="lead")
	lead.add_nuclide("Bi209", 3.2964E-02)
	lead.set_density("sum")
	mats[lead.key] = lead
	
	# Aluminum
	al = TreatMaterial(name="Aluminum")
	al_nuclides = {
		"Al27": 5.9477E-02,
		"Fe54": 2.5591E-05,
		"Fe56": 4.0136E-04,
		"Fe57": 9.2739E-06,
		"Fe58": 1.2249E-06,
	}
	_add_nuclides(al_nuclides, al)
	mats[al.key] = al
	mats["Al1100"] = al
	mats["Al6061"] = al
	mats["Al6063"] = al
	
	# Steel
	steel = TreatMaterial(name="Steel")
	steel_nuclides = {
		"Fe54" : 5.0819E-03,
		"Fe56" : 7.6860E-02,
		"Fe57" : 1.7447E-03,
		"Fe58" : 2.2647E-04,
		"Mo92" : 8.11748E-05,
		"Mo94" : 5.05975E-05,
		"Mo95" : 8.70824E-05,
		"Mo96" : 9.12396E-05,
		"Mo97" : 5.22385E-05,
		"Mo98" : 1.31991E-04,
		"Mo100": 5.26761E-05,
		"C0"   : 1.4000E-03,
	}
	_add_nuclides(steel_nuclides, steel)
	mats["Mild Steel"] = steel
	mats["Carbon Steel"] = steel
	mats["SS304"] = steel
	
	# Concrete. "From Connie", whatever that means
	# Includes S(a,b) tables for H2O and D2O
	concrete = TreatMaterial(name="Concrete")
	concrete_nuclides = {
		"Ca40": 2.5914E-03,
		"Ca42": 1.7296E-05,
		"Ca43": 3.6088E-06,
		"Ca44": 5.5763E-05,
		"Ca46": 1.0693E-07,
		"Ca48": 4.9989E-06,
		"Si28": 1.5236E-03,
		"Si29": 7.7399E-05,
		"Si30": 5.1082E-05,
		"Al27": 1.1921E-03,
		"Fe54": 1.0360E-03,
		"Fe56": 1.6262E-02,
		"Fe57": 3.7557E-04,
		"Fe58": 4.9981E-05,
		"Mg24": 9.5284E-04,
		"Mg25": 1.2063E-04,
		"Mg26": 1.3281E-04,
		"S32" : 4.8069E-05,
		"S33" : 3.7953E-07,
		"S34" : 2.1507E-06,
		"S36" : 5.0604E-09,
		"K39" : 2.0056E-05,
		"K40" : 2.5162E-09,
		"K41" : 1.4474E-06,
		"Na23": 3.2685E-05,
		"Mn55": 2.8557E-05,
		"V50" : 4.0548E-08,
		"V51" : 1.6178E-05,
		"Cr50": 1.1582E-07,
		"Cr52": 2.2335E-06,
		"Cr53": 2.5326E-07,
		"Cr54": 6.3043E-08,
		"Ti46": 5.9935E-05,
		"Ti47": 5.4050E-05,
		"Ti48": 5.3556E-04,
		"Ti49": 3.9303E-05,
		"Ti50": 3.7632E-05,
		"O16" : 4.7228E-02,
		"O17" : 1.7953E-05,
		"H1"  : 2.3634E-02,
		"H2"  : 2.7182E-06,
	}
	_add_nuclides(concrete_nuclides, concrete)
	concrete.add_s_alpha_beta("c_H_in_H2O")
	concrete.add_s_alpha_beta("c_D_in_D2O")
	mats["Concrete"] = concrete
	
	# Graphite--with fractional S(a,b) tables
	graphite = TreatMaterial(name="Graphite")
	graphite_nuclides = {
		"B10" : 3.517E-08,
		"B11" : 1.509E-07,
		"C0"  : 4.9360E-02 + 3.4300E-02,
		"Fe54": 1.054E-06,
		"Fe56": 1.652E-05,
		"Fe57": 3.818E-07,
		"Fe58": 5.043E-08,
	}
	_add_nuclides(graphite_nuclides, graphite)
	graphite.add_s_alpha_beta("c_Graphite", fraction=graphite_sab)
	mats[graphite.name] = graphite
	# Graphite with boron impurity. A placebo, since it's not used in Serpent model.
	mats[graphite.name + " 5.9 ppm"] = graphite
	mats[graphite.name + " 7.6 ppm"] = graphite
	mats[graphite.name + " 9.8 ppm"] = graphite
	
	# Fuel, with real boron impurities and partial S(a,b)
	fuel_nuclides = {
		"C0"  : 5.0874E-02 + 3.5353E-02,
		"U235": 8.6849E-06,
		"U238": 6.2967E-07,
		"Fe54": 6.5286E-07,
		"Fe56": 1.0239E-05,
		"Fe57": 2.3659E-07,
		"Fe58": 3.1248E-08,
		"O16" : 1.8623E-05,
	}
	"""Boron concentration for 7.6 ppm are given in the deck.
	A conversion is done below to get 5.9 ppm.

	There were also values LABELED as 7.6 ppm which were actually
	(7.6/5.9)*7.6 ppm -- or roughly 9.8 ppm.

	I believe the creator of the Serpent deck confused the 5.9 for the 7.6
	and included these as a mistake. Nevertheless, in case these values were
	used for the Serpent calcs, I have included them in this script."""
	b10_76 = 1.4495E-07
	b11_76 = 5.8343E-07
	impurities = OrderedDict()
	impurities[5.9] = (b10_76*5.9/7.6, b11_76*5.9/7.6)
	impurities[7.6] = (b10_76, b11_76)
	impurities[9.8] = (b10_76*7.6/5.9, b11_76*7.6/5.9)
	for b in impurities:
		b10, b11 = impurities[b]
		fname = "Fuel {0:1.1f} ppm".format(b)
		fuel = TreatMaterial(name=fname, key="fuel")
		fuel.add_nuclide("B10", b10)
		fuel.add_nuclide("B11", b11)
		_add_nuclides(fuel_nuclides, fuel)
		fuel.add_s_alpha_beta("c_Graphite", fraction=fuel_sab)
		mats[fname] = fuel
	
	# Dysprosium
	dy = TreatMaterial(name='Dysprosium absorber',
	                   key="dysprosium")
	dy_nuclides = {
		"Er162": 2.1370E-08,
		"Er164": 2.4614E-07,
		"Er166": 5.1507E-06,
		"Er167": 3.5159E-06,
		"Er168": 4.1476E-06,
		"Er170": 2.2923E-06,
		"Ho165": 1.5591E-05,
		"Dy156": 1.7705E-05,
		"Dy158": 3.0036E-05,
		"Dy160": 7.3636E-04,
		"Dy161": 5.9721E-03,
		"Dy162": 8.0544E-03,
		"Dy163": 7.8713E-03,
		"Dy164": 8.9349E-03,
	}
	_add_nuclides(dy_nuclides, dy)
	mats["Dysprosium"] = dy
	
	# Generate the library
	serpent_library = MaterialLib()
	for _key, _mat in mats.items():
		serpent_library.add_material(_mat, _key.lower())
	
	return serpent_library


