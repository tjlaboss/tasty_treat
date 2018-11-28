# Plot Power
#
# Plot axial and radial power profiles

import openmc
from pylab import *

sys.path.append("..")
#import constants as c


def plot_axial_power(xlist, zlist, title_text=""):
  """Plot the axial power distribution

  Parameters:
  -----------
  xlist:          array or list of the power magnitude
  zlist:          array or list of the z-values (cm) of the powers
  title_text:     string containing the plot title
                  [Default: empty string]


  Returns:
  --------
  axial_plot:    pyplot.plot instance
  """
  figure()
  axial_plot = plot(xlist, zlist)
  xlabel("Relative power")
  ylabel("z (cm)")
  grid()
  if title_text:
    title(title_text, fontsize=20)
  return axial_plot


def plot_radial_power(radial_power, bounds=(-1, 1, -1, 1), title_text=""):
  """Plot the radial power distribution

  Parameters:
  -----------
  radial_power:   [x, y] array of the power distribution
  bounds:         (-x, +x, -y, +y) bounds to use for labeling the axes
                  [Default: -1 to 1]
  title_text:     string containing the plot title
                  [Default: empty string]

  Returns:
  --------
  radial_plot:    pyplot.plot instance
  """
  figure()
  radial_power /= np.nanmean(radial_power)
  scale = max(nanmax(radial_power) - 1, 1 - abs(nanmin(radial_power)))
  print(nanmin(radial_power), nanmax(radial_power))
  radial_plot = rad_plot = imshow(radial_power, cmap="jet", extent=bounds,
                                  vmax=1+scale, vmin=1-scale)

  colorbar(rad_plot)
  if title_text:
    title(title_text, fontsize=20)
  return radial_plot


# Test
if __name__ == "__main__":
  zed = cuts.Z0
  directory = "m8cal_core"
  sp = openmc.StatePoint("../../../{}/statepoint.1000.h5".format(directory))
  lat = sp.summary.geometry.get_all_lattices()[c.ROOT_LATTICE]
  test_group = meshes.get_mesh_group_from_lattice(lat, z0=zed)
  test_group.nzs = cuts.n_cuts
  test_group.dzs = cuts.dzs
  test_group.build_group()
  xlist, zlist = test_group.get_axial_power(sp, eps=1E-5)
  x0 = test_group.x0
  y0 = test_group.y0
  bounds = (x0, -x0, y0, -y0)
  plot_axial_power(xlist, zed+zlist)
  #plot_radial_power((test_group.get_radial_power(sp, zval=250, eps=0)), bounds)
  plot_radial_power(test_group.get_radial_power_by_tally(sp, tally_id=10, index=3), bounds)
  show()
