""" corebuilder.py

This module provides several classes that facilitate easier modelling of TREAT
with OpenMC

"""

import openmc
import math

class TemplatedLattice(openmc.RectLattice):
  """Extends OpenMC lattices for setting universes in a templated fashion"""

  def __init__(self, *args, **kwargs):
    super(TemplatedLattice, self).__init__(*args, **kwargs)
    self.positions = {}
    self.template = []

  def setTemplate(self, template):
    """ Set the lattice template
    
    :param template:
    """
    self.template = template

  def setPosition(self, key, univ):
    """Set an individual position in the lattice"""
    self.positions[key] = univ
  
  def updatePositions(self, univs):
    """Update multiple positions in the lattice with a dictionary"""
    self.positions.update(univs)

  def finalize(self):
  
    if self.template == []:
      raise Exception("No template set for:\n{0}".format(self))

    universes = []
    for row in self.template:
      r = []
      for item in row:
        try:
          r.append(self.positions[item.strip()])
        except KeyError:
          raise Exception("Must set template position '{0}' for template " +\
                          " in:\n{1}".format(item.strip(), self))
      universes.append(r)
    self.universes = universes


_created_cells = {}


class TranslationRotationMixin(object):
  def __init__(self):
    self.finalized = False
    self.name = ""

  def translate_rotate(self, t_vector=None, r_vector=None):
    """Create a translated and/or version of this universe

    Parameter
    ---------
    t_vector:         translation vector
    r_vector:         rotation vector

    Returns
    -------
    new_universe:     a Universe filled with this IniniteElement, but translated
    """
    assert self.finalized, "This Element must be finalized before translating."
    assert not all(v is None for v in [t_vector, r_vector]), \
      "You must specify t_vector, r_vector, or both."
    name = self.name[:]
    new_cell = openmc.Cell()
    new_cell.fill = self
    if t_vector:
      name += " [translated]"
      new_cell.translation = t_vector
    if r_vector:
      name += " [rotated]"
      new_cell.rotation = r_vector
    new_cell.name = name
    new_universe = openmc.Universe(name=new_cell.name, cells=[new_cell])
    return new_universe


