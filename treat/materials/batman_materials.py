# BATMAN Materials
# 
# Materials from the BATMAN report: INL/ EXT-15-35372
#
# The vast majority of this was done by Carl Haugen (cchaugen@mit.edu).
# I (Travis) don't know for sure how this all works or where some of the
# equations came from. Every material composition that was given in the
# BATMAN was reproduced here. The rest were educated guesses.
#
# ...anyhow, I adapted that materials module to make a MaterialLib().

from collections import OrderedDict
from .material_lib import MaterialLib, TreatMaterial
from openmc.data import atomic_mass, atomic_weight

## Data
_MB10 = atomic_mass('B10')
_MB11 = atomic_mass('B11')
_MU234 = atomic_mass('U234')
_MU235 = atomic_mass('U235')
_MU236 = atomic_mass('U236')
_MU238 = atomic_mass('U238')

# Tunable boron impurity in the fuel. Set here to allow importing into the elements module when generating fuel elements, so that
# boron impurity doesn't need to be set by the user separately in two different files
_wBpFuels = [0.0000059, 0.0000076]  # 5.9 ppm boron by weight is the recommended boron
# impurity in the fuel in BATMAN, but 7.6 ppm is also cited in the original report
_wBpGraphite = [0.0000059,
                0.0000076]  # In case you want to set graphite boron impurity to something other than the 1 ppm CP2 default
# Here set to be the same values as in the fuel.
# PLEASE NOTE there are currently other differences in the impurities in the definitions besides boron ppm


