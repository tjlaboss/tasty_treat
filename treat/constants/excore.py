# Excore
#
# Parameters for TREAT excore details (e.g. reflector, thermal column, etc)

from .common import *

# Radial parameters according to the NRL model
# Note that these vary from the numbers in BATMAN and ANL reports.
nrl_gap = 4.445
nrl_liner_thick = 0.3175
nrl_graphite_thick = 61.595

# Radial parameters for TREAT excore details (e.g. reflector, thermal column, etc)
airGapThickness = 5.08 # Width of the air gap between the core and the permanent reflector.
                             # Found a width of 2 inches in an old ANL report
innerLinerThick = 0.625 # Old ANL report says excore reflector has a 1/4 inch thick aluminum liner between it and main core
reflectorThickness = 60.96 # Total width of the reflector, from core facing side to concrete facing side
reflBlockShortDim = 10.16 # Reflector is composed of 4 inch square blocks that seem to be 2 feet long
reflBlockLongDim = 60.96 # Reflector is composed of 4 inch square blocks that seem to be 2 feet long
tieBoltDrillHoleSR = 1.27 # Radius of the smaller hole drilled into some reflector blocks for tie bolts
tieBoltDrillHoleLR = 2.143125 # Radius of the large entry hole drilled into some reflector blocks for tie bolts
tieBoltLargeLength = 1.74625 + 0.524626 # Depth of the thicker part of the tie bolt drill holes in the reflector blocks
grphInstrHoleR = 8.255 # Radius of the large instrument hole drilled out of a 2x2 set of graphite blocks
reflLinerHW = 125.73 # Half width of the steel reflector liner the permanent reflector and the outer concrete
linerInstrHoleR = 8.89 # Radius of the large instrument holes in the steel reflector liner
innerLinerNHoleHW = 18.0975 # Half width of the hole in the north inner liner
innerLinerWSHoleHW = 5.3975 # Half width of the oversimplified hole in the west and south inner liners
innerLinerEHoleHW = 40.64 # Half width of the hole in the east inner liner
outerLinerThick = 0.14986  # Thickness of the outer steel liner sheets: #16 GA
outerLinerHW_N_x = 18.0975  # Half-height of the hole in the north outer liner
outerLinerHW_N_z = 40.64  # Half-width of the hole in the north outer liner
outerLinerHW_WS_xy = 5.40  # Half-width of the main hole in the west and south outer liners
outerLinerHW_WS_z = 30.48  # Half-height of the main hole in the west and south outer liners
outerLinerHW_E_y = 73.66  # Half-width of the main hole in the east outer liner
outerLinerHW_E_z = 76.2  # Half-height of the main hole in the east outer liner
outerLinerHW_WS_aux_x = 3.21  # Half-width of the little auxiliary hole in the west and south outer liners
outerLiner_WS_aux_z = 5.08  # Height of the little auxiliary hole in the west and south outer liners
outerLinerSteelHW = 121.92  # Half-height of the steel liner plates
tieBoltCloseDist = 35.56 # Distance from origin of the closer reflector tie bolt
tieBoltFarDist = 86.36 # Distance from origin of the farther reflector tie bolt
instrHoleDist = 60.96 # Distance from origin of the reflector instrument holes
nGateEdgeDist = 22.86 # Half width from the origin to the outer edge of the north gate
nGateWideDist = 20.0025 # Half width from the origin to the edge of the wide part of the north gate mobile graphite
nGateThinDist = 17.859375 # Half width from the origin to the edge of the thin part of the north gate mobile graphite
wSGateEdgeDist = 10.16 # Half width from the origin to the outer edge of the south and west gates
wSGateWideDist = 7.381875 # Half width from the origin to the edge of the wide part of the south and west gates mobile graphite
wSGateThinDist = 5.23875 # Half width from the origin to the edge of the thin part of the south and west gates mobile graphite
gateLinerThick = 0.15875 # The aluminum liner for the gates is 1/16 of an inch thick
nGateIEdgeDist = nGateEdgeDist - gateLinerThick # Distance to inside of liner
wSGateIEdgeDist = wSGateEdgeDist - gateLinerThick
gateRearIndent = 2.69875 # 1 1/16 inch difference between the gate liner front and rear portions
gateDepth = 40.005 # Thickness of the graphite gates
gateRearDepth = 20.32 # Depth of the rear section of the gate cavity liners
gateWideDepth = 20.0025 # Thickness of the wide portion of the graphite gates
radialShieldHW_i = 167.64 # Distance from the origin to the inside surface of the radial concrete biological shield
radialShieldHW_o = 320.04 # Distance from the origin to the main outside surface of the radial concrete biological shield
shieldCornerHW = 64.77 # Half width of the corners on the outside of concrete shielding
mainShieldSurfHW = radialShieldHW_o - shieldCornerHW * RT2 # Half with of the main outer biological shield surf
shieldCornerDist = RT2*mainShieldSurfHW + shieldCornerHW # Distance from origin to the external corners of bio shield
excore8inchPipeL = 78.105 # Length of the 8 inch diameter segments of the PVC pipes in the biological shield
excore8inchPipeR = 10.16 # Radius of those pipes
excore6inchPipeMainL = (radialShieldHW_o - radialShieldHW_i) - excore8inchPipeL # Length of the 6 inch diameter segments
                       # of the PVC pipes in the biological shield, on the N, W, S surfaces
