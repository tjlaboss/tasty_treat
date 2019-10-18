# Elements
#
# Numeric constants related to the dimensions of TREAT elements

from .common import *

# Radial parameters
#
# Standard fuel element
fuel_or         = 3.800*IN/2.0    # Half width of the outer surface of the graphite compact in the TREAT fuel assembly
clad_ir         = 4.9657   # Half width of the inner surface of the zircalloy cladding in the TREAT fuel assembly
clad_or         = 5.0292   # Half width of the outer surface of the zircalloy cladding in the TREAT fuel assembly
fuel_chamf_len  = 0.612*IN  # Length of the chamfer surface on the outside of the fuel
fuel_surf_hw    = fuel_or - fuel_chamf_len/RT2 # Half with of the main fuel surface (non chamfered surface)
clad_chamf_len  = 0.625*IN
zr_clad_thick   = 0.0635   # Thickness of the thinner zirconinum clad around the active fuel region
zr_gap_thick    = clad_ir - fuel_or
# Diagonal dists
fuel_o_diag  = RT2*fuel_surf_hw + fuel_chamf_len/2.0 # Distance from origin to the fuel chamfer surfaces
clad_i_diag  = fuel_o_diag + (clad_ir - fuel_or) # Distance from origin to the clad chamfer inner surfaces
clad_o_diag  = clad_i_diag + (clad_or - clad_ir)  # Distance from origin to the clad chamfer outer surfaces

# Plug above/below active fuel in fuel elements
plug_or = 3.780*IN/2.0
can_or = 3.960*IN/2.0
plug_chamf_len = 0.605*IN
plug_clad_thick = 0.05*IN
can_ir = can_or - plug_clad_thick
plug_gap_thick = can_ir - plug_or
# Diagonal dists
plug_surf_hw = plug_or - fuel_chamf_len/RT2
plug_o_diag  = RT2*plug_surf_hw + plug_chamf_len/2.0

# Reflector elements
# Zirc elements match fuel dimensions
zr_graph_or = fuel_or
zr_graph_chamf_len = fuel_chamf_len
# Aluminum dummies match plug dimensions
al_graph_or = plug_or
al_graph_chamf_len = plug_chamf_len
al_clad_thick   = plug_clad_thick    # Thickness of the thicker aluminum clad around the reflector region




# not sure about these yet
mainCladSurfHW  = fuel_surf_hw + TANPI8*(clad_or - fuel_or) #
thinCladSurfInnerHW  = fuel_surf_hw + TANPI8*(clad_ir - fuel_or) #
thinCladChamfIW = fuel_chamf_len + 2.0*TANPI8*(clad_ir - fuel_or) #

