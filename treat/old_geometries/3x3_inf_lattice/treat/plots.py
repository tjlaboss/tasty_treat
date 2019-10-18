"""plots.py

"""

from collections import OrderedDict
from common_files.treat.baseplot import BasePlot
import common_files.treat.constants as c


class Plots(BasePlot):
  def __init__(self, mats, xwidth=3*c.latticePitch, ywidth=3*c.latticePitch,
               H=c.struct_UpperAir_top - c.struct_CoreFloor_top):
    """ Creates TREAT plots"""
    super().__init__(mats, xwidth, ywidth, H)
    extra_xzs = OrderedDict({
      "midElement_xz": (0, 0, (H/2 + c.struct_CoreFloor_top) )
    })
    self._add_plots(xz_dict=extra_xzs)
