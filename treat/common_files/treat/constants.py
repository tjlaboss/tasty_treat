
import math

TANPI8 = math.tan(math.pi/8)
ROOT_LATTICE = 10

############## Control Rod Insertion Details ##############
## Steps withdrawn for each RCCA bank
rcca_max_steps = 2000 # Assume a certain number of step positions for the control rods. 
                      # Possible positions go from 0 to max steps (0 being fully inserted)
                      # Note that according to the BATMAN report, the shutdown rods should have fine control up to
                      # either 2,900 steps or 29,000 steps depending on whether a potentiometer position indicator or
                      # a selsyn position indicator was used. Analagously, the transient rods should have fine control
                      # up to either 2,000 steps or 20,000 steps with those indicators.
# Note that while the control rod drives push the control rods into the core from the bottom, the poison section is on 
# the top of the rod. Thus when the drives are pushed fully into the core, the poison section is not overlapping the active
# fuel region, and the control rods are refered to as "fully withdrawn". Conversely, when the rod drives have fully pulled
# out of the core, the poison section is at maximum overlap with the active fuel region, and the control rods are refered
# to as "fully inserted".
rcca_bank_steps_withdrawn = {
  'Benchmark_Inserted': 0, # For the 3x3 control rod element benchmark problem
  'Benchmark_Withdrawn': rcca_max_steps, # For the 3x3 control rod element benchmark problem
  'MCM': rcca_max_steps, # TODO Check this. Currently assuming minimum critical mass control rods are fully withdrawn
  'M8_C_NE': rcca_max_steps, # TODO Determine the actual insertion level for M8Cal rods
  'M8_C_NW': rcca_max_steps, # TODO Determine the actual insertion level for M8Cal rods
  'M8_C_SE': rcca_max_steps, # TODO Determine the actual insertion level for M8Cal rods
  'M8_C_SW': rcca_max_steps, # TODO Determine the actual insertion level for M8Cal rods
  'M8_S_NE': rcca_max_steps, # TODO Determine the actual insertion level for M8Cal rods
  'M8_S_NW': rcca_max_steps, # TODO Determine the actual insertion level for M8Cal rods
  'M8_S_SE': rcca_max_steps, # TODO Determine the actual insertion level for M8Cal rods
  'M8_S_SW': rcca_max_steps, # TODO Determine the actual insertion level for M8Cal rods
  'M8_T_NE': rcca_max_steps, # TODO Determine the actual insertion level for M8Cal rods
  'M8_T_NW': rcca_max_steps, # TODO Determine the actual insertion level for M8Cal rods
  'M8_T_SE': rcca_max_steps, # TODO Determine the actual insertion level for M8Cal rods
  'M8_T_SW': rcca_max_steps, # TODO Determine the actual insertion level for M8Cal rods
}
rcca_banks = rcca_bank_steps_withdrawn.keys()

############## Geometry paramters ##############

## element width parameters
pelletOR        = 4.826    # Half width of the outer surface of the graphite compact in the TREAT fuel assembly
cladIR          = 4.9657   # Half width of the inner surface of the zircalloy cladding in the TREAT fuel assembly
cladOR          = 5.0292   # Half width of the outer surface of the zircalloy cladding in the TREAT fuel assembly
fuelChamfOW     = 1.55448  # Length of the chamfer surface on the outside of the fuel
mainFuelSurfHW  = pelletOR - fuelChamfOW / math.sqrt(2.0) # Half with of the main fuel surface (non chamfered surface)
fuelChamfDist   = math.sqrt(2.0)*mainFuelSurfHW + fuelChamfOW / 2.0 # Distance from origin to the fuel chamfer surfaces
cladChamfDistI  = fuelChamfDist + (cladIR - pelletOR) # Distance from origin to the clad chamfer inner surfaces
cladChamfDistO  = cladChamfDistI + (cladOR - cladIR)  # Distance from origin to the clad chamfer outer surfaces
mainCladSurfHW  = mainFuelSurfHW + TANPI8 * (cladOR - pelletOR) # 
thinCladSurfInnerHW  = mainFuelSurfHW + TANPI8 * (cladIR - pelletOR) #
thinCladChamfIW = fuelChamfOW + 2.0*TANPI8 * (cladIR - pelletOR) #
# Some width parameters from the non-active regions of the element (spacers & reflector)
PlugHW          = 4.8006   # Half width of the long & short plug pieces from the top and bottom reflector zone (center to face)
PlugChamfOW     = 1.5367   # Length of the chamfer surface on the long & short plugs of the reflector region
thickCladWidth  = 0.127    # Thickness of the thicker aluminum clad around the reflector region 
thinCladWidth   = 0.0635   # Thickness of the thinner zirconinum clad around the active fuel region 
thickCladIR     = cladOR - thickCladWidth
thickCladChamfIW = PlugChamfOW + 2.0*TANPI8 * (thickCladIR - PlugHW) #
mainPlugSurfHW  = PlugHW - PlugChamfOW / math.sqrt(2.0) # Half with of the main plug surface (non chamfered surface)
thickCladSurfInnerHW  = mainPlugSurfHW + TANPI8 * (thickCladIR - PlugHW) #
plugChamfDist   = math.sqrt(2.0)*mainPlugSurfHW + PlugChamfOW / 2.0 # Distance from origin to the fuel chamfer surfaces
thickCladChamfDistI  = plugChamfDist + (thickCladIR - PlugHW) # Distance from origin to the clad chamfer inner surfaces
topShortPlugIR  = 0.9525   # Inner radius of the off gas channel for the short plug in the upper reflector
plugMachinedHW  = 4.1656   # Half width of the parts of the short plug directly adjacent to the fuel machined to a square shape
endTubeCladW    = thickCladWidth   # Width of the cladding in the end tubes
offGasTubeOR    = 0.47625  # Outer radius of the off gas tube above the fueled region
offGasCladW     = 0.1143   # Width of the off gas tube material
offGasTubeIR    = offGasTubeOR - offGasCladW # Radius of the inside of the off gas tube
divotRadius     = 0.3571875# Radius of the divots between the aluminum and zirconium spacers
tabHalfWidth    = 3.4925   # Half width of the triangular tab in the top and bottom reflector regions
                           # TODO The tab is not currently included because it is a small bit of Zr metal that introduces rotation
                           # to regular fuel elements, and would require axially sloped surfaces. Really should be in there, though
tabThickness    = 0.238125 # Thickness of the tab
# Interior dimensions of control rod elements
crdUpperCenterR = 3.25755  # Radius of the central hole in the upper long and short plug sections
crdUpperDrillDist = 4.445  # Distance from center point in upper short plug to center of drilled offgas hole
crdDrillCardDist = crdUpperDrillDist / math.sqrt(2.0) # Distance in the x and y cardinal directions to center of drilled offgas hole
crdUpperOffgasR = 0.9525   # Radius of drilled offgas hole in upper short plug
crdLowerCenterR = 2.87734375 # Radius of the central hole in the lower long and short plug sections & base
crdCenterR      = 2.9591   # Radius of central hole in fuel block for control assemblies
crdBearThinIR   = 2.8702   # Inner radius of the thin part of the bearing tube in the control rod elements
crdBearOR       = 3.15595  # Outer radius of the bearing tube in the control rod elements
crdBearThickIR  = 2.54     # Inner radius of the thick part of the bearing tube
crdBushIR       = 2.25552  # Inner radius of the graphitar bushing in the control rod elements
crdBushOR       = crdBearThinIR # Outer radius of the graphitar bushing
crdBushRetainIR = 2.54     # Inner radius of the metal retainer keeping the graphitar bushing in place
crdBushRetainOR = crdBearThinIR # Outer radius of the bushing retainer
crdElemOR       = 2.8575   # Outer radius of the Zr tube in the control rod elements covering the fuel section, lower axial reflector
                           # and a small part of the upper axial reflector
crdElemCldWdth  = 0.3175   # Thickness of the wall of the Zr tube in the control rod elements
crdElemIR       = crdElemOR - crdElemCldWdth # Inner radius of the Zr tube in the control rods
# Geometry data for the control rods themselves, not just the assemblies containing them
rcca_OR         = 2.22250  # Outer radius of the clad on the control rods themselves
rcca_clad_Width = 0.3175   # Width of the cladding around the poison etc sections
rcca_clad_IR    = rcca_OR - rcca_clad_Width # 
rcca_active_OR  = rcca_clad_IR # Poison and other internal components to the control rods
rcca_adapter_OR = 0.79375  # adapter grapple at the top of the control rod
rcca_stock_OR   = 2.06375  # circular stock part way up the adapter grapple
# Geometry data needed for the access hole elements
accessWindowHW  = 3.4925   # Half width of the access hole in the dummy access hole elements
accessStiffHW   = 3.4925   # Half width of the stiffener supporting the zirc tube in the access hole elements
accessStiffTab  = 0.9525   # Width of the tab at the end of the stiffener
accessStiffProj = 1.27     # Dimension of the sloped part of the stiffener, projected onto the main cladding wall
accessStiffSlope= accessStiffProj * math.sqrt(2.0) # Dimension of the sloped part of the stiffener
accessStiffMain = accessStiffHW - accessStiffTab - accessStiffProj # Half width of the main part of the stiffener that sticks out
accessStiffWallDist = cladIR - thinCladWidth # Distance from the origin of the outside surface of wall component of the stiffener
accessStiffMainInnerDist = cladIR - accessStiffProj + thinCladWidth # Distance from origin to wall facing surface of main stiffener section
accessStiffMainOuterDist = accessStiffMainInnerDist - thinCladWidth # Distance from origin to center facing surface of stiffener section
accessStiffAngleCenterDist = (cladIR - accessStiffProj - accessStiffMain) / math.sqrt(2.0) 
                                                  # Distance from the origin to the center facing surface of the angled stiffener plane
