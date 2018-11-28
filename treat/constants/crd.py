# CRD
#
# Interior dimensions of control rod elements

from .common import *


fuel_channel_r = 2.330*IN/2.0  # Radius of the hole in the active fuel region
tube_or        = 2.8575   # Outer radius of the Zr tube in the control rod elements covering the fuel section, lower axial reflector
                          # and a small part of the upper_ axial reflector
tube_thick     = 0.3175   # thickness of the wall of the Zr tube in the control rod elements
tube_ir        = tube_or - tube_thick # Inner radius of the Zr tube in the control rods

plug_channel_r = 2.565*IN/2.0  # Radius of the central hole in the upper_ long and short plug sections


upper_drill_dist = 4.445  # Distance from center point in upper_ short plug to center of drilled offgas hole
drill_card_dist = upper_drill_dist / RT2 # Distance in the x and y cardinal directions to center of drilled offgas hole
upper_offgas_r = 0.9525   # Radius of drilled offgas hole in upper_ short plug
lower_center_r = 2.87734375 # Radius of the central hole in the lower_ long and short plug sections & base
center_r       = 2.9591   # Radius of central hole in fuel block for control assemblies
bear_thin_ir   = 2.8702   # Inner radius of the thin part of the bearing tube in the control rod elements
bear_or        = 3.15595  # Outer radius of the bearing tube in the control rod elements
bear_thick_ir  = 2.54     # Inner radius of the thick part of the bearing tube
bush_ir        = 2.25552  # Inner radius of the graphitar bushing in the control rod elements
bush_or        = bear_thin_ir # Outer radius of the graphitar bushing
bush_retain_ir = 2.54     # Inner radius of the metal retainer keeping the graphitar bushing in place
bush_retain_or = bear_thin_ir # Outer radius of the bushing retainer
