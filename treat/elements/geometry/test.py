# Test
#
# test out the new geometry functions

from openmc import *

from elements.geometry import Layer, Manager

man = Manager()

mat1 = Material()
mat1.set_density('g/cc', 1.0)
mat1.add_nuclide('pu239', 1)
mat2 = Material()
mat2.set_density('g/cc', 1.0)
mat2.add_nuclide('u238', 1)
Materials([mat1, mat2]).export_to_xml()

# inner octagon
#oct0 = man.get_octagon(r0=1, diag=1, innermost=True)
oct0 = man.get_circle(r0=1, innermost=True)

lk = Layer(man, oct0, mat1)
lk.add_ring(mat2, "octagon", thick=0.1, d=1.1)
lk.add_ring("void", "octagon", thick=0.05)
lk.finalize()

# set root universe and make geometry
geom = Geometry()
root_universe = Universe()
root_cell = openmc.Cell(fill=lk.universe, name="root cell")
root_universe.add_cell(root_cell)
geom.root_universe = root_universe
geom.export_to_xml()

# plots
p = Plot()
p.basis = 'xy'
p.origin = (0,0,0)
p.width = [3, 3]
lots = Plots()
lots.append(p)
lots.export_to_xml()

# essential settings
s = Settings()
s.export_to_xml()