accessStiffAngleWallDist = accessStiffAngleCenterDist + thinCladWidth 
                                                  # Distance from the origin to the wall facing surface of the angled stiffener plane

## lattice parameters
latticePitch    = 10.16    # Proper assembly / lattice pitch
n_lattice_positions = 19   #

# Element height parameters
regularFuelWithSpacer   = 122.2375    # Height of the active component of a standard fuel assembly, plus the two spacers on either end
largeBlockFuelHeight    = 20.16125    # Larger of the two active fuel block sizes
smallBlockFuelHeight    = 10.00125    # Smaller of the two active fuel block sizes
regularActiveFuelHeight = 6*largeBlockFuelHeight    # Height of the active component of a standard fuel assembly
topLongPlugHeight       = 40.64       # Long plug height in the upper reflector
bottomLongPlugHeight    = 36.5125     # Long plug height in the lower reflector
topEndTubeHeight        = 63.261875   # Height of the aluminum end tube for the upper reflector
bottomEndTubeHeight     = 59.134375   # Height of the aluminum end tube for the lower reflector
shortPlugTotalHeight    = 22.06625    # Total height of both the upper and lower reflector short plugs
shortPlugMachineHeight  = 8.89        # Height of only the part of the short plug that has been machined to a square configuration
shortPlugMainHeight     = shortPlugTotalHeight - shortPlugMachineHeight # Height of the remainder (NOTE not accounting for the lip)
offGasTubeHeight        = 5.715       # Height of the cylindical tube section of the off gas tube (NOTE again not accounting for lip)
crdOffgasDrillHeight    = 10.4775     # Height / Depth of the tube drilled in the control rod upper short plug for the offgas tube
crdLowerLPlugHeight2    = 40.64       # First of the two alternate heights listed for the lower short plug in the control rod element
crdLowerLPlugHeight3    = 39.6875     # Second of the two alternate heights listed for the lower short plug in the control rod element
crdBaseHeight           = 1.905       # height of the metal base at the bottom of the contro, rod elements
crdBearHeight           = 73.898125   # Total height of the bearing tube in the control rod element
crdBearThinBushHeight   = 14.2875     # Height of the thin part of the bearing tube (this includes the graphitar bushing)
crdBearThickHeight      = crdBearHeight - crdBearThinBushHeight # Remaining bearing height
crdBearBushHeight       = 5.08        # Height of graphitar bushing in the bearing tube
crdBearBushRetainHeight = 1.27        # Height of the aluminum retainer keeping the graphitar bushing in place
crdBearThinHeight       = crdBearThinBushHeight - crdBearBushHeight - crdBearBushRetainHeight # Purely the thin part of the bearing
crdOffGasHeight         = 9.525       # Height of the off center offgas tube in the control rod elements
crdElemTotalHeight      = 200.898125  # Total height of the Zr tube inside the control rod elements
crdElemFuelHeight       = 122.2375    # Height of the crd elements' Zr tube in the fuel region (including Zr spacers and gaps)
crdElemLowerHeight      = 70.881875   # Height of the crd elements' Zr tube in the lower axial reflector region (including Al spacer)
crdElemUpperHeight      = crdElemTotalHeight - crdElemFuelHeight - crdElemLowerHeight 
                          # Height of the crd elements' Zr tube in the upper axial reflector region (including Al spacer)
offGasCrimpHeight       = 0.635       # Height of the crimped top of the off gas tube
fuelZrSpacerWidth       = 0.3175      # Height of the Zirc spacers on either side of the fuel assembly (NOTE not including divots)
ZrDivotHeight           = 0.3175      # Height of the divots separating the Zr and Al spacers (TODO put these into the model)
# TODO - there seems to be a minor inconsistency between the active fuel height in the control rod document and the assembly document - look into?
fuelAlSpacerWidth       = 0.238125    # Height of the Aluminum spacers on either side of the Zirc spacers, flanking the top and bottom reflectors
weldHeight              = 1.349375    # Height of the thicker welded aluminum strips directly adjacent to the aluminum spacer in the 
                                      # reflector region (TODO include these in the model - need width info from somewhere)
tabStraightHeight       = 2.54        # Height of the straight segment of the reflector regions tabs
tabTriangleHeight       = 6.4008      # Height of the pseudo triangular portion of the reflector tabs
# Calculate unaccounted for space in the upper and lower reflector regions
regularUpperStructHeight = 11.58875   # Height of the aluminum plug above a standard fuel assembly
regularLowerStructHeight = 15.24      # Height of the aluminum support pin a standard fuel assembly
# The top fuel fitting dimensions
upper_head_tff_base = 1.27 + 1.905    # Height of the straight, octagonal base of the top fuel fitting
upper_head_tff_mid = 2.54             # Height of the sloped, octagonal middle portion of the top fuel fitting
upper_head_tff_neck = 3.175           # Height of the straight, cylindrical neck of the top fuel fitting
upper_head_tff_top_cone = 2.54        # Height of the sloped, cylindrical top of the top fuel fitting
# The bottom fuel fitting dimensions
support_pin_bff_base = 1.905          # Height of the straight, octagonal base (top) of the bottom fuel fitting
support_pin_bff_cone = 2.143          # Height of the sloped, cylindrical middle portion of the bottom fuel fitting
support_pin_bff_prong = 12.7          # Height of the straight, cylindrical long prong of the bottom fuel fitting
# The half-width bottom fuel fitting dimensions
hw_support_pin_bff_cone  = 0.789      # Height of the sloped, cylindrical middle portion
hw_support_pin_bff_prong = 14.844     # Height of the straight, cylindrical long prong
hw_support_pin_bff_r     = 0.714      # Radius of the half-spherical tip
hw_bff_base_height = 1.905
hw_p2_height = 1.905
hw_p1_height = hw_p2_height
hw_lead_height = 20.32
hw_reg_bff_height = hw_support_pin_bff_cone + hw_support_pin_bff_prong + hw_support_pin_bff_cone
hw_reg_tff_clad_base_height = 1.902
hw_reg_tff_expo_base_height = 0 # TBD
hw_reg_tff_mid_cone_height = 2.065 - hw_reg_tff_expo_base_height
hw_reg_tff_head_height = 5.715
# Ignore the chamfered top
hw_reg_tff_height = hw_reg_tff_mid_cone_height + hw_reg_tff_head_height + hw_reg_tff_expo_base_height
hw_reg_total_height = 270.431
hw_reg_graphite_height = hw_reg_total_height - hw_reg_bff_height - hw_bff_base_height \
  - hw_p2_height - 2*hw_lead_height - hw_p1_height - hw_reg_tff_clad_base_height - hw_reg_tff_height

# Some structural heights for the control rod elements
crdUpperHeadHeight      = 5.87375     # Total height of the aluminum head fixture above the upper axial reflector region
crdUpperHead_base_height = crdUpperHeadHeight - 3.33  # Height of the straight part of the aluminum head
crdUpperTubeHeight      = 5.715       # Height of the extra control rod guide tube above the upper axial reflector region
crdLowerBaseHeight      = 1.905       # Height of the aluminum base support fixture below the lower axial reflector region
crdLowerTubeHeight      = 10.16       # Height of the extra control rod guide tube below the lower axial reflector region


# Define heights we need for the access hole elements
accessElementTotalHeight = 272.335625 # The total height of the entire element
accessElementTotalTop = 52.308125     # The total height of everything above the graphite plug: same for every window height
accessElementTotalBot = 74.13625      # The total height of everything below the middle window layer
accessWindowAndPlug   = accessElementTotalHeight - accessElementTotalTop - accessElementTotalBot
# Windows
accessWindow48Height    = 121.92      # Height of the window in the 48 inch access hole dummy element (H1-8, H11-18)
accessWindow485Height   = 123.19      # Height of the window in the 48.5 inch access hole dummy element (H9,10)
accessWindow495Height   = 125.73      # Height of the window in the 49.5 inch access hole dummy element (H19B,20B)
accessWindow50Height    = 127.00      # Height of the window in the 50 inch access hole half width dummy element (H21?)
accessTube48TotalHgt    = 127.635     # Total height of the tube containing the access window for the 48 and 48.5 inch
                                      # access hole dummy elements
accessTube485TotalHgt   = accessTube48TotalHgt
accessTube495TotalHgt   = 130.175     # Total height of the tube containing the access window for the 49.5 inch
                                      # access hole dummy elements
accessTube50TotalHgt    = 141.367
accessCapHgt            = 1.5875      # Height of the Zirc caps on (both?) sides of the access hole window (i.e. the part that overlaps
                                      # with the graphite plugs
