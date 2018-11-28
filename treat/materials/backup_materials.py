# Backup materials
#
# Material definitions that need a home

from collections import OrderedDict
from .material_lib import MaterialLib, TreatMaterial


def get_backup_library():
	"""Generate the library of backup materials.
	
	Returns:
	--------
	MaterialLib()
	"""
	mats = OrderedDict()
	# Helium
	# Not in Serpent
	# Not in NRL
	mats['Helium'] = TreatMaterial(name='Helium')
	mats['Helium'].set_density('g/cc', 0.0015981)
	mats['Helium'].add_nuclide('He4', 1.0)
	
	# Lead
	# Not in NRL
	mats['Lead'] = TreatMaterial(name='Lead B29')
	mats['Lead'].temperature = 300
	mats['Lead'].set_density('g/cc', 11.34)
	mats['Lead'].add_element('Pb', 0.9994, 'wo')
	# The following are the max weight percents of the only two elements with > 0.002 wt %, and will be
	# approximated as making up the balance
	mats['Lead'].add_element('Bi', 0.0005, 'wo')
	mats['Lead'].add_element('Ag', 0.0001, 'wo')
	
	# Kannigen Nickel
	# Not in Serpent
	# Not in NRL
	mats['K Nickel'] = TreatMaterial(name='Kannigen Nickel')
	mats['K Nickel'].temperature = 300
	mats['K Nickel'].set_density('g/cc', 7.95)
	mats['K Nickel'].add_element('Ni', 0.895, 'wo')
	mats['K Nickel'].add_element('P', 0.105, 'wo')
	
	# Chrome
	# Not in Serpent
	# Not in NRL
	mats['Chromium'] = TreatMaterial(name='Chrome Plating')
	mats['Chromium'].temperature = 300
	mats['Chromium'].set_density('g/cc', 7.2)
	mats['Chromium'].add_element('Cr', 1.0, 'wo')
	
	# Boron steel
	# Not in Serpent
	# Not in NRL
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
	
	# Boral
	# Not in Serpent
	# Not in NRL
	"""Data regarding the Boral utilized at TREAT is not available.
	However, description of the Boral is very similar to descriptive
	data available for the early development of Boral at ORNL.

	Impurities have been neglected. All boral is far from the fuel,
	and the neutron interactions will be dominated by the boron anyway."""
	boral = TreatMaterial(name="50:50 ORNL Boral",
	                      key="boral")
	boral.set_density("g/cc", 2.53)
	boral.add_element("B", 0.36, "wo")
	boral.add_element("Al", 0.089, "wo")
	boral.add_nuclide("C0", 0.551, "wo")
	mats['Boral'] = boral
	
	# Create dysprosium material (density data from wikipedia)
	mats['Dysprosium'] = TreatMaterial(name='Dysprosium absorber',
	                                   key="dysprosium")
	mats['Dysprosium'].temperature = 300
	mats['Dysprosium'].set_density('g/cc', 8.54)
	mats['Dysprosium'].add_element('Dy', 1.000, 'wo')
	
	# Sodium bonding material
	# Not in Serpent
	# Not in NRL
	mats['Sodium'] = TreatMaterial(name='Sodium bonding',
	                               key="sodium")
	mats['Sodium'].temperature = 300
	mats['Sodium'].set_density('g/cc', 0.968)
	mats['Sodium'].add_element('Na', 1.000, 'wo')
	
	# Helium-Argon inert gas for experiment plenum
	# Not in Serpent
	# Not in NRL
	mats['HeAr'] = TreatMaterial(name='75% He, 25% Ar inert gas mixture',
	                             key="hear")
	mats['HeAr'].temperature = 300
	mats['HeAr'].set_density('g/cc', (0.75*0.0001786 + 0.25*0.001784))
	mats['HeAr'].add_element('He', 0.750, 'wo')
	mats['HeAr'].add_element('Ar', 0.250, 'wo')
	
	# Special M8Cal fuels
	# None were in Serpent
	# None were in NRL as far as I know, although there were other fuel compositions
	"""The material composition definitions in the M8Cal report did not add up to 100%
	Some approximations / assumptions were made"""
	# Create the fuel material for pin T-433 and H-307
	
	mats['M8 Fuel 1'] = TreatMaterial(name='Fuel material for M8 Cal pins T-433 and H-307')
	mats['M8 Fuel 1'].temperature = 300
	mats['M8 Fuel 1'].set_density('g/cc', 15.8)
	mats['M8 Fuel 1'].add_element('Zr', 0.097 + 0.0064, 'wo')  # Unspecified general material added as Zr
	mats['M8 Fuel 1'].add_nuclide('U234', 0.0063*0.8966, 'wo')
	mats['M8 Fuel 1'].add_nuclide('U235', 0.6550*0.8966, 'wo')
	mats['M8 Fuel 1'].add_nuclide('U236', 0.0037*0.8966, 'wo')
	mats['M8 Fuel 1'].add_nuclide('U238', (0.305 + 0.03)*0.8966, 'wo')  # Unspecified Uranium added as U238
	
	# Create the fuel material for pin T-462
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
	mats['M8 Fuel 3'] = TreatMaterial(name='Fuel material for M8 Cal pins H-316')
	mats['M8 Fuel 3'].temperature = 300
	mats['M8 Fuel 3'].set_density('g/cc', 15.8)
	mats['M8 Fuel 3'].add_element('Zr', 0.1000, 'wo')  # No unspecified general material to add
	mats['M8 Fuel 3'].add_nuclide('U234', 0.0049*0.6198, 'wo')
	mats['M8 Fuel 3'].add_nuclide('U235', 0.4608*0.6198, 'wo')
	mats['M8 Fuel 3'].add_nuclide('U236', 0.0024*0.6198, 'wo')
	mats['M8 Fuel 3'].add_nuclide('U238', (0.5326 - 0.0007)*0.6198, 'wo')  # Extra Uranium taken away from U238
	mats['M8 Fuel 3'].add_nuclide('Pu239', (0.8726 - 0.0004)*0.2802,
	                              'wo')  # Extra Plutonium taken away from Pu239
	mats['M8 Fuel 3'].add_nuclide('Pu240', 0.1181*0.2802, 'wo')
	mats['M8 Fuel 3'].add_nuclide('Pu241', 0.0075*0.2802, 'wo')
	mats['M8 Fuel 3'].add_nuclide('Pu242', 0.0022*0.2802, 'wo')
	
	# Generate the library
	backup_library = MaterialLib()
	for _key, _mat in mats.items():
		backup_library.add_material(_mat, _key.lower())
	
	return backup_library
