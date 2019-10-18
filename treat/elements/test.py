# Test
#
# test out the new geometry functions

import sys; sys.path.append("..")
from openmc import *
from geometry import Layer
from geometry import Manager
import element

man = Manager()

mat1 = Material()
mat1.set_density('g/cc', 1.0)
mat1.add_nuclide('pu239', 1)
mat2 = Material()
mat2.set_density('g/cc', 1.0)
mat2.add_nuclide('u238', 1)
Materials([mat1, mat2]).export_to_xml()

# inner octagon
oct0 = man.get_octagon(r0=1, diag=1, innermost=True)
circ0 = man.get_circle(r0=1, innermost=True)

l1 = Layer(man, circ0, mat1)
l1.add_ring(mat2, "octagon", thick=0.1, d=1.1)
l1.add_ring("void", "octagon", thick=0.05)
l1.finalize()

l2 = Layer(man, oct0, mat1)
l2.add_ring(mat2, "octagon", thick=0.05)
l2.add_ring("void", "octagon", thick=0.1)
l2.finalize()

# Make a 2-layer element
el = element.Element(man, -1, l1.rmax)
el.add_layer(l1, 1.0)
el.add_layer(l2, 2.0)
el.finalize()

# set root universe and make geometry
geom = Geometry()
root_universe = Universe()
root_cell = openmc.Cell(fill=el.universe, name="root cell")
root_universe.add_cell(root_cell)
geom.root_universe = root_universe
geom.export_to_xml()

# plots
lots = Plots()
p1 = Plot()
p1.basis = 'xy'
p1.origin = (0,0,0.5)
p1.width = [3, 3]
lots.append(p1)
p2 = Plot()
p2.basis = 'xy'
p2.origin = (0,0,1.5)
p2.width = [3, 3]
lots.append(p2)
lots.export_to_xml()

# essential settings
s = Settings()
s.export_to_xml()

