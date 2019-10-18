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
    extra_radials = OrderedDict({
      "upperCrdThinAlBearing": (c.struct_crdBearThin_top + c.struct_crdElemTube_top)/2.0,
      "upperCrdBushRetMsp": (c.struct_crdBearThin_top + c.struct_UpperShortPlug_mid)/2.0,
      "upperCrdBushRet": (c.struct_crdBushRet_top + c.struct_UpperShortPlug_mid)/2.0,
      "upperCrdBushOGTube": (c.struct_crdBushRet_top + c.struct_crdOffGasTube_top)/2.0,
      "upperCrdBushOGCrimp": (c.struct_crdOffGasCrimp_top + c.struct_crdOffGasTube_top)/2.0,
      "upperCrdBushOGHole": (c.struct_crdOffGasCrimp_top + c.struct_crdOffGasDrillHole_top)/2.0,
      "upperCrdBush": (c.struct_crdBush_top + c.struct_crdOffGasDrillHole_top)/2.0,
      "upperCrdSP": (c.struct_crdBush_top + c.struct_UpperShortPlug_top)/2.0,
      "upperCrdHeadTop": (c.struct_upperCrdHead_mid + c.struct_upperCrdHead_top)/2.0,
      "upperCrdHeadBase": (c.struct_UpperLongPlug_top + c.struct_upperCrdHead_mid)/2.0,
      "upperCrdExtraBearing": (c.struct_upperCrdTube_top + c.struct_upperCrdHead_top)/2.0,
      "upperCrdZrGuideTube": (c.struct_UpperAlSpace_top + c.struct_crdElemTube_top)/2.0,
      "lowerCrdBase": (c.struct_lowerCrdBase_bot + c.struct_LowerReflec_bot)/2.0,
      "lowerCrdTube": (c.struct_lowerCrdBase_bot + c.struct_lowerCrdTube_bot)/2.0,
    })
    extra_xzs = OrderedDict({
      "midElement_xz": (0, 0, (H/2 + c.struct_CoreFloor_top) )
    })
    self._add_plots(xy_dict=extra_radials, xz_dict=extra_xzs)