excore6inchPipeR = 7.62 # Radius of those pipes
shieldGateLargeW = 101.6 # Width of the large (exterior) holes that can contain concrete blocks in the biological shield
shieldGateSmallW = 60.96 # Width of the smaller (interior) holes in the concrete biological shield
thermColumnSmallHW = 76.2 # Half width of the smaller segment of the square graphite thermal column
thermColumnLargeHW = 86.36 # Half width of the larger segment of the square graphite thermal column
thermColumnSmallDepth = 76.2 # Depth of the smaller segment of the graphite thermal column into the concrete shield
thermColumnMidpoint = radialShieldHW_i + thermColumnSmallDepth   # Distance from origin to divider
elemGuideOR = 2.2225 # Outer radius of the steel fuel element support pin guide below the grid plate
crdGuideOR = 3.4528125 # Outer radius of the steel tube guide for the control rods
topPlugRadius = 163.18 #165.1  # Radius of the top plug assembly
topPlugSlotHW = 12.7  # Half-width of the radial slot (average)
topPlugShortEdge = 26.67  # Short edge of the slot. It is smaller than this, but no other dimensions are listed.

# Some relative excore radial distances, from the center of the core outwards
inner = LATTICE_WIDTH / 2.0   # Where excore content starts radially (distance from origin)
gapOuter = inner + airGapThickness # How far out the air gap adjacent to the core extends
innerLinerOuter = gapOuter + innerLinerThick # How far out the inner aluminum liner extends from the origin
reflecInner = innerLinerOuter
reflecMid = reflecInner + reflectorThickness - tieBoltLargeLength # Distance from the origin to the
                                                    # point in the reflector where the tie bolt heads start
gateWideEnd = reflecInner + gateWideDepth # Distance from origin to end of wide parts of the gates
gateGrphEnd = reflecInner + gateDepth # Distance from origin to end of the graphite gates
reflecOuter = innerLinerOuter + reflectorThickness # How far out the graphite of the perm reflector extends
gateFrontEnd = reflecOuter - gateRearDepth # End of the front part of the gate casing (part with the graphite)
gateFrontCladStart = gateFrontEnd - gateLinerThick # Interior of the vertical liner of the gate
# The steel reflector liner
outerLinerOuter = reflecOuter + outerLinerThick
# Where excore content ends radially (distance from origin)
outer = radialShieldHW_o

# Axial parameters for TREAT excore details
reflectorHeight = 233.68 # Height of the excore permanent reflector. NOTE the reflector does not go to the top of the elements
linerHeight = 238.76 # Height of the steel liner between the core and the permanent reflector
innerLinerNHoleBottom = 81.28 # Height of the hole in the north aluminum inner liner from the bottom of the liner
innerLinerNHoleHeight = 81.28 # Height of the hole itself in the north aluminum inner liner
innerLinerWSHoleBottom = 67.31 # Height of the oversimplified hole in west and south aluminum inner liners from bottom of liner
innerLinerWSHoleHeight = 103.1875 # Height of the oversimplified hole itself in the west and south aluminum inner liners
innerLinerEHoleBottom = 45.72 # Height of the hole in the east aluminum inner liner from the bottom of the liner
innerLinerEHoleHeight = 142.24 # Height of the hole itself in the north aluminum inner liner
reflNHole_bot = 81.28 # Height from the base of the reflector up to the bottom of the openable north perm reflector hole
reflWHole_bot = 91.44 # Height from the base of the reflector up to the bottom of the openable west perm reflector hole
reflSHole_bot = 91.44 # Height from the base of the reflector up to the bottom of the openable south perm reflector hole
# TODO dummy parameters below - while these are probably roughly right, there is some detail on the blocks that is missing
nReflHoleHeight = 110 # How high the movable graphite block in the north reflector wall can be raised
wReflHoleHeight = 100 # How high the movable graphite block in the west reflector wall can be raised
sReflHoleHeight = 100 # How high the movable graphite block in the south reflector wall can be raised
####
tieBoltHeight_bot =  15.24 # Distance from the bottom of the reflector to the lower tie bolt center
tieBoltHeight_mid = 116.84 # Distance from the bottom of the reflector to the middle tie bolt center
tieBoltHeight_top = 218.44 # Distance from the bottom of the reflector to the upper tie bolt center
reflInstrHoleHeight_bot =  91.44 # Distance from the bottom of the reflector to the lower reflector instrument hole center
reflInstrHoleHeight_top = 162.56 # Distance from the bottom of the reflector to the upper reflector instrument hole center
refGateHeight = 154.305 # Height of the graphite blocks that comprise the gates
refGateLinerTotalHeight = 152.4 # Total height of the aluminum casing for the reflector gate cavity liners
refGateLinerUpperHeight = 71.12 # Height of the upper portion of the aluminum gate cavity liner
refGateLinerLowerHeight = refGateLinerTotalHeight - refGateLinerUpperHeight
shieldTotalHeight = 487.68 # Height from bottom of fuel support fitting / bottom of perm reflector to top of biological shield
shieldVoidHeight = 292.1 # Height of the void in the biological sheild that containts the perm reflector, etc
coreVoidHeight = 348.615 # Height of the void in the biological sheild that containts the core elements
shieldCeilingHeight = shieldTotalHeight - shieldVoidHeight # Height of the ceiling of the biological sheild
shieldFloorHeight = 121.92 # Height of the concrete floor between the core and the lower control rod drive room
shieldGateLargeH = 91.44 # Height of the large (exterior) holes that can contain concrete blocks in the biological shield
shieldGateSmallH = 60.96 # Height of the smaller (interior) holes in the concrete biological shield
sheildGateCenterH = 124.46 # Height of the center of the holes in biological shield, relative to the bottom of perm reflector
gridPlateThick = 2.54 # Grid plate below the fuel is 1 inch thick
elemGuideH = 10.795 # Height of the metal element
lowerAirH = 30.48 # Height of the air section below the grid plate (this includes the element guides)
lowerVoidH = lowerAirH - elemGuideH # The void section below both the grid plate and the element guides
topPlug_boral_height = 0.635
topPlug_steel_height = 30.48
topPlug_checker_height = 0.635