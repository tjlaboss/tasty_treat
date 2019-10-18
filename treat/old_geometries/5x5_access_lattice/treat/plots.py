"""plots.py

"""

from collections import OrderedDict
from common_files.treat.baseplot import BasePlot
import common_files.treat.constants as c


class Plots(BasePlot):
  def __init__(self, mats, xwidth=5*c.latticePitch, ywidth=5*c.latticePitch,
               H=c.struct_UpperAir_top - c.struct_CoreFloor_top):
    """ Creates TREAT plots"""
    super().__init__(mats, xwidth, ywidth, H)
    extra_xys = OrderedDict({
      "upperAccessZrTube": (c.struct_accessWindow48_top + c.struct_accessTube48_top)/2.0,
      "upperAccessSpacer": (c.struct_accessTube48_top + c.struct_accessZr48_top)/2.0,
      "upperAccessZrSP": (c.struct_accessZr48_top + c.struct_accessUpperSP48_lower)/2.0,
      "upperAccessPb": (c.struct_accessUpperDummy_top + c.struct_accessUpperLead_top)/2.0,
    })
    extra_xzs = OrderedDict({
      "midElement_xz": (0, 0, (H/2 + c.struct_CoreFloor_top) )
    })
    extra_yzs = OrderedDict({
      "midElement_yz": (0, 0, (H/2 + c.struct_CoreFloor_top) )
    })
    self._add_plots(xy_dict=extra_xys, xz_dict=extra_xzs, yz_dict=extra_yzs)