accessLeadPlugHgt       = 5.159375    # Height of the lead plugs on either side if the graphite plugs
accessZrHgt             = 0.238125    # Height of the thin zirconium layer separating the plugs from the empty tube in access hole elems
accessWindowOverlap     = 1.5875      # The overlapping distance at either end
accessWindowLowerHollow = 1.27        # The empty can at the lower end of the tube

# The empty cans at the upper end of the tube
accessWindow48UpperHollow = accessTube48TotalHgt - 2*accessWindowOverlap - accessWindowLowerHollow - accessWindow48Height
accessWindow485UpperHollow = accessTube485TotalHgt - 2*accessWindowOverlap - accessWindowLowerHollow - accessWindow485Height
accessWindow495UpperHollow = accessTube495TotalHgt - 2*accessWindowOverlap - accessWindowLowerHollow - accessWindow495Height
accessWindow50UpperHollow = accessTube50TotalHgt - 2*accessWindowOverlap - accessWindowLowerHollow - accessWindow50Height
# Plugs and stuff
accessBottomSPTotalHgt  = 16.66875    # Total height of the bottom short plug in access hole dummy elements
accessSPMachHgt         = 9.2075      # Height of machined part of the short plugs in access hole dummy elements
accessBottomSPMainHgt   = accessBottomSPTotalHgt - accessSPMachHgt    # Height of unmachined part of the bottom short plug
                                                                      # in access hole dummy elements
accessTopCanMinuend = accessWindowAndPlug + 2*accessWindowOverlap     # The fixed can size for all 3 heights
accessTopSP48TotalHgt   = accessTopCanMinuend - accessTube48TotalHgt  # Total height of the top short plug
accessTopSP48MainHgt    = accessTopSP48TotalHgt - accessSPMachHgt     # Height of unmachined part of the top short plug
accessTopSP485TotalHgt   = accessTopCanMinuend - accessTube485TotalHgt
accessTopSP485MainHgt    = accessTopSP485TotalHgt - accessSPMachHgt
accessTopSP495TotalHgt   = accessTopCanMinuend - accessTube495TotalHgt
accessTopSP495MainHgt    = accessTopSP495TotalHgt - accessSPMachHgt
accessTopSP50TotalHgt   = accessTopCanMinuend - accessTube50TotalHgt
accessTopSP50MainHgt    = accessTopSP50TotalHgt - accessSPMachHgt
accessDummyHgt          = 35.56       # Height of the dummy graphite plug (long plug) for the access hole dummy elements


# Dimensions of top fuel fitting
# Base level (octagon)
tff_base_thick = 1.27                                   # Wall thickness of the top fuel fitting's octagonal base
tff_base_corner_length_o = 1.5875                       # Length the short side of the octagonal base
tff_base_radius_i = 3.81                                # Inner "radius" of the octagonal base
tff_base_radius_o = tff_base_radius_i + tff_base_thick  # Outher "radius" of the octagonal base
tff_outer_corner = math.sqrt(2)*tff_base_radius_o
# Diagonal distances to the short edge/corner of the octagonal base:
tff_base_origin_to_outer_edge = tff_outer_corner - tff_base_corner_length_o/2.0               # Outer edge
tff_base_corner_length_i = tff_base_corner_length_o - 2*TANPI8*tff_base_thick  # Inner edge
# Middle cone level (octagon)
tff_mid_thick = 1.27                                    # Wall thickness of the sloped portion of the octagonal base
tff_mid_corner_length_o = (tff_base_corner_length_o + tff_base_corner_length_i)/2.0
tff_mid_radius_i = 3.175                                # Inner "radius" of the octagonal middle portion
tff_mid_radius_o = tff_mid_radius_i + tff_mid_thick     # Outer "radius" of the octagonal middle portion
tff_mid_outer_corner = math.sqrt(2)*tff_mid_radius_o
# Diagonal distances to the short edge/corner of the octagonal middle portion:
tff_mid_origin_to_outer_edge = tff_mid_outer_corner - tff_mid_corner_length_o/2.0             # Outer edge
tff_mid_corner_length_i = tff_mid_corner_length_o - 2*TANPI8*tff_mid_thick     # Inner edge
# Neck level (cylinder)
tff_neck_radius_i = 2.54
tff_neck_radius_o = tff_base_radius_i + 0.3175
# Top cone level (cylinder)
tff_cone_top_radius_i = tff_neck_radius_i
tff_cone_top_radius_o = tff_cone_top_radius_i + 1.905

# Dimensions of bottom fuel fitting
# Base level (octagon)
bff_base_corner_length = 1.56  # Wall thickness of the bottom fuel fitting's octagonal base
bff_base_radius = 4.9          # Outer "radius" of the bottom fuel fitting's octagonal base
# Diagonal distance to the short edge/corner of the octagonal base:
bff_base_origin_to_outer_edge = math.sqrt(2)*bff_base_radius - bff_base_corner_length/2.0
# Middle cone level (cylinder)
bff_cone_radius = 2.342
# Prong level (cylinder)
bff_prong_radius = 1.27

# Dimensions of the half-width bottom fuel fitting
hw_bff_offset_y = 1.905
# Cone level (sloped cylinder)
hw_bff_cone_radius = 1.261
# Prong level (straight cylinder)
hw_bff_prong_radius = .864
# And, of course, the sphere has just a single radius.

# Dimensions of the half-width lifting adapter (analagous to tff)
# Big bottom octagon (no cladding)
hw_tff_big_radius = 5.08  # The "radius" of the big exposed bottom octagon
hw_tff_big_short_dist = 1.331
hw_tff_big_corner_length = math.sqrt(2)*hw_tff_big_short_dist
hw_tff_big_origin_to_outer_edge = math.sqrt(2)*hw_tff_big_radius - hw_tff_big_corner_length/2.0
# Small top octagon
hw_tff_head_radius = 3.810  # The "radius" of the smaller top octagon
hw_tff_head_corner_length = hw_tff_big_corner_length - 2*TANPI8*hw_tff_big_corner_length
hw_tff_head_origin_to_outer_edge = math.sqrt(2)*hw_tff_head_radius - hw_tff_head_corner_length/2
# Average octagon to use for the sloped portion
hw_tff_mid_radius = (hw_tff_big_radius + hw_tff_head_radius)/2
hw_tff_mid_corner_length = (hw_tff_big_corner_length + hw_tff_head_corner_length)/2
hw_tff_mid_origin_to_outer_edge = (hw_tff_big_origin_to_outer_edge + hw_tff_head_origin_to_outer_edge)/2

# Dimensions of the half-width element layers
# Lead brick (Fig. 2.235)
hw_lead_radius = 4.90                                       # "Radius" of the octagonal lead brick
hw_lead_short_dist = 1.1887                                 # Horizontal dist. across the lead corner
hw_lead_corner_length = math.sqrt(2)*hw_lead_short_dist     # Diagonal dist. across the lead corner
hw_lead_origin_to_outer_edge = \
  math.sqrt(2)*hw_lead_radius - hw_lead_corner_length/2.0   # Dist. from the origin to the lead corner
# Can and gap
hw_can_thick = .0635                                        # Zirc can thickness
hw_can_radius_i = 4.9657                                    # Inner "radius" of can
hw_can_radius_o = hw_can_radius_i + hw_can_thick            # Outer "radius" of can
hw_gap_thick = hw_can_radius_i - hw_lead_radius             # Air gap thickness
hw_can_corner_length_i = \
  hw_lead_corner_length + 2*TANPI8*hw_gap_thick             # Diagonal dist. across the air corner
hw_gap_origin_to_outer_edge = \
  hw_lead_origin_to_outer_edge + hw_gap_thick               # Dist. from the origin to the air corner
hw_can_corner_length_o = \
  hw_can_corner_length_i + 2*TANPI8*hw_can_thick            # Diagnonal dist. across the can corner
hw_can_origin_to_outer_edge = \
  hw_gap_origin_to_outer_edge + hw_can_thick                # Dist. from the origin to the can corner
# Half-width
hw_total_half_can_o_width = 4.7625
hw_origin_to_half_can_o = hw_total_half_can_o_width - hw_can_radius_o
hw_origin_to_half_can_i = hw_origin_to_half_can_o - hw_can_thick
hw_origin_to_half_lead = hw_origin_to_half_can_i - hw_gap_thick
# Access hole
hw_acc_window_width = 6.985


# Dimensions of upper control rod head fitting
# Base level (octagon)
crd_head_base_corner_length_o = math.sqrt(2)*1.27  # Approximate length of the short side of the octagonal base
crd_head_base_radius_o = 5.08                      # "Radius" of the octagonal base
crd_head_base_outer_corner = math.sqrt(2)*crd_head_base_radius_o
crd_head_base_origin_to_outer_edge = crd_head_base_outer_corner - crd_head_base_corner_length_o/2.0
# Top level (octagon)
crd_head_top_radius_o = 4.44                       # "Radius" of the octagonal top
crd_head_top_corner_length_o = math.sqrt(2)*0.27   # Approximate length of the short side of the octagonal top
crd_head_top_outer_corner = math.sqrt(2)*crd_head_top_radius_o
crd_head_top_origin_to_outer_edge = crd_head_top_outer_corner - crd_head_top_corner_length_o/2.0