class InfiniteElement(openmc.Universe, TranslationRotationMixin):
  """ Class for creating a simple element universe infinite in the z direction
  
  InfiniteElements consist of a set of radii and materials that define rings.
  
  This class provides an easy way to wrap an element inside additional rings, or
  a square grid around the outside.

  """
  
  def __init__(self, *args, **kwargs):
    """ Create a new InfiniteElement
    """
    super(InfiniteElement, self).__init__(*args, **kwargs)
    self.radii = []           # The surfaces needed for the cell that is currently being built
    self.box = []             # Is the current cell a square geometry (default is simple cylinder)
    self.octagon = []         # Is the current cell an octagonal geometry of the type required for TREAT elements
    self.fills = []           # Materials that will be filled into the cell
    self.rot = []
    self.first = []           # Is this the interior cell of a subset of rings
    self.prevBox = []         # If not the interior cell, is the previous cell a box type (default is cylinder)
    self.prevOctagon = []     # If not the interior cell, is the previous cell a TREAT octagon
    self.nEnclaves = []       # Number of smaller circular regions within this fill region that will not be filled with the
                              # same material (NOTE this does not include the standard interior region centered at the origin)
    self.window = []          # Logical flag for the special case of doing a windowed element. It will set whether we cut out a region
                              # in the middle or not
    self.stiffener = []       # Whether we have to build the strange stiffener surface
    self.finalized = False

  def add_ring(self, fill, surf, box=False, rot=None, octagon=False, first=False, prevBox=False, prevOctagon=False, \
               nEnclaves=0, window=False, stiffener=False):
    """ Adds a ring to the element
    
    Element must be built from the inside out. Materials for new rings are from
    the surface of the previous ring to the provided new surface.
    
    If the ring we want to add is a box, surf should be a dictionary of 4
    surfaces for the top, bottom, left, and right surfaces with keys "N", "S",
    "W", and "E", respectively.

    It's up to the user to check for overlapping cell definitions.
    
    :param fill: material or filling universe for new ring
    :param surf: outer surface of new ring (or dictionary if box ring)
    :param box: whether or not we're adding a boxy ring (e.g. for grids)
    :param rot: openmc rotation string for filled cells
    
    """
    self.radii.append(surf)
    self.box.append(box)
    self.octagon.append(octagon)
    self.fills.append(fill)
    self.first.append(first)
    self.prevBox.append(prevBox)
    self.prevOctagon.append(prevOctagon)
    self.nEnclaves.append(nEnclaves)
    self.window.append(window)
    self.stiffener.append(stiffener)
    self.rot.append(rot)

  def add_last_ring(self, fill, rot=None):
    """ Adds the outermost cell in the element that goes to infinity

    :param fill: material or filling universe for outermost region

    """
    self.fills.append(fill)
    self.rot.append(rot)

  def finalize(self):
    """ Creates Cell objects according to the element specification"""

    if self.finalized:
      return

    ## Loop over each ring and add cells for inner rings
    params = zip(self.radii, self.box, self.fills, self.rot, self.octagon, self.first, \
                 self.prevBox, self.prevOctagon, self.nEnclaves, self.window, self.stiffener)
    for i, (radius, box, fill, rot, octagon, first, prevBox, prevOctagon, nEnclaves, \
            window, stiffener) in enumerate(params):

      label = "{0} radial {1}: {2}".format(self._name, i, fill._name)

      if first:
        # this is the first ring of the subset

        if octagon:
          # this first ring is an octagonal ring in the manner of the treat reactor

          # If we don't have to build the stiffener for the access hole elements, do the standard surface generation
          if not stiffener:
            # Define the cells
            if not window: # We don't have a window in the clad, so do the standard center, north, and south cells
              cellC = openmc.Cell(name=(label+" box C"), fill=fill)
              cellN = openmc.Cell(name=(label+" box N"), fill=fill)
              cellS = openmc.Cell(name=(label+" box S"), fill=fill)
            else: # We need to do two sub cells for each
              cellCe = openmc.Cell(name=(label+" box C, east half"), fill=fill)
              cellNe = openmc.Cell(name=(label+" box N, east half"), fill=fill)
              cellSe = openmc.Cell(name=(label+" box S, east half"), fill=fill)
              cellCw = openmc.Cell(name=(label+" box C, west half"), fill=fill)
              cellNw = openmc.Cell(name=(label+" box N, west half"), fill=fill)
              cellSw = openmc.Cell(name=(label+" box S, west half"), fill=fill)
            cellE = openmc.Cell(name=(label+" box E"), fill=fill)
            cellW = openmc.Cell(name=(label+" box W"), fill=fill)
            cellNE = openmc.Cell(name=(label+" box NE"), fill=fill)
            cellNW = openmc.Cell(name=(label+" box NW"), fill=fill)
            cellSE = openmc.Cell(name=(label+" box SE"), fill=fill)
            cellSW = openmc.Cell(name=(label+" box SW"), fill=fill)
            # Add the surfaces to the cells
            if not window: # We don't have a window in the clad, so do the standard center, north, and south cells
              # Central Cell
              cellC.region  = -radius['IN'] # North face
              cellC.region &= +radius['IS'] # South face
              cellC.region &= -radius['IE'] # East face
              cellC.region &= +radius['IW'] # West face
              # North Cell
              cellN.region  = -radius['N']  # North face
              cellN.region &= +radius['IN'] # South face
              cellN.region &= -radius['IE'] # East face
              cellN.region &= +radius['IW'] # West face
              # South Cell
              cellS.region  = -radius['IS'] # North face
              cellS.region &= +radius['S']  # South face
              cellS.region &= -radius['IE'] # East face
              cellS.region &= +radius['IW'] # West face
            else: # We need to do two sub cells for each
              # Central Cell, east half
              cellCe.region  = -radius['IN']      # North face
              cellCe.region &= +radius['IS']      # South face
              cellCe.region &= -radius['IE']      # East face
              cellCe.region &= +radius['windowE'] # West face
              # North Cell, east half
              cellNe.region  = -radius['N']       # North face
              cellNe.region &= +radius['IN']      # South face
              cellNe.region &= -radius['IE']      # East face
              cellNe.region &= +radius['windowE'] # West face
              # South Cell, east half
              cellSe.region  = -radius['IS']      # North face
              cellSe.region &= +radius['S']       # South face
              cellSe.region &= -radius['IE']      # East face
              cellSe.region &= +radius['windowE'] # West face
              # Central Cell, west half
              cellCw.region  = -radius['IN']      # North face
              cellCw.region &= +radius['IS']      # South face
              cellCw.region &= -radius['windowW'] # East face
              cellCw.region &= +radius['IW']      # West face
              # North Cell, west half
              cellNw.region  = -radius['N']       # North face
              cellNw.region &= +radius['IN']      # South face
              cellNw.region &= -radius['windowW'] # East face
              cellNw.region &= +radius['IW']      # West face
              # South Cell, west half
              cellSw.region  = -radius['IS']      # North face
              cellSw.region &= +radius['S']       # South face
              cellSw.region &= -radius['windowW'] # East face
              cellSw.region &= +radius['IW']      # West face
            # East Cell
            cellE.region  = -radius['IN'] # North face
            cellE.region &= +radius['IS'] # South face
            cellE.region &= -radius['E']  # East face
            cellE.region &= +radius['IE'] # West face
            # West Cell
            cellW.region  = -radius['IN'] # North face
            cellW.region &= +radius['IS'] # South face
            cellW.region &= -radius['IW'] # East face
            cellW.region &= +radius['W']  # West face
            # North-East Cell
            cellNE.region  = -radius['NE'] # North-East face
            cellNE.region &= +radius['IN'] # South face
            cellNE.region &= +radius['IE'] # West face
            # North-West Cell
            cellNW.region  = -radius['NW'] # North-West face
            cellNW.region &= +radius['IN'] # South face
            cellNW.region &= -radius['IW'] # East face
            # South-East Cell
            cellSE.region  = -radius['IS'] # North face
            cellSE.region &= +radius['SE'] # South-East face
            cellSE.region &= +radius['IE'] # West face
            # South-West Cell
            cellSW.region  = -radius['IS'] # North face
            cellSW.region &= +radius['SW'] # South-West face
            cellSW.region &= -radius['IW'] # East face
            if not window: # We don't have a window in the clad, so do the standard center, north, and south cells
              self.add_cell(cellC)
              self.add_cell(cellN)
              self.add_cell(cellS)
            else: # We need to do two sub cells for each
              self.add_cell(cellCe)
              self.add_cell(cellNe)
              self.add_cell(cellSe)
              self.add_cell(cellCw)
              self.add_cell(cellNw)
              self.add_cell(cellSw)
            self.add_cell(cellE)
            self.add_cell(cellW)
            self.add_cell(cellNE)
            self.add_cell(cellNW)
            self.add_cell(cellSE)
            self.add_cell(cellSW)

          else: # We have to go through and build the surfaces such that they can accomodate both stiffeners
            # Define the cells
            if not window: # We don't have a window in the clad, so do the standard center, north, and south cells
              cellC = openmc.Cell(name=(label+" box C"), fill=fill)
              cellN = openmc.Cell(name=(label+" box N"), fill=fill)
              cellS = openmc.Cell(name=(label+" box S"), fill=fill)
              cellE = openmc.Cell(name=(label+" box E"), fill=fill)
              cellW = openmc.Cell(name=(label+" box W"), fill=fill)
            else: # We need to do two sub cells for each
              cellNe = openmc.Cell(name=(label+" box N, east half"), fill=fill)
              cellSe = openmc.Cell(name=(label+" box S, east half"), fill=fill)
              cellNw = openmc.Cell(name=(label+" box N, west half"), fill=fill)
              cellSw = openmc.Cell(name=(label+" box S, west half"), fill=fill)
              # We are going to fold the east and west cells into CE and CW
              cellCEo = openmc.Cell(name=(label+" box C, east half, wall facing region"), fill=fill)
              cellCWo = openmc.Cell(name=(label+" box C, west half, wall facing region"), fill=fill)
              cellCEi = openmc.Cell(name=(label+" box C, east half, center facing region"), fill=fill)
              cellCWi = openmc.Cell(name=(label+" box C, west half, center facing region"), fill=fill)
            cellNE = openmc.Cell(name=(label+" box NE"), fill=fill)
            cellNW = openmc.Cell(name=(label+" box NW"), fill=fill)
            cellSE = openmc.Cell(name=(label+" box SE"), fill=fill)
            cellSW = openmc.Cell(name=(label+" box SW"), fill=fill)
            cellNE_filler = openmc.Cell(name=(label+" NE filler"), fill=fill)
            cellNW_filler = openmc.Cell(name=(label+" NW filler"), fill=fill)
            cellSE_filler = openmc.Cell(name=(label+" SE filler"), fill=fill)
            cellSW_filler = openmc.Cell(name=(label+" SW filler"), fill=fill)
            # Add the surfaces to the cells
            if not window: # We don't have a window in the clad, so do the standard center, north, and south cells
              # Central Cell
              cellC.region  = -radius['IN'] # North face
              cellC.region &= +radius['IS'] # South face
              cellC.region &= -radius['stiffWallE'] # East face
              cellC.region &= +radius['stiffWallW'] # West face
              cellC.region &= (-radius['stiffCenterNE'] | -radius['stiffMainCenterE'] | +radius['stiffCenterSE']) # East cutout
              cellC.region &= (-radius['stiffCenterNW'] | +radius['stiffMainCenterW'] | +radius['stiffCenterSW']) # West cutout
              # North Cell
              cellN.region  = -radius['N']  # North face
              cellN.region &= +radius['IN'] # South face
              cellN.region &= -radius['IE'] # East face
              cellN.region &= +radius['IW'] # West face
              # South Cell
              cellS.region  = -radius['IS'] # North face
              cellS.region &= +radius['S']  # South face
              cellS.region &= -radius['IE'] # East face
              cellS.region &= +radius['IW'] # West face
              # East Cell
              cellE.region  = -radius['stiffWallSE']    # North-West face
              cellE.region &= +radius['stiffWallNE']    # South-West face
              cellE.region &= -radius['E']              # East face
              cellE.region &= +radius['stiffMainWallE'] # West face
              # West Cell
              cellW.region  = -radius['stiffWallSW']    # North-East face
              cellW.region &= +radius['stiffWallNW']    # South-East face
              cellW.region &= -radius['stiffMainWallW'] # East face
              cellW.region &= +radius['W']              # West face
            else: # We need to do two sub cells for each
              # North Cell, east half
              cellNe.region  = -radius['N']       # North face
              cellNe.region &= +radius['IN']      # South face
              cellNe.region &= -radius['IE']      # East face
              cellNe.region &= +radius['windowE'] # West face
              # South Cell, east half
              cellSe.region  = -radius['IS']      # North face
              cellSe.region &= +radius['S']       # South face
              cellSe.region &= -radius['IE']      # East face
              cellSe.region &= +radius['windowE'] # West face
              # North Cell, west half
              cellNw.region  = -radius['N']       # North face
              cellNw.region &= +radius['IN']      # South face
              cellNw.region &= -radius['windowW'] # East face
              cellNw.region &= +radius['IW']      # West face
              # South Cell, west half
              cellSw.region  = -radius['IS']      # North face
              cellSw.region &= +radius['S']       # South face
              cellSw.region &= -radius['windowW'] # East face
              cellSw.region &= +radius['IW']      # West face
              # Central Cell, east half, wall facing region
              cellCEo.region  = -radius['stiffWallSE']    # North-West face
              cellCEo.region &= +radius['stiffWallNE']    # South-West face
              cellCEo.region &= -radius['E']              # East face
              cellCEo.region &= +radius['stiffMainWallE'] # West face
              # Central Cell, west half, wall facing region
              cellCWo.region  = -radius['stiffWallSW']    # North-East face
              cellCWo.region &= +radius['stiffWallNW']    # South-East face
              cellCWo.region &= -radius['stiffMainWallW'] # East face
              cellCWo.region &= +radius['W']              # West face
              # Central Cell, east half, center facing region
              # First do the union of surfaces comprising the part of the stiffener that sticks out
              cellCEi.region  = (-radius['stiffCenterNE'] | -radius['stiffMainCenterE'] | +radius['stiffCenterSE'])
              cellCEi.region &= -radius['IN']         # North face
              cellCEi.region &= +radius['IS']         # South face
              cellCEi.region &= -radius['stiffWallE'] # East face
              cellCEi.region &= +radius['windowE']    # West face
              # Central Cell, west half, center facing region
              # First do the union of surfaces comprising the part of the stiffener that sticks out
              cellCWi.region  = (-radius['stiffCenterNW'] | +radius['stiffMainCenterW'] | +radius['stiffCenterSW'])
              cellCWi.region &= -radius['IN']         # North face
              cellCWi.region &= +radius['IS']         # South face
              cellCWi.region &= -radius['windowW']    # East face
              cellCWi.region &= +radius['stiffWallW'] # West face
            # North-East Cell
            cellNE.region  = -radius['NE'] # North-East face
            cellNE.region &= +radius['IN'] # South face
            cellNE.region &= +radius['IE'] # West face
            # North-West Cell
            cellNW.region  = -radius['NW'] # North-West face
            cellNW.region &= +radius['IN'] # South face
            cellNW.region &= -radius['IW'] # East face
            # South-East Cell
            cellSE.region  = -radius['IS'] # North face
            cellSE.region &= +radius['SE'] # South-East face
            cellSE.region &= +radius['IE'] # West face
            # South-West Cell
            cellSW.region  = -radius['IS'] # North face
            cellSW.region &= +radius['SW'] # South-West face
            cellSW.region &= -radius['IW'] # East face
            # East half, north gap filler
            cellNE_filler.region  = -radius['IN']         # North face
            cellNE_filler.region &= +radius['stiffWallN'] # South face
            cellNE_filler.region &= -radius['E']          # East face
            cellNE_filler.region &= +radius['stiffWallE'] # West face
            # East half, south gap filler
            cellSE_filler.region  = -radius['stiffWallS'] # North face
            cellSE_filler.region &= +radius['IS']         # South face
            cellSE_filler.region &= -radius['E']          # East face
            cellSE_filler.region &= +radius['stiffWallE'] # West face
            # West half, north gap filler
            cellNW_filler.region  = -radius['IN']         # North face
            cellNW_filler.region &= +radius['stiffWallN'] # South face
            cellNW_filler.region &= -radius['stiffWallW'] # East face
            cellNW_filler.region &= +radius['W']          # West face
            # West half, south gap filler
            cellSW_filler.region  = -radius['stiffWallS'] # North face
            cellSW_filler.region &= +radius['IS']         # South face
            cellSW_filler.region &= -radius['stiffWallW'] # East face
            cellSW_filler.region &= +radius['W']          # West face
            if not window: # We don't have a window in the clad, so do the standard center, north, and south cells
              self.add_cell(cellC)
              self.add_cell(cellN)
              self.add_cell(cellS)
              self.add_cell(cellE)
              self.add_cell(cellW)
            else: # We need to do two sub cells for each
              self.add_cell(cellNe)
              self.add_cell(cellSe)
              self.add_cell(cellNw)
              self.add_cell(cellSw)
              self.add_cell(cellCEo)
              self.add_cell(cellCWo)
              self.add_cell(cellCEi)
              self.add_cell(cellCWi)
            self.add_cell(cellNE_filler)
            self.add_cell(cellSE_filler)
            self.add_cell(cellNW_filler)
            self.add_cell(cellSW_filler)
            self.add_cell(cellNE)
            self.add_cell(cellNW)
            self.add_cell(cellSE)
            self.add_cell(cellSW)

        elif box:
          # this first ring is a box ring

          cell = openmc.Cell(name=label, fill=fill)
          cell.region  = +radius['S']
          cell.region &= -radius['N']
          cell.region &= +radius['W']
          cell.region &= -radius['E']
          if rot is not None: 
            cell.rotation = rot
          self.add_cell(cell)

        elif stiffener:
          # The user has asked for a stiffener without any other options (besides "first") - i.e. just put the stiffeners in
          cellE = openmc.Cell(name=(label+" east stiffener"), fill=fill) 
          cellW = openmc.Cell(name=(label+" west stiffener"), fill=fill) 
          # Do east stiffener first
          cellE.region  = (-radius['stiffWallNE'] | -radius['stiffMainWallE'] | +radius['stiffWallSE'])
          cellE.region &= -radius['E'] # East surface that is directly against the wall
          cellE.region &= +radius['stiffMainCenterE'] # West surface of part that sticks out
          cellE.region &= -radius['stiffWallN'] # North surface
          cellE.region &= +radius['stiffWallS'] # South surface
          cellE.region &= (+radius['stiffWallE'] | -radius['stiffCenterSE']) # North-West surface
          cellE.region &= (+radius['stiffWallE'] | +radius['stiffCenterNE']) # South-West surface
          # Next do west stiffener
          cellW.region  = (-radius['stiffWallNW'] | +radius['stiffMainWallW'] | +radius['stiffWallSW'])
          cellW.region &= +radius['W'] # West surface that is directly against the wall
          cellW.region &= -radius['stiffMainCenterW'] # East surface of part that sticks out
          cellW.region &= -radius['stiffWallN'] # North surface
          cellW.region &= +radius['stiffWallS'] # South surface
          cellW.region &= (-radius['stiffWallW'] | -radius['stiffCenterSW']) # North-East surface
          cellW.region &= (-radius['stiffWallW'] | +radius['stiffCenterNW']) # South-East surface
          self.add_cell(cellE)
          self.add_cell(cellW)

        else:
          # this first ring is a regular cylinder

          cell = openmc.Cell(name=label, fill=fill)
          cell.region  = -radius
          if rot is not None: 
            cell.rotation = rot
          self.add_cell(cell)

      else:
        # this is not the first ring

        if prevOctagon:
          # the last ring was an octagon - need to make many cells

          if octagon:
            # this is an octagonal ring, and the last one was also an octagonal ring

            # Define the cells
            # Basic cells comprising the rectangles directly adjacent to the long (non-chamfered)
            # surfaces of the fuel element
            if not window: # We don't have a window in the clad, so do the standard north and south cells
              cellN = openmc.Cell(name=(label+" box N"), fill=fill)
              cellS = openmc.Cell(name=(label+" box S"), fill=fill)
            else: # We need to do two sub cells for each
              cellNe = openmc.Cell(name=(label+" box N, east half"), fill=fill)
              cellNw = openmc.Cell(name=(label+" box N, west half"), fill=fill)
              cellSe = openmc.Cell(name=(label+" box S, east half"), fill=fill)
              cellSw = openmc.Cell(name=(label+" box S, west half"), fill=fill)
            cellE = openmc.Cell(name=(label+" box E"), fill=fill)
            cellW = openmc.Cell(name=(label+" box W"), fill=fill)
            # Cells comprising the rectangles directly adjacent to the short (chamfered)
            # surfaces of the fuel element
            cellNE = openmc.Cell(name=(label+" box NE"), fill=fill)
            cellNW = openmc.Cell(name=(label+" box NW"), fill=fill)
            cellSE = openmc.Cell(name=(label+" box SE"), fill=fill)
            cellSW = openmc.Cell(name=(label+" box SW"), fill=fill)
            # Cells connecting the two previous sets
            cellNNE = openmc.Cell(name=(label+" box NNE"), fill=fill) # N cell to NE cell
            cellNNW = openmc.Cell(name=(label+" box NNW"), fill=fill) # N cell to NW cell
            cellESE = openmc.Cell(name=(label+" box ESE"), fill=fill) # E cell to SE cell
            cellWSW = openmc.Cell(name=(label+" box WSW"), fill=fill) # W cell to SW cell
            cellENE = openmc.Cell(name=(label+" box ENE"), fill=fill) # E cell to NE cell
            cellWNW = openmc.Cell(name=(label+" box WNW"), fill=fill) # W cell to NW cell
            cellSSE = openmc.Cell(name=(label+" box SSE"), fill=fill) # S cell to SE cell
            cellSSW = openmc.Cell(name=(label+" box SSW"), fill=fill) # S cell to SW cell

            # Add the surfaces to the cells

            if not window: # We don't have a window in the clad, so do the standard north and south cells
              # North Cell
              cellN.region  = -radius['N']     # North face
              cellN.region &= +radius['prevN'] # South face
              cellN.region &= -radius['IE']    # East face
              cellN.region &= +radius['IW']    # West face
              # South Cell
              cellS.region  = -radius['prevS'] # North face
              cellS.region &= +radius['S']     # South face
              cellS.region &= -radius['IE']    # East face
              cellS.region &= +radius['IW']    # West face
            else: # We need to do two sub cells for each
              # North Cell, east half
              cellNe.region  = -radius['N']       # North face
              cellNe.region &= +radius['prevN']   # South face
              cellNe.region &= -radius['IE']      # East face
              cellNe.region &= +radius['windowE'] # West face
              # North Cell, west half
              cellNw.region  = -radius['N']       # North face
              cellNw.region &= +radius['prevN']   # South face
              cellNw.region &= -radius['windowW'] # East face
              cellNw.region &= +radius['IW']      # West face
              # South Cell, east half
              cellSe.region  = -radius['prevS']   # North face
              cellSe.region &= +radius['S']       # South face
              cellSe.region &= -radius['IE']      # East face
              cellSe.region &= +radius['windowE'] # West face
              # South Cell, west half
              cellSw.region  = -radius['prevS']   # North face
              cellSw.region &= +radius['S']       # South face
              cellSw.region &= -radius['windowW'] # East face
              cellSw.region &= +radius['IW']      # West face
            # East Cell
            cellE.region  = -radius['IN']    # North face
            cellE.region &= +radius['IS']    # South face
            cellE.region &= -radius['E']     # East face
            cellE.region &= +radius['prevE'] # West face
            # West Cell
            cellW.region  = -radius['IN']    # North face
            cellW.region &= +radius['IS']    # South face
            cellW.region &= -radius['prevW'] # East face
            cellW.region &= +radius['W']     # West face

            # North-East Cell
            cellNE.region  = -radius['NE']     # North-East face
            cellNE.region &= +radius['ISE']    # South-East face
            cellNE.region &= +radius['prevNE'] # South-West face
            cellNE.region &= -radius['INW']    # North-West face
            # North-West Cell
            cellNW.region  = -radius['NW']     # North-West face
            cellNW.region &= +radius['ISW']    # South-West face
            cellNW.region &= +radius['prevNW'] # South-East face
            cellNW.region &= -radius['INE']    # North-East face
            # South-East Cell
            cellSE.region  = +radius['SE']     # South-East face
            cellSE.region &= -radius['INE']    # North-East face
            cellSE.region &= -radius['prevSE'] # North-West face
            cellSE.region &= +radius['ISW']    # South-West face
            # South-West Cell
            cellSW.region  = +radius['SW']     # South-West face
            cellSW.region &= -radius['INW']    # North-West face
            cellSW.region &= -radius['prevSW'] # North-East face
            cellSW.region &= +radius['ISE']    # South-East face

            # North-North-East Cell
            cellNNE.region  = -radius['N']   # North face
            cellNNE.region &= +radius['INW'] # South-East face
            cellNNE.region &= -radius['NE']  # North-East face
            cellNNE.region &= +radius['IE']  # West face
            # North-North-West Cell
            cellNNW.region  = -radius['N']   # North face
            cellNNW.region &= +radius['INE'] # South-West face
            cellNNW.region &= -radius['IW']  # East face
            cellNNW.region &= -radius['NW']  # North-West face
            # South-South-East Cell
            cellSSE.region  = +radius['S']   # South face
            cellSSE.region &= -radius['ISW'] # North-East face
            cellSSE.region &= +radius['SE']  # South-East face
            cellSSE.region &= +radius['IE']  # West face
            # South-South-West Cell
            cellSSW.region  = +radius['SW']  # South-West face
            cellSSW.region &= -radius['ISE'] # North-West face
            cellSSW.region &= -radius['IW']  # East face
            cellSSW.region &= +radius['S']   # South face
            # East-North-East Cell
            cellENE.region  = -radius['NE']  # North-East face
            cellENE.region &= -radius['E']   # East face
            cellENE.region &= +radius['IN']  # South face
            cellENE.region &= -radius['ISE'] # North-West face
            # West-North-West Cell
            cellWNW.region  = -radius['NW']  # North-West face
            cellWNW.region &= +radius['W']   # West face
            cellWNW.region &= +radius['IN']  # South face
            cellWNW.region &= -radius['ISW'] # North-East face
            # East-South-East Cell
            cellESE.region  = +radius['SE']  # South-East face
            cellESE.region &= -radius['E']   # East face
            cellESE.region &= -radius['IS']  # North face
            cellESE.region &= +radius['INE'] # South-West face
            # West-South-West Cell
            cellWSW.region  = +radius['SW']  # South-West face
            cellWSW.region &= +radius['W']   # West face
            cellWSW.region &= -radius['IS']  # North face
            cellWSW.region &= +radius['INW'] # South-East face

            # Add the cells 
            if not window: # We don't have a window in the clad, so do the standard north and south cells
              self.add_cell(cellN)
              self.add_cell(cellS)
            else: # We need to do two sub cells for each
              self.add_cell(cellNe)
              self.add_cell(cellNw)
              self.add_cell(cellSe)
              self.add_cell(cellSw)
            self.add_cell(cellE)
            self.add_cell(cellW)
            self.add_cell(cellNE)
            self.add_cell(cellNW)
            self.add_cell(cellSE)
            self.add_cell(cellSW)
            self.add_cell(cellNNE)
            self.add_cell(cellNNW)
            self.add_cell(cellSSE)
            self.add_cell(cellSSW)
            self.add_cell(cellENE)
            self.add_cell(cellWNW)
            self.add_cell(cellESE)
            self.add_cell(cellWSW)

          elif box:
            # this is a box ring, and the last one was an octagonal ring
            # TODO Look at this - it seems incorrect, like not accounting for the triangles at the
            #      chamfered corners of the octagon

            for d in ['N', 'S', 'E', 'W']:
              boxlabel = "{0} box {1}".format(label, d)
              cell = openmc.Cell(name=boxlabel, fill=fill)
              if d == 'N':
                cell.region  = +radius['prevN']
                cell.region &= -radius['N']
                cell.region &= +radius['W']
                cell.region &= -radius['E']
              elif d == 'S':
                cell.region  = +radius['S']
                cell.region &= -radius['prevS']
                cell.region &= +radius['W']
                cell.region &= -radius['E']
              elif d == 'E':
                cell.region  = +radius['prevE']
                cell.region &= -radius['E']
                cell.region &= +radius['prevS']
                cell.region &= -radius['prevN']
              elif d == 'W':
                cell.region  = +radius['W']
                cell.region &= -radius['prevW']
                cell.region &= +radius['prevS']
                cell.region &= -radius['prevN']
              if rot is not None: 
                cell.rotation = rot
              self.add_cell(cell)

          else:
            # this is a regular cylinder, and the last one was an octagonal ring
            # TODO Look at this - it seems incorrect, like not accounting for the triangles at the
            #      chamfered corners of the octagon

            for d in ['N', 'S', 'E', 'W']:
              boxlabel = "{0} box {1}".format(label, d)
              cell = openmc.Cell(name=boxlabel, fill=fill)
              cell.region  = -radius['R']
              if d == 'N':
                cell.region &= +radius['prevN']
              elif d == 'S':        
                cell.region &= -radius['prevS']
              elif d == 'E':        
                cell.region &= +radius['prevE']
                cell.region &= +radius['prevS']
                cell.region &= -radius['prevN']
              elif d == 'W':       
                cell.region &= -radius['prevW']
                cell.region &= +radius['prevS']
                cell.region &= -radius['prevN']
              if rot is not None: 
                cell.rotation = rot
              self.add_cell(cell)

        elif prevBox:
          # the last ring was a box - need to make 4 cells

          if box:
            # this is a box ring, and the last one was also a box ring

            for d in ['N', 'S', 'E', 'W']:
              boxlabel = "{0} box {1}".format(label, d)
              cell = openmc.Cell(name=boxlabel, fill=fill)
              if d == 'N':
                cell.region  = +radius['prevN']
                cell.region &= -radius['N']
                cell.region &= +radius['W']
                cell.region &= -radius['E']
              elif d == 'S':
                cell.region  = +radius['S']
                cell.region &= -radius['prevS']
                cell.region &= +radius['W']
                cell.region &= -radius['E']
              elif d == 'E':
                cell.region  = +radius['prevE']
                cell.region &= -radius['E']
                cell.region &= +radius['prevS']
                cell.region &= -radius['prevN']
              elif d == 'W':
                cell.region  = +radius['W']
                cell.region &= -radius['prevW']
                cell.region &= +radius['prevS']
                cell.region &= -radius['prevN']
              if rot is not None: 
                cell.rotation = rot
              self.add_cell(cell)

          elif octagon:
            # There are two cases that we need to handle. The first is where the vertices of the box
            # are inside the triangles formed by the octagon's corners (a large box inside a relatively
            # small octagon) and the second where the vertices of the box are outside the triangles 
            # formed by the corners of the octagon (a small box inside a relatively large octagon)
            # I expect that only the former case will be relevant for TREAT, but we should at least
            # have a warning for the user in case something unexpected is requested.

            # First, check to see which case we have
            chamf_position = radius['E'].coefficients['x0'] - radius['Dummy'].coefficients['x0']/math.sqrt(2.0)
            box_position = radius['prevE'].coefficients['x0']

            if (chamf_position < box_position):
              # We have the expected case of a box tightly fitting inside the octagon

              # Go through and start generating the cells
              # Basic cells comprising the rectangles directly adjacent to the long (non-chamfered)
              # surfaces of the fuel element
              cellN = openmc.Cell(name=(label+" box N"), fill=fill)
              cellS = openmc.Cell(name=(label+" box S"), fill=fill)
              cellE = openmc.Cell(name=(label+" box E"), fill=fill)
              cellW = openmc.Cell(name=(label+" box W"), fill=fill)
              # Cells comprising the rectangles directly adjacent to the short (chamfered)
              # surfaces of the fuel element
              cellNE = openmc.Cell(name=(label+" box NE"), fill=fill)
              cellNW = openmc.Cell(name=(label+" box NW"), fill=fill)
              cellSE = openmc.Cell(name=(label+" box SE"), fill=fill)
              cellSW = openmc.Cell(name=(label+" box SW"), fill=fill)
              # Cells connecting the two previous sets
              cellNNE = openmc.Cell(name=(label+" box NNE"), fill=fill) # N cell to NE cell
              cellNNW = openmc.Cell(name=(label+" box NNW"), fill=fill) # N cell to NW cell
              cellESE = openmc.Cell(name=(label+" box ESE"), fill=fill) # E cell to SE cell
              cellWSW = openmc.Cell(name=(label+" box WSW"), fill=fill) # W cell to SW cell
              cellENE = openmc.Cell(name=(label+" box ENE"), fill=fill) # E cell to NE cell
              cellWNW = openmc.Cell(name=(label+" box WNW"), fill=fill) # W cell to NW cell
              cellSSE = openmc.Cell(name=(label+" box SSE"), fill=fill) # S cell to SE cell
              cellSSW = openmc.Cell(name=(label+" box SSW"), fill=fill) # S cell to SW cell
            
              # Add the surfaces to the cells
            
              # North Cell
              cellN.region  = -radius['N']     # North face
              cellN.region &= +radius['prevN'] # South face
              cellN.region &= -radius['IE']    # East face
              cellN.region &= +radius['IW']    # West face
              # South Cell
              cellS.region  = -radius['prevS'] # North face
              cellS.region &= +radius['S']     # South face
              cellS.region &= -radius['IE']    # East face
              cellS.region &= +radius['IW']    # West face
              # East Cell
              cellE.region  = -radius['IN']    # North face
              cellE.region &= +radius['IS']    # South face
              cellE.region &= -radius['E']     # East face
              cellE.region &= +radius['prevE'] # West face
              # West Cell
              cellW.region  = -radius['IN']    # North face
              cellW.region &= +radius['IS']    # South face
              cellW.region &= -radius['prevW'] # East face
              cellW.region &= +radius['W']     # West face
            
              # North-East Cell
              cellNE.region  = -radius['NE']    # North-East face
              cellNE.region &= +radius['prevN'] # South face
              cellNE.region &= +radius['prevE'] # West face
              # North-West Cell
              cellNW.region  = -radius['NW']    # North-West face
              cellNW.region &= +radius['prevN'] # South face
              cellNW.region &= -radius['prevW'] # East face
              # South-East Cell
              cellSE.region  = +radius['SE']    # South-East face
              cellSE.region &= -radius['prevS'] # North face
              cellSE.region &= +radius['prevE'] # West face
              # South-West Cell
              cellSW.region  = +radius['SW']    # South-West face
              cellSW.region &= -radius['prevS'] # North face
              cellSW.region &= -radius['prevW'] # East face
            
              # North-North-East Cell
              cellNNE.region  = -radius['prevE'] # East face
              cellNNE.region &= +radius['prevN'] # South face
              cellNNE.region &= -radius['NE']    # North-East face
              cellNNE.region &= +radius['IE']    # West face
              # North-North-West Cell
              cellNNW.region  = +radius['prevN'] # South face
              cellNNW.region &= +radius['prevW'] # West face
              cellNNW.region &= -radius['IW']    # East face
              cellNNW.region &= -radius['NW']    # North-West face
              # South-South-East Cell
              cellSSE.region  = -radius['prevE'] # East face
              cellSSE.region &= -radius['prevS'] # North face
              cellSSE.region &= +radius['SE']    # South-East face
              cellSSE.region &= +radius['IE']    # West face
              # South-South-West Cell
              cellSSW.region  = +radius['SW']    # South-West face
              cellSSW.region &= -radius['prevS'] # North face
              cellSSW.region &= -radius['IW']    # East face
              cellSSW.region &= +radius['prevW'] # West face
              # East-North-East Cell
              cellENE.region  = -radius['NE']    # North-East face
              cellENE.region &= +radius['prevE'] # West face
              cellENE.region &= +radius['IN']    # South face
              cellENE.region &= -radius['prevN'] # North face
              # West-North-West Cell
              cellWNW.region  = -radius['NW']    # North-West face
              cellWNW.region &= -radius['prevN'] # North face
              cellWNW.region &= +radius['IN']    # South face
              cellWNW.region &= -radius['prevW'] # East face
              # East-South-East Cell
              cellESE.region  = +radius['SE']    # South-East face
              cellESE.region &= +radius['prevE'] # West face
              cellESE.region &= -radius['IS']    # North face
              cellESE.region &= +radius['prevS'] # South face
              # West-South-West Cell
              cellWSW.region  = +radius['SW']    # South-West face
              cellWSW.region &= -radius['prevW'] # East face
              cellWSW.region &= -radius['IS']    # North face
              cellWSW.region &= +radius['prevS'] # South face
            
              # Add the cells 
              self.add_cell(cellN)
              self.add_cell(cellS)
              self.add_cell(cellE)
              self.add_cell(cellW)
              self.add_cell(cellNE)
              self.add_cell(cellNW)
              self.add_cell(cellSE)
              self.add_cell(cellSW)
              self.add_cell(cellNNE)
              self.add_cell(cellNNW)
              self.add_cell(cellSSE)
              self.add_cell(cellSSW)
              self.add_cell(cellENE)
              self.add_cell(cellWNW)
              self.add_cell(cellESE)
              self.add_cell(cellWSW)
            else:
              # We have the other case of a small box loosely fitting inside an octagon
              print("WARNING: the user requested a small box surrounded by a large octagon."+\
                    " This has not yet been implimented")

          else:
            # this is a regular cylinder, and the last one was a box ring

            for d in ['N', 'S', 'E', 'W']:
              boxlabel = "{0} box {1}".format(label, d)
              cell = openmc.Cell(name=boxlabel, fill=fill)
              cell.region  = -r
              if d == 'N':
                cell.region &= +radius['prevN']
              elif d == 'S':
                cell.region &= -radius['prevS']
              elif d == 'E':
                cell.region &= +radius['prevE']
                cell.region &= +radius['prevS']
                cell.region &= -radius['prevN']
              elif d == 'W':
                cell.region &= -radius['prevW']
                cell.region &= +radius['prevS']
                cell.region &= -radius['prevN']
              if rot is not None: 
                cell.rotation = rot
              self.add_cell(cell)

        else:
          # the last ring was a regular cylinder
          
          if octagon:
            # this is an octagonal ring, and the last one was a regular cylinder
            # Define the cells
            cellC = openmc.Cell(name=(label+" box C"), fill=fill)
            cellN = openmc.Cell(name=(label+" box N"), fill=fill)
            cellS = openmc.Cell(name=(label+" box S"), fill=fill)
            cellE = openmc.Cell(name=(label+" box E"), fill=fill)
            cellW = openmc.Cell(name=(label+" box W"), fill=fill)
            cellNE = openmc.Cell(name=(label+" box NE"), fill=fill)
            cellNW = openmc.Cell(name=(label+" box NW"), fill=fill)
            cellSE = openmc.Cell(name=(label+" box SE"), fill=fill)
            cellSW = openmc.Cell(name=(label+" box SW"), fill=fill)
            # Add the surfaces to the cells
            # Central Cell
            cellC.region  = +radius['prevR'] # Central cylinder
            cellC.region &= -radius['IN']    # North face
            cellC.region &= +radius['IS']    # South face
            cellC.region &= -radius['IE']    # East face
            cellC.region &= +radius['IW']    # West face
            # North Cell
            cellN.region  = -radius['N']  # North face
            cellN.region &= +radius['IN'] # South face
            cellN.region &= -radius['IE'] # East face
            cellN.region &= +radius['IW'] # West face
            # South Cell
            cellS.region  = -radius['IS'] # North face
            cellS.region &= +radius['S']  # South face
            cellS.region &= -radius['IE'] # East face
            cellS.region &= +radius['IW'] # West face
            # East Cell
            cellE.region  = -radius['IN'] # North face
            cellE.region &= +radius['IS'] # South face
            cellE.region &= -radius['E']  # East face
            cellE.region &= +radius['IE'] # West face
            # West Cell
            cellW.region  = -radius['IN'] # North face
            cellW.region &= +radius['IS'] # South face
            cellW.region &= -radius['IW'] # East face
            cellW.region &= +radius['W']  # West face
            # North-East Cell
            cellNE.region  = -radius['NE'] # North-East face
            cellNE.region &= +radius['IN'] # South face
            cellNE.region &= +radius['IE'] # West face
            # North-West Cell
            cellNW.region  = -radius['NW'] # North-West face
            cellNW.region &= +radius['IN'] # South face
            cellNW.region &= -radius['IW'] # East face
            # South-East Cell
            cellSE.region  = +radius['SE'] # South-East face
            cellSE.region &= -radius['IS'] # North face
            cellSE.region &= +radius['IE'] # West face
            # South-West Cell
            cellSW.region  = +radius['SW'] # South-West face
            cellSW.region &= -radius['IS'] # North face
            cellSW.region &= -radius['IW'] # East face
            # Cut out the regions that have enclaves
            if nEnclaves > 0: # This is one of the inside / outside geometry pairs where we have to deal with making circular
                              # holes of empty space to include off center cell elements
              for counter in range(1,nEnclaves+1):
                local_string  = 'Enclave' + str(counter) # Expecting each of the ZCylinder keys for subsequent enclaves to be 
                                                         # of the format 'Enclave1', 'Enclave2', 'Enclave3', etc
                cellC.region   &= +radius[local_string]  # Region that does not get filled with our material for this cell
                cellN.region   &= +radius[local_string]  # Most of the enclaves will be cut out of the central cell, but
                cellS.region   &= +radius[local_string]  # there is the possibility for some overlap with the outer cells.
                cellE.region   &= +radius[local_string]  # Go through and explicitly state for each cell that it should not
                cellW.region   &= +radius[local_string]  # contain any enclave region
                cellNE.region  &= +radius[local_string]  # 
                cellNW.region  &= +radius[local_string]  # 
                cellSE.region  &= +radius[local_string]  # 
                cellSW.region  &= +radius[local_string]  # 
            # Add the cells 
            self.add_cell(cellC)
            self.add_cell(cellN)
            self.add_cell(cellS)
            self.add_cell(cellE)
            self.add_cell(cellW)
            self.add_cell(cellNE)
            self.add_cell(cellNW)
            self.add_cell(cellSE)
            self.add_cell(cellSW)

          elif box:
            # this is a box ring, and the last one was a regular cylinder

            cell = openmc.Cell(name=label, fill=fill)
            cell.region  = +radius['prevR']
            cell.region &= +radius['S']
            cell.region &= -radius['N']
            cell.region &= +radius['W']
            cell.region &= -radius['E']
            if rot is not None: 
              cell.rotation = rot
            # Cut out the region that has enclaves
            if nEnclaves > 0: # This is one of the inside / outside geometry pairs where we have to deal with making circular
                              # holes of empty space to include off center cell elements
              for counter in range(1,nEnclaves+1):
                local_string  = 'Enclave' + str(counter) # Expecting each of the ZCylinder keys for subsequent enclaves to be 
                                                         # of the format 'Enclave1', 'Enclave2', 'Enclave3', etc
                cell.region   &= +radius[local_string]  # Region that does not get filled with our material for this cell
            self.add_cell(cell)

          else:
            # this is a regular ring, and the last one was a regular cylinder

            cell = openmc.Cell(name=label, fill=fill)
            cell.region  = +radius['prevR']
            cell.region &= -radius['R']
            if rot is not None: 
              cell.rotation = rot
            self.add_cell(cell)

    ## Now write the outermost cell(s) that go to infinity

    label = "{0} radial outer: {1}".format(self._name, self.fills[-1]._name)

    if self.octagon[-1]:
      # the last one is an octagonal cell, we need outer cells to infinity

      # Define the cells
      cellN = openmc.Cell(name=(label+" box N"), fill=self.fills[-1])
      cellS = openmc.Cell(name=(label+" box S"), fill=self.fills[-1])
      cellE = openmc.Cell(name=(label+" box E"), fill=self.fills[-1])
      cellW = openmc.Cell(name=(label+" box W"), fill=self.fills[-1])
      cellNE_I = openmc.Cell(name=(label+" box NE inner"), fill=self.fills[-1])
      cellNW_I = openmc.Cell(name=(label+" box NW inner"), fill=self.fills[-1])
      cellSE_I = openmc.Cell(name=(label+" box SE inner"), fill=self.fills[-1])
      cellSW_I = openmc.Cell(name=(label+" box SW inner"), fill=self.fills[-1])
      cellNE = openmc.Cell(name=(label+" box NE"), fill=self.fills[-1])
      cellNW = openmc.Cell(name=(label+" box NW"), fill=self.fills[-1])
      cellSE = openmc.Cell(name=(label+" box SE"), fill=self.fills[-1])
      cellSW = openmc.Cell(name=(label+" box SW"), fill=self.fills[-1])
      # Add the surfaces to the cells
      # North Cell
      cellN.region  = +self.radii[-1]['N'] # South face
      cellN.region &= -self.radii[-1]['E'] # East face
      cellN.region &= +self.radii[-1]['W'] # West face
      # South Cell
      cellS.region  = -self.radii[-1]['S'] # North face
      cellS.region &= -self.radii[-1]['E'] # East face
      cellS.region &= +self.radii[-1]['W'] # West face
      # East Cell
      cellE.region  = -self.radii[-1]['N'] # North face
      cellE.region &= +self.radii[-1]['S'] # South face
      cellE.region &= +self.radii[-1]['E'] # West face
      # West Cell
      cellW.region  = -self.radii[-1]['N'] # North face
      cellW.region &= +self.radii[-1]['S'] # South face
      cellW.region &= -self.radii[-1]['W'] # East face
      # North-East Cell
      cellNE.region    = +self.radii[-1]['N']  # South face
      cellNE.region   &= +self.radii[-1]['E']  # West face
      # Inner North-East Cell
      cellNE_I.region  = -self.radii[-1]['N']  # North face
      cellNE_I.region &= -self.radii[-1]['E']  # East face
      cellNE_I.region &= +self.radii[-1]['NE'] # South-West face
      # North-West Cell
      cellNW.region    = +self.radii[-1]['N']  # South face
      cellNW.region   &= -self.radii[-1]['W']  # East face
      # Inner North-West Cell
      cellNW_I.region  = -self.radii[-1]['N']  # North face
      cellNW_I.region &= +self.radii[-1]['W']  # West face
      cellNW_I.region &= +self.radii[-1]['NW'] # South-East face
      # South-East Cell
      cellSE.region    = -self.radii[-1]['S']  # North face
      cellSE.region   &= +self.radii[-1]['E']  # West face
      # Inner South-East Cell
      cellSE_I.region  = +self.radii[-1]['S']  # South face
      cellSE_I.region &= -self.radii[-1]['E']  # East face
      cellSE_I.region &= -self.radii[-1]['SE'] # North-West face
      # South-West Cell
      cellSW.region    = -self.radii[-1]['S']  # North face
      cellSW.region   &= -self.radii[-1]['W']  # East face
      # Inner South-West Cell
      cellSW_I.region  = +self.radii[-1]['S']  # South face
      cellSW_I.region &= +self.radii[-1]['W']  # West face
      cellSW_I.region &= -self.radii[-1]['SW'] # North-East face
      # Add the cells 
      self.add_cell(cellN)
      self.add_cell(cellS)
      self.add_cell(cellE)
      self.add_cell(cellW)
      self.add_cell(cellNE)
      self.add_cell(cellNE_I)
      self.add_cell(cellNW)
      self.add_cell(cellNW_I)
      self.add_cell(cellSE)
      self.add_cell(cellSE_I)
      self.add_cell(cellSW)
      self.add_cell(cellSW_I)

    elif self.box[-1]:
      # the last one is a box, we need 4 outer cells to infinity

      for d in ['N', 'S', 'E', 'W']:
        boxlabel = "{0} box {1}".format(label, d)

        cell = openmc.Cell(name=boxlabel, fill=self.fills[-1])
        if d == 'N':
          cell.region  = +self.radii[-1]['N']
        elif d == 'S':
          cell.region  = -self.radii[-1]['S']
        elif d == 'E':
          cell.region  = +self.radii[-1]['E']
          cell.region &= +self.radii[-1]['S']
          cell.region &= -self.radii[-1]['N']
        elif d == 'W':
          cell.region  = -self.radii[-1]['W']
          cell.region &= +self.radii[-1]['S']
          cell.region &= -self.radii[-1]['N']
        if self.rot[-1] is not None: 
          cell.rotation = self.rot[-1]
        self.add_cell(cell)

    else:

      # the last one is a regular cylindrical ring - just one cell to infinity
      cell = openmc.Cell(name=label, fill=self.fills[-1])
      if isinstance(self.radii[-1], dict):
        cell.region  = +self.radii[-1]['R']
      elif isinstance(self.radii[-1], (openmc.ZCylinder, openmc.Sphere)):
        cell.region  = +self.radii[-1]
      if self.rot[-1] is not None: 
        cell.rotation = self.rot[-1]
      self.add_cell(cell)

    self.finalized = True