def get_batman_materials():
	"""TODO: Implement `graphite_sab`, `fuel_sab`, and other arguments"""
	
	# Initialize openmc material dictionary
	mats = OrderedDict()
	
	##############################################
	# Create materials that use natural abundances
	##############################################
	
	# Create air material
	mats['Air'] = TreatMaterial(name='Air')
	mats['Air'].temperature = 300
	mats['Air'].set_density('g/cc', 0.000616)
	mats['Air'].add_nuclide('O16', 0.2095, 'ao')
	mats['Air'].add_element('N', 0.7809, 'ao')
	mats['Air'].add_element('Ar', 0.00933, 'ao')
	mats['Air'].add_nuclide('C0', 0.00027, 'ao')
	
	# Create B4C control rod material
	# Original pre 1960 material (low packing density)
	mats['B4C Rod Old'] = TreatMaterial(name='Pre 1960 B4C Control Rods')
	mats['B4C Rod Old'].temperature = 300
	mats['B4C Rod Old'].set_density('g/cc', 1.60)
	mats['B4C Rod Old'].add_element('B', 0.7826, 'wo')
	mats['B4C Rod Old'].add_nuclide('C0', 0.2174, 'wo')
	
	# Create B4C control rod material
	# New post 1967 material (high packing density)
	# Did not create a material for the 1960-1967
	# control rods because am unsure of the composition of
	# and density contribution from the epoxy resin that was present.
	mats['B4C Rod'] = TreatMaterial(name='Post 1967 B4C Control Rods')
	mats['B4C Rod'].temperature = 300
	mats['B4C Rod'].set_density('g/cc', 1.80)
	mats['B4C Rod'].add_element('B', 0.7826, 'wo')
	mats['B4C Rod'].add_nuclide('C0', 0.2174, 'wo')
	
	# Create He gas gap material
	mats['Helium'] = TreatMaterial(name='Helium')
	mats['Helium'].temperature = 300
	mats['Helium'].set_density('g/cc', 0.0015981)
	mats['Helium'].add_element('He', 1.0, 'wo')
	
	# Create zircaloy 4 material
	mats['Zirc4'] = TreatMaterial(name='Zircaloy 4', key="zirc")
	mats['Zirc4'].temperature = 300
	mats['Zirc4'].set_density('g/cc', 6.56)
	mats['Zirc4'].add_element('Cr', 0.0010, 'wo')
	mats['Zirc4'].add_element('Fe', 0.0021, 'wo')
	mats['Zirc4'].add_element('Zr', 0.9824, 'wo')
	mats['Zirc4'].add_element('Sn', 0.0145, 'wo')
	
	# Create Zircaloy 3
	# See Section 3.3.2 of the BATMAN report
	zr3 = TreatMaterial(name='Zircaloy 3')
	zr3.temperature = 300
	zr3.set_density("g/cc", 6.53)
	zr3_elements_ppm = {'C' : 120, 'N': 51, 'O': 920, 'H': 22,
	                    'Sn': 3000, 'Fe': 2600}
	for e in zr3_elements_ppm:
		wt = zr3_elements_ppm[e]*1E-6
		if e == 'O':
			zr3.add_nuclide('O16', wt, 'wo')
		elif e == 'C':
			zr3.add_nuclide('C0', wt, 'wo')
		else:
			zr3.add_element(e, wt, 'wo')
	zr3_wt = 1 - sum(zr3_elements_ppm.values())*1E-6
	zr3.add_element('Zr', zr3_wt, 'wo')
	mats['Zirc3'] = zr3
	
	# Create Kannigen Nickel material
	mats['K Nickel'] = TreatMaterial(name='Kannigen Nickel')
	mats['K Nickel'].temperature = 300
	mats['K Nickel'].set_density('g/cc', 7.95)
	mats['K Nickel'].add_element('Ni', 0.895, 'wo')
	mats['K Nickel'].add_element('P', 0.105, 'wo')
	
	# Create Lead material
	mats['Lead'] = TreatMaterial(name='Lead B29')
	mats['Lead'].temperature = 300
	mats['Lead'].set_density('g/cc', 11.34)
	mats['Lead'].add_element('Pb', 0.9994, 'wo')
	# The following are the max weight percents of the only two elements with > 0.002 wt %, and will be
	# approximated as making up the balance
	mats['Lead'].add_element('Bi', 0.0005, 'wo')
	mats['Lead'].add_element('Ag', 0.0001, 'wo')
	
	# Create Chrome material
	mats['Chromium'] = TreatMaterial(name='Chrome Plating')
	mats['Chromium'].temperature = 300
	mats['Chromium'].set_density('g/cc', 7.2)
	mats['Chromium'].add_element('Cr', 1.0, 'wo')
	
	# Aluminum compositions
	#
	# Aluminum 1100
	# Standard composition from the BATMAN report
	# Section 3.4.1, Table 3.15
	al1100 = TreatMaterial(name="Aluminum 1100")
	al1100.temperature = 300
	al1100.set_density("g/cc", 2.70)
	# According to Aluminum.org, Al1001 must be >= 99% Al
	# impurities have been estimated from the remaining 1%.
	al1001_elements_pct = {"Fe": 0.33, "Si": 0.57,  # Si + Fe < 0.95%
	                       "Cu": 0.1,  # 0.05 < Cu < 0.20
	                       "Al": 99.0}
	for e in al1001_elements_pct:
		wt = al1001_elements_pct[e]/100.0
		al1100.add_element(e, wt, 'wo')
	mats['Al1100'] = al1100
	
	# Aluminum 6061
	# Standard composition from the BATMAN report
	# Section 3.4.2, Table 3.16
	al6061 = TreatMaterial(name="Aluminum 6061")
	al6061.temperature = 300
	al6061.set_density("g/cc", 2.70)
	# Guesses at the impurities
	al6061_elements_pct = {"Fe": 0.33, "Si": 0.57,
	                       "Cu": 0.20, "Mg": 1.0
	                       }
	for e in al6061_elements_pct:
		wt = al6061_elements_pct[e]/100.0
		al6061.add_element(e, wt, 'wo')
	al6061.add_element("Al", 1 - sum(al6061_elements_pct.values())/100.0, 'wo')
	mats['Al6061'] = al6061
	
	# Create aluminum 6063 material
	# Composition of Aluminum 6063 taken from material supplier "onlinemetals.com"
	# Used these values to estimate reasonable values
	# Seems to be consistent with wikipedia and aalco (British metal supplier)
	mats['Al6063'] = TreatMaterial(name='Aluminum 6063')
	mats['Al6063'].temperature = 300
	mats['Al6063'].set_density('g/cc', 2.685)
	mats['Al6063'].add_element('Si', 0.0040, 'wo')  # Value between 0.20 w% and 0.60 w%
	mats['Al6063'].add_element('Mg', 0.00675, 'wo')  # Value between 0.45 w% and 0.90 w%
	mats['Al6063'].add_element('Fe', 0.0025, 'wo')  # Maximum value of 0.35 w%
	mats['Al6063'].add_element('Al', 0.98675, 'wo')  # Balance
	
	# Steels
	#
	# 3.5.1 Low-Carbon Mild Steel
	# As described in Table 3.18 of the BATMAN Report
	mild_steel = TreatMaterial(name="Mild Steel")
	mild_steel.set_density("g/cc", 7.835)
	mild_steel_element_pcts = {"C" : 0.15,  # Min. for 1018, mid-range for A36
	                           "Mn": 1.0,  # Max. for 1018, lower-range for A36
	                           "Si": 0.15,  # Not in 1018, min. for A36
	                           }
	for e in mild_steel_element_pcts:
		wt = mild_steel_element_pcts[e]/100.0
		if e == "C":
			mild_steel.add_nuclide("C0", wt, 'wo')
		else:
			mild_steel.add_element(e, wt, 'wo')
	mild_steel.add_element("Fe", 1 - sum(mild_steel_element_pcts.values())/100.0, 'wo')
	mats['Mild Steel'] = mild_steel
	
	# Create carbon steel material
	mats['Carbon Steel'] = TreatMaterial(name='Carbon Steel')
	mats['Carbon Steel'].temperature = 300
	mats['Carbon Steel'].set_density('g/cc', 7.835)
	mats['Carbon Steel'].add_nuclide('C0', 0.0018, 'wo')
	mats['Carbon Steel'].add_element('Mn', 0.0085, 'wo')
	mats['Carbon Steel'].add_element('Si', 0.0020, 'wo')
	mats['Carbon Steel'].add_element('Cr', 0.0010, 'wo')
	mats['Carbon Steel'].add_element('Ni', 0.0010, 'wo')
	mats['Carbon Steel'].add_element('Cu', 0.0010, 'wo')
	mats['Carbon Steel'].add_element('Fe', 0.9847, 'wo')
	
	# Create stainless steel material
	mats['SS304'] = TreatMaterial(name='Stainless Steel 304')
	mats['SS304'].temperature = 300
	mats['SS304'].set_density('g/cc', 8.00)
	mats['SS304'].add_nuclide('C0', 0.0005, 'wo')
	mats['SS304'].add_element('Cr', 0.1900, 'wo')
	mats['SS304'].add_element('Ni', 0.1000, 'wo')
	mats['SS304'].add_element('Mn', 0.0100, 'wo')
	mats['SS304'].add_element('Si', 0.0040, 'wo')
	mats['SS304'].add_element('Fe', 0.6955, 'wo')
	
	# Create boron steel
	# The composition of boron steel was not provided in the BATMAN report
	# Wide-ish ranges of values were obtained from http://www.ssab.us/products/brands/ssab-boron-steel
	boron_steel = TreatMaterial(name="SSAB Boron-Steel")
	boron_steel.set_density("g/cc", 7.8)
	bsteel_element_pcts = {"C" : 0.28,
	                       "Si": 0.2,
	                       "Mn": 1.3,
	                       "Cr": 0.2,
	                       "B" : 0.003}  # 0.0008 - 0.0050 wt%
	for e in bsteel_element_pcts:
		wt = bsteel_element_pcts[e]/100.0
		if e == "C":
			boron_steel.add_nuclide('C0', wt, 'wo')
		else:
			boron_steel.add_element(e, wt, 'wo')
	boron_steel.add_element("Fe", 1 - sum(bsteel_element_pcts.values())/100.0, 'wo')
	mats['Boron Steel'] = boron_steel
	
	# Create boral (Section 3.8.2)
	"""Data regarding the Boral utilized at TREAT is not available. However, description of the Boral is
	very similar to descriptive data available for the early development of Boral at ORNL."""
	# Impurities have been neglected. All boral is far from the fuel,
	# and the neutron interactions will be dominated by the boron anyway.
	boral = TreatMaterial(name="50:50 ORNL Boral")
	boral.set_density("g/cc", 2.53)
	boral.add_element("B", 0.36, "wo")
	boral.add_element("Al", 0.089, "wo")
	boral.add_nuclide("C0", 0.551, "wo")
	mats['Boral'] = boral
	
	# Create concrete material for the excore shielding and other structural needs
	mats['Concrete'] = TreatMaterial(name='High-Density Heavy Magnetite and / or Hematite Concrete')
	mats['Concrete'].temperature = 300
	mats['Concrete'].set_density('g/cc', 3.364)  # Take the midpoint value for density
	mats['Concrete'].add_element('Ca', (0.074*(40.078/(40.078 + 16))), 'wo')
	mats['Concrete'].add_element('Si', (0.049*(28.085/(28.085 + 2*16))), 'wo')
	mats['Concrete'].add_element('Al', (0.030*(2*26.982/(2*26.982 + 3*16))), 'wo')
	mats['Concrete'].add_element('Fe', (0.5552*(2*55.845/(2*55.845 + 3*16)) + 0.1290*(55.845/(55.845 + 16))), 'wo')
	mats['Concrete'].add_element('Mg', (0.024*(24.305/(24.305 + 16))), 'wo')
	mats['Concrete'].add_element('S', (0.002*(32.06/(32.06 + 3*16))), 'wo')
	mats['Concrete'].add_element('K', (0.0005*(2*39.098/(2*39.098 + 16))), 'wo')
	mats['Concrete'].add_element('Na', (0.0005*(2*22.990/(2*22.990 + 16))), 'wo')
	mats['Concrete'].add_element('Mn', (0.001*(54.938/(54.938 + 16))), 'wo')
	mats['Concrete'].add_element('V', (0.0006*(2*50.942/(2*50.942 + 3*16))), 'wo')
	mats['Concrete'].add_element('Cr', (0.0001*(2*51.996/(2*51.996 + 3*16))), 'wo')
	mats['Concrete'].add_element('Ti', (0.029*(47.867/(47.867 + 2*16))), 'wo')
	mats['Concrete'].add_element('H', (0.1051*(2*1.008/(2*1.008 + 16))), 'wo')
	mats['Concrete'].add_nuclide('O16', (0.074*(16/(40.078 + 16)) + 0.049*(2*16/(28.085 + 2*16)) +
	                                     0.030*(3*16/(2*26.982 + 3*16)) + 0.5552*(3*16/(2*55.845 + 3*16)) +
	                                     0.1290*(16/(55.845 + 16)) + 0.024*(16/(24.305 + 16)) +
	                                     0.002*(3*16/(32.06 + 3*16)) + 0.0005*(16/(2*39.098 + 16)) +
	                                     0.0005*(16/(2*22.990 + 16)) + 0.001*(16/(54.938 + 16)) +
	                                     0.0006*(3*16/(2*50.942 + 3*16)) + 0.0001*(3*16/(2*51.996 + 3*16)) +
	                                     0.029*(2*16/(47.867 + 2*16)) + 0.1051*(16/(2*1.008 + 16))), 'wo')
	
	# Create pure graphite material modeled off of standard nuclear grade graphite
	# This should be used to represent the Chicago pile graphite in TREAT
	# Density of graphite from Kord's document - low because of ~25% void fraction
	mats['Graphite'] = TreatMaterial(name='Chicago Pile Graphite')
	mats['Graphite'].temperature = 300
	mats['Graphite'].set_density('g/cc', 1.67)
	wBpRef = 0.000001  # Take boron impurity to be 1 ppm by weight
	wHpRef = 0.0002*(2/18)  # Take water impurity to be 200 ppm by weight
	wOpRef = 0.0002*(16/18)  # Take water impurity to be 200 ppm by weight
	wCpRef = 1.0 - wBpRef - wHpRef - wOpRef  # Carbon accounts for the balance
	mats['Graphite'].add_nuclide('C0', wCpRef, 'wo')
	mats['Graphite'].add_element('B', wBpRef, 'wo')
	mats['Graphite'].add_nuclide('O16', wOpRef, 'wo')
	mats['Graphite'].add_element('H', wHpRef, 'wo')
	mats['Graphite'].add_s_alpha_beta('c_Graphite', fraction=1.0)
	
	##############################################
	# Create special materials
	##############################################
	
	########## Graphite with Boron Impurity #################
	
	# Create pure graphite material with the option for easily variable boron amount
	# Assume that there are the same impurities as in fuel graphite
	# Currently believe this material definition is unnecessary, but leaving it in should
	# it ever be needed in the future
	# Density of graphite from Kord's document - low because of ~25% void fraction
	for boron in _wBpGraphite:  # wBpGraphite defined at the beginning of the file
		boron_name = boron*1E6
		mat_graph = 'Graphite {0:1.1f} ppm'.format(boron_name)
		mat_graph_name = 'Graphite {0:1.1f} ppm Boron Impurity'.format(boron_name)
		mats[mat_graph] = TreatMaterial(name=mat_graph_name)
		mats[mat_graph].temperature = 300
		mats[mat_graph].set_density('g/cc', 1.67)
		wFepRef = 0.000267
		wVpRef = 0.00003
		wHpRef = 0.00097  # 970 ppm due to incomplete baking of the graphite blocks
		# TODO Am I missing an oxygen impurity?
		wCpRef = 1.0 - boron - wFepRef - wVpRef - wHpRef
		mats[mat_graph].add_nuclide('C0', wCpRef, 'wo')
		mats[mat_graph].add_element('B', boron, 'wo')
		mats[mat_graph].add_element('Fe', wFepRef, 'wo')
		mats[mat_graph].add_element('V', wVpRef, 'wo')
		mats[mat_graph].add_element('H', wHpRef, 'wo')
		mats[mat_graph].add_s_alpha_beta('c_Graphite', fraction=1.0)
	
	#################### TREAT Fuel #########################
	
	#############################################################################
	# From BATMAN Report
	# Specify fuel compositions to be calculated
	# Weight percent of Uranium in fuel
	wUpFuel = 0.00211
	enr_25 = 0.93239
	enr_24 = 0.00910
	enr_26 = 0.00428
	enr_28 = 0.05413
	den = 1.73
	# Density is only slightly higher than graphite because of the low uranium weight percent
	
	# After baking, the UO_2 in the fuel was found to typically have a slight surplus of oxygen
	O_to_U_ratio = 2.06
	
	# Loop around compositions and manually calculate
	for wBpFuel in _wBpFuels:  # wBpFuels defined at the beginning of the file
		
		# Calculate molar mass of Uranium
		MU = 1.0/(enr_24/_MU234 + enr_25/_MU235 + enr_26/_MU236 + enr_28/_MU238)
		
		# Determine molar mass of UO2
		MUO2 = MU + O_to_U_ratio*atomic_weight('O')
		
		# Weight percent of Oxygen in fuel
		# TODO determine if there should be addition oxygen associated with any water contributing
		#      to the hydrogen impurity (seems unlikely to be a significant contributor)
		wOpFuel = wUpFuel*(1.0 - MU/MUO2)
		
		# Weight percent of Iron in fuel
		wFepFuel = 0.000267
		
		# Weight percent of Vanadium in fuel
		wVpFuel = 0.00003
		
		# Weight percent of hydrogen in the fuel
		wHpFuel = 0.00097  # 970 ppm due to incomplete baking of the graphite blocks
		# NOTE: This weight percent of hydrogen is uncertain. The 970 ppm comes from an experiment
		#       simulating TREAT fuel element baking carried out by B&W. However, this experiment
		#       only went up to 900 C during the baking, while the real fuel blocks were baked at
		#       950 C. While both of these temperatures are too low to fully graphitize the carbon
		#       (59% has often been quoted as the graphitization fraction in TREAT fuel) and cause
		#       the release of the hydrogen that came from the hydrocarbons used to supply the carbon
		#       for the graphite, the 950 C temperatures would cause TREAT fuel material to have less
		#       hydrogen than the B&W test. The real TREAT fuel hydrogen impurity will be somewhere
		#       between the ~ 0.1 wgt % in the B&W test and the < 0.005 wgt % seen in carbon fully
		#       graphitized at 3000 C. Since the hydrogen impurity is likely significantly closer to
		#       the former value, it will be used for the time being. This is something that should
		#       be looked at further in the future, since it seems to be accepted that hydrogen will
		#       act as a poison in this reactor, and neglecting it completely (as some early models
		#       from INL, MIT NRL, and Michigan seem to be doing) is unphysical, and the magnitude of
		#       the effect is unknown.
		
		# Weight percent of Graphite in fuel
		wCpFuel = 1.0 - wUpFuel - wOpFuel - wFepFuel - wVpFuel - wBpFuel - wHpFuel
		
		# Calculate Uranium isotopic weight fractions
		w_24 = enr_24*wUpFuel
		w_25 = enr_25*wUpFuel
		w_26 = enr_26*wUpFuel
		w_28 = enr_28*wUpFuel
		
		# Finally, add each of these materials to the fuel itself
		boron_name = wBpFuel*1E6
		mat_fuel = 'Fuel {0:1.1f} ppm'.format(boron_name)
		mat_fuel_name = 'Fuel {0:1.1f} ppm Boron Impurity'.format(boron_name)
		mats[mat_fuel] = TreatMaterial(name=mat_fuel_name, key="fuel")
		mats[mat_fuel].temperature = 300
		mats[mat_fuel].set_density('g/cc', den)
		mats[mat_fuel].add_nuclide('C0', wCpFuel, 'wo')
		mats[mat_fuel].add_element('B', wBpFuel, 'wo')
		mats[mat_fuel].add_element('Fe', wFepFuel, 'wo')
		mats[mat_fuel].add_element('V', wVpFuel, 'wo')
		mats[mat_fuel].add_element('H', wHpFuel, 'wo')
		mats[mat_fuel].add_nuclide('O16', wOpFuel, 'wo')
		mats[mat_fuel].add_nuclide('U234', w_24, 'wo')
		mats[mat_fuel].add_nuclide('U235', w_25, 'wo')
		mats[mat_fuel].add_nuclide('U236', w_26, 'wo')
		mats[mat_fuel].add_nuclide('U238', w_28, 'wo')
		mats[mat_fuel].add_s_alpha_beta('c_Graphite', fraction=0.59)
	
	###################################################################
	# Create some material definitions that will be needed for M8Cal
	###################################################################
	
	# Create dysprosium material (density data from wikipedia)
	mats['Dysprosium'] = TreatMaterial(name='Dysprosium absorber')
	mats['Dysprosium'].temperature = 300
	mats['Dysprosium'].set_density('g/cc', 8.54)
	mats['Dysprosium'].add_element('Dy', 1.000, 'wo')
	
	# Create sodium bonding material (density data from wikipedia)
	mats['Sodium'] = TreatMaterial(name='Sodium bonding')
	mats['Sodium'].temperature = 300
	mats['Sodium'].set_density('g/cc', 0.968)
	mats['Sodium'].add_element('Na', 1.000, 'wo')
	
	# Create helium-argon inert gas material for experiment plenum (density data from wikipedia)
	mats['HeAr'] = TreatMaterial(name='75% He, 25% Ar inert gas mixture')
	mats['HeAr'].temperature = 300
	mats['HeAr'].set_density('g/cc', (0.75*0.0001786 + 0.25*0.001784))
	mats['HeAr'].add_element('He', 0.750, 'wo')
	mats['HeAr'].add_element('Ar', 0.250, 'wo')
	
	# Create the fuel material for pin T-433 and H-307
	# TODO the material composition definitions in the M8Cal report did not add up to 100%
	#      Some approximations / assumptions were made
	mats['M8 Fuel 1'] = TreatMaterial(name='Fuel material for M8 Cal pins T-433 and H-307')
	mats['M8 Fuel 1'].temperature = 300
	mats['M8 Fuel 1'].set_density('g/cc', 15.8)
	mats['M8 Fuel 1'].add_element('Zr', 0.097 + 0.0064, 'wo')  # Unspecified general material added as Zr
	mats['M8 Fuel 1'].add_nuclide('U234', 0.0063*0.8966, 'wo')
	mats['M8 Fuel 1'].add_nuclide('U235', 0.6550*0.8966, 'wo')
	mats['M8 Fuel 1'].add_nuclide('U236', 0.0037*0.8966, 'wo')
	mats['M8 Fuel 1'].add_nuclide('U238', (0.305 + 0.03)*0.8966, 'wo')  # Unspecified Uranium added as U238
	
	# Create the fuel material for pin T-462
	# TODO the material composition definitions in the M8Cal report did not add up to 100%
	#      Some approximations / assumptions were made
	mats['M8 Fuel 2'] = TreatMaterial(name='Fuel material for M8 Cal pins T-462')
	mats['M8 Fuel 2'].temperature = 300
	mats['M8 Fuel 2'].set_density('g/cc', 15.8)
	mats['M8 Fuel 2'].add_element('Zr', 0.0978 + 0.0044, 'wo')  # Unspecified general material added as Zr
	mats['M8 Fuel 2'].add_nuclide('U234', 0.0056*0.7071, 'wo')
	mats['M8 Fuel 2'].add_nuclide('U235', 0.5688*0.7071, 'wo')
	mats['M8 Fuel 2'].add_nuclide('U236', 0.0032*0.7071, 'wo')
	mats['M8 Fuel 2'].add_nuclide('U238', 0.4224*0.7071, 'wo')  # No unspecified Uranium to add
	mats['M8 Fuel 2'].add_nuclide('Pu239', 0.9384*0.1907, 'wo')
	mats['M8 Fuel 2'].add_nuclide('Pu240', 0.0582*0.1907, 'wo')
	mats['M8 Fuel 2'].add_nuclide('Pu241', 0.0029*0.1907, 'wo')
	mats['M8 Fuel 2'].add_nuclide('Pu242', 0.0005*0.1907, 'wo')  # No unspecified Plutonium to add
	
	# Create the fuel material for pin H-316
	# TODO the material composition definitions in the M8Cal report did not add up to 100%
	#      Some approximations / assumptions were made
	mats['M8 Fuel 3'] = TreatMaterial(name='Fuel material for M8 Cal pins H-316')
	mats['M8 Fuel 3'].temperature = 300
	mats['M8 Fuel 3'].set_density('g/cc', 15.8)
	mats['M8 Fuel 3'].add_element('Zr', 0.1000, 'wo')  # No unspecified general material to add
	mats['M8 Fuel 3'].add_nuclide('U234', 0.0049*0.6198, 'wo')
	mats['M8 Fuel 3'].add_nuclide('U235', 0.4608*0.6198, 'wo')
	mats['M8 Fuel 3'].add_nuclide('U236', 0.0024*0.6198, 'wo')
	mats['M8 Fuel 3'].add_nuclide('U238', (0.5326 - 0.0007)*0.6198, 'wo')  # Extra Uranium taken away from U238
	mats['M8 Fuel 3'].add_nuclide('Pu239', (0.8726 - 0.0004)*0.2802, 'wo')  # Extra Plutonium taken away from Pu239
	mats['M8 Fuel 3'].add_nuclide('Pu240', 0.1181*0.2802, 'wo')
	mats['M8 Fuel 3'].add_nuclide('Pu241', 0.0075*0.2802, 'wo')
	mats['M8 Fuel 3'].add_nuclide('Pu242', 0.0022*0.2802, 'wo')
	
	###############################################################################
	
	# Generate the library
	batman_library = MaterialLib()
	for _key, _mat in mats.items():
		batman_library.add_material(_mat, _key.lower())
	
	return batman_library