# Control rod height parameters
# First set up some dimensional parameters for the control rods (i.e. don't do any control rod positioning yet)                  
rcca_grappleLength_top          = 2.8575      # Height of the first part of the control rod adapter grapple, before the stock
rcca_stockLength                = 0.635       # Height of the stock on the control rod adapeter grapple
rcca_grappleLength_bot          = 4.1275      # Height of the second part of the control rod adapter grapple, after the stock
rcca_grappleWideLength_bot      = 0.635       # Height of the last part of the adapter grapple, where it widens before the main CRD
rcca_poisonLength_total         = 152.4       # Total height of the control rod poison section
rcca_poisonStructLength_top     = 6.0325      # Height of the top steel segment for the control rod poison section
rcca_poisonStructLength_bot     = 3.81        # Height of the bottom steel segment for the control rod poison section
rcca_poisonTypeIExtraGrph       = 45.72 - rcca_poisonStructLength_bot # In the old Type I rods, the bottom 18" of the poison 
                                                                      # section is graphite instead of B4C
rcca_poisonTypeIB4CLength       = rcca_poisonLength_total - rcca_poisonStructLength_top - rcca_poisonStructLength_bot - \
                                  rcca_poisonTypeIExtraGrph # Amount of B4C in Type I rods
rcca_poisonTypeIIB4CLength      = rcca_poisonLength_total - rcca_poisonStructLength_top - rcca_poisonStructLength_bot # Amount of B4C 
                                                                                                                      # in Type II rods
rcca_ZrFollowLength_total       = 152.4       # Total height of the control rod Zirconium follower section
rcca_ZrFollowStructLength_top   = 6.0325      # Height of the top steel segment for the control rod Zirconium follower section
rcca_ZrFollowStructLength_bot   = 6.0325      # Height of the bottom steel segment for the control rod Zirconium follower section
rcca_ZrFollowGrphLength         = rcca_ZrFollowLength_total - rcca_ZrFollowStructLength_top - rcca_ZrFollowStructLength_bot # Graphite
rcca_TransUpFollowLength_total  = 46.6725     # Total height of the transient control rod upper follower section
rcca_ShutdUpFollowLength_total  = 60.96       # Total height of the shutdown control rod upper follower section
rcca_UpFollowStructLength_top   = 17.78       # Height of the top steel segment for the control rod upper follower section
rcca_UpFollowStructLength_bot   = 6.0325      # Height of the bottom steel segment for the control rod upper follower section
rcca_TransUpFollowGrphLength    = rcca_TransUpFollowLength_total - rcca_UpFollowStructLength_top - rcca_UpFollowStructLength_bot#Transient
rcca_ShutdUpFollowGrphLength    = rcca_ShutdUpFollowLength_total - rcca_UpFollowStructLength_top - rcca_UpFollowStructLength_bot#Shutdown
rcca_FollowLength_total         = 151.60498   # Total height of the control rod bottom follower section
rcca_FollowStructLength_top     = 3.81        # Height of the top steel segment for the control rod bottom follower section
rcca_FollowStructLength_bot     = 8.89        # Height of the bottom steel segment for the control rod bottom follower section
rcca_FollowGrphLength           = rcca_ZrFollowLength_total - rcca_ZrFollowStructLength_top - rcca_ZrFollowStructLength_bot # Graphite 
rcca_ShutdownTravelDist         = 147.32      # Maximum distance the shutdown rods can travel (i.e. distance from fully inserted to
                                              # fully withdrawn)
rcca_TransientTravelDist        = 101.6       # Maximum distance the transient rods can travel (i.e. distance from fully inserted to
                                              # fully withdrawn)
rcca_ShutdownStepWidth          = rcca_ShutdownTravelDist / rcca_max_steps # Size of each step for the shutdown rods
rcca_TransientStepWidth         = rcca_TransientTravelDist / rcca_max_steps # Size of each step for the transient rods
rcca_shutWdAboveFuelHeight      = 16.764      # Height of the bottom of the active boron above the top of the active fuel when 
                                              # shutdown rods are fully withdrawn from the core
rcca_shutInBelowFuelHeight      = rcca_ShutdownTravelDist - regularActiveFuelHeight - rcca_shutWdAboveFuelHeight  # Distance the bottom 
                                              # of the active boron is below the bottom of the active fuel when 
                                              # shutdown rods are fully inserted into the core
rcca_transWdAboveFuelHeight     =  4.826      # Height of the bottom of the active boron above the top of the active fuel when 
                                              # transient rods are fully withdrawn from the core
rcca_transInAboveFuelHeight     = 24.384      # Distance the bottom of the active boron is above the bottom of the active fuel when 
                                              # transient rods are fully inserted into the core. NOTE this is slightly off from what
                                              # would be calculated if used activeFuelHeight - travelDist + transWdAboveFuelHeight
# Radial parameters for TREAT excore details (e.g. reflector, thermal column, etc)
excoreAirGapThickness = 5.08 # Width of the air gap between the core and the permanent reflector. 
                             # Found a width of 2 inches in an old ANL report
excoreInnerLinerThick = 0.625 # Old ANL report says excore reflector has a 1/4 inch thick aluminum liner between it and main core
excoreReflectorThickness = 60.96 # Total width of the reflector, from core facing side to concrete facing side
excoreReflBlockShortDim = 10.16 # Reflector is composed of 4 inch square blocks that seem to be 2 feet long
excoreReflBlockLongDim = 60.96 # Reflector is composed of 4 inch square blocks that seem to be 2 feet long
excoreTieBoltDrillHoleSR = 1.27 # Radius of the smaller hole drilled into some reflector blocks for tie bolts
excoreTieBoltDrillHoleLR = 2.143125 # Radius of the large entry hole drilled into some reflector blocks for tie bolts
excoreTieBoltLargeLength = 1.74625 + 0.524626 # Depth of the thicker part of the tie bolt drill holes in the reflector blocks
excoreGrphInstrHoleR = 8.255 # Radius of the large instrument hole drilled out of a 2x2 set of graphite blocks
excoreReflLinerHW = 125.73 # Half width of the steel reflector liner the permanent reflector and the outer concrete
excoreLinerInstrHoleR = 8.89 # Radius of the large instrument holes in the steel reflector liner
excoreInnerLinerNHoleHW = 18.0975 # Half width of the hole in the north inner liner
excoreInnerLinerWSHoleHW = 5.3975 # Half width of the oversimplified hole in the west and south inner liners
excoreInnerLinerEHoleHW = 40.64 # Half width of the hole in the east inner liner
excoreOuterLinerThick = 0.14986  # Thickness of the outer steel liner sheets: #16 GA
excoreOuterLinerHW_N_x = 18.0975  # Half-height of the hole in the north outer liner
excoreOuterLinerHW_N_z = 40.64  # Half-width of the hole in the north outer liner
excoreOuterLinerHW_WS_xy = 5.40  # Half-width of the main hole in the west and south outer liners
excoreOuterLinerHW_WS_z = 30.48  # Half-height of the main hole in the west and south outer liners
excoreOuterLinerHW_E_y = 73.66  # Half-width of the main hole in the east outer liner
excoreOuterLinerHW_E_z = 76.2  # Half-height of the main hole in the east outer liner
excoreOuterLinerHW_WS_aux_x = 3.21  # Half-width of the little auxiliary hole in the west and south outer liners
excoreOuterLiner_WS_aux_z = 5.08  # Height of the little auxiliary hole in the west and south outer liners
excoreOuterLinerSteelHW = 121.92  # Half-height of the steel liner plates
excoreTieBoltCloseDist = 35.56 # Distance from origin of the closer reflector tie bolt
excoreTieBoltFarDist = 86.36 # Distance from origin of the farther reflector tie bolt
excoreInstrHoleDist = 60.96 # Distance from origin of the reflector instrument holes
excoreNGateEdgeDist = 22.86 # Half width from the origin to the outer edge of the north gate
excoreNGateWideDist = 20.0025 # Half width from the origin to the edge of the wide part of the north gate mobile graphite
excoreNGateThinDist = 17.859375 # Half width from the origin to the edge of the thin part of the north gate mobile graphite
excoreWSGateEdgeDist = 10.16 # Half width from the origin to the outer edge of the south and west gates
excoreWSGateWideDist = 7.381875 # Half width from the origin to the edge of the wide part of the south and west gates mobile graphite
excoreWSGateThinDist = 5.23875 # Half width from the origin to the edge of the thin part of the south and west gates mobile graphite
excoreGateLinerThick = 0.15875 # The aluminum liner for the gates is 1/16 of an inch thick
excoreNGateIEdgeDist = excoreNGateEdgeDist - excoreGateLinerThick # Distance to inside of liner
excoreWSGateIEdgeDist = excoreWSGateEdgeDist - excoreGateLinerThick
excoreGateRearIndent = 2.69875 # 1 1/16 inch difference between the gate liner front and rear portions
excoreGateDepth = 40.005 # Thickness of the graphite gates
excoreGateRearDepth = 20.32 # Depth of the rear section of the gate cavity liners
excoreGateWideDepth = 20.0025 # Thickness of the wide portion of the graphite gates
excoreRadialShieldHW_i = 167.64 # Distance from the origin to the inside surface of the radial concrete biological shield
excoreRadialShieldHW_o = 320.04 # Distance from the origin to the main outside surface of the radial concrete biological shield
excoreShieldCornerHW = 64.77 # Half width of the corners on the outside of concrete shielding
mainShieldSurfHW = excoreRadialShieldHW_o - excoreShieldCornerHW * math.sqrt(2.0) # Half with of the main outer biological shield surf
shieldCornerDist = math.sqrt(2.0)*mainShieldSurfHW + excoreShieldCornerHW # Distance from origin to the external corners of bio shield
excore8inchPipeL = 78.105 # Length of the 8 inch diameter segments of the PVC pipes in the biological shield
excore8inchPipeR = 10.16 # Radius of those pipes
excore6inchPipeMainL = (excoreRadialShieldHW_o - excoreRadialShieldHW_i) - excore8inchPipeL # Length of the 6 inch diameter segments 
                       # of the PVC pipes in the biological shield, on the N, W, S surfaces
