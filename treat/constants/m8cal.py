# M8Cal
#
# Some parameters from the M8Cal calibration vessel

from .common import *

# Radial
can_shortHW_o = 5.0546 # Half width of the short segment of the M8Cal calibration vessel outside can
can_thickness = 0.127 # Thickness of the M8Cal vessel can
can_shortHW_i = can_shortHW_o - can_thickness # Half width of the short segment interior of the M8Cal vessel outside can
can_longHW_o = 10.1346 # Half width of the long segment of the M8Cal calibration vessel outside can
can_longHW_i = can_longHW_o - can_thickness # Half width of the long segment interior of the M8Cal vessel outside can
can_circR_i = 9.7028 # Radius of the interior surface of the M8Cal vessel circular inside can
can_circR_o = can_circR_i + can_thickness # Radius of the exterior surface of the M8Cal vessel circular inside can
can_chamf_OW = RT2*1.3096875 # Full width of the outside chamfer surfaces of the M8Cal outer can
fuel_pin_dist = 0.79375 # Distance from origin of each of the two fuel pins in the M8Cal experiment vessel
fuel_pinClad_OR = 0.2921 # Outer radius of the clad of each of the M8Cal fuel pins
fuel_pin_R = 0.21971 # Outer radius of the fuel pin itself for the M8Cal vessel
fuel_pinBond_OR = 0.254 # Outer radius of the sodium bond between the fuel pin and the clad material
fuel_flowTube_IR = 0.36703 # Inner radius of the flow tube around the M8Cal fuel pins
fuel_flowTube_OR = 0.47625 # Outer radius of the flow tube around the M8Cal fuel pins
test_calTrain_IR = 1.4224 # Inner radius of the M8Cal stainless steel calibration test train outer tube
test_calTrain_OR = 1.5875 # Outer radius of the M8Cal stainless steel calibration test train outer tube
test_calTest_IR = 1.63703 # Inner radius of the M8Cal stainless steel calibration loop test section
test_calTest_OR = 2.56921 # Outer radius of the M8Cal stainless steel calibration loop test section
test_AlSleeve_OR = 2.7051 # Outer radius of the M8Cal aluminum sleeve around the experiment positions
test_ssSleeve_OR = 2.86258 # Outer radius of the M8Cal stainless steel sleeve around the experiment positions
dys_largeThickness = 0.0508 # Thickness of the thickest part of the dysprosium shaping collars
dys_middleThickness = 0.04318 # Thickness of the middle part of the dysprosium shaping collars
dys_smallThickness = 0.00508 # Thickness of the thinest part of the dysprosium shaping collars
test_smallDys_OR = test_ssSleeve_OR + dys_smallThickness # Outer radius of the thinner part of the dysprosium collar
test_middleDys_OR = test_ssSleeve_OR + dys_middleThickness # Outer radius of the middle part of the dysprosium collar
test_largeDys_OR = test_ssSleeve_OR + dys_largeThickness # Outer radius of the thicker part of the dysprosium collar
test_dummy_OR = 3.03022 # Outer radius of the M8Cal outer stainless steel dummy heaters

# Axial
fuel_pin_H = 34.29 # Height of the active fuel pin in the M8Cal experiment positions
                      # Note that the midpoint of this fuel pin sits at the midpoint of the core active fuel
fuel_pinBottomFitting_H = 1.90754 # Height of the fitting below the M8Cal fuel pin
fuel_pinTopNa_H = 0.635 # Height of the sodium layer directly above the M8Cal fuel pin
fuel_pinPlenum_H = 24.59736 # Height of the plenum region above the M8Cal fuel pin
fuel_pinTopFitting_H = 2.31648 # Height of the fitting at the top of the M8Cal fuel pin
tube_upperTotal_H = 74.93 # Height of the whole dysprosium lined tube above the mid core point
tube_upperSteel_H = 10.16 # Height of the segment with no dysprosium lining above the mid core point
tube_upperThinDys_H = 17.145 - tube_upperSteel_H # Height of the segment with thin dysprosium lining above the midpoint
tube_upperMidDys_H = 30.48 - tube_upperThinDys_H - tube_upperSteel_H # Height of the segment with moderate dysprosium 
                                                                              # lining above the midpoint
tube_upperThickDys_H = tube_upperTotal_H - tube_upperMidDys_H - tube_upperThinDys_H - tube_upperSteel_H 
                        # Height of the segment with thick dysprosium lining above the midpoint
tube_lowerTotal_H = 76.2 # Height of the whole dysprosium lined tube below the mid core point
tube_lowerSteel_H = 8.89 # Height of the segment with no dysprosium lining below the mid core point
tube_lowerThinDys_H = 17.145 - tube_lowerSteel_H # Height of the segment with thin dysprosium lining below the midpoint
tube_lowerMidDys_H = 30.48 - tube_lowerThinDys_H - tube_lowerSteel_H # Height of the segment with moderate dysprosium 
                                                                              # lining below the midpoint
tube_lowerThickDys_H = tube_lowerTotal_H - tube_lowerMidDys_H - tube_lowerThinDys_H - tube_lowerSteel_H 
                        # Height of the segment with thick dysprosium lining below the midpoint