# RCCA
#
# Control Rod Insertion Details

MAX_STEPS = 2000  # Steps withdrawn for each RCCA bank
"""
Assume a certain number of step positions for the control rods.
Possible positions go from 0 to max steps (0 being fully inserted)
Note that according to the BATMAN report, the shutdown rods should have fine control up to
either 2,900 steps or 29,000 steps depending on whether a potentiometer position indicator or
a selsyn position indicator was used. Analagously, the transient rods should have fine control
up to either 2,000 steps or 20,000 steps with those indicators.
Note that while the control rod drives push the control rods into the core from the bottom, the poison section is on
the top of the rod. Thus when the drives are pushed fully into the core, the poison section is not overlapping the active
fuel region, and the control rods are refered to as "fully withdrawn". Conversely, when the rod drives have fully pulled
out of the core, the poison section is at maximum overlap with the active fuel region, and the control rods are refered
to as "fully inserted".
"""
BANK_STEPS_WITHDRAWN = {
  'Benchmark_Inserted': 0, # For the 3x3 control rod element benchmark problem
  'Benchmark_Withdrawn': MAX_STEPS, # For the 3x3 control rod element benchmark problem
  'MCM'    : MAX_STEPS, # TODO Check this. Currently assuming minimum critical mass control rods are fully withdrawn
  'M8_C_NE': MAX_STEPS, # TODO Determine the actual insertion level for M8Cal rods
  'M8_C_NW': MAX_STEPS, # TODO Determine the actual insertion level for M8Cal rods
  'M8_C_SE': MAX_STEPS, # TODO Determine the actual insertion level for M8Cal rods
  'M8_C_SW': MAX_STEPS, # TODO Determine the actual insertion level for M8Cal rods
  'M8_S_NE': MAX_STEPS, # TODO Determine the actual insertion level for M8Cal rods
  'M8_S_NW': MAX_STEPS, # TODO Determine the actual insertion level for M8Cal rods
  'M8_S_SE': MAX_STEPS, # TODO Determine the actual insertion level for M8Cal rods
  'M8_S_SW': MAX_STEPS, # TODO Determine the actual insertion level for M8Cal rods
  'M8_T_NE': MAX_STEPS, # TODO Determine the actual insertion level for M8Cal rods
  'M8_T_NW': MAX_STEPS, # TODO Determine the actual insertion level for M8Cal rods
  'M8_T_SE': MAX_STEPS, # TODO Determine the actual insertion level for M8Cal rods
  'M8_T_SW': MAX_STEPS, # TODO Determine the actual insertion level for M8Cal rods
}
BANKS = BANK_STEPS_WITHDRAWN.keys()

# Geometry data for the control rods themselves, not just the assemblies containing them
clad_or    = 2.22250  # Outer radius of the clad on the control rods themselves
clad_thick = 0.3175   # Width of the cladding around the poison etc sections
active_r    = clad_or - clad_thick  # Active portion of the control rock
adapter_or = 0.79375  # adapter grapple at the top of the control rod
stock_or   = 2.06375  # circular stock part way up the adapter grapple