class AxialElement(openmc.Universe, TranslationRotationMixin):
  """ Class for containing a complete axial description of an element
  
  AxialElements consist of a set of InfiniteElements and the axial planes that
  define the axial boundaries of each.  They also allow for a fully-constructed
  element to be "wrapped" by another element, e.g., elements containing grids or
  guide tubes.
  
  """

  def __init__(self, *args, **kwargs):
    """ Create a new AxialElement
    """
    super(AxialElement, self).__init__(*args, **kwargs)
    self.axials = []
    self.elements = []
    self.finalized = False
    self.outermost = None

  def add_axial_section(self, axial_plane, element):
    """ Adds an axial section to the stack
    
    Stacks must be built from the bottom-up. Each new section goes from the
    previous axial_plane to the given axial_plane (or from infinity to the
    given plane if it's the first section added).
    
    It's up to the user to ensure that all planes are z-planes, and that
    sections are added in the correct order.

    A call to add_last_axial_section must be made to add the top-most section.

    :param axial_plane: Axial surface below which to add the new element
    :param element: InfiniteElement or material to add to the top of the stack
    
    """
    self.axials.append(axial_plane)
    self.elements.append(element)
    if isinstance(element, InfiniteElement):
      self.compare_outermost(element)

  def add_last_axial_section(self, element):
    """ Adds the last axial section to the top of the stack
    
    :param element: InfiniteElement or material that goes to infinity at the top
    
    """
    self.elements.append(element)
    if isinstance(element, InfiniteElement):
      self.compare_outermost(element)

  def compare_outermost(self, element):
    """ Finds if the element has the largest outer radius amongst all sections
    """
    if not self.outermost:
      self.outermost = element
    else:
      if isinstance(self.outermost.radii[-1], (openmc.ZCylinder, openmc.Sphere)):
        # current is a basic OpenMC cylinder
        current = self.outermost.radii[-1].coefficients['R']
      elif 'R' in self.outermost.radii[-1].keys():
        # current is a basic cylinder within a dictionary
        current = self.outermost.radii[-1]['R'].coefficients['R']
      else:
        # current is a box or TREAT octagon
        current = self.outermost.radii[-1]['N'].coefficients['y0']
      if isinstance(element.radii[-1], openmc.ZCylinder):
        # new one is a basic OpenMC cylinder
        new = element.radii[-1].coefficients['R']
      elif 'R' in element.radii[-1].keys():
        # new one is a basic cylinder within a dictionary
        new = element.radii[-1]['R'].coefficients['R']
      else:
        # new one is a box or TREAT octagon
        new = element.radii[-1]['N'].coefficients['y0']
      if new > current:
        self.outermost = element

  def add_wrapper(self, wrapper):
    """ Adds a element to wrap the height, returning a new InfiniteElement
    
    This should only be called after AFTER all axial sections are added.

    This uses the outer-most radius amongst all elements in the wrappee, and
    uses that to form the ring of the new InfiniteElement.  It's up to the user
    to make sure all radii of the outer element are larger than the this radius,
    otherwise cells in the wrapper may be clipped.

    :param wrapper: Another InfiniteElement or AxialElement to wrap this element

    """

    if self == wrapper:
      return self

    new_name = "({0}) wrapped by ({1})".format(self._name, wrapper._name)

    if new_name in _created_cells:
      return _created_cells[new_name]

    # Finalize the current element
    self.finalize()

    # Make a new element
    new_elem = InfiniteElement(name=new_name)

    # Fill the inner ring with the wrapped universe
    elem = self.outermost
    new_elem.add_ring(self, elem.radii[-1], box=elem.box[-1], rot=elem.rot[-1], octagon=elem.octagon[-1], first=True)

    # Fill the outermost ring with the wrapping universe
    new_elem.add_last_ring(wrapper)
    
    _created_cells[new_name] = new_elem

    return new_elem

  def finalize(self):
    """ Creates the Cells for this universe
    """

    if self.finalized:
      return

    # Instantiate radial cells
    for elem in self.elements:
      if isinstance(elem, InfiniteElement) and not elem.finalized:
        elem.finalize()
    
    # Instantiate the axial cells
    for i, (elem, plane) in enumerate(zip(self.elements, self.axials)):

      label = "{0} axial {1}: {2}".format(self._name, i, elem._name)
      cell = openmc.Cell(name=label, fill=elem)

      if i == 0:
        # Bottom section

        cell.region  = -plane

      else:
        # Middle section

        cell.region  = -plane
        cell.region &= +self.axials[i-1]

      self.add_cell(cell)

    # Top section
    label = "{0} axial top: {1}".format(self._name, self.elements[-1]._name)
    cell = openmc.Cell(name=label, fill=self.elements[-1])
    cell.region  = +self.axials[-1]
  
    self.add_cell(cell)
  
    self.finalized = True