excore6inchPipeR = 7.62 # Radius of those pipes
excoreShieldGateLargeW = 101.6 # Width of the large (exterior) holes that can contain concrete blocks in the biological shield
excoreShieldGateSmallW = 60.96 # Width of the smaller (interior) holes in the concrete biological shield
excoreThermColumnSmallHW = 76.2 # Half width of the smaller segment of the square graphite thermal column
excoreThermColumnLargeHW = 86.36 # Half width of the larger segment of the square graphite thermal column
excoreThermColumnSmallDepth = 76.2 # Depth of the smaller segment of the graphite thermal column into the concrete shield
excoreThermColumnMidpoint = excoreRadialShieldHW_i + excoreThermColumnSmallDepth   # Distance from origin to divider
excoreElemGuideOR = 2.2225 # Outer radius of the steel fuel element support pin guide below the grid plate
excoreCrdGuideOR = 3.4528125 # Outer radius of the steel tube guide for the control rods
excoreTopPlugRadius = 163.18 #165.1  # Radius of the top plug assembly
excoreTopPlugSlotHW = 12.7  # Half-width of the radial slot (average)
excoreTopPlugShortEdge = 26.67  # Short edge of the slot. It is smaller than this, but no other dimensions are listed.

# Some relative excore radial distances, from the center of the core outwards
excoreInner = latticePitch * n_lattice_positions / 2.0   # Where excore content starts radially (distance from origin)
excoreGapOuter = excoreInner + excoreAirGapThickness # How far out the air gap adjacent to the core extends
excoreInnerLinerOuter = excoreGapOuter + excoreInnerLinerThick # How far out the inner aluminum liner extends from the origin
excoreReflecInner = excoreInnerLinerOuter
excoreReflecMid = excoreReflecInner + excoreReflectorThickness - excoreTieBoltLargeLength # Distance from the origin to the
                                                    # point in the reflector where the tie bolt heads start
excoreGateWideEnd = excoreReflecInner + excoreGateWideDepth # Distance from origin to end of wide parts of the gates
excoreGateGrphEnd = excoreReflecInner + excoreGateDepth # Distance from origin to end of the graphite gates
excoreReflecOuter = excoreInnerLinerOuter + excoreReflectorThickness # How far out the graphite of the perm reflector extends
excoreGateFrontEnd = excoreReflecOuter - excoreGateRearDepth # End of the front part of the gate casing (part with the graphite)
excoreGateFrontCladStart = excoreGateFrontEnd - excoreGateLinerThick # Interior of the vertical liner of the gate
# The steel reflector liner
excoreOuterLinerOuter = excoreReflecOuter + excoreOuterLinerThick
# Where excore content ends radially (distance from origin)
excoreOuter = excoreRadialShieldHW_o

# Axial parameters for TREAT excore details
excoreReflectorHeight = 233.68 # Height of the excore permanent reflector. NOTE the reflector does not go to the top of the elements
excoreLinerHeight = 238.76 # Height of the steel liner between the core and the permanent reflector
excoreInnerLinerNHoleBottom = 81.28 # Height of the hole in the north aluminum inner liner from the bottom of the liner
excoreInnerLinerNHoleHeight = 81.28 # Height of the hole itself in the north aluminum inner liner
excoreInnerLinerWSHoleBottom = 67.31 # Height of the oversimplified hole in west and south aluminum inner liners from bottom of liner
excoreInnerLinerWSHoleHeight = 103.1875 # Height of the oversimplified hole itself in the west and south aluminum inner liners
excoreInnerLinerEHoleBottom = 45.72 # Height of the hole in the east aluminum inner liner from the bottom of the liner
excoreInnerLinerEHoleHeight = 142.24 # Height of the hole itself in the north aluminum inner liner
excoreReflNHole_bot = 81.28 # Height from the base of the reflector up to the bottom of the openable north perm reflector hole
excoreReflWHole_bot = 91.44 # Height from the base of the reflector up to the bottom of the openable west perm reflector hole
excoreReflSHole_bot = 91.44 # Height from the base of the reflector up to the bottom of the openable south perm reflector hole
# TODO dummy parameters below - while these are probably roughly right, there is some detail on the blocks that is missing
excoreNReflHoleHeight = 110 # How high the movable graphite block in the north reflector wall can be raised
excoreWReflHoleHeight = 100 # How high the movable graphite block in the west reflector wall can be raised
excoreSReflHoleHeight = 100 # How high the movable graphite block in the south reflector wall can be raised
####
excoreTieBoltHeight_bot =  15.24 # Distance from the bottom of the reflector to the lower tie bolt center
excoreTieBoltHeight_mid = 116.84 # Distance from the bottom of the reflector to the middle tie bolt center
excoreTieBoltHeight_top = 218.44 # Distance from the bottom of the reflector to the upper tie bolt center
excoreReflInstrHoleHeight_bot =  91.44 # Distance from the bottom of the reflector to the lower reflector instrument hole center
excoreReflInstrHoleHeight_top = 162.56 # Distance from the bottom of the reflector to the upper reflector instrument hole center
excoreRefGateHeight = 154.305 # Height of the graphite blocks that comprise the gates
excoreRefGateLinerTotalHeight = 152.4 # Total height of the aluminum casing for the reflector gate cavity liners
excoreRefGateLinerUpperHeight = 71.12 # Height of the upper portion of the aluminum gate cavity liner
excoreRefGateLinerLowerHeight = excoreRefGateLinerTotalHeight - excoreRefGateLinerUpperHeight
excoreShieldTotalHeight = 487.68 # Height from bottom of fuel support fitting / bottom of perm reflector to top of biological shield
excoreShieldVoidHeight = 292.1 # Height of the void in the biological sheild that containts the perm reflector, etc
excoreCoreVoidHeight = 348.615 # Height of the void in the biological sheild that containts the core elements
excoreShieldCeilingHeight = excoreShieldTotalHeight - excoreShieldVoidHeight # Height of the ceiling of the biological sheild
excoreShieldFloorHeight = 121.92 # Height of the concrete floor between the core and the lower control rod drive room
excoreShieldGateLargeH = 91.44 # Height of the large (exterior) holes that can contain concrete blocks in the biological shield
excoreShieldGateSmallH = 60.96 # Height of the smaller (interior) holes in the concrete biological shield
excoreSheildGateCenterH = 124.46 # Height of the center of the holes in biological shield, relative to the bottom of perm reflector
excoreGridPlateThick = 2.54 # Grid plate below the fuel is 1 inch thick
excoreElemGuideH = 10.795 # Height of the metal element 
excoreLowerAirH = 30.48 # Height of the air section below the grid plate (this includes the element guides)
excoreLowerVoidH = excoreLowerAirH - excoreElemGuideH # The void section below both the grid plate and the element guides
excoreTopPlug_boral_height = 0.635
excoreTopPlug_steel_height = 30.48
excoreTopPlug_checker_height = 0.635

