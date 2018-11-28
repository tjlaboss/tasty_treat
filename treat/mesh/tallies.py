# OpenMC z-mesh
#
# Some code to slice the Serpent assemblies

from copy import deepcopy

import openmc
import openmc.mgxs as mgxs
from .meshes import MeshGroup
from . import cuts


def build_tallies(lat_id, geometry, export_file="tallies.xml"):
  """Create the 'tallies.xml' file

  Parameters
  ----------
  lat_id:       int; the id of the lattice in the geometry
                  (c.ROOT_LATTICE should exist)
  geometry:     openmc.Geometry; the model's geometry. May be created through the API
                  (probably what's done here), or loaded through a statepoint or summary.
  export_file:  str; path to the file to export the Tallies() to.
                  [Default: "tallies.xml"]

  """
  # Extract the geometry from an existing summary

  # This is the main lattice. I will have to do something different for a lone element.
  lattice = geometry.get_all_lattices()[lat_id]
  nx = lattice.shape[0]
  ny = lattice.shape[1]

  tallies_xml = openmc.Tallies()

  # Exploit the pwr.mesh module
  low_left = [None]*3
  low_left[0:2] = deepcopy(lattice.lower_left)[0:2]
  low_left[2] = cuts.Z0
  axial_mesh = MeshGroup(lattice.pitch, nx, ny, low_left)
  n = len(cuts.dzs)
  for i in range(n):
    dz = cuts.dzs[i]
    nz = cuts.n_cuts[i]
    axial_mesh.add_mesh(nz=nz, dz=dz)

  # Build the mesh library
  mesh_lib = mgxs.Library(geometry)
  mesh_lib.domain_type = "mesh"
  mesh_lib.domains = axial_mesh.meshes
  mesh_lib.build_library()
  mesh_lib.add_to_tallies_file(tallies_xml)
  # Wrap it up in a nice XML file
  tallies_xml.extend(axial_mesh.tallies)
  tallies_xml.export_to_xml(export_file)