class PartialElement(openmc.Universe, TranslationRotationMixin):
  def __init__(self, full_element, y_surfs,
               outer_fill, clad_fill=None, gap_fill=None,
               clad_o_surfs=None, clad_i_surfs=None,
               window_width=None,
               *args, **kwargs):
    """Container for an InfiniteElement which occupies only part of its cell

    It is important to note that this exclusively builds the IniniteElement
     portion below the y-axis. If you need the element part to exist in the
     other orientations, use the translate_rotate() method inherited from
     TranslationRotationMixin.

    (Note: `clad_o_surfs` and `clad_i_surfs` were intended to take
     the surface dictionary used by InfiniteElement.add_ring(). However,
     only the 'E' and 'W' keys are actually used.)


    Required Parameters:
    --------------------
    full_element:     InfiniteElement or other Universe which occupies part
                        of this universe.

    y_surfs:          dictionary of openmc.Plane, such that
                        {'fill': required; YPlane below which
                                  the InfiniteElement exists
                         'gap':  optional; YPlane below which
                                  a gap exists
                         'clad': optional; YPlane below which
                                  the clad exists }

    outer_fill:       Material, Universe, or InfiniteElement with which to fill
                        all space above the highest YPlane in y_surfs


    Optional Parameters:
    --------------------
    clad_fill:        Material or Universe with which to fill the 'clad' layer

    gap_fill:         Material or Universe with which to fill the 'gap' layer

    clad_o_surfs:     if `clad_fill` is specified, dictionary of surfaces
                        defining the outside of the clad region.

    clad_i_surfs:     if `gap_fill` is specified, dictionary of surfaces
                        defining the outside of the gap region.

    window_width:     float; x-width in cm of an access hole opening,
                        if one is present.
    """
    super().__init__(*args, **kwargs)
    self.full_element = full_element
    self.y_surfs = y_surfs
    self.outer_fill = outer_fill
    self.clad_fill = clad_fill
    self.gap_fill = gap_fill
    self.clad_o_surfs = clad_o_surfs
    self.clad_i_surfs = clad_i_surfs
    self.window_width = window_width

  def finalize(self):
    half_fillcell = openmc.Cell(name="Half lead brick (inside)")
    half_fillcell.fill = self.full_element
    half_fillcell.region = -self.y_surfs['fill']
    self.add_cell(half_fillcell)
    last_y = self.y_surfs['fill']

    if 'gap' in self.y_surfs:
      assert self.gap_fill is not None, \
        "You have specified a gap in y_surfs, but not a material or universe " \
        "with which to fill the gap."
      half_gap_cell = openmc.Cell(name=self.name + " (gap)")
      half_gap_cell.fill = self.gap_fill
      half_gap_cell.region = +last_y & -self.y_surfs['gap']

      if self.clad_i_surfs is not None:
        half_gap_cell.region &= +self.clad_i_surfs['W'] & -self.clad_i_surfs['E']

      self.add_cell(half_gap_cell)
      last_y = self.y_surfs['gap']

    if 'clad' in self.y_surfs:
      assert self.gap_fill is not None, \
        "You have specified a clad in y_surfs, but not a material or universe " \
        "with which to fill the clad."
      half_can_cell = openmc.Cell(name=self.name + " (clad)")
      half_can_cell.fill = self.clad_fill
      half_can_cell.region = +last_y & -self.y_surfs['clad']

      if self.window_width:
        hw = self.window_width/2.0
        half_window_E = openmc.XPlane(name="Half-width element, east edge of window",
                                      x0=+hw)
        half_window_W = openmc.XPlane(name="Half-width element, west edge of window",
                                      x0=-hw)
        window_side = (-self.clad_o_surfs['E'] & +half_window_E) | \
                      (+self.clad_o_surfs['W'] & -half_window_W)
        half_can_cell.region &= window_side

        window_cell = openmc.Cell(name="Half-width window")
        window_cell.fill = self.outer_fill
        window_cell.region = +half_window_W & -half_window_E & \
                             +last_y & -self.y_surfs['clad']
        self.add_cell(window_cell)
      else:
        half_can_cell.region &= +self.clad_o_surfs['W'] & -self.clad_o_surfs['E']

      if self.clad_o_surfs is not None and self.clad_i_surfs is not None:
        half_can_fixW = openmc.Cell(name=self.name + " (west clad fill)")
        half_can_fixW.fill = self.clad_fill
        half_can_fixW.region = +self.clad_o_surfs['W'] & -self.clad_i_surfs['W'] & \
                               +self.y_surfs['fill'] & -self.y_surfs['gap']

        half_can_fixE = openmc.Cell(name=self.name + " (east clad fill)")
        half_can_fixE.fill = self.clad_fill
        half_can_fixE.region = +self.clad_i_surfs['E'] & -self.clad_o_surfs['E'] & \
                               +self.y_surfs['fill'] & -self.y_surfs['gap']
        self.add_cells((half_can_fixE, half_can_fixW))

      self.add_cell(half_can_cell)
      last_y = self.y_surfs['clad']

      # And then fix the little outer box
      if self.clad_o_surfs is not None or self.clad_i_surfs is not None:
        half_gap_fixW = openmc.Cell(name=self.name + " (west outer box fill)")
        half_gap_fixW.fill = self.outer_fill
        half_gap_fixW.region = +self.y_surfs['fill'] & -last_y

        half_gap_fixE = openmc.Cell(name=self.name + " (east outer box fill)")
        half_gap_fixE.fill = self.outer_fill
        half_gap_fixE.region = +self.y_surfs['fill'] & -last_y

        if self.clad_o_surfs is not None:
          half_gap_fixW.region &= -self.clad_o_surfs['W']
          half_gap_fixE.region &= +self.clad_o_surfs['E']
        else:
          half_gap_fixW.region &= -self.clad_i_surfs['W']
          half_gap_fixE.region &= +self.clad_i_surfs['E']

        self.add_cells((half_gap_fixE, half_gap_fixW))

    half_out_cell = openmc.Cell(name=self.name + " (outside)")
    half_out_cell.fill = self.outer_fill
    half_out_cell.region = +last_y
    self.add_cell(half_out_cell)
