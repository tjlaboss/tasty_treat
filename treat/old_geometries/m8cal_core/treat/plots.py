"""plots.py

"""

from collections import OrderedDict
from common_files.treat.baseplot import BasePlot
import common_files.treat.constants as c


class Plots(BasePlot):
# def __init__(self, mats, xwidth=(2.0*c.excoreReflecOuter), ywidth=(2.0*c.excoreReflecOuter),
#              H=c.struct_HighestExtent - c.struct_LowestExtent):
  def __init__(self, mats, xwidth=(2.0*c.excoreOuter+c.latticePitch), ywidth=(2.0*c.excoreOuter+c.latticePitch),
               H=c.struct_HighestExtent - c.struct_LowestExtent):
    """ Creates TREAT plots"""
    super().__init__(mats, xwidth, ywidth, H)
    extra_xys = OrderedDict({
      "upperTieBolt": c.struct_excoreTieBoltUpper,
      "middleTieBolt": c.struct_excoreTieBoltMiddle,
      "lowerTieBolt": c.struct_excoreTieBoltLower,
      "upperInstrumentTube": c.struct_excoreReflInstrUpper,
      "lowerInstrumentTube": c.struct_excoreReflInstrBottom,
      "excureTopPlugBoral": (c.struct_excore_upper_boral_top + c.struct_excore_steel_top)/2.0
    })
    extra_xzs = OrderedDict({
      "midElement_xz": (0, 0, self._H/2),
      "midFirstCrdLayer_xz": (0, 2.0*c.latticePitch, self._H/2),
      "midSecondCrdLayer_xz": (0, 4.0*c.latticePitch, self._H/2),
      "midThirdCrdLayer_xz": (0, 6.0*c.latticePitch, self._H/2),
      "midFourthCrdLayer_xz": (0, 7.0*c.latticePitch, self._H/2),
    })
    extra_yzs = OrderedDict({
      "midElement_yz": self._H/2
    })

    self._add_plots(xy_dict=extra_xys, xz_dict=extra_xzs, yz_dict=extra_yzs, res=2000)