# Some parameters from the M8Cal calibration vessel
# Radial
m8_can_shortHW_o = 5.0546 # Half width of the short segment of the M8Cal calibration vessel outside can
m8_can_thickness = 0.127 # Thickness of the M8Cal vessel can
m8_can_shortHW_i = m8_can_shortHW_o - m8_can_thickness # Half width of the short segment interior of the M8Cal vessel outside can
m8_can_longHW_o = 10.1346 # Half width of the long segment of the M8Cal calibration vessel outside can
m8_can_longHW_i = m8_can_longHW_o - m8_can_thickness # Half width of the long segment interior of the M8Cal vessel outside can
m8_can_circR_i = 9.7028 # Radius of the interior surface of the M8Cal vessel circular inside can
m8_can_circR_o = m8_can_circR_i + m8_can_thickness # Radius of the exterior surface of the M8Cal vessel circular inside can
m8_can_chamf_OW = math.sqrt(2.0) * 1.3096875 # Full width of the outside chamfer surfaces of the M8Cal outer can
m8_fuel_pin_dist = 0.79375 # Distance from origin of each of the two fuel pins in the M8Cal experiment vessel
m8_fuel_pinClad_OR = 0.2921 # Outer radius of the clad of each of the M8Cal fuel pins
m8_fuel_pin_R = 0.21971 # Outer radius of the fuel pin itself for the M8Cal vessel
m8_fuel_pinBond_OR = 0.254 # Outer radius of the sodium bond between the fuel pin and the clad material
m8_fuel_flowTube_IR = 0.36703 # Inner radius of the flow tube around the M8Cal fuel pins
m8_fuel_flowTube_OR = 0.47625 # Outer radius of the flow tube around the M8Cal fuel pins
m8_test_calTrain_IR = 1.4224 # Inner radius of the M8Cal stainless steel calibration test train outer tube
m8_test_calTrain_OR = 1.5875 # Outer radius of the M8Cal stainless steel calibration test train outer tube
m8_test_calTest_IR = 1.63703 # Inner radius of the M8Cal stainless steel calibration loop test section
m8_test_calTest_OR = 2.56921 # Outer radius of the M8Cal stainless steel calibration loop test section
m8_test_AlSleeve_OR = 2.7051 # Outer radius of the M8Cal aluminum sleeve around the experiment positions
m8_test_ssSleeve_OR = 2.86258 # Outer radius of the M8Cal stainless steel sleeve around the experiment positions
m8_dys_largeThickness = 0.0508 # Thickness of the thickest part of the dysprosium shaping collars
m8_dys_middleThickness = 0.04318 # Thickness of the middle part of the dysprosium shaping collars
m8_dys_smallThickness = 0.00508 # Thickness of the thinest part of the dysprosium shaping collars
m8_test_smallDys_OR = m8_test_ssSleeve_OR + m8_dys_smallThickness # Outer radius of the thinner part of the dysprosium collar
m8_test_middleDys_OR = m8_test_ssSleeve_OR + m8_dys_middleThickness # Outer radius of the middle part of the dysprosium collar
m8_test_largeDys_OR = m8_test_ssSleeve_OR + m8_dys_largeThickness # Outer radius of the thicker part of the dysprosium collar
m8_test_dummy_OR = 3.03022 # Outer radius of the M8Cal outer stainless steel dummy heaters
# Axial
m8_fuel_pin_H = 34.29 # Height of the active fuel pin in the M8Cal experiment positions
                      # Note that the midpoint of this fuel pin sits at the midpoint of the core active fuel
m8_fuel_pinBottomFitting_H = 1.90754 # Height of the fitting below the M8Cal fuel pin
m8_fuel_pinTopNa_H = 0.635 # Height of the sodium layer directly above the M8Cal fuel pin
m8_fuel_pinPlenum_H = 24.59736 # Height of the plenum region above the M8Cal fuel pin
m8_fuel_pinTopFitting_H = 2.31648 # Height of the fitting at the top of the M8Cal fuel pin
m8_tube_upperTotal_H = 74.93 # Height of the whole dysprosium lined tube above the mid core point
m8_tube_upperSteel_H = 10.16 # Height of the segment with no dysprosium lining above the mid core point
m8_tube_upperThinDys_H = 17.145 - m8_tube_upperSteel_H # Height of the segment with thin dysprosium lining above the midpoint
m8_tube_upperMidDys_H = 30.48 - m8_tube_upperThinDys_H - m8_tube_upperSteel_H # Height of the segment with moderate dysprosium 
                                                                              # lining above the midpoint
m8_tube_upperThickDys_H = m8_tube_upperTotal_H - m8_tube_upperMidDys_H - m8_tube_upperThinDys_H - m8_tube_upperSteel_H 
                        # Height of the segment with thick dysprosium lining above the midpoint
m8_tube_lowerTotal_H = 76.2 # Height of the whole dysprosium lined tube below the mid core point
m8_tube_lowerSteel_H = 8.89 # Height of the segment with no dysprosium lining below the mid core point
m8_tube_lowerThinDys_H = 17.145 - m8_tube_lowerSteel_H # Height of the segment with thin dysprosium lining below the midpoint
m8_tube_lowerMidDys_H = 30.48 - m8_tube_lowerThinDys_H - m8_tube_lowerSteel_H # Height of the segment with moderate dysprosium 
                                                                              # lining below the midpoint
m8_tube_lowerThickDys_H = m8_tube_lowerTotal_H - m8_tube_lowerMidDys_H - m8_tube_lowerThinDys_H - m8_tube_lowerSteel_H 
                        # Height of the segment with thick dysprosium lining below the midpoint

# Core Structures Axial Heights
struct_LowestExtent             =   0.00000						 # Bottom of the universe
struct_CoreFloor_top            =   struct_LowestExtent + (excoreShieldFloorHeight - excoreLowerAirH)
struct_CoreVoid_top             =   struct_CoreFloor_top + excoreLowerVoidH              # 
struct_CoreGuide_top            =   struct_CoreVoid_top + excoreElemGuideH               #
struct_CoreGridPlate_top        =   struct_CoreGuide_top + excoreGridPlateThick          #
# Bottom fuel fitting and support pin
struct_bff_base_bot             =   struct_CoreGridPlate_top                             # Base of bff sits directly on grid plate
struct_bff_cone_bot             =   struct_bff_base_bot - support_pin_bff_cone           #
struct_Support_bot              =   struct_bff_cone_bot - support_pin_bff_prong          #
struct_bff_base_top             =   struct_bff_base_bot + support_pin_bff_base           #
struct_LowerReflec_bot        	=   struct_bff_base_top
struct_LowerLongPlug_top       	=   struct_LowerReflec_bot + bottomLongPlugHeight	 #
struct_LowerShortPlug_mid      	=   struct_LowerLongPlug_top + shortPlugMainHeight	 #
struct_LowerShortPlug_top      	=   struct_LowerShortPlug_mid + shortPlugMachineHeight	 #
struct_LowerAlSpace_top       	=   struct_LowerShortPlug_top + fuelAlSpacerWidth 	 #
struct_LowerGap_top             =   struct_LowerAlSpace_top + ZrDivotHeight	 	 #
struct_LowerZrSpace_top       	=   struct_LowerGap_top + fuelZrSpacerWidth 		 #

# Fuel Rod			
fuel_ActiveFuel_bot           	=	   struct_LowerZrSpace_top				 #
fuel_ActiveFuel_top           	=	   fuel_ActiveFuel_bot + regularActiveFuelHeight	 #
# Core Structures
struct_UpperZrSpace_bot         =	   fuel_ActiveFuel_top			 		 # same as fuel_ActiveFuel_top
struct_UpperZrSpace_top         =	   struct_UpperZrSpace_bot + fuelZrSpacerWidth 		 #
struct_UpperGap_top             =	   struct_UpperZrSpace_top + ZrDivotHeight 		 #
struct_UpperAlSpace_top       	=	   struct_UpperGap_top + fuelAlSpacerWidth 		 #
struct_OffGas_bot               =	   struct_UpperAlSpace_top		 		 #
struct_UpperReflec_bot        	=	   struct_UpperAlSpace_top 				 #
struct_OffGas_top               =	   struct_OffGas_bot + offGasTubeHeight	 		 #
struct_UpperCrimp_bot        	=	   struct_OffGas_top					 #
struct_UpperCrimp_top       	=	   struct_UpperCrimp_bot + offGasCrimpHeight		 #
struct_UpperShortPlug_bot       =	   struct_UpperAlSpace_top		 		 #
struct_UpperShortPlug_mid       =	   struct_UpperShortPlug_bot + shortPlugMachineHeight	 #
struct_UpperShortPlug_top       =	   struct_UpperShortPlug_mid + shortPlugMainHeight	 #
struct_UpperLongPlug_top        =          struct_UpperShortPlug_top + topLongPlugHeight         #
struct_UpperReflec_top          =	   struct_UpperLongPlug_top
struct_upper_head_bot           =	   struct_UpperReflec_top				 # same as struct_UpperReflec_top
struct_tff_base_top             =          struct_upper_head_bot + upper_head_tff_base
struct_tff_mid_top              =          struct_tff_base_top + upper_head_tff_mid
struct_tff_neck_top             = struct_tff_mid_top + upper_head_tff_neck
struct_upper_head_top        	= struct_tff_neck_top + upper_head_tff_top_cone
struct_UpperAir_top             = struct_bff_base_bot + excoreShieldVoidHeight
struct_UpperCoreAir_top         = struct_bff_base_bot + excoreCoreVoidHeight
struct_HighestExtent          	= struct_UpperAir_top + excoreShieldCeilingHeight                # concrete ceiling above the core

# Some extra relative height positions required for the control rod elements
struct_lowerCrdBase_bot         =          struct_LowerReflec_bot - crdLowerBaseHeight           #
struct_lowerCrdTube_bot         =          struct_lowerCrdBase_bot - crdLowerTubeHeight          #
struct_upperCrdHead_mid         =          struct_UpperLongPlug_top + crdUpperHead_base_height   #
struct_upperCrdHead_top         =          struct_UpperLongPlug_top + crdUpperHeadHeight         #
struct_upperCrdTube_top         =          struct_upperCrdHead_top + crdUpperTubeHeight          #
struct_crdElemTube_top          =          struct_UpperGap_top + crdElemUpperHeight              #
struct_crdBearThin_top          =          struct_UpperGap_top + crdBearThinHeight               #
struct_crdBushRet_top           =          struct_crdBearThin_top + crdBearBushRetainHeight      #
struct_crdOffGasTube_top        =          struct_UpperAlSpace_top + crdOffGasHeight             #
struct_crdOffGasCrimp_top       =          struct_crdOffGasTube_top + offGasCrimpHeight          #
struct_crdOffGasDrillHole_top   =          struct_UpperAlSpace_top + crdOffgasDrillHeight        #
struct_crdBush_top              =          struct_crdBushRet_top + crdBearBushHeight             #

# Set the relative heights for dummy access hole elements
struct_accessLowerLead_top      =          struct_LowerReflec_bot + accessLeadPlugHgt            #
struct_accessLowerDummy_top     =          struct_accessLowerLead_top + accessDummyHgt           #
struct_accessLowerSP_mid        =          struct_accessLowerDummy_top + accessBottomSPMainHgt   #
struct_accessLowerSP_upper      =          struct_accessLowerSP_mid+accessSPMachHgt-accessCapHgt #
struct_accessLowerSP_top        =          struct_accessLowerSP_upper + accessCapHgt             #
struct_accessLowerZr_top        =          struct_accessLowerSP_top + accessZrHgt                #
#struct_accessWindow_bot         =          struct_accessLowerZr_top + accessTubeLowerHgt         #
struct_accessWindow_bot         = struct_accessLowerZr_top + accessWindowLowerHollow
# Here is where our heights will start to diverge for the different dummy access hole elements
struct_accessWindow48_top       =          struct_accessWindow_bot + accessWindow48Height        #
struct_accessTube48_top         =          struct_accessWindow48_top  + accessWindow48UpperHollow     #
struct_accessZr48_top           =          struct_accessTube48_top  + accessZrHgt                #
struct_accessUpperSP48_lower    =          struct_accessZr48_top  + accessCapHgt                 #
struct_accessUpperSP48_mid      =          struct_accessUpperSP48_lower +accessSPMachHgt-accessCapHgt#
struct_accessUpperSP48_top      =          struct_accessUpperSP48_mid  +  accessTopSP48MainHgt   #

struct_accessWindow485_top      =          struct_accessWindow_bot + accessWindow485Height       #
struct_accessTube485_top        =          struct_accessWindow485_top + accessWindow485UpperHollow    #
struct_accessZr485_top          =          struct_accessTube485_top + accessZrHgt                #
struct_accessUpperSP485_lower   =          struct_accessZr485_top + accessCapHgt                 #
struct_accessUpperSP485_mid     =          struct_accessUpperSP485_lower+accessSPMachHgt-accessCapHgt#
struct_accessUpperSP485_top     =          struct_accessUpperSP485_mid +  accessTopSP485MainHgt   #

struct_accessWindow495_top      =          struct_accessWindow_bot + accessWindow495Height       #
struct_accessTube495_top        =          struct_accessWindow495_top + accessWindow495UpperHollow    #
struct_accessZr495_top          =          struct_accessTube495_top + accessZrHgt                #
struct_accessUpperSP495_lower   =          struct_accessZr495_top + accessCapHgt                 #
struct_accessUpperSP495_mid     =          struct_accessUpperSP495_lower+accessSPMachHgt-accessCapHgt#
struct_accessUpperSP495_top     =          struct_accessUpperSP495_mid +  accessTopSP495MainHgt   #

struct_accessWindow50_top       =          struct_accessWindow_bot + accessWindow50Height        #
struct_accessTube50_top         =          struct_accessWindow50_top  + accessWindow50UpperHollow     #
struct_accessZr50_top           =          struct_accessTube50_top  + accessZrHgt                #
struct_accessUpperSP50_lower    =          struct_accessZr50_top  + accessCapHgt                 #
struct_accessUpperSP50_mid      =          struct_accessUpperSP50_lower +accessSPMachHgt-accessCapHgt#
struct_accessUpperSP50_top      =          struct_accessUpperSP50_mid  +  accessTopSP50MainHgt   #

# These heights should now be back in line with each other, excepting some possible roundoff error during
# the subsequent addtions. Do a quick check to make sure that the user did not erroniously change a height
# that broke this
assert( abs(struct_accessUpperSP48_top - struct_accessUpperSP485_top) < 1E-13 and \
        abs(struct_accessUpperSP48_top - struct_accessUpperSP495_top) < 1E-13 ), \
  "\nstruct_accessUpperSP48_top:  {}," \
  "\nstruct_accessUpperSP485_top: {}," \
  "\nstruct_accessUpperSP495_top: {}.".format(struct_accessUpperSP48_top, struct_accessUpperSP485_top, struct_accessUpperSP495_top)
# Now go back to having a single relative height parameter
struct_accessUpperDummy_top     =          struct_accessUpperSP48_top + accessDummyHgt           #
struct_accessUpperLead_top      =          struct_accessUpperDummy_top + accessLeadPlugHgt       #
struct_accessUpperPlug_top      =          struct_accessUpperLead_top + regularUpperStructHeight #

# Half-width bottom fuel fitting and support pin
struct_hw_bff_cone_top = struct_bff_base_bot
struct_hw_bff_prong_top = struct_hw_bff_cone_top - hw_support_pin_bff_cone
struct_hw_bff_sphere_top = struct_hw_bff_prong_top - hw_support_pin_bff_prong
struct_hw_bff_sphere_bot = struct_hw_bff_sphere_top - hw_support_pin_bff_r
struct_hw_base_top = struct_hw_bff_cone_top + hw_bff_base_height
struct_hw_p2_top = struct_hw_base_top + hw_p2_height
struct_hw_lower_lead_top = struct_hw_p2_top + 2*hw_lead_height
struct_hw_reg_graphite_top = struct_hw_lower_lead_top + hw_reg_graphite_height
# some differences for the access hole version
struct_hw_p1_top = struct_hw_reg_graphite_top + hw_p1_height
struct_hw_tff_clad_base_top = struct_hw_p1_top + hw_reg_tff_clad_base_height
struct_hw_tff_mid_cone_top = struct_hw_tff_clad_base_top + hw_reg_tff_mid_cone_height
struct_hw_tff_top = struct_hw_tff_clad_base_top + hw_reg_tff_height
# Layers for slotted half-width element
struct_hw_acc_upper_lead_top = struct_hw_reg_graphite_top
struct_hw_acc_upper_graphite_top = struct_hw_acc_upper_lead_top - hw_lead_height
struct_hw_acc_upper_graphite_bot = struct_accessUpperSP48_lower


# Set up the relative heights in the core for both fully inserted shutdown and transient control rods
struct_rcca_shutActB4C_bot     = fuel_ActiveFuel_bot - rcca_shutInBelowFuelHeight  # Relative position of B4C when shut rod withdrawn
struct_rcca_transActB4C_bot    = fuel_ActiveFuel_bot + rcca_transInAboveFuelHeight # Relative position of B4C when trans rod withdrawn
struct_rcca_shutActB4C_top     = struct_rcca_shutActB4C_bot  + rcca_poisonTypeIIB4CLength # Top of B4C active section
struct_rcca_transActB4C_top    = struct_rcca_transActB4C_bot + rcca_poisonTypeIIB4CLength # Top of B4C active section
struct_rcca_shutTypeIGrph_top  = struct_rcca_shutActB4C_bot  + rcca_poisonTypeIExtraGrph  # Top of extra graphite in Type I CRDs
struct_rcca_transTypeIGrph_top = struct_rcca_transActB4C_bot + rcca_poisonTypeIExtraGrph  # Top of extra graphite in Type I CRDs
struct_rcca_shutB4CuS_top      = struct_rcca_shutActB4C_top  + rcca_poisonStructLength_top # Top of B4C section upper plug
struct_rcca_transB4CuS_top     = struct_rcca_transActB4C_top + rcca_poisonStructLength_top # Top of B4C section upper plug
struct_rcca_shutGw_top         = struct_rcca_shutB4CuS_top  + rcca_grappleWideLength_bot # Top of wide section of the grapple
struct_rcca_transGw_top        = struct_rcca_transB4CuS_top + rcca_grappleWideLength_bot # Top of wide section of the grapple
struct_rcca_shutGl_top         = struct_rcca_shutGw_top  + rcca_grappleLength_bot # Top of lower thin section of the grapple
struct_rcca_transGl_top        = struct_rcca_transGw_top + rcca_grappleLength_bot # Top of lower thin section of the grapple
struct_rcca_shutGs_top         = struct_rcca_shutGl_top  + rcca_stockLength # Top of stock section of the grapple
struct_rcca_transGs_top        = struct_rcca_transGl_top + rcca_stockLength # Top of stock section of the grapple
struct_rcca_shutGu_top         = struct_rcca_shutGs_top  + rcca_grappleLength_top # Top of upper thin section of the grapple
struct_rcca_transGu_top        = struct_rcca_transGs_top + rcca_grappleLength_top # Top of upper thin section of the grapple
struct_rcca_shutB4ClS_bot      = struct_rcca_shutActB4C_bot  - rcca_poisonStructLength_bot # Bottom of B4C section lower plug
struct_rcca_transB4ClS_bot     = struct_rcca_transActB4C_bot - rcca_poisonStructLength_bot # Bottom of B4C section lower plug
struct_rcca_shutZruS_bot       = struct_rcca_shutB4ClS_bot  - rcca_ZrFollowStructLength_top # Bottom of Zr follower section upper plug
struct_rcca_transZruS_bot      = struct_rcca_transB4ClS_bot - rcca_ZrFollowStructLength_top # Bottom of Zr follower section upper plug
struct_rcca_shutZrAct_bot      = struct_rcca_shutZruS_bot  - rcca_ZrFollowGrphLength # Bottom of Zr follower section active graphite
struct_rcca_transZrAct_bot     = struct_rcca_transZruS_bot - rcca_ZrFollowGrphLength # Bottom of Zr follower section active graphite
struct_rcca_shutZrlS_bot       = struct_rcca_shutZrAct_bot  - rcca_ZrFollowStructLength_bot # Bottom of Zr follower section lower plug
struct_rcca_transZrlS_bot      = struct_rcca_transZrAct_bot - rcca_ZrFollowStructLength_bot # Bottom of Zr follower section lower plug
struct_rcca_shutUpFoluS_bot    = struct_rcca_shutZrlS_bot  - rcca_UpFollowStructLength_top # Bottom of upper follower section upper plug
struct_rcca_transUpFoluS_bot   = struct_rcca_transZrlS_bot - rcca_UpFollowStructLength_top # Bottom of upper follower section upper plug
struct_rcca_shutUpFolAct_bot   = struct_rcca_shutUpFoluS_bot  - rcca_ShutdUpFollowGrphLength # Bottom of upper follower active graphite
struct_rcca_transUpFolAct_bot  = struct_rcca_transUpFoluS_bot - rcca_TransUpFollowGrphLength # Bottom of upper follower active graphite
struct_rcca_shutUpFollS_bot    = struct_rcca_shutUpFolAct_bot  - rcca_UpFollowStructLength_bot # Bottom of u follower section lower plug
struct_rcca_transUpFollS_bot   = struct_rcca_transUpFolAct_bot - rcca_UpFollowStructLength_bot # Bottom of u follower section lower plug
struct_rcca_shutFoluS_bot      = struct_rcca_shutUpFollS_bot  - rcca_FollowStructLength_top # Bottom of follower section upper plug
struct_rcca_transFoluS_bot     = struct_rcca_transUpFollS_bot - rcca_FollowStructLength_top # Bottom of follower section upper plug
struct_rcca_shutFolAct_bot     = struct_rcca_shutFoluS_bot    - rcca_FollowGrphLength # Bottom of follower active graphite
struct_rcca_transFolAct_bot    = struct_rcca_transFoluS_bot   - rcca_FollowGrphLength # Bottom of follower active graphite
struct_rcca_shutFollS_bot      = struct_rcca_shutFolAct_bot   - rcca_FollowStructLength_bot # Bottom of follower section adapter
struct_rcca_transFollS_bot     = struct_rcca_transFolAct_bot  - rcca_FollowStructLength_bot # Bottom of follower section adapter
rcca_Rod_bot                   = struct_LowestExtent  # same as struct_LowestExtent - even at maximum insertion, some follower
                                                      # should extend outside of what is currently being modelled.
# Some relative axial heights for the excore details
struct_excoreRefl_top = struct_bff_base_bot + excoreReflectorHeight
struct_excoreInnerLinerNWindow_bot = struct_bff_base_bot + excoreInnerLinerNHoleBottom
struct_excoreInnerLinerNWindow_top = struct_excoreInnerLinerNWindow_bot + excoreInnerLinerNHoleHeight
struct_excoreOuterLinerWindow_mid = (struct_excoreInnerLinerNWindow_top + struct_excoreInnerLinerNWindow_bot)/2.0
struct_excoreInnerLinerWSWindow_bot = struct_bff_base_bot + excoreInnerLinerWSHoleBottom
struct_excoreInnerLinerWSWindow_top = struct_excoreInnerLinerWSWindow_bot + excoreInnerLinerWSHoleHeight
struct_excoreInnerLinerEWindow_bot = struct_bff_base_bot + excoreInnerLinerEHoleBottom
struct_excoreInnerLinerEWindow_top = struct_excoreInnerLinerEWindow_bot + excoreInnerLinerEHoleHeight
struct_excoreReflNHole_bot = struct_bff_base_bot + excoreReflNHole_bot
struct_excoreReflWHole_bot = struct_bff_base_bot + excoreReflWHole_bot
struct_excoreReflSHole_bot = struct_bff_base_bot + excoreReflSHole_bot
struct_excoreTieBoltLower = struct_bff_base_bot + excoreTieBoltHeight_bot
struct_excoreTieBoltMiddle = struct_bff_base_bot + excoreTieBoltHeight_mid
struct_excoreTieBoltUpper = struct_bff_base_bot + excoreTieBoltHeight_top
struct_excoreReflInstrBottom = struct_bff_base_bot + excoreReflInstrHoleHeight_bot
struct_excoreReflInstrUpper = struct_bff_base_bot + excoreReflInstrHoleHeight_top
struct_excoreReflGateLinerNLowerClad_bot = struct_excoreReflNHole_bot + excoreRefGateLinerLowerHeight - excoreGateLinerThick
struct_excoreReflGateLinerNLowerClad_top = struct_excoreReflGateLinerNLowerClad_bot + excoreGateLinerThick
struct_excoreReflGateLinerNUpperClad_bot = struct_excoreReflNHole_bot + excoreRefGateLinerTotalHeight - excoreGateLinerThick
struct_excoreReflGateLinerNUpperClad_top = struct_excoreReflGateLinerNUpperClad_bot + excoreGateLinerThick
struct_excoreReflGateLinerWLowerClad_bot = struct_excoreReflWHole_bot + excoreRefGateLinerLowerHeight - excoreGateLinerThick
struct_excoreReflGateLinerWLowerClad_top = struct_excoreReflGateLinerWLowerClad_bot + excoreGateLinerThick
struct_excoreReflGateLinerWUpperClad_bot = struct_excoreReflWHole_bot + excoreRefGateLinerTotalHeight - excoreGateLinerThick
struct_excoreReflGateLinerWUpperClad_top = struct_excoreReflGateLinerWUpperClad_bot + excoreGateLinerThick
struct_excoreReflGateLinerSLowerClad_bot = struct_excoreReflSHole_bot + excoreRefGateLinerLowerHeight - excoreGateLinerThick
struct_excoreReflGateLinerSLowerClad_top = struct_excoreReflGateLinerSLowerClad_bot + excoreGateLinerThick
struct_excoreReflGateLinerSUpperClad_bot = struct_excoreReflSHole_bot + excoreRefGateLinerTotalHeight - excoreGateLinerThick
struct_excoreReflGateLinerSUpperClad_top = struct_excoreReflGateLinerSUpperClad_bot + excoreGateLinerThick
struct_excore_plug_bot = struct_UpperCoreAir_top
struct_excore_lower_boral_top = struct_excore_plug_bot + excoreTopPlug_boral_height
struct_excore_steel_top = struct_excore_lower_boral_top + excoreTopPlug_steel_height
struct_excore_upper_boral_top = struct_excore_steel_top + excoreTopPlug_boral_height
struct_excore_plug_top = struct_excore_upper_boral_top + excoreTopPlug_checker_height
struct_ThermColumnZorigin = struct_CoreGridPlate_top + 124.46

# Some relative axial heights for use in building the M8Cal experiment model
fuel_ActiveFuel_mid = (fuel_ActiveFuel_bot + fuel_ActiveFuel_top) / 2.0
struct_m8_fuelPin_bot = fuel_ActiveFuel_mid - m8_fuel_pin_H/2.0
struct_m8_fuelPin_top = struct_m8_fuelPin_bot + m8_fuel_pin_H
struct_m8_fuelBottomFitting_bot = struct_m8_fuelPin_bot - m8_fuel_pinBottomFitting_H
struct_m8_fuelNa_top = struct_m8_fuelPin_top + m8_fuel_pinTopNa_H
struct_m8_fuelPlenum_top = struct_m8_fuelNa_top + m8_fuel_pinPlenum_H
struct_m8_fuelTopFitting_top = struct_m8_fuelPlenum_top + m8_fuel_pinTopFitting_H
struct_m8_dysTotal_top = fuel_ActiveFuel_mid + m8_tube_upperTotal_H
struct_m8_dysTotal_bot = fuel_ActiveFuel_mid - m8_tube_lowerTotal_H
struct_m8_dysBare_top = fuel_ActiveFuel_mid + m8_tube_upperSteel_H
struct_m8_dysBare_bot = fuel_ActiveFuel_mid - m8_tube_lowerSteel_H
struct_m8_dysThin_top = struct_m8_dysBare_top + m8_tube_upperThinDys_H
struct_m8_dysThin_bot = struct_m8_dysBare_bot - m8_tube_lowerThinDys_H
struct_m8_dysMid_top = struct_m8_dysThin_top + m8_tube_upperMidDys_H
struct_m8_dysMid_bot = struct_m8_dysThin_bot - m8_tube_lowerMidDys_H
struct_m8_dysThick_top = struct_m8_dysMid_top + m8_tube_upperThickDys_H
struct_m8_dysThick_bot = struct_m8_dysMid_bot - m8_tube_lowerThickDys_H


