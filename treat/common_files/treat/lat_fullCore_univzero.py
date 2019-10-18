"""univzero.py

Provides a container class for the TREAT main universe cells

"""

import common_files.treat.constants as c
import math
import openmc

class UniverseZero(openmc.Universe):

  def __init__(self, core, mats):
    """ Creates TREAT infinite lattice of basic fuel assemblies """

    super(UniverseZero, self).__init__(name='Main TREAT lattice universe', universe_id=0)

    self.core = core # Here, the "core" is just a 3x3 set of elements element that will be surrounded by reflective surfaces
                     # Leaving the term core because that will become more appropriate when going to larger lattices
    self.mats = mats

    self._add_permanent_reflector()
    self._add_biological_shield()
    self._add_outer_universe()
    self._add_core()
    self._create_main_universe()

  def _add_permanent_reflector(self):
    """ Adds the various cells that comprise the TREAT excore reflector """

    self.s_upperBound = openmc.ZPlane(name='Highest Extent', z0=c.struct_HighestExtent, boundary_type='vacuum')
    self.s_lowerBound = openmc.ZPlane(name='Lowest Extent', z0=c.struct_LowestExtent, boundary_type='vacuum')
    self.s_reflecFloor = openmc.ZPlane(name='Reflector Floor', z0=c.struct_bff_base_bot) # Floor of Refl is at
                                                                                 # bottom of wide part of support pin
    self.s_belowCoreFloor = openmc.ZPlane(name='Top of concrete floor below the core', z0=c.struct_CoreFloor_top)
    self.s_aboveReflRoof = openmc.ZPlane(name='Bottom of the concrete ceiling above the permanent reflector', z0=c.struct_UpperAir_top)
    self.s_aboveCoreRoof = openmc.ZPlane(name='Bottom of the concrete ceiling above the core', z0=c.struct_UpperCoreAir_top)

    # First do the air gap between the core itself and the permanent reflector
    fill_material = self.mats['Air']
    region_name = 'Gap between core and permanent reflector'
    # Define the surfaces we'll need
    self.s_coreBound_N = openmc.YPlane(name='N Core Bound', y0= c.excoreInner)
    self.s_coreBound_S = openmc.YPlane(name='S Core Bound', y0=-c.excoreInner)
    self.s_coreBound_E = openmc.XPlane(name='E Core Bound', x0= c.excoreInner)
    self.s_coreBound_W = openmc.XPlane(name='W Core Bound', x0=-c.excoreInner)
    self.s_coreGapOuter_N = openmc.YPlane(name='N core adjacent air gap outer', y0= c.excoreGapOuter)
    self.s_coreGapOuter_S = openmc.YPlane(name='S core adjacent air gap outer', y0=-c.excoreGapOuter)
    self.s_coreGapOuter_E = openmc.XPlane(name='E core adjacent air gap outer', x0= c.excoreGapOuter)
    self.s_coreGapOuter_W = openmc.XPlane(name='W core adjacent air gap outer', x0=-c.excoreGapOuter)
    # Define the cells to hold the air
    self.c_coreAirGap_N = openmc.Cell(name=('N ' + region_name), fill=fill_material)
    self.c_coreAirGap_S = openmc.Cell(name=('S ' + region_name), fill=fill_material)
    self.c_coreAirGap_E = openmc.Cell(name=('E ' + region_name), fill=fill_material)
    self.c_coreAirGap_W = openmc.Cell(name=('W ' + region_name), fill=fill_material)
    # Go through and build the cells
    self.c_coreAirGap_N.region = -self.s_coreGapOuter_N & +self.s_coreBound_N & -self.s_coreGapOuter_E \
                               & +self.s_coreGapOuter_W & -self.s_aboveCoreRoof & +self.s_reflecFloor
    self.c_coreAirGap_S.region = +self.s_coreGapOuter_S & -self.s_coreBound_S & -self.s_coreGapOuter_E \
                               & +self.s_coreGapOuter_W & -self.s_aboveCoreRoof & +self.s_reflecFloor
    self.c_coreAirGap_E.region = -self.s_coreBound_N & +self.s_coreBound_S & -self.s_coreGapOuter_E \
                               & +self.s_coreBound_E & -self.s_aboveCoreRoof & +self.s_reflecFloor
    self.c_coreAirGap_W.region = -self.s_coreBound_N & +self.s_coreBound_S & -self.s_coreBound_W \
                               & +self.s_coreGapOuter_W & -self.s_aboveCoreRoof & +self.s_reflecFloor

    # Next do the thin aluminum between the core adjacent gap and the permanent reflector
    # Define the surfaces we'll need
    self.s_coreInnerLinerO_N = openmc.YPlane(name='N inner Aluminum liner outer', y0= c.excoreInnerLinerOuter)
    self.s_coreInnerLinerO_S = openmc.YPlane(name='S inner Aluminum liner outer', y0=-c.excoreInnerLinerOuter)
    self.s_coreInnerLinerO_E = openmc.XPlane(name='E inner Aluminum liner outer', x0= c.excoreInnerLinerOuter)
    self.s_coreInnerLinerO_W = openmc.XPlane(name='W inner Aluminum liner outer', x0=-c.excoreInnerLinerOuter)
    self.s_coreInnerLiner_top = openmc.ZPlane(name='Reflector Inner Liner Top', z0=c.struct_excoreRefl_top)
    # Go through and create the many cells we will need, then build them
    # First the areas above and below the liner
    self.c_coreLinerUAir_N = openmc.Cell(name='Air above north inner aluminum liner', fill=self.mats['Air'])
    self.c_coreLinerLCon_N = openmc.Cell(name='Concrete below north inner aluminum liner', fill=self.mats['Concrete'])
    self.c_coreLinerUAir_N.region = +self.s_coreGapOuter_N & -self.s_coreInnerLinerO_N & -self.s_coreInnerLinerO_E \
                               & +self.s_coreInnerLinerO_W & -self.s_aboveCoreRoof & +self.s_coreInnerLiner_top
    self.c_coreLinerLCon_N.region = +self.s_coreBound_N & -self.s_coreInnerLinerO_N & -self.s_coreInnerLinerO_E \
                               & +self.s_coreInnerLinerO_W & -self.s_reflecFloor & +self.s_lowerBound
    self.c_coreLinerUAir_S = openmc.Cell(name='Air above south inner aluminum liner', fill=self.mats['Air'])
    self.c_coreLinerLCon_S = openmc.Cell(name='Concrete below south inner aluminum liner', fill=self.mats['Concrete'])
    self.c_coreLinerUAir_S.region = -self.s_coreGapOuter_S & +self.s_coreInnerLinerO_S & -self.s_coreInnerLinerO_E \
                               & +self.s_coreInnerLinerO_W & -self.s_aboveCoreRoof & +self.s_coreInnerLiner_top
    self.c_coreLinerLCon_S.region = -self.s_coreBound_S & +self.s_coreInnerLinerO_S & -self.s_coreInnerLinerO_E \
                               & +self.s_coreInnerLinerO_W & -self.s_reflecFloor & +self.s_lowerBound
    self.c_coreLinerUAir_E = openmc.Cell(name='Air above east inner aluminum liner', fill=self.mats['Air'])
    self.c_coreLinerLCon_E = openmc.Cell(name='Concrete below east inner aluminum liner', fill=self.mats['Concrete'])
    self.c_coreLinerUAir_E.region = +self.s_coreGapOuter_S & -self.s_coreGapOuter_N & -self.s_coreInnerLinerO_E \
                               & +self.s_coreGapOuter_E & -self.s_aboveCoreRoof & +self.s_coreInnerLiner_top
    self.c_coreLinerLCon_E.region = +self.s_coreBound_S & -self.s_coreBound_N & -self.s_coreInnerLinerO_E \
                               & +self.s_coreBound_E & -self.s_reflecFloor & +self.s_lowerBound
    self.c_coreLinerUAir_W = openmc.Cell(name='Air above west inner aluminum liner', fill=self.mats['Air'])
    self.c_coreLinerLCon_W = openmc.Cell(name='Concrete below west inner aluminum liner', fill=self.mats['Concrete'])
    self.c_coreLinerUAir_W.region = +self.s_coreGapOuter_S & -self.s_coreGapOuter_N & -self.s_coreGapOuter_W \
                               & +self.s_coreInnerLinerO_W & -self.s_aboveCoreRoof & +self.s_coreInnerLiner_top
    self.c_coreLinerLCon_W.region = +self.s_coreBound_S & -self.s_coreBound_N & -self.s_coreBound_W \
                               & +self.s_coreInnerLinerO_W & -self.s_reflecFloor & +self.s_lowerBound
    # Define some surfaces for when we are building the actual aluminum liner itself
    self.s_inner_liner_N_window_E = openmc.XPlane(name='N inner Aluminum liner window E surface',
                                                  x0=+c.excoreInnerLinerNHoleHW)
    self.s_inner_liner_N_window_W = openmc.XPlane(name='N inner Aluminum liner window W surface',
                                                  x0=-c.excoreInnerLinerNHoleHW)
    self.s_inner_liner_N_window_bot = openmc.ZPlane(name='N inner Aluminum liner window bottom surface',
                                                    z0=c.struct_excoreInnerLinerNWindow_bot)
    self.s_inner_liner_N_window_top = openmc.ZPlane(name='N inner Aluminum liner window top surface',
                                                    z0=c.struct_excoreInnerLinerNWindow_top)

    self.s_core_liner_S_window_E = openmc.XPlane(name='S inner Aluminum liner window E surface', x0=+c.excoreInnerLinerWSHoleHW)
    self.s_core_liner_S_window_W = openmc.XPlane(name='S inner Aluminum liner window W surface', x0=-c.excoreInnerLinerWSHoleHW)
    self.s_core_liner_E_window_N = openmc.YPlane(name='E inner Aluminum liner window N surface', y0=+c.excoreInnerLinerEHoleHW)
    self.s_core_liner_E_window_S = openmc.YPlane(name='E inner Aluminum liner window S surface', y0=-c.excoreInnerLinerEHoleHW)
    self.s_core_liner_W_window_N = openmc.YPlane(name='W inner Aluminum liner window N surface', y0=+c.excoreInnerLinerWSHoleHW)
    self.s_core_liner_W_window_S = openmc.YPlane(name='W inner Aluminum liner window S surface', y0=-c.excoreInnerLinerWSHoleHW)
    self.s_core_liner_WS_window_bot = openmc.ZPlane(name='S and W inner Aluminum liner window bottom surface',
                                                    z0=c.struct_excoreInnerLinerWSWindow_bot)
    self.s_core_liner_WS_window_top = openmc.ZPlane(name='S and W inner Aluminum liner window top surface',
                                                    z0=c.struct_excoreInnerLinerWSWindow_top)
    self.s_core_liner_E_window_bot = openmc.ZPlane(name='E inner Aluminum liner window bottom surface',
                                                   z0=c.struct_excoreInnerLinerEWindow_bot)
    self.s_core_liner_E_window_top = openmc.ZPlane(name='E inner Aluminum liner window top surface',
                                                   z0=c.struct_excoreInnerLinerEWindow_top)
    # Go through and build the cells
    self.c_coreLinerN_E = openmc.Cell(name='East part of north inner aluminum liner', fill=self.mats['Al1100'])
    self.c_coreLinerN_W = openmc.Cell(name='West part of north inner aluminum liner', fill=self.mats['Al1100'])
    self.c_coreLinerN_top = openmc.Cell(name='Part of north inner aluminum liner above the window', fill=self.mats['Al1100'])
    self.c_coreLinerN_bot = openmc.Cell(name='Part of north inner aluminum liner below the window', fill=self.mats['Al1100'])
    self.c_coreLinerN_win = openmc.Cell(name='Window in the north inner aluminum liner', fill=self.mats['Air'])
    self.c_coreLinerN_E.region = +self.s_coreGapOuter_N & -self.s_coreInnerLinerO_N & -self.s_coreInnerLinerO_E \
                               & +self.s_inner_liner_N_window_E & +self.s_reflecFloor & -self.s_coreInnerLiner_top
    self.c_coreLinerN_W.region = +self.s_coreGapOuter_N & -self.s_coreInnerLinerO_N & -self.s_inner_liner_N_window_W \
                               & +self.s_coreInnerLinerO_W & +self.s_reflecFloor & -self.s_coreInnerLiner_top
    self.c_coreLinerN_top.region = +self.s_coreGapOuter_N & -self.s_coreInnerLinerO_N & -self.s_inner_liner_N_window_E \
                                 & +self.s_inner_liner_N_window_W & +self.s_inner_liner_N_window_top & -self.s_coreInnerLiner_top
    self.c_coreLinerN_bot.region = +self.s_coreGapOuter_N & -self.s_coreInnerLinerO_N & -self.s_inner_liner_N_window_E \
                                 & +self.s_inner_liner_N_window_W & +self.s_reflecFloor & -self.s_inner_liner_N_window_bot
    self.c_coreLinerN_win.region = +self.s_coreGapOuter_N & -self.s_coreInnerLinerO_N & -self.s_inner_liner_N_window_E \
                            & +self.s_inner_liner_N_window_W & +self.s_inner_liner_N_window_bot & -self.s_inner_liner_N_window_top
    self.c_coreLinerS_E = openmc.Cell(name='East part of south inner aluminum liner', fill=self.mats['Al1100'])
    self.c_coreLinerS_W = openmc.Cell(name='West part of south inner aluminum liner', fill=self.mats['Al1100'])
    self.c_coreLinerS_top = openmc.Cell(name='Part of south inner aluminum liner above the window', fill=self.mats['Al1100'])
    self.c_coreLinerS_bot = openmc.Cell(name='Part of south inner aluminum liner below the window', fill=self.mats['Al1100'])
    self.c_coreLinerS_win = openmc.Cell(name='Window in the south inner aluminum liner', fill=self.mats['Air'])
    self.c_coreLinerS_E.region = -self.s_coreGapOuter_S & +self.s_coreInnerLinerO_S & -self.s_coreInnerLinerO_E \
                               & +self.s_core_liner_S_window_E & +self.s_reflecFloor & -self.s_coreInnerLiner_top
    self.c_coreLinerS_W.region = -self.s_coreGapOuter_S & +self.s_coreInnerLinerO_S & -self.s_core_liner_S_window_W \
                               & +self.s_coreInnerLinerO_W & +self.s_reflecFloor & -self.s_coreInnerLiner_top
    self.c_coreLinerS_top.region = -self.s_coreGapOuter_S & +self.s_coreInnerLinerO_S & -self.s_core_liner_S_window_E \
                                 & +self.s_core_liner_S_window_W & +self.s_core_liner_WS_window_top & -self.s_coreInnerLiner_top
    self.c_coreLinerS_bot.region = -self.s_coreGapOuter_S & +self.s_coreInnerLinerO_S & -self.s_core_liner_S_window_E \
                                 & +self.s_core_liner_S_window_W & +self.s_reflecFloor & -self.s_core_liner_WS_window_bot
    self.c_coreLinerS_win.region = -self.s_coreGapOuter_S & +self.s_coreInnerLinerO_S & -self.s_core_liner_S_window_E \
                            & +self.s_core_liner_S_window_W & +self.s_core_liner_WS_window_bot & -self.s_core_liner_WS_window_top
    self.c_coreLinerE_N = openmc.Cell(name='North part of east inner aluminum liner', fill=self.mats['Al1100'])
    self.c_coreLinerE_S = openmc.Cell(name='South part of east inner aluminum liner', fill=self.mats['Al1100'])
    self.c_coreLinerE_top = openmc.Cell(name='Part of east inner aluminum liner above the window', fill=self.mats['Al1100'])
    self.c_coreLinerE_bot = openmc.Cell(name='Part of east inner aluminum liner below the window', fill=self.mats['Al1100'])
    self.c_coreLinerE_win = openmc.Cell(name='Window in the east inner aluminum liner', fill=self.mats['Air'])
    self.c_coreLinerE_N.region = +self.s_core_liner_E_window_N & -self.s_coreGapOuter_N & -self.s_coreInnerLinerO_E \
                               & +self.s_coreGapOuter_E & +self.s_reflecFloor & -self.s_coreInnerLiner_top
    self.c_coreLinerE_S.region = -self.s_core_liner_E_window_S & +self.s_coreGapOuter_S & -self.s_coreInnerLinerO_E \
                               & +self.s_coreGapOuter_E & +self.s_reflecFloor & -self.s_coreInnerLiner_top
    self.c_coreLinerE_top.region = -self.s_core_liner_E_window_N & +self.s_core_liner_E_window_S & -self.s_coreInnerLinerO_E \
                                 & +self.s_coreGapOuter_E & +self.s_core_liner_E_window_top & -self.s_coreInnerLiner_top
    self.c_coreLinerE_bot.region = -self.s_core_liner_E_window_N & +self.s_core_liner_E_window_S & -self.s_coreInnerLinerO_E \
                                 & +self.s_coreGapOuter_E & +self.s_reflecFloor & -self.s_core_liner_E_window_bot
    self.c_coreLinerE_win.region = -self.s_core_liner_E_window_N & +self.s_core_liner_E_window_S & -self.s_coreInnerLinerO_E \
                            & +self.s_coreGapOuter_E & +self.s_core_liner_E_window_bot & -self.s_core_liner_E_window_top
    self.c_coreLinerW_N = openmc.Cell(name='North part of west inner aluminum liner', fill=self.mats['Al1100'])
    self.c_coreLinerW_S = openmc.Cell(name='South part of west inner aluminum liner', fill=self.mats['Al1100'])
    self.c_coreLinerW_top = openmc.Cell(name='Part of west inner aluminum liner above the window', fill=self.mats['Al1100'])
    self.c_coreLinerW_bot = openmc.Cell(name='Part of west inner aluminum liner below the window', fill=self.mats['Al1100'])
    self.c_coreLinerW_win = openmc.Cell(name='Window in the west inner aluminum liner', fill=self.mats['Air'])
    self.c_coreLinerW_N.region = +self.s_core_liner_W_window_N & -self.s_coreGapOuter_N & +self.s_coreInnerLinerO_W \
                               & -self.s_coreGapOuter_W & +self.s_reflecFloor & -self.s_coreInnerLiner_top
    self.c_coreLinerW_S.region = -self.s_core_liner_W_window_S & +self.s_coreGapOuter_S & +self.s_coreInnerLinerO_W \
                               & -self.s_coreGapOuter_W & +self.s_reflecFloor & -self.s_coreInnerLiner_top
    self.c_coreLinerW_top.region = -self.s_core_liner_W_window_N & +self.s_core_liner_W_window_S & +self.s_coreInnerLinerO_W \
                                 & -self.s_coreGapOuter_W & +self.s_core_liner_WS_window_top & -self.s_coreInnerLiner_top
    self.c_coreLinerW_bot.region = -self.s_core_liner_W_window_N & +self.s_core_liner_W_window_S & +self.s_coreInnerLinerO_W \
                                 & -self.s_coreGapOuter_W & +self.s_reflecFloor & -self.s_core_liner_WS_window_bot
    self.c_coreLinerW_win.region = -self.s_core_liner_W_window_N & +self.s_core_liner_W_window_S & +self.s_coreInnerLinerO_W \
                            & -self.s_coreGapOuter_W & +self.s_core_liner_WS_window_bot & -self.s_core_liner_WS_window_top

    # The steel reflector liner
    ztop = c.struct_excoreOuterLinerWindow_mid + c.excoreOuterLinerSteelHW
    s_steel_liner_top = openmc.ZPlane(name='Steel Reflector Liner top', z0=ztop)
    # Surfaces for the N, S, and W steel reflector liner
    s_steel_liner_N_o = openmc.YPlane(name='North Steel Reflector Liner, outer',
                                      y0=+c.excoreOuterLinerOuter)
    s_steel_liner_S_o = openmc.YPlane(name='South Steel Reflector Liner, outer',
                                      y0=-c.excoreOuterLinerOuter)
    s_steel_liner_W_o = openmc.XPlane(name='West Steel Reflector Liner, outer',
                                      x0=-c.excoreOuterLinerOuter)
    s_steel_liner_E_o = openmc.XPlane(name='East Steel Reflector Liner, outer',
                                      x0=+c.excoreOuterLinerOuter)

    # Surfaces for the windows in the outer liner
    zbot = c.struct_excoreOuterLinerWindow_mid - c.excoreOuterLinerHW_N_z
    ztop = c.struct_excoreOuterLinerWindow_mid + c.excoreOuterLinerHW_N_z
    s_outer_liner_N_window_E = openmc.XPlane(name='North outer Steel liner window E',
                                             x0=+c.excoreOuterLinerHW_N_x)
    s_outer_liner_N_window_W = openmc.XPlane(name='North outer Steel liner window W',
                                             x0=-c.excoreOuterLinerHW_N_x)
    s_outer_liner_N_window_bot = openmc.ZPlane(name='North outer Steel liner window bottom', z0=zbot)
    s_outer_liner_N_window_top = openmc.ZPlane(name='North outer Steel liner window top', z0=ztop)

    # For the west and south sides, approximating the little auxiliary extension
    # as part of the main rectangle
    zbot = c.struct_excoreOuterLinerWindow_mid - c.excoreOuterLinerHW_WS_z
    ztop = c.struct_excoreOuterLinerWindow_mid + c.excoreOuterLinerHW_WS_z + c.excoreOuterLiner_WS_aux_z
    s_outer_liner_S_window_E = openmc.XPlane(name='South outer steel liner window E',
                                              x0=+c.excoreOuterLinerHW_WS_xy)
    s_outer_liner_S_window_W = openmc.XPlane(name='South outer steel liner window W',
                                              x0=-c.excoreOuterLinerHW_WS_xy)
    s_outer_liner_WS_window_bot = openmc.ZPlane(name='West and South outer Steel liner window bottom', z0=zbot)
    s_outer_liner_WS_window_top = openmc.ZPlane(name='West and South outer Steel liner window top', z0=ztop)

    s_outer_liner_W_window_N = openmc.YPlane(name='West outer steel liner window N',
                                             y0=+c.excoreOuterLinerHW_WS_xy)
    s_outer_liner_W_window_S = openmc.YPlane(name='West outer steel liner window S',
                                             y0=-c.excoreOuterLinerHW_WS_xy)

    zbot = c.struct_excoreOuterLinerWindow_mid - c.excoreOuterLinerHW_E_z
    ztop = c.struct_excoreOuterLinerWindow_mid + c.excoreOuterLinerHW_E_z
    s_outer_liner_E_window_N = openmc.YPlane(name='East outer Steel liner window N',
                                             y0=+c.excoreOuterLinerHW_E_y)
    s_outer_liner_E_window_S = openmc.YPlane(name='East outer Steel liner window S',
                                             y0=-c.excoreOuterLinerHW_E_y)
    s_outer_liner_E_window_bot = openmc.ZPlane(name='East outer Steel liner window bottom', z0=zbot)
    s_outer_liner_E_window_top = openmc.ZPlane(name='East outer Steel liner window top', z0=ztop)

    # Start building the actual graphite cells that comprise the excore reflector
    # Go through and create all the various surfaces that we will need
    self.s_reflO_N = openmc.YPlane(name='Permanent reflector outer N', y0= c.excoreReflecOuter)
    self.s_reflO_S = openmc.YPlane(name='Permanent reflector outer S', y0=-c.excoreReflecOuter)
    self.s_reflO_E = openmc.XPlane(name='Permanent reflector outer E', x0= c.excoreReflecOuter)
    self.s_reflO_W = openmc.XPlane(name='Permanent reflector outer W', x0=-c.excoreReflecOuter)
    self.s_reflI_N = openmc.YPlane(name='Permanent reflector inner N', y0= c.excoreReflecInner)
    self.s_reflI_S = openmc.YPlane(name='Permanent reflector inner S', y0=-c.excoreReflecInner)
    self.s_reflI_E = openmc.XPlane(name='Permanent reflector inner E', x0= c.excoreReflecInner)
    self.s_reflI_W = openmc.XPlane(name='Permanent reflector inner W', x0=-c.excoreReflecInner)
    self.s_refl_top = openmc.ZPlane(name='Permanent reflector top', z0=c.struct_excoreRefl_top)
    self.s_reflM_N = openmc.YPlane(name='Permanent reflector tie bold widening point N', y0= c.excoreReflecMid)
    self.s_reflM_S = openmc.YPlane(name='Permanent reflector tie bold widening point S', y0=-c.excoreReflecMid)
    self.s_reflM_E = openmc.XPlane(name='Permanent reflector tie bold widening point E', x0= c.excoreReflecMid)
    self.s_reflM_W = openmc.XPlane(name='Permanent reflector tie bold widening point W', x0=-c.excoreReflecMid)
    self.s_reflTieSmall_FN_bot = openmc.XCylinder(name='Permanent reflector thin tie bolt far N, bottom', \
                                 R=c.excoreTieBoltDrillHoleSR, y0= c.excoreTieBoltFarDist, z0=c.struct_excoreTieBoltLower)
    self.s_reflTieSmall_CN_bot = openmc.XCylinder(name='Permanent reflector thin tie bolt close N, bottom', \
                                 R=c.excoreTieBoltDrillHoleSR, y0= c.excoreTieBoltCloseDist, z0=c.struct_excoreTieBoltLower)
    self.s_reflTieSmall_CS_bot = openmc.XCylinder(name='Permanent reflector thin tie bolt close S, bottom', \
                                 R=c.excoreTieBoltDrillHoleSR, y0=-c.excoreTieBoltCloseDist, z0=c.struct_excoreTieBoltLower)
    self.s_reflTieSmall_FS_bot = openmc.XCylinder(name='Permanent reflector thin tie bolt far S, bottom', \
                                 R=c.excoreTieBoltDrillHoleSR, y0=-c.excoreTieBoltFarDist, z0=c.struct_excoreTieBoltLower)
    self.s_reflTieSmall_FN_mid = openmc.XCylinder(name='Permanent reflector thin tie bolt far N, middle', \
                                 R=c.excoreTieBoltDrillHoleSR, y0= c.excoreTieBoltFarDist, z0=c.struct_excoreTieBoltMiddle)
    self.s_reflTieSmall_CN_mid = openmc.XCylinder(name='Permanent reflector thin tie bolt close N, middle', \
                                 R=c.excoreTieBoltDrillHoleSR, y0= c.excoreTieBoltCloseDist, z0=c.struct_excoreTieBoltMiddle)
    self.s_reflTieSmall_CS_mid = openmc.XCylinder(name='Permanent reflector thin tie bolt close S, middle', \
                                 R=c.excoreTieBoltDrillHoleSR, y0=-c.excoreTieBoltCloseDist, z0=c.struct_excoreTieBoltMiddle)
    self.s_reflTieSmall_FS_mid = openmc.XCylinder(name='Permanent reflector thin tie bolt far S, middle', \
                                 R=c.excoreTieBoltDrillHoleSR, y0=-c.excoreTieBoltFarDist, z0=c.struct_excoreTieBoltMiddle)
    self.s_reflTieSmall_FN_top = openmc.XCylinder(name='Permanent reflector thin tie bolt far N, top', \
                                 R=c.excoreTieBoltDrillHoleSR, y0= c.excoreTieBoltFarDist, z0=c.struct_excoreTieBoltUpper)
    self.s_reflTieSmall_CN_top = openmc.XCylinder(name='Permanent reflector thin tie bolt close N, top', \
                                 R=c.excoreTieBoltDrillHoleSR, y0= c.excoreTieBoltCloseDist, z0=c.struct_excoreTieBoltUpper)
    self.s_reflTieSmall_CS_top = openmc.XCylinder(name='Permanent reflector thin tie bolt close S, top', \
                                 R=c.excoreTieBoltDrillHoleSR, y0=-c.excoreTieBoltCloseDist, z0=c.struct_excoreTieBoltUpper)
    self.s_reflTieSmall_FS_top = openmc.XCylinder(name='Permanent reflector thin tie bolt far S, top', \
                                 R=c.excoreTieBoltDrillHoleSR, y0=-c.excoreTieBoltFarDist, z0=c.struct_excoreTieBoltUpper)
    self.s_reflTieLarge_FN_bot = openmc.XCylinder(name='Permanent reflector thick tie bolt far N, bottom', \
                                 R=c.excoreTieBoltDrillHoleLR, y0= c.excoreTieBoltFarDist, z0=c.struct_excoreTieBoltLower)
    self.s_reflTieLarge_CN_bot = openmc.XCylinder(name='Permanent reflector thick tie bolt close N, bottom', \
                                 R=c.excoreTieBoltDrillHoleLR, y0= c.excoreTieBoltCloseDist, z0=c.struct_excoreTieBoltLower)
    self.s_reflTieLarge_CS_bot = openmc.XCylinder(name='Permanent reflector thick tie bolt close S, bottom', \
                                 R=c.excoreTieBoltDrillHoleLR, y0=-c.excoreTieBoltCloseDist, z0=c.struct_excoreTieBoltLower)
    self.s_reflTieLarge_FS_bot = openmc.XCylinder(name='Permanent reflector thick tie bolt far S, bottom', \
                                 R=c.excoreTieBoltDrillHoleLR, y0=-c.excoreTieBoltFarDist, z0=c.struct_excoreTieBoltLower)
    self.s_reflTieLarge_FN_mid = openmc.XCylinder(name='Permanent reflector thick tie bolt far N, middle', \
                                 R=c.excoreTieBoltDrillHoleLR, y0= c.excoreTieBoltFarDist, z0=c.struct_excoreTieBoltMiddle)
    self.s_reflTieLarge_CN_mid = openmc.XCylinder(name='Permanent reflector thick tie bolt close N, middle', \
                                 R=c.excoreTieBoltDrillHoleLR, y0= c.excoreTieBoltCloseDist, z0=c.struct_excoreTieBoltMiddle)
    self.s_reflTieLarge_CS_mid = openmc.XCylinder(name='Permanent reflector thick tie bolt close S, middle', \
                                 R=c.excoreTieBoltDrillHoleLR, y0=-c.excoreTieBoltCloseDist, z0=c.struct_excoreTieBoltMiddle)
    self.s_reflTieLarge_FS_mid = openmc.XCylinder(name='Permanent reflector thick tie bolt far S, middle', \
                                 R=c.excoreTieBoltDrillHoleLR, y0=-c.excoreTieBoltFarDist, z0=c.struct_excoreTieBoltMiddle)
    self.s_reflTieLarge_FN_top = openmc.XCylinder(name='Permanent reflector thick tie bolt far N, top', \
                                 R=c.excoreTieBoltDrillHoleLR, y0= c.excoreTieBoltFarDist, z0=c.struct_excoreTieBoltUpper)
    self.s_reflTieLarge_CN_top = openmc.XCylinder(name='Permanent reflector thick tie bolt close N, top', \
                                 R=c.excoreTieBoltDrillHoleLR, y0= c.excoreTieBoltCloseDist, z0=c.struct_excoreTieBoltUpper)
    self.s_reflTieLarge_CS_top = openmc.XCylinder(name='Permanent reflector thick tie bolt close S, top', \
                                 R=c.excoreTieBoltDrillHoleLR, y0=-c.excoreTieBoltCloseDist, z0=c.struct_excoreTieBoltUpper)
    self.s_reflTieLarge_FS_top = openmc.XCylinder(name='Permanent reflector thick tie bolt far S, top', \
                                 R=c.excoreTieBoltDrillHoleLR, y0=-c.excoreTieBoltFarDist, z0=c.struct_excoreTieBoltUpper)
    self.s_reflTieSmall_FE_bot = openmc.YCylinder(name='Permanent reflector thin tie bolt far E, bottom', \
                                 R=c.excoreTieBoltDrillHoleSR, x0= c.excoreTieBoltFarDist, z0=c.struct_excoreTieBoltLower)
    self.s_reflTieSmall_CE_bot = openmc.YCylinder(name='Permanent reflector thin tie bolt close E, bottom', \
                                 R=c.excoreTieBoltDrillHoleSR, x0= c.excoreTieBoltCloseDist, z0=c.struct_excoreTieBoltLower)
    self.s_reflTieSmall_CW_bot = openmc.YCylinder(name='Permanent reflector thin tie bolt close W, bottom', \
                                 R=c.excoreTieBoltDrillHoleSR, x0=-c.excoreTieBoltCloseDist, z0=c.struct_excoreTieBoltLower)
    self.s_reflTieSmall_FW_bot = openmc.YCylinder(name='Permanent reflector thin tie bolt far W, bottom', \
                                 R=c.excoreTieBoltDrillHoleSR, x0=-c.excoreTieBoltFarDist, z0=c.struct_excoreTieBoltLower)
    self.s_reflTieSmall_FE_mid = openmc.YCylinder(name='Permanent reflector thin tie bolt far E, middle', \
                                 R=c.excoreTieBoltDrillHoleSR, x0= c.excoreTieBoltFarDist, z0=c.struct_excoreTieBoltMiddle)
    self.s_reflTieSmall_CE_mid = openmc.YCylinder(name='Permanent reflector thin tie bolt close E, middle', \
                                 R=c.excoreTieBoltDrillHoleSR, x0= c.excoreTieBoltCloseDist, z0=c.struct_excoreTieBoltMiddle)
    self.s_reflTieSmall_CW_mid = openmc.YCylinder(name='Permanent reflector thin tie bolt close W, middle', \
                                 R=c.excoreTieBoltDrillHoleSR, x0=-c.excoreTieBoltCloseDist, z0=c.struct_excoreTieBoltMiddle)
    self.s_reflTieSmall_FW_mid = openmc.YCylinder(name='Permanent reflector thin tie bolt far W, middle', \
                                 R=c.excoreTieBoltDrillHoleSR, x0=-c.excoreTieBoltFarDist, z0=c.struct_excoreTieBoltMiddle)
    self.s_reflTieSmall_FE_top = openmc.YCylinder(name='Permanent reflector thin tie bolt far E, top', \
                                 R=c.excoreTieBoltDrillHoleSR, x0= c.excoreTieBoltFarDist, z0=c.struct_excoreTieBoltUpper)
    self.s_reflTieSmall_CE_top = openmc.YCylinder(name='Permanent reflector thin tie bolt close E, top', \
                                 R=c.excoreTieBoltDrillHoleSR, x0= c.excoreTieBoltCloseDist, z0=c.struct_excoreTieBoltUpper)
    self.s_reflTieSmall_CW_top = openmc.YCylinder(name='Permanent reflector thin tie bolt close W, top', \
                                 R=c.excoreTieBoltDrillHoleSR, x0=-c.excoreTieBoltCloseDist, z0=c.struct_excoreTieBoltUpper)
    self.s_reflTieSmall_FW_top = openmc.YCylinder(name='Permanent reflector thin tie bolt far W, top', \
                                 R=c.excoreTieBoltDrillHoleSR, x0=-c.excoreTieBoltFarDist, z0=c.struct_excoreTieBoltUpper)
    self.s_reflTieLarge_FE_bot = openmc.YCylinder(name='Permanent reflector thick tie bolt far E, bottom', \
                                 R=c.excoreTieBoltDrillHoleLR, x0= c.excoreTieBoltFarDist, z0=c.struct_excoreTieBoltLower)
    self.s_reflTieLarge_CE_bot = openmc.YCylinder(name='Permanent reflector thick tie bolt close E, bottom', \
                                 R=c.excoreTieBoltDrillHoleLR, x0= c.excoreTieBoltCloseDist, z0=c.struct_excoreTieBoltLower)
    self.s_reflTieLarge_CW_bot = openmc.YCylinder(name='Permanent reflector thick tie bolt close W, bottom', \
                                 R=c.excoreTieBoltDrillHoleLR, x0=-c.excoreTieBoltCloseDist, z0=c.struct_excoreTieBoltLower)
    self.s_reflTieLarge_FW_bot = openmc.YCylinder(name='Permanent reflector thick tie bolt far W, bottom', \
                                 R=c.excoreTieBoltDrillHoleLR, x0=-c.excoreTieBoltFarDist, z0=c.struct_excoreTieBoltLower)
    self.s_reflTieLarge_FE_mid = openmc.YCylinder(name='Permanent reflector thick tie bolt far E, middle', \
                                 R=c.excoreTieBoltDrillHoleLR, x0= c.excoreTieBoltFarDist, z0=c.struct_excoreTieBoltMiddle)
    self.s_reflTieLarge_CE_mid = openmc.YCylinder(name='Permanent reflector thick tie bolt close E, middle', \
                                 R=c.excoreTieBoltDrillHoleLR, x0= c.excoreTieBoltCloseDist, z0=c.struct_excoreTieBoltMiddle)
    self.s_reflTieLarge_CW_mid = openmc.YCylinder(name='Permanent reflector thick tie bolt close W, middle', \
                                 R=c.excoreTieBoltDrillHoleLR, x0=-c.excoreTieBoltCloseDist, z0=c.struct_excoreTieBoltMiddle)
    self.s_reflTieLarge_FW_mid = openmc.YCylinder(name='Permanent reflector thick tie bolt far W, middle', \
                                 R=c.excoreTieBoltDrillHoleLR, x0=-c.excoreTieBoltFarDist, z0=c.struct_excoreTieBoltMiddle)
    self.s_reflTieLarge_FE_top = openmc.YCylinder(name='Permanent reflector thick tie bolt far E, top', \
                                 R=c.excoreTieBoltDrillHoleLR, x0= c.excoreTieBoltFarDist, z0=c.struct_excoreTieBoltUpper)
    self.s_reflTieLarge_CE_top = openmc.YCylinder(name='Permanent reflector thick tie bolt close E, top', \
                                 R=c.excoreTieBoltDrillHoleLR, x0= c.excoreTieBoltCloseDist, z0=c.struct_excoreTieBoltUpper)
    self.s_reflTieLarge_CW_top = openmc.YCylinder(name='Permanent reflector thick tie bolt close W, top', \
                                 R=c.excoreTieBoltDrillHoleLR, x0=-c.excoreTieBoltCloseDist, z0=c.struct_excoreTieBoltUpper)
    self.s_reflTieLarge_FW_top = openmc.YCylinder(name='Permanent reflector thick tie bolt far W, top', \
                                 R=c.excoreTieBoltDrillHoleLR, x0=-c.excoreTieBoltFarDist, z0=c.struct_excoreTieBoltUpper)
    # These surfaces are used throughout the reflector and liner.
    self.s_reflInstr_N_top = openmc.YCylinder(name='Permanent reflector upper north instrument hole',
                             R=c.excoreGrphInstrHoleR, x0= c.excoreInstrHoleDist, z0=c.struct_excoreReflInstrUpper)
    self.s_reflInstr_N_bot = openmc.YCylinder(name='Permanent reflector lower north instrument hole',
                             R=c.excoreGrphInstrHoleR, x0= c.excoreInstrHoleDist, z0=c.struct_excoreReflInstrBottom)
    self.s_reflInstr_W_top = openmc.XCylinder(name='Permanent reflector upper west instrument hole',
                             R=c.excoreGrphInstrHoleR, y0= c.excoreInstrHoleDist, z0=c.struct_excoreReflInstrUpper)
    self.s_reflInstr_W_bot = openmc.XCylinder(name='Permanent reflector lower west instrument hole',
                             R=c.excoreGrphInstrHoleR, y0= c.excoreInstrHoleDist, z0=c.struct_excoreReflInstrBottom)
    self.s_reflInstr_S_top = openmc.YCylinder(name='Permanent reflector upper south instrument hole',
                             R=c.excoreGrphInstrHoleR, x0=-c.excoreInstrHoleDist, z0=c.struct_excoreReflInstrUpper)
    self.s_reflInstr_S_bot = openmc.YCylinder(name='Permanent reflector lower south instrument hole',
                             R=c.excoreGrphInstrHoleR, x0=-c.excoreInstrHoleDist, z0=c.struct_excoreReflInstrBottom)
    self.s_reflNGate_E_o = openmc.XPlane(name='Permanent reflector north gate outer east surface', x0= c.excoreNGateEdgeDist)
    self.s_reflNGate_W_o = openmc.XPlane(name='Permanent reflector north gate outer west surface', x0=-c.excoreNGateEdgeDist)
    self.s_reflSGate_E_o = openmc.XPlane(name='Permanent reflector south gate outer east surface', x0= c.excoreWSGateEdgeDist)
    self.s_reflSGate_W_o = openmc.XPlane(name='Permanent reflector south gate outer west surface', x0=-c.excoreWSGateEdgeDist)
    self.s_reflWGate_N_o = openmc.YPlane(name='Permanent reflector west gate outer north surface', y0= c.excoreWSGateEdgeDist)
    self.s_reflWGate_S_o = openmc.YPlane(name='Permanent reflector west gate outer south surface', y0=-c.excoreWSGateEdgeDist)
    # We will need more surfaces when building the gates but for now let us build the various cells for the permanent reflector
    # that are outside of that
    # Air cells
    self.c_coreReflUAir_NNE = openmc.Cell(name='East side air above north permanent reflector', fill=self.mats['Air'])
    self.c_coreReflUAir_NNW = openmc.Cell(name='West side air above north permanent reflector', fill=self.mats['Air'])
    self.c_coreReflLCon_N = openmc.Cell(name='Concrete below north permanent reflector', fill=self.mats['Concrete'])
    self.c_coreReflUCon_NNE = openmc.Cell(name='East side concrete above north permanent reflector', fill=self.mats['Concrete'])
    self.c_coreReflUCon_NNW = openmc.Cell(name='West side concrete above north permanent reflector', fill=self.mats['Concrete'])
    self.c_coreReflUAir_NNE.region = +self.s_reflI_N & -self.s_reflO_N & -self.s_reflO_E \
                          & +self.s_reflNGate_E_o & -self.s_aboveReflRoof & +self.s_refl_top
    self.c_coreReflUAir_NNW.region = +self.s_reflI_N & -self.s_reflO_N & +self.s_reflO_W \
                          & -self.s_reflNGate_W_o & -self.s_aboveReflRoof & +self.s_refl_top
    self.c_coreReflLCon_N.region = +self.s_reflI_N & -self.s_reflO_N & -self.s_reflO_E \
                          & +self.s_reflO_W & +self.s_lowerBound & -self.s_reflecFloor
    self.c_coreReflUCon_NNE.region = +self.s_reflI_N & -self.s_reflO_N & -self.s_reflO_E \
                          & +self.s_reflNGate_E_o & +self.s_aboveReflRoof & -self.s_aboveCoreRoof
    self.c_coreReflUCon_NNW.region = +self.s_reflI_N & -self.s_reflO_N & +self.s_reflO_W \
                          & -self.s_reflNGate_W_o & +self.s_aboveReflRoof & -self.s_aboveCoreRoof
    self.c_coreReflUAir_SSE = openmc.Cell(name='East side air above south permanent reflector', fill=self.mats['Air'])
    self.c_coreReflUAir_SSW = openmc.Cell(name='West side air above south permanent reflector', fill=self.mats['Air'])
    self.c_coreReflLCon_S = openmc.Cell(name='Concrete below south permanent reflector', fill=self.mats['Concrete'])
    self.c_coreReflUCon_SSE = openmc.Cell(name='East side concrete above south permanent reflector', fill=self.mats['Concrete'])
    self.c_coreReflUCon_SSW = openmc.Cell(name='West side concrete above south permanent reflector', fill=self.mats['Concrete'])
    self.c_coreReflUAir_SSE.region = +self.s_reflO_S & -self.s_reflI_S & -self.s_reflO_E \
                          & +self.s_reflSGate_E_o & -self.s_aboveReflRoof & +self.s_refl_top
    self.c_coreReflUAir_SSW.region = +self.s_reflO_S & -self.s_reflI_S & -self.s_reflSGate_W_o \
                          & +self.s_reflO_W & -self.s_aboveReflRoof & +self.s_refl_top
    self.c_coreReflLCon_S.region = -self.s_reflI_S & +self.s_reflO_S & -self.s_reflO_E \
                          & +self.s_reflO_W & -self.s_reflecFloor & +self.s_lowerBound
    self.c_coreReflUCon_SSE.region = +self.s_reflO_S & -self.s_reflI_S & -self.s_reflO_E \
                          & +self.s_reflSGate_E_o & +self.s_aboveReflRoof & -self.s_aboveCoreRoof
    self.c_coreReflUCon_SSW.region = +self.s_reflO_S & -self.s_reflI_S & -self.s_reflSGate_W_o \
                          & +self.s_reflO_W & +self.s_aboveReflRoof & -self.s_aboveCoreRoof
    self.c_coreReflUAir_E = openmc.Cell(name='Air above east permanent reflector', fill=self.mats['Air'])
    self.c_coreReflLCon_E = openmc.Cell(name='Concrete below east permanent reflector', fill=self.mats['Concrete'])
    self.c_coreReflUCon_E = openmc.Cell(name='Concrete above east permanent reflector', fill=self.mats['Concrete'])
    self.c_coreReflUAir_E.region = +self.s_reflI_S & -self.s_reflI_N & -self.s_reflO_E \
                          & +self.s_reflI_E & -self.s_aboveReflRoof & +self.s_refl_top
    self.c_coreReflLCon_E.region = +self.s_reflI_S & -self.s_reflI_N & -self.s_reflO_E \
                          & +self.s_reflI_E & -self.s_reflecFloor & +self.s_lowerBound
    self.c_coreReflUCon_E.region = +self.s_reflI_S & -self.s_reflI_N & -self.s_reflO_E \
                          & +self.s_reflI_E & +self.s_aboveReflRoof & -self.s_aboveCoreRoof
    self.c_coreReflUAir_WNW = openmc.Cell(name='North side air above west permanent reflector', fill=self.mats['Air'])
    self.c_coreReflUAir_WSW = openmc.Cell(name='South side air above west permanent reflector', fill=self.mats['Air'])
    self.c_coreReflLCon_W = openmc.Cell(name='Concrete below west permanent reflector', fill=self.mats['Concrete'])
    self.c_coreReflUCon_WNW = openmc.Cell(name='North side concrete above west permanent reflector', fill=self.mats['Concrete'])
    self.c_coreReflUCon_WSW = openmc.Cell(name='South side concrete above west permanent reflector', fill=self.mats['Concrete'])
    self.c_coreReflUAir_WNW.region = +self.s_reflWGate_N_o & -self.s_reflI_N & -self.s_reflI_W \
                          & +self.s_reflO_W & -self.s_aboveReflRoof & +self.s_refl_top
    self.c_coreReflUAir_WSW.region = +self.s_reflI_S & -self.s_reflWGate_S_o & -self.s_reflI_W \
                          & +self.s_reflO_W & -self.s_aboveReflRoof & +self.s_refl_top
    self.c_coreReflLCon_W.region = +self.s_reflI_S & -self.s_reflI_N & -self.s_reflI_W \
                          & +self.s_reflO_W & -self.s_reflecFloor & +self.s_lowerBound
    self.c_coreReflUCon_WNW.region = +self.s_reflWGate_N_o & -self.s_reflI_N & -self.s_reflI_W \
                          & +self.s_reflO_W & +self.s_aboveReflRoof & -self.s_aboveCoreRoof
    self.c_coreReflUCon_WSW.region = +self.s_reflI_S & -self.s_reflWGate_S_o & -self.s_reflI_W \
                          & +self.s_reflO_W & +self.s_aboveReflRoof & -self.s_aboveCoreRoof
    # Reflector itself
    self.c_coreRefl_NE = openmc.Cell(name='North-East part of permanent reflector', fill=self.mats['Graphite'])
    self.c_coreRefl_NW = openmc.Cell(name='North-West part of permanent reflector', fill=self.mats['Graphite'])
    self.c_coreRefl_SE = openmc.Cell(name='South-East part of permanent reflector', fill=self.mats['Graphite'])
    self.c_coreRefl_SW = openmc.Cell(name='South-West part of permanent reflector', fill=self.mats['Graphite'])
    self.c_coreRefl_NE.region = -self.s_reflO_N & +self.s_reflI_N & -self.s_reflO_E & +self.s_reflI_E \
                              & +self.s_reflecFloor & -self.s_refl_top
    self.c_coreRefl_NW.region = -self.s_reflO_N & +self.s_reflI_N & -self.s_reflI_W & +self.s_reflO_W \
                              & +self.s_reflecFloor & -self.s_refl_top
    self.c_coreRefl_SE.region = -self.s_reflI_S & +self.s_reflO_S & -self.s_reflO_E & +self.s_reflI_E \
                              & +self.s_reflecFloor & -self.s_refl_top
    self.c_coreRefl_SW.region = -self.s_reflI_S & +self.s_reflO_S & -self.s_reflI_W & +self.s_reflO_W \
                              & +self.s_reflecFloor & -self.s_refl_top
    self.c_coreRefl_E_i = openmc.Cell(name='Inner East part of permanent reflector', fill=self.mats['Graphite'])
    self.c_coreRefl_E_o = openmc.Cell(name='Outer East part of permanent reflector', fill=self.mats['Graphite'])
    self.c_coreRefl_E_i.region = -self.s_reflI_N & +self.s_reflI_S & -self.s_reflM_E & +self.s_reflI_E \
                              & +self.s_reflecFloor & -self.s_refl_top \
                              & +self.s_reflTieSmall_FN_bot & +self.s_reflTieSmall_FN_mid & +self.s_reflTieSmall_FN_top \
                              & +self.s_reflTieSmall_CN_bot                               & +self.s_reflTieSmall_CN_top \
                              & +self.s_reflTieSmall_CS_bot                               & +self.s_reflTieSmall_CS_top \
                              & +self.s_reflTieSmall_FS_bot & +self.s_reflTieSmall_FS_mid & +self.s_reflTieSmall_FS_top
    self.c_coreRefl_E_o.region = -self.s_reflI_N & +self.s_reflI_S & -self.s_reflO_E & +self.s_reflM_E \
                              & +self.s_reflecFloor & -self.s_refl_top \
                              & +self.s_reflTieLarge_FN_bot & +self.s_reflTieLarge_FN_mid & +self.s_reflTieLarge_FN_top \
                              & +self.s_reflTieLarge_CN_bot                               & +self.s_reflTieLarge_CN_top \
                              & +self.s_reflTieLarge_CS_bot                               & +self.s_reflTieLarge_CS_top \
                              & +self.s_reflTieLarge_FS_bot & +self.s_reflTieLarge_FS_mid & +self.s_reflTieLarge_FS_top
    self.c_coreReflTP_E_i_FN_bot = openmc.Cell(name='Inner East permanent reflector lower far N tie bolt', fill=self.mats['Al1100'])
    self.c_coreReflTP_E_o_FN_bot = openmc.Cell(name='Outer East permanent reflector lower far N tie bolt', fill=self.mats['Al1100'])
    self.c_coreReflTP_E_i_FN_mid = openmc.Cell(name='Inner East permanent reflector middle far N tie bolt', fill=self.mats['Al1100'])
    self.c_coreReflTP_E_o_FN_mid = openmc.Cell(name='Outer East permanent reflector middle far N tie bolt', fill=self.mats['Al1100'])
    self.c_coreReflTP_E_i_FN_top = openmc.Cell(name='Inner East permanent reflector upper far N tie bolt', fill=self.mats['Al1100'])
    self.c_coreReflTP_E_o_FN_top = openmc.Cell(name='Outer East permanent reflector upper far N tie bolt', fill=self.mats['Al1100'])
    self.c_coreReflTP_E_i_CN_bot = openmc.Cell(name='Inner East permanent reflector lower close N tie bolt', fill=self.mats['Al1100'])
    self.c_coreReflTP_E_o_CN_bot = openmc.Cell(name='Outer East permanent reflector lower close N tie bolt', fill=self.mats['Al1100'])
    self.c_coreReflTP_E_i_CN_top = openmc.Cell(name='Inner East permanent reflector upper close N tie bolt', fill=self.mats['Al1100'])
    self.c_coreReflTP_E_o_CN_top = openmc.Cell(name='Outer East permanent reflector upper close N tie bolt', fill=self.mats['Al1100'])
    self.c_coreReflTP_E_i_CS_bot = openmc.Cell(name='Inner East permanent reflector lower close S tie bolt', fill=self.mats['Al1100'])
    self.c_coreReflTP_E_o_CS_bot = openmc.Cell(name='Outer East permanent reflector lower close S tie bolt', fill=self.mats['Al1100'])
    self.c_coreReflTP_E_i_CS_top = openmc.Cell(name='Inner East permanent reflector upper close S tie bolt', fill=self.mats['Al1100'])
    self.c_coreReflTP_E_o_CS_top = openmc.Cell(name='Outer East permanent reflector upper close S tie bolt', fill=self.mats['Al1100'])
    self.c_coreReflTP_E_i_FS_bot = openmc.Cell(name='Inner East permanent reflector lower far S tie bolt', fill=self.mats['Al1100'])
    self.c_coreReflTP_E_o_FS_bot = openmc.Cell(name='Outer East permanent reflector lower far S tie bolt', fill=self.mats['Al1100'])
    self.c_coreReflTP_E_i_FS_mid = openmc.Cell(name='Inner East permanent reflector middle far S tie bolt', fill=self.mats['Al1100'])
    self.c_coreReflTP_E_o_FS_mid = openmc.Cell(name='Outer East permanent reflector middle far S tie bolt', fill=self.mats['Al1100'])
    self.c_coreReflTP_E_i_FS_top = openmc.Cell(name='Inner East permanent reflector upper far S tie bolt', fill=self.mats['Al1100'])
    self.c_coreReflTP_E_o_FS_top = openmc.Cell(name='Outer East permanent reflector upper far S tie bolt', fill=self.mats['Al1100'])
    self.c_coreReflTP_E_i_FN_bot.region = -self.s_reflTieSmall_FN_bot & +self.s_reflI_E & -self.s_reflM_E
    self.c_coreReflTP_E_o_FN_bot.region = -self.s_reflTieLarge_FN_bot & +self.s_reflM_E & -self.s_reflO_E
    self.c_coreReflTP_E_i_FN_mid.region = -self.s_reflTieSmall_FN_mid & +self.s_reflI_E & -self.s_reflM_E
    self.c_coreReflTP_E_o_FN_mid.region = -self.s_reflTieLarge_FN_mid & +self.s_reflM_E & -self.s_reflO_E
    self.c_coreReflTP_E_i_FN_top.region = -self.s_reflTieSmall_FN_top & +self.s_reflI_E & -self.s_reflM_E
    self.c_coreReflTP_E_o_FN_top.region = -self.s_reflTieLarge_FN_top & +self.s_reflM_E & -self.s_reflO_E
    self.c_coreReflTP_E_i_CN_bot.region = -self.s_reflTieSmall_CN_bot & +self.s_reflI_E & -self.s_reflM_E
    self.c_coreReflTP_E_o_CN_bot.region = -self.s_reflTieLarge_CN_bot & +self.s_reflM_E & -self.s_reflO_E
    self.c_coreReflTP_E_i_CN_top.region = -self.s_reflTieSmall_CN_top & +self.s_reflI_E & -self.s_reflM_E
    self.c_coreReflTP_E_o_CN_top.region = -self.s_reflTieLarge_CN_top & +self.s_reflM_E & -self.s_reflO_E
    self.c_coreReflTP_E_i_CS_bot.region = -self.s_reflTieSmall_CS_bot & +self.s_reflI_E & -self.s_reflM_E
    self.c_coreReflTP_E_o_CS_bot.region = -self.s_reflTieLarge_CS_bot & +self.s_reflM_E & -self.s_reflO_E
    self.c_coreReflTP_E_i_CS_top.region = -self.s_reflTieSmall_CS_top & +self.s_reflI_E & -self.s_reflM_E
    self.c_coreReflTP_E_o_CS_top.region = -self.s_reflTieLarge_CS_top & +self.s_reflM_E & -self.s_reflO_E
    self.c_coreReflTP_E_i_FS_bot.region = -self.s_reflTieSmall_FS_bot & +self.s_reflI_E & -self.s_reflM_E
    self.c_coreReflTP_E_o_FS_bot.region = -self.s_reflTieLarge_FS_bot & +self.s_reflM_E & -self.s_reflO_E
    self.c_coreReflTP_E_i_FS_mid.region = -self.s_reflTieSmall_FS_mid & +self.s_reflI_E & -self.s_reflM_E
    self.c_coreReflTP_E_o_FS_mid.region = -self.s_reflTieLarge_FS_mid & +self.s_reflM_E & -self.s_reflO_E
    self.c_coreReflTP_E_i_FS_top.region = -self.s_reflTieSmall_FS_top & +self.s_reflI_E & -self.s_reflM_E
    self.c_coreReflTP_E_o_FS_top.region = -self.s_reflTieLarge_FS_top & +self.s_reflM_E & -self.s_reflO_E
    self.c_coreRefl_N_i_E = openmc.Cell(name='Inner North part of permanent reflector, east side', fill=self.mats['Graphite'])
    self.c_coreRefl_N_o_E = openmc.Cell(name='Outer North part of permanent reflector, east side', fill=self.mats['Graphite'])
    self.c_coreRefl_N_i_W = openmc.Cell(name='Inner North part of permanent reflector, west side', fill=self.mats['Graphite'])
    self.c_coreRefl_N_o_W = openmc.Cell(name='Outer North part of permanent reflector, west side', fill=self.mats['Graphite'])
    self.c_coreRefl_N_i_E.region = -self.s_reflM_N & +self.s_reflI_N & -self.s_reflI_E & +self.s_reflNGate_E_o \
                              & +self.s_reflecFloor & -self.s_refl_top \
                              & +self.s_reflTieSmall_FE_bot & +self.s_reflTieSmall_FE_mid & +self.s_reflTieSmall_FE_top \
                              & +self.s_reflTieSmall_CE_bot & +self.s_reflTieSmall_CE_mid & +self.s_reflTieSmall_CE_top \
                              & +self.s_reflInstr_N_bot & +self.s_reflInstr_N_top
    self.c_coreRefl_N_o_E.region = -self.s_reflO_N & +self.s_reflM_N & -self.s_reflI_E & +self.s_reflNGate_E_o \
                              & +self.s_reflecFloor & -self.s_refl_top \
                              & +self.s_reflTieLarge_FE_bot & +self.s_reflTieLarge_FE_mid & +self.s_reflTieLarge_FE_top \
                              & +self.s_reflTieLarge_CE_bot & +self.s_reflTieLarge_CE_mid & +self.s_reflTieLarge_CE_top \
                              & +self.s_reflInstr_N_bot & +self.s_reflInstr_N_top
    self.c_coreRefl_N_i_W.region = -self.s_reflM_N & +self.s_reflI_N & -self.s_reflNGate_W_o & +self.s_reflI_W \
                              & +self.s_reflecFloor & -self.s_refl_top \
                              & +self.s_reflTieSmall_FW_bot & +self.s_reflTieSmall_FW_mid & +self.s_reflTieSmall_FW_top \
                              & +self.s_reflTieSmall_CW_bot & +self.s_reflTieSmall_CW_mid & +self.s_reflTieSmall_CW_top
    self.c_coreRefl_N_o_W.region = -self.s_reflO_N & +self.s_reflM_N & -self.s_reflNGate_W_o & +self.s_reflI_W \
                              & +self.s_reflecFloor & -self.s_refl_top \
                              & +self.s_reflTieLarge_FW_bot & +self.s_reflTieLarge_FW_mid & +self.s_reflTieLarge_FW_top \
                              & +self.s_reflTieLarge_CW_bot & +self.s_reflTieLarge_CW_mid & +self.s_reflTieLarge_CW_top
    self.c_coreReflTP_N_i_FE_bot = openmc.Cell(name='Inner North permanent reflector lower far E tie bolt', fill=self.mats['Al1100'])
    self.c_coreReflTP_N_o_FE_bot = openmc.Cell(name='Outer North permanent reflector lower far E tie bolt', fill=self.mats['Al1100'])
    self.c_coreReflTP_N_i_FE_mid = openmc.Cell(name='Inner North permanent reflector middle far E tie bolt', fill=self.mats['Al1100'])
    self.c_coreReflTP_N_o_FE_mid = openmc.Cell(name='Outer North permanent reflector middle far E tie bolt', fill=self.mats['Al1100'])
    self.c_coreReflTP_N_i_FE_top = openmc.Cell(name='Inner North permanent reflector upper far E tie bolt', fill=self.mats['Al1100'])
    self.c_coreReflTP_N_o_FE_top = openmc.Cell(name='Outer North permanent reflector upper far E tie bolt', fill=self.mats['Al1100'])
    self.c_coreReflTP_N_i_CE_bot = openmc.Cell(name='Inner North permanent reflector lower close E tie bolt', fill=self.mats['Al1100'])
    self.c_coreReflTP_N_o_CE_bot = openmc.Cell(name='Outer North permanent reflector lower close E tie bolt', fill=self.mats['Al1100'])
    self.c_coreReflTP_N_i_CE_mid = openmc.Cell(name='Inner North permanent reflector middle close E tie bolt', fill=self.mats['Al1100'])
    self.c_coreReflTP_N_o_CE_mid = openmc.Cell(name='Outer North permanent reflector middle close E tie bolt', fill=self.mats['Al1100'])
    self.c_coreReflTP_N_i_CE_top = openmc.Cell(name='Inner North permanent reflector upper close E tie bolt', fill=self.mats['Al1100'])
    self.c_coreReflTP_N_o_CE_top = openmc.Cell(name='Outer North permanent reflector upper close E tie bolt', fill=self.mats['Al1100'])
    self.c_coreReflTP_N_i_CW_bot = openmc.Cell(name='Inner North permanent reflector lower close W tie bolt', fill=self.mats['Al1100'])
    self.c_coreReflTP_N_o_CW_bot = openmc.Cell(name='Outer North permanent reflector lower close W tie bolt', fill=self.mats['Al1100'])
    self.c_coreReflTP_N_i_CW_mid = openmc.Cell(name='Inner North permanent reflector middle close W tie bolt', fill=self.mats['Al1100'])
    self.c_coreReflTP_N_o_CW_mid = openmc.Cell(name='Outer North permanent reflector middle close W tie bolt', fill=self.mats['Al1100'])
    self.c_coreReflTP_N_i_CW_top = openmc.Cell(name='Inner North permanent reflector upper close W tie bolt', fill=self.mats['Al1100'])
    self.c_coreReflTP_N_o_CW_top = openmc.Cell(name='Outer North permanent reflector upper close W tie bolt', fill=self.mats['Al1100'])
    self.c_coreReflTP_N_i_FW_bot = openmc.Cell(name='Inner North permanent reflector lower far W tie bolt', fill=self.mats['Al1100'])
    self.c_coreReflTP_N_o_FW_bot = openmc.Cell(name='Outer North permanent reflector lower far W tie bolt', fill=self.mats['Al1100'])
    self.c_coreReflTP_N_i_FW_mid = openmc.Cell(name='Inner North permanent reflector middle far W tie bolt', fill=self.mats['Al1100'])
    self.c_coreReflTP_N_o_FW_mid = openmc.Cell(name='Outer North permanent reflector middle far W tie bolt', fill=self.mats['Al1100'])
    self.c_coreReflTP_N_i_FW_top = openmc.Cell(name='Inner North permanent reflector upper far W tie bolt', fill=self.mats['Al1100'])
    self.c_coreReflTP_N_o_FW_top = openmc.Cell(name='Outer North permanent reflector upper far W tie bolt', fill=self.mats['Al1100'])
    self.c_coreReflTP_N_i_FE_bot.region = -self.s_reflTieSmall_FE_bot & +self.s_reflI_N & -self.s_reflM_N
    self.c_coreReflTP_N_o_FE_bot.region = -self.s_reflTieLarge_FE_bot & +self.s_reflM_N & -self.s_reflO_N
    self.c_coreReflTP_N_i_FE_mid.region = -self.s_reflTieSmall_FE_mid & +self.s_reflI_N & -self.s_reflM_N
    self.c_coreReflTP_N_o_FE_mid.region = -self.s_reflTieLarge_FE_mid & +self.s_reflM_N & -self.s_reflO_N
    self.c_coreReflTP_N_i_FE_top.region = -self.s_reflTieSmall_FE_top & +self.s_reflI_N & -self.s_reflM_N
    self.c_coreReflTP_N_o_FE_top.region = -self.s_reflTieLarge_FE_top & +self.s_reflM_N & -self.s_reflO_N
    self.c_coreReflTP_N_i_CE_bot.region = -self.s_reflTieSmall_CE_bot & +self.s_reflI_N & -self.s_reflM_N
    self.c_coreReflTP_N_o_CE_bot.region = -self.s_reflTieLarge_CE_bot & +self.s_reflM_N & -self.s_reflO_N
    self.c_coreReflTP_N_i_CE_mid.region = -self.s_reflTieSmall_CE_mid & +self.s_reflI_N & -self.s_reflM_N
    self.c_coreReflTP_N_o_CE_mid.region = -self.s_reflTieLarge_CE_mid & +self.s_reflM_N & -self.s_reflO_N
    self.c_coreReflTP_N_i_CE_top.region = -self.s_reflTieSmall_CE_top & +self.s_reflI_N & -self.s_reflM_N
    self.c_coreReflTP_N_o_CE_top.region = -self.s_reflTieLarge_CE_top & +self.s_reflM_N & -self.s_reflO_N
    self.c_coreReflTP_N_i_CW_bot.region = -self.s_reflTieSmall_CW_bot & +self.s_reflI_N & -self.s_reflM_N
    self.c_coreReflTP_N_o_CW_bot.region = -self.s_reflTieLarge_CW_bot & +self.s_reflM_N & -self.s_reflO_N
    self.c_coreReflTP_N_i_CW_mid.region = -self.s_reflTieSmall_CW_mid & +self.s_reflI_N & -self.s_reflM_N
    self.c_coreReflTP_N_o_CW_mid.region = -self.s_reflTieLarge_CW_mid & +self.s_reflM_N & -self.s_reflO_N
    self.c_coreReflTP_N_i_CW_top.region = -self.s_reflTieSmall_CW_top & +self.s_reflI_N & -self.s_reflM_N
    self.c_coreReflTP_N_o_CW_top.region = -self.s_reflTieLarge_CW_top & +self.s_reflM_N & -self.s_reflO_N
    self.c_coreReflTP_N_i_FW_bot.region = -self.s_reflTieSmall_FW_bot & +self.s_reflI_N & -self.s_reflM_N
    self.c_coreReflTP_N_o_FW_bot.region = -self.s_reflTieLarge_FW_bot & +self.s_reflM_N & -self.s_reflO_N
    self.c_coreReflTP_N_i_FW_mid.region = -self.s_reflTieSmall_FW_mid & +self.s_reflI_N & -self.s_reflM_N
    self.c_coreReflTP_N_o_FW_mid.region = -self.s_reflTieLarge_FW_mid & +self.s_reflM_N & -self.s_reflO_N
    self.c_coreReflTP_N_i_FW_top.region = -self.s_reflTieSmall_FW_top & +self.s_reflI_N & -self.s_reflM_N
    self.c_coreReflTP_N_o_FW_top.region = -self.s_reflTieLarge_FW_top & +self.s_reflM_N & -self.s_reflO_N
    self.c_coreReflInstr_N_bot = openmc.Cell(name='Bottom North permanent reflector instrument tube', fill=self.mats['Air'])
    self.c_coreReflInstr_N_top = openmc.Cell(name='Top North permanent reflector instrument tube', fill=self.mats['Air'])
    self.c_coreReflInstr_N_bot.region = -self.s_reflInstr_N_bot & +self.s_reflI_N & -self.s_reflO_N
    self.c_coreReflInstr_N_top.region = -self.s_reflInstr_N_top & +self.s_reflI_N & -self.s_reflO_N
    self.c_coreRefl_S_i_E = openmc.Cell(name='Inner South part of permanent reflector, east side', fill=self.mats['Graphite'])
    self.c_coreRefl_S_o_E = openmc.Cell(name='Outer South part of permanent reflector, east side', fill=self.mats['Graphite'])
    self.c_coreRefl_S_i_W = openmc.Cell(name='Inner South part of permanent reflector, west side', fill=self.mats['Graphite'])
    self.c_coreRefl_S_o_W = openmc.Cell(name='Outer South part of permanent reflector, west side', fill=self.mats['Graphite'])
    self.c_coreRefl_S_i_E.region = -self.s_reflI_S & +self.s_reflM_S & -self.s_reflI_E & +self.s_reflSGate_E_o \
                              & +self.s_reflecFloor & -self.s_refl_top \
                              & +self.s_reflTieSmall_FE_bot & +self.s_reflTieSmall_FE_mid & +self.s_reflTieSmall_FE_top \
                              & +self.s_reflTieSmall_CE_bot & +self.s_reflTieSmall_CE_mid & +self.s_reflTieSmall_CE_top
    self.c_coreRefl_S_o_E.region = -self.s_reflM_S & +self.s_reflO_S & -self.s_reflI_E & +self.s_reflSGate_E_o \
                              & +self.s_reflecFloor & -self.s_refl_top \
                              & +self.s_reflTieLarge_FE_bot & +self.s_reflTieLarge_FE_mid & +self.s_reflTieLarge_FE_top \
                              & +self.s_reflTieLarge_CE_bot & +self.s_reflTieLarge_CE_mid & +self.s_reflTieLarge_CE_top
    self.c_coreRefl_S_i_W.region = -self.s_reflI_S & +self.s_reflM_S & -self.s_reflSGate_W_o & +self.s_reflI_W \
                              & +self.s_reflecFloor & -self.s_refl_top \
                              & +self.s_reflTieSmall_FW_bot & +self.s_reflTieSmall_FW_mid & +self.s_reflTieSmall_FW_top \
                              & +self.s_reflTieSmall_CW_bot & +self.s_reflTieSmall_CW_mid & +self.s_reflTieSmall_CW_top \
                              & +self.s_reflInstr_S_bot & +self.s_reflInstr_S_top
    self.c_coreRefl_S_o_W.region = -self.s_reflM_S & +self.s_reflO_S & -self.s_reflSGate_W_o & +self.s_reflI_W \
                              & +self.s_reflecFloor & -self.s_refl_top \
                              & +self.s_reflTieLarge_FW_bot & +self.s_reflTieLarge_FW_mid & +self.s_reflTieLarge_FW_top \
                              & +self.s_reflTieLarge_CW_bot & +self.s_reflTieLarge_CW_mid & +self.s_reflTieLarge_CW_top \
                              & +self.s_reflInstr_S_bot & +self.s_reflInstr_S_top
    self.c_coreReflTP_S_i_FE_bot = openmc.Cell(name='Inner South permanent reflector lower far E tie bolt', fill=self.mats['Al1100'])
    self.c_coreReflTP_S_o_FE_bot = openmc.Cell(name='Outer South permanent reflector lower far E tie bolt', fill=self.mats['Al1100'])
    self.c_coreReflTP_S_i_FE_mid = openmc.Cell(name='Inner South permanent reflector middle far E tie bolt', fill=self.mats['Al1100'])
    self.c_coreReflTP_S_o_FE_mid = openmc.Cell(name='Outer South permanent reflector middle far E tie bolt', fill=self.mats['Al1100'])
    self.c_coreReflTP_S_i_FE_top = openmc.Cell(name='Inner South permanent reflector upper far E tie bolt', fill=self.mats['Al1100'])
    self.c_coreReflTP_S_o_FE_top = openmc.Cell(name='Outer South permanent reflector upper far E tie bolt', fill=self.mats['Al1100'])
    self.c_coreReflTP_S_i_CE_bot = openmc.Cell(name='Inner South permanent reflector lower close E tie bolt', fill=self.mats['Al1100'])
    self.c_coreReflTP_S_o_CE_bot = openmc.Cell(name='Outer South permanent reflector lower close E tie bolt', fill=self.mats['Al1100'])
    self.c_coreReflTP_S_i_CE_mid = openmc.Cell(name='Inner South permanent reflector middle close E tie bolt', fill=self.mats['Al1100'])
    self.c_coreReflTP_S_o_CE_mid = openmc.Cell(name='Outer South permanent reflector middle close E tie bolt', fill=self.mats['Al1100'])
    self.c_coreReflTP_S_i_CE_top = openmc.Cell(name='Inner South permanent reflector upper close E tie bolt', fill=self.mats['Al1100'])
    self.c_coreReflTP_S_o_CE_top = openmc.Cell(name='Outer South permanent reflector upper close E tie bolt', fill=self.mats['Al1100'])
    self.c_coreReflTP_S_i_CW_bot = openmc.Cell(name='Inner South permanent reflector lower close W tie bolt', fill=self.mats['Al1100'])
    self.c_coreReflTP_S_o_CW_bot = openmc.Cell(name='Outer South permanent reflector lower close W tie bolt', fill=self.mats['Al1100'])
    self.c_coreReflTP_S_i_CW_mid = openmc.Cell(name='Inner South permanent reflector middle close W tie bolt', fill=self.mats['Al1100'])
    self.c_coreReflTP_S_o_CW_mid = openmc.Cell(name='Outer South permanent reflector middle close W tie bolt', fill=self.mats['Al1100'])
    self.c_coreReflTP_S_i_CW_top = openmc.Cell(name='Inner South permanent reflector upper close W tie bolt', fill=self.mats['Al1100'])
    self.c_coreReflTP_S_o_CW_top = openmc.Cell(name='Outer South permanent reflector upper close W tie bolt', fill=self.mats['Al1100'])
    self.c_coreReflTP_S_i_FW_bot = openmc.Cell(name='Inner South permanent reflector lower far W tie bolt', fill=self.mats['Al1100'])
    self.c_coreReflTP_S_o_FW_bot = openmc.Cell(name='Outer South permanent reflector lower far W tie bolt', fill=self.mats['Al1100'])
    self.c_coreReflTP_S_i_FW_mid = openmc.Cell(name='Inner South permanent reflector middle far W tie bolt', fill=self.mats['Al1100'])
    self.c_coreReflTP_S_o_FW_mid = openmc.Cell(name='Outer South permanent reflector middle far W tie bolt', fill=self.mats['Al1100'])
    self.c_coreReflTP_S_i_FW_top = openmc.Cell(name='Inner South permanent reflector upper far W tie bolt', fill=self.mats['Al1100'])
    self.c_coreReflTP_S_o_FW_top = openmc.Cell(name='Outer South permanent reflector upper far W tie bolt', fill=self.mats['Al1100'])
    self.c_coreReflTP_S_i_FE_bot.region = -self.s_reflTieSmall_FE_bot & -self.s_reflI_S & +self.s_reflM_S
    self.c_coreReflTP_S_o_FE_bot.region = -self.s_reflTieLarge_FE_bot & -self.s_reflM_S & +self.s_reflO_S
    self.c_coreReflTP_S_i_FE_mid.region = -self.s_reflTieSmall_FE_mid & -self.s_reflI_S & +self.s_reflM_S
    self.c_coreReflTP_S_o_FE_mid.region = -self.s_reflTieLarge_FE_mid & -self.s_reflM_S & +self.s_reflO_S
    self.c_coreReflTP_S_i_FE_top.region = -self.s_reflTieSmall_FE_top & -self.s_reflI_S & +self.s_reflM_S
    self.c_coreReflTP_S_o_FE_top.region = -self.s_reflTieLarge_FE_top & -self.s_reflM_S & +self.s_reflO_S
    self.c_coreReflTP_S_i_CE_bot.region = -self.s_reflTieSmall_CE_bot & -self.s_reflI_S & +self.s_reflM_S
    self.c_coreReflTP_S_o_CE_bot.region = -self.s_reflTieLarge_CE_bot & -self.s_reflM_S & +self.s_reflO_S
    self.c_coreReflTP_S_i_CE_mid.region = -self.s_reflTieSmall_CE_mid & -self.s_reflI_S & +self.s_reflM_S
    self.c_coreReflTP_S_o_CE_mid.region = -self.s_reflTieLarge_CE_mid & -self.s_reflM_S & +self.s_reflO_S
    self.c_coreReflTP_S_i_CE_top.region = -self.s_reflTieSmall_CE_top & -self.s_reflI_S & +self.s_reflM_S
    self.c_coreReflTP_S_o_CE_top.region = -self.s_reflTieLarge_CE_top & -self.s_reflM_S & +self.s_reflO_S
    self.c_coreReflTP_S_i_CW_bot.region = -self.s_reflTieSmall_CW_bot & -self.s_reflI_S & +self.s_reflM_S
    self.c_coreReflTP_S_o_CW_bot.region = -self.s_reflTieLarge_CW_bot & -self.s_reflM_S & +self.s_reflO_S
    self.c_coreReflTP_S_i_CW_mid.region = -self.s_reflTieSmall_CW_mid & -self.s_reflI_S & +self.s_reflM_S
    self.c_coreReflTP_S_o_CW_mid.region = -self.s_reflTieLarge_CW_mid & -self.s_reflM_S & +self.s_reflO_S
    self.c_coreReflTP_S_i_CW_top.region = -self.s_reflTieSmall_CW_top & -self.s_reflI_S & +self.s_reflM_S
    self.c_coreReflTP_S_o_CW_top.region = -self.s_reflTieLarge_CW_top & -self.s_reflM_S & +self.s_reflO_S
    self.c_coreReflTP_S_i_FW_bot.region = -self.s_reflTieSmall_FW_bot & -self.s_reflI_S & +self.s_reflM_S
    self.c_coreReflTP_S_o_FW_bot.region = -self.s_reflTieLarge_FW_bot & -self.s_reflM_S & +self.s_reflO_S
    self.c_coreReflTP_S_i_FW_mid.region = -self.s_reflTieSmall_FW_mid & -self.s_reflI_S & +self.s_reflM_S
    self.c_coreReflTP_S_o_FW_mid.region = -self.s_reflTieLarge_FW_mid & -self.s_reflM_S & +self.s_reflO_S
    self.c_coreReflTP_S_i_FW_top.region = -self.s_reflTieSmall_FW_top & -self.s_reflI_S & +self.s_reflM_S
    self.c_coreReflTP_S_o_FW_top.region = -self.s_reflTieLarge_FW_top & -self.s_reflM_S & +self.s_reflO_S
    self.c_coreReflInstr_S_bot = openmc.Cell(name='Bottom South permanent reflector instrument tube', fill=self.mats['Air'])
    self.c_coreReflInstr_S_top = openmc.Cell(name='Top South permanent reflector instrument tube', fill=self.mats['Air'])
    self.c_coreReflInstr_S_bot.region = -self.s_reflInstr_S_bot & -self.s_reflI_S & +self.s_reflO_S
    self.c_coreReflInstr_S_top.region = -self.s_reflInstr_S_top & -self.s_reflI_S & +self.s_reflO_S
    self.c_coreRefl_W_i_N = openmc.Cell(name='Inner West part of permanent reflector, south side', fill=self.mats['Graphite'])
    self.c_coreRefl_W_o_N = openmc.Cell(name='Outer West part of permanent reflector, south side', fill=self.mats['Graphite'])
    self.c_coreRefl_W_i_S = openmc.Cell(name='Inner West part of permanent reflector, south side', fill=self.mats['Graphite'])
    self.c_coreRefl_W_o_S = openmc.Cell(name='Outer West part of permanent reflector, south side', fill=self.mats['Graphite'])
    self.c_coreRefl_W_i_N.region = -self.s_reflI_W & +self.s_reflM_W & -self.s_reflI_N & +self.s_reflWGate_N_o \
                              & +self.s_reflecFloor & -self.s_refl_top \
                              & +self.s_reflTieSmall_FN_bot & +self.s_reflTieSmall_FN_mid & +self.s_reflTieSmall_FN_top \
                              & +self.s_reflTieSmall_CN_bot & +self.s_reflTieSmall_CN_mid & +self.s_reflTieSmall_CN_top \
                              & +self.s_reflInstr_W_bot & +self.s_reflInstr_W_top
    self.c_coreRefl_W_o_N.region = -self.s_reflM_W & +self.s_reflO_W & -self.s_reflI_N & +self.s_reflWGate_N_o \
                              & +self.s_reflecFloor & -self.s_refl_top \
                              & +self.s_reflTieLarge_FN_bot & +self.s_reflTieLarge_FN_mid & +self.s_reflTieLarge_FN_top \
                              & +self.s_reflTieLarge_CN_bot & +self.s_reflTieLarge_CN_mid & +self.s_reflTieLarge_CN_top \
                              & +self.s_reflInstr_W_bot & +self.s_reflInstr_W_top
    self.c_coreRefl_W_i_S.region = -self.s_reflI_W & +self.s_reflM_W & -self.s_reflWGate_S_o & +self.s_reflI_S \
                              & +self.s_reflecFloor & -self.s_refl_top \
                              & +self.s_reflTieSmall_FS_bot & +self.s_reflTieSmall_FS_mid & +self.s_reflTieSmall_FS_top \
                              & +self.s_reflTieSmall_CS_bot & +self.s_reflTieSmall_CS_mid & +self.s_reflTieSmall_CS_top
    self.c_coreRefl_W_o_S.region = -self.s_reflM_W & +self.s_reflO_W & -self.s_reflWGate_S_o & +self.s_reflI_S \
                              & +self.s_reflecFloor & -self.s_refl_top \
                              & +self.s_reflTieLarge_FS_bot & +self.s_reflTieLarge_FS_mid & +self.s_reflTieLarge_FS_top \
                              & +self.s_reflTieLarge_CS_bot & +self.s_reflTieLarge_CS_mid & +self.s_reflTieLarge_CS_top
    self.c_coreReflTP_W_i_FN_bot = openmc.Cell(name='Inner West permanent reflector lower far N tie bolt', fill=self.mats['Al1100'])
    self.c_coreReflTP_W_o_FN_bot = openmc.Cell(name='Outer West permanent reflector lower far N tie bolt', fill=self.mats['Al1100'])
    self.c_coreReflTP_W_i_FN_mid = openmc.Cell(name='Inner West permanent reflector middle far N tie bolt', fill=self.mats['Al1100'])
    self.c_coreReflTP_W_o_FN_mid = openmc.Cell(name='Outer West permanent reflector middle far N tie bolt', fill=self.mats['Al1100'])
    self.c_coreReflTP_W_i_FN_top = openmc.Cell(name='Inner West permanent reflector upper far N tie bolt', fill=self.mats['Al1100'])
    self.c_coreReflTP_W_o_FN_top = openmc.Cell(name='Outer West permanent reflector upper far N tie bolt', fill=self.mats['Al1100'])
    self.c_coreReflTP_W_i_CN_bot = openmc.Cell(name='Inner West permanent reflector lower close N tie bolt', fill=self.mats['Al1100'])
    self.c_coreReflTP_W_o_CN_bot = openmc.Cell(name='Outer West permanent reflector lower close N tie bolt', fill=self.mats['Al1100'])
    self.c_coreReflTP_W_i_CN_mid = openmc.Cell(name='Inner West permanent reflector middle close N tie bolt', fill=self.mats['Al1100'])
    self.c_coreReflTP_W_o_CN_mid = openmc.Cell(name='Outer West permanent reflector middle close N tie bolt', fill=self.mats['Al1100'])
    self.c_coreReflTP_W_i_CN_top = openmc.Cell(name='Inner West permanent reflector upper close N tie bolt', fill=self.mats['Al1100'])
    self.c_coreReflTP_W_o_CN_top = openmc.Cell(name='Outer West permanent reflector upper close N tie bolt', fill=self.mats['Al1100'])
    self.c_coreReflTP_W_i_CS_bot = openmc.Cell(name='Inner West permanent reflector lower close S tie bolt', fill=self.mats['Al1100'])
    self.c_coreReflTP_W_o_CS_bot = openmc.Cell(name='Outer West permanent reflector lower close S tie bolt', fill=self.mats['Al1100'])
    self.c_coreReflTP_W_i_CS_mid = openmc.Cell(name='Inner West permanent reflector middle close S tie bolt', fill=self.mats['Al1100'])
    self.c_coreReflTP_W_o_CS_mid = openmc.Cell(name='Outer West permanent reflector middle close S tie bolt', fill=self.mats['Al1100'])
    self.c_coreReflTP_W_i_CS_top = openmc.Cell(name='Inner West permanent reflector upper close S tie bolt', fill=self.mats['Al1100'])
    self.c_coreReflTP_W_o_CS_top = openmc.Cell(name='Outer West permanent reflector upper close S tie bolt', fill=self.mats['Al1100'])
    self.c_coreReflTP_W_i_FS_bot = openmc.Cell(name='Inner West permanent reflector lower far S tie bolt', fill=self.mats['Al1100'])
    self.c_coreReflTP_W_o_FS_bot = openmc.Cell(name='Outer West permanent reflector lower far S tie bolt', fill=self.mats['Al1100'])
    self.c_coreReflTP_W_i_FS_mid = openmc.Cell(name='Inner West permanent reflector middle far S tie bolt', fill=self.mats['Al1100'])
    self.c_coreReflTP_W_o_FS_mid = openmc.Cell(name='Outer West permanent reflector middle far S tie bolt', fill=self.mats['Al1100'])
    self.c_coreReflTP_W_i_FS_top = openmc.Cell(name='Inner West permanent reflector upper far S tie bolt', fill=self.mats['Al1100'])
    self.c_coreReflTP_W_o_FS_top = openmc.Cell(name='Outer West permanent reflector upper far S tie bolt', fill=self.mats['Al1100'])
    self.c_coreReflTP_W_i_FN_bot.region = -self.s_reflTieSmall_FN_bot & -self.s_reflI_W & +self.s_reflM_W
    self.c_coreReflTP_W_o_FN_bot.region = -self.s_reflTieLarge_FN_bot & -self.s_reflM_W & +self.s_reflO_W
    self.c_coreReflTP_W_i_FN_mid.region = -self.s_reflTieSmall_FN_mid & -self.s_reflI_W & +self.s_reflM_W
    self.c_coreReflTP_W_o_FN_mid.region = -self.s_reflTieLarge_FN_mid & -self.s_reflM_W & +self.s_reflO_W
    self.c_coreReflTP_W_i_FN_top.region = -self.s_reflTieSmall_FN_top & -self.s_reflI_W & +self.s_reflM_W
    self.c_coreReflTP_W_o_FN_top.region = -self.s_reflTieLarge_FN_top & -self.s_reflM_W & +self.s_reflO_W
    self.c_coreReflTP_W_i_CN_bot.region = -self.s_reflTieSmall_CN_bot & -self.s_reflI_W & +self.s_reflM_W
    self.c_coreReflTP_W_o_CN_bot.region = -self.s_reflTieLarge_CN_bot & -self.s_reflM_W & +self.s_reflO_W
    self.c_coreReflTP_W_i_CN_mid.region = -self.s_reflTieSmall_CN_mid & -self.s_reflI_W & +self.s_reflM_W
    self.c_coreReflTP_W_o_CN_mid.region = -self.s_reflTieLarge_CN_mid & -self.s_reflM_W & +self.s_reflO_W
    self.c_coreReflTP_W_i_CN_top.region = -self.s_reflTieSmall_CN_top & -self.s_reflI_W & +self.s_reflM_W
    self.c_coreReflTP_W_o_CN_top.region = -self.s_reflTieLarge_CN_top & -self.s_reflM_W & +self.s_reflO_W
    self.c_coreReflTP_W_i_CS_bot.region = -self.s_reflTieSmall_CS_bot & -self.s_reflI_W & +self.s_reflM_W
    self.c_coreReflTP_W_o_CS_bot.region = -self.s_reflTieLarge_CS_bot & -self.s_reflM_W & +self.s_reflO_W
    self.c_coreReflTP_W_i_CS_mid.region = -self.s_reflTieSmall_CS_mid & -self.s_reflI_W & +self.s_reflM_W
    self.c_coreReflTP_W_o_CS_mid.region = -self.s_reflTieLarge_CS_mid & -self.s_reflM_W & +self.s_reflO_W
    self.c_coreReflTP_W_i_CS_top.region = -self.s_reflTieSmall_CS_top & -self.s_reflI_W & +self.s_reflM_W
    self.c_coreReflTP_W_o_CS_top.region = -self.s_reflTieLarge_CS_top & -self.s_reflM_W & +self.s_reflO_W
    self.c_coreReflTP_W_i_FS_bot.region = -self.s_reflTieSmall_FS_bot & -self.s_reflI_W & +self.s_reflM_W
    self.c_coreReflTP_W_o_FS_bot.region = -self.s_reflTieLarge_FS_bot & -self.s_reflM_W & +self.s_reflO_W
    self.c_coreReflTP_W_i_FS_mid.region = -self.s_reflTieSmall_FS_mid & -self.s_reflI_W & +self.s_reflM_W
    self.c_coreReflTP_W_o_FS_mid.region = -self.s_reflTieLarge_FS_mid & -self.s_reflM_W & +self.s_reflO_W
    self.c_coreReflTP_W_i_FS_top.region = -self.s_reflTieSmall_FS_top & -self.s_reflI_W & +self.s_reflM_W
    self.c_coreReflTP_W_o_FS_top.region = -self.s_reflTieLarge_FS_top & -self.s_reflM_W & +self.s_reflO_W
    self.c_coreReflInstr_W_bot = openmc.Cell(name='Bottom West permanent reflector instrument tube', fill=self.mats['Air'])
    self.c_coreReflInstr_W_top = openmc.Cell(name='Top West permanent reflector instrument tube', fill=self.mats['Air'])
    self.c_coreReflInstr_W_bot.region = -self.s_reflInstr_W_bot & -self.s_reflI_W & +self.s_reflO_W
    self.c_coreReflInstr_W_top.region = -self.s_reflInstr_W_top & -self.s_reflI_W & +self.s_reflO_W
    # Now go back and actually create the surfaces we will need for the gates
    self.s_reflNGateHole_bot = openmc.ZPlane(name='Permanent reflector north gate hole bottom', z0= c.struct_excoreReflNHole_bot)
    self.s_reflSGateHole_bot = openmc.ZPlane(name='Permanent reflector south gate hole bottom', z0= c.struct_excoreReflSHole_bot)
    self.s_reflWGateHole_bot = openmc.ZPlane(name='Permanent reflector west gate hole bottom', z0= c.struct_excoreReflWHole_bot)
    # Generate the surfaces for this particular configuration of gates. The surface position will depend on how "open"
    # the gates are. This is a unable parameter that is set by the user in the core.py script for the local benchmark.
    # The values range from 0 to 1 for each gate, with 0 indicating that the gate is fully closed, and 1 indicating that
    # the gate has been raised to the maximum possible height (which is set in constants.py, and is a feature of the core
    # roof geometry - these values should not be changed by the user).
    self.s_reflNGate_bot = openmc.ZPlane(name='Permanent reflector north gate bottom', z0= \
                           (c.struct_excoreReflNHole_bot + self.core.NBlockPos*c.excoreNReflHoleHeight) )
    self.s_reflSGate_bot = openmc.ZPlane(name='Permanent reflector south gate bottom', z0= \
                           (c.struct_excoreReflSHole_bot + self.core.SBlockPos*c.excoreSReflHoleHeight) )
    self.s_reflWGate_bot = openmc.ZPlane(name='Permanent reflector west gate bottom', z0= \
                           (c.struct_excoreReflWHole_bot + self.core.WBlockPos*c.excoreWReflHoleHeight) )
    # TODO the next 3 surfaces should also be raised up by the height of the gate handles
    self.s_reflNGate_top = openmc.ZPlane(name='Permanent reflector north gate top', z0= \
                           (c.struct_excoreReflNHole_bot + self.core.NBlockPos*c.excoreNReflHoleHeight + c.excoreRefGateHeight) )
    self.s_reflSGate_top = openmc.ZPlane(name='Permanent reflector south gate top', z0= \
                           (c.struct_excoreReflSHole_bot + self.core.SBlockPos*c.excoreSReflHoleHeight + c.excoreRefGateHeight) )
    self.s_reflWGate_top = openmc.ZPlane(name='Permanent reflector west gate top', z0= \
                           (c.struct_excoreReflWHole_bot + self.core.WBlockPos*c.excoreWReflHoleHeight + c.excoreRefGateHeight) )

    # Create the graphite cells below gates
    self.c_coreReflGate_N_bot = openmc.Cell(name='Graphite below the north permanent reflector gate', fill=self.mats['Graphite'])
    self.c_coreReflGate_S_bot = openmc.Cell(name='Graphite below the south permanent reflector gate', fill=self.mats['Graphite'])
    self.c_coreReflGate_W_bot = openmc.Cell(name='Graphite below the west permanent reflector gate', fill=self.mats['Graphite'])
    self.c_coreReflGate_N_bot.region = -self.s_reflO_N & +self.s_reflI_N & -self.s_reflNGate_E_o & +self.s_reflNGate_W_o \
                              & +self.s_reflecFloor & -self.s_reflNGateHole_bot
    self.c_coreReflGate_S_bot.region = -self.s_reflI_S & +self.s_reflO_S & -self.s_reflSGate_E_o & +self.s_reflSGate_W_o \
                              & +self.s_reflecFloor & -self.s_reflSGateHole_bot
    self.c_coreReflGate_W_bot.region = -self.s_reflI_W & +self.s_reflO_W & -self.s_reflWGate_N_o & +self.s_reflWGate_S_o \
                              & +self.s_reflecFloor & -self.s_reflWGateHole_bot
    # Create the surfaces for the non-moving parts of the gates
    self.s_reflNGateL_E_i = openmc.XPlane(name='Permanent reflector north gate liner inner east surface', x0= c.excoreNGateIEdgeDist)
    self.s_reflNGateL_W_i = openmc.XPlane(name='Permanent reflector north gate liner inner west surface', x0=-c.excoreNGateIEdgeDist)
    self.s_reflSGateL_E_i = openmc.XPlane(name='Permanent reflector south gate liner inner east surface', x0= c.excoreWSGateIEdgeDist)
    self.s_reflSGateL_W_i = openmc.XPlane(name='Permanent reflector south gate liner inner west surface', x0=-c.excoreWSGateIEdgeDist)
    self.s_reflWGateL_N_i = openmc.YPlane(name='Permanent reflector west gate liner inner north surface', y0= c.excoreWSGateIEdgeDist)
    self.s_reflWGateL_S_i = openmc.YPlane(name='Permanent reflector west gate liner inner south surface', y0=-c.excoreWSGateIEdgeDist)
    self.s_reflNGateR_E_o = openmc.XPlane(name='Permanent reflector north gate rear liner outer east surface', \
                            x0= (c.excoreNGateEdgeDist - c.excoreGateRearIndent))
    self.s_reflNGateR_W_o = openmc.XPlane(name='Permanent reflector north gate rear liner outer west surface', \
                            x0=-(c.excoreNGateEdgeDist - c.excoreGateRearIndent))
    self.s_reflSGateR_E_o = openmc.XPlane(name='Permanent reflector south gate rear liner outer east surface', \
                            x0= (c.excoreWSGateEdgeDist - c.excoreGateRearIndent))
    self.s_reflSGateR_W_o = openmc.XPlane(name='Permanent reflector south gate rear liner outer west surface', \
                            x0=-(c.excoreWSGateEdgeDist - c.excoreGateRearIndent))
    self.s_reflWGateR_N_o = openmc.YPlane(name='Permanent reflector west gate rear liner outer north surface', \
                            y0= (c.excoreWSGateEdgeDist - c.excoreGateRearIndent))
    self.s_reflWGateR_S_o = openmc.YPlane(name='Permanent reflector west gate rear liner outer south surface', \
                            y0=-(c.excoreWSGateEdgeDist - c.excoreGateRearIndent))
    self.s_reflNGateR_E_i = openmc.XPlane(name='Permanent reflector north gate rear liner inner east surface', \
                            x0= (c.excoreNGateEdgeDist - c.excoreGateRearIndent - c.excoreGateLinerThick))
    self.s_reflNGateR_W_i = openmc.XPlane(name='Permanent reflector north gate rear liner inner west surface', \
                            x0=-(c.excoreNGateEdgeDist - c.excoreGateRearIndent - c.excoreGateLinerThick))
    self.s_reflSGateR_E_i = openmc.XPlane(name='Permanent reflector south gate rear liner inner east surface', \
                            x0= (c.excoreWSGateEdgeDist - c.excoreGateRearIndent - c.excoreGateLinerThick))
    self.s_reflSGateR_W_i = openmc.XPlane(name='Permanent reflector south gate rear liner inner west surface', \
                            x0=-(c.excoreWSGateEdgeDist - c.excoreGateRearIndent - c.excoreGateLinerThick))
    self.s_reflWGateR_N_i = openmc.YPlane(name='Permanent reflector west gate rear liner inner north surface', \
                            y0= (c.excoreWSGateEdgeDist - c.excoreGateRearIndent - c.excoreGateLinerThick))
    self.s_reflWGateR_S_i = openmc.YPlane(name='Permanent reflector west gate rear liner inner south surface', \
                            y0=-(c.excoreWSGateEdgeDist - c.excoreGateRearIndent - c.excoreGateLinerThick))
    self.s_reflNGate_E_wide = openmc.XPlane(name='Permanent reflector north gate wide graphite part east surface', \
                           x0= c.excoreNGateWideDist)
    self.s_reflNGate_W_wide = openmc.XPlane(name='Permanent reflector north gate wide graphite part west surface', \
                           x0=-c.excoreNGateWideDist)
    self.s_reflSGate_E_wide = openmc.XPlane(name='Permanent reflector south gate wide graphite part east surface', \
                           x0= c.excoreWSGateWideDist)
    self.s_reflSGate_W_wide = openmc.XPlane(name='Permanent reflector south gate wide graphite part west surface', \
                           x0=-c.excoreWSGateWideDist)
    self.s_reflWGate_N_wide = openmc.YPlane(name='Permanent reflector west gate wide graphite part north surface', \
                           y0= c.excoreWSGateWideDist)
    self.s_reflWGate_S_wide = openmc.YPlane(name='Permanent reflector west gate wide graphite part south surface', \
                           y0=-c.excoreWSGateWideDist)
    self.s_reflNGate_E_thin = openmc.XPlane(name='Permanent reflector north gate thin graphite part east surface', \
                           x0= c.excoreNGateThinDist)
    self.s_reflNGate_W_thin = openmc.XPlane(name='Permanent reflector north gate thin graphite part west surface', \
                           x0=-c.excoreNGateThinDist)
    self.s_reflSGate_E_thin = openmc.XPlane(name='Permanent reflector south gate thin graphite part east surface', \
                           x0= c.excoreWSGateThinDist)
    self.s_reflSGate_W_thin = openmc.XPlane(name='Permanent reflector south gate thin graphite part west surface', \
                           x0=-c.excoreWSGateThinDist)
    self.s_reflWGate_N_thin = openmc.YPlane(name='Permanent reflector west gate thin graphite part north surface', \
                           y0= c.excoreWSGateThinDist)
    self.s_reflWGate_S_thin = openmc.YPlane(name='Permanent reflector west gate thin graphite part south surface', \
                           y0=-c.excoreWSGateThinDist)
    self.s_reflNGateGrphWide_rear = openmc.YPlane(name='Permanent reflector north gate wide graphite part rear surface', \
                                    y0= c.excoreGateWideEnd)
    self.s_reflSGateGrphWide_rear = openmc.YPlane(name='Permanent reflector south gate wide graphite part rear surface', \
                                    y0=-c.excoreGateWideEnd)
    self.s_reflWGateGrphWide_rear = openmc.XPlane(name='Permanent reflector west gate wide graphite part rear surface', \
                                    x0=-c.excoreGateWideEnd)
    self.s_reflNGateGrphThin_rear = openmc.YPlane(name='Permanent reflector north gate thin graphite part rear surface', \
                                    y0= c.excoreGateGrphEnd)
    self.s_reflSGateGrphThin_rear = openmc.YPlane(name='Permanent reflector south gate thin graphite part rear surface', \
                                    y0=-c.excoreGateGrphEnd)
    self.s_reflWGateGrphThin_rear = openmc.XPlane(name='Permanent reflector west gate thin graphite part rear surface', \
                                    x0=-c.excoreGateGrphEnd)
    self.s_reflNGateWideRear_i = openmc.YPlane(name='Permanent reflector north gate wide liner inner surface', \
                            y0= c.excoreGateFrontCladStart)
    self.s_reflSGateWideRear_i = openmc.YPlane(name='Permanent reflector south gate wide liner inner surface', \
                            y0=-c.excoreGateFrontCladStart)
    self.s_reflWGateWideRear_i = openmc.XPlane(name='Permanent reflector west gate wide liner inner surface', \
                            x0=-c.excoreGateFrontCladStart)
    self.s_reflNGateWideRear_o = openmc.YPlane(name='Permanent reflector north gate wide liner outer surface', \
                            y0= c.excoreGateFrontEnd)
    self.s_reflSGateWideRear_o = openmc.YPlane(name='Permanent reflector south gate wide liner outer surface', \
                            y0=-c.excoreGateFrontEnd)
    self.s_reflWGateWideRear_o = openmc.XPlane(name='Permanent reflector west gate wide liner outer surface', \
                            x0=-c.excoreGateFrontEnd)
    self.s_reflNGateMidAxial_i = openmc.ZPlane(name='Permanent reflector north gate short segment liner inner surface', \
                            z0= c.struct_excoreReflGateLinerNLowerClad_bot)
    self.s_reflSGateMidAxial_i = openmc.ZPlane(name='Permanent reflector south gate short segment liner inner surface', \
                            z0= c.struct_excoreReflGateLinerSLowerClad_bot)
    self.s_reflWGateMidAxial_i = openmc.ZPlane(name='Permanent reflector west gate short segment liner inner surface', \
                            z0= c.struct_excoreReflGateLinerWLowerClad_bot)
    self.s_reflNGateMidAxial_o = openmc.ZPlane(name='Permanent reflector north gate short segment liner outer surface', \
                            z0= c.struct_excoreReflGateLinerNLowerClad_top)
    self.s_reflSGateMidAxial_o = openmc.ZPlane(name='Permanent reflector south gate short segment liner outer surface', \
                            z0= c.struct_excoreReflGateLinerSLowerClad_top)
    self.s_reflWGateMidAxial_o = openmc.ZPlane(name='Permanent reflector west gate short segment liner outer surface', \
                            z0= c.struct_excoreReflGateLinerWLowerClad_top)
    self.s_reflNGateTopAxial_i = openmc.ZPlane(name='Permanent reflector north gate tall segment liner inner surface', \
                            z0= c.struct_excoreReflGateLinerNUpperClad_bot)
    self.s_reflSGateTopAxial_i = openmc.ZPlane(name='Permanent reflector south gate tall segment liner inner surface', \
                            z0= c.struct_excoreReflGateLinerSUpperClad_bot)
    self.s_reflWGateTopAxial_i = openmc.ZPlane(name='Permanent reflector west gate tall segment liner inner surface', \
                            z0= c.struct_excoreReflGateLinerWUpperClad_bot)
    self.s_reflNGateTopAxial_o = openmc.ZPlane(name='Permanent reflector north gate tall segment liner outer surface', \
                            z0= c.struct_excoreReflGateLinerNUpperClad_top)
    self.s_reflSGateTopAxial_o = openmc.ZPlane(name='Permanent reflector south gate tall segment liner outer surface', \
                            z0= c.struct_excoreReflGateLinerSUpperClad_top)
    self.s_reflWGateTopAxial_o = openmc.ZPlane(name='Permanent reflector west gate tall segment liner outer surface', \
                            z0= c.struct_excoreReflGateLinerWUpperClad_top)
    # Build some cells for those regions
    self.c_coreReflGateGrph_N_rear = openmc.Cell(name='Graphite behind the north permanent reflector gate', fill=self.mats['Graphite'])
    self.c_coreReflGateGrph_S_rear = openmc.Cell(name='Graphite behind the south permanent reflector gate', fill=self.mats['Graphite'])
    self.c_coreReflGateGrph_W_rear = openmc.Cell(name='Graphite behind the west permanent reflector gate', fill=self.mats['Graphite'])
    self.c_coreReflGateGrph_N_rear.region = -self.s_reflO_N & +self.s_reflNGateWideRear_o & -self.s_reflNGate_E_o & \
                              +self.s_reflNGate_W_o & +self.s_reflNGateHole_bot & -self.s_refl_top & \
                              ( -self.s_reflNGateR_W_o | +self.s_reflNGateMidAxial_o | +self.s_reflNGateR_E_o )
    self.c_coreReflGateGrph_S_rear.region = +self.s_reflO_S & -self.s_reflSGateWideRear_o & -self.s_reflSGate_E_o & \
                              +self.s_reflSGate_W_o & +self.s_reflSGateHole_bot & -self.s_refl_top & \
                              ( -self.s_reflSGateR_W_o | +self.s_reflSGateMidAxial_o | +self.s_reflSGateR_E_o )
    self.c_coreReflGateGrph_W_rear.region = +self.s_reflO_W & -self.s_reflWGateWideRear_o & -self.s_reflWGate_N_o & \
                              +self.s_reflWGate_S_o & +self.s_reflWGateHole_bot & -self.s_refl_top & \
                              ( -self.s_reflWGateR_S_o | +self.s_reflWGateMidAxial_o | +self.s_reflWGateR_N_o )
    self.c_coreReflGateLiner_N_rear = openmc.Cell(name='Liner behind the north permanent reflector gate', fill=self.mats['Al1100'])
    self.c_coreReflGateLiner_S_rear = openmc.Cell(name='Liner behind the south permanent reflector gate', fill=self.mats['Al1100'])
    self.c_coreReflGateLiner_W_rear = openmc.Cell(name='Liner behind the west permanent reflector gate', fill=self.mats['Al1100'])
    self.c_coreReflGateLiner_N_rear.region = -self.s_reflO_N & +self.s_reflNGateWideRear_o & -self.s_reflNGateR_E_o & \
                              +self.s_reflNGateR_W_o & +self.s_reflNGateHole_bot & -self.s_reflNGateMidAxial_o & \
                              ( -self.s_reflNGateR_W_i | +self.s_reflNGateMidAxial_i | +self.s_reflNGateR_E_i )
    self.c_coreReflGateLiner_S_rear.region = +self.s_reflO_S & -self.s_reflSGateWideRear_o & -self.s_reflSGateR_E_o & \
                              +self.s_reflSGateR_W_o & +self.s_reflSGateHole_bot & -self.s_reflSGateMidAxial_o & \
                              ( -self.s_reflSGateR_W_i | +self.s_reflSGateMidAxial_i | +self.s_reflSGateR_E_i )
    self.c_coreReflGateLiner_W_rear.region = +self.s_reflO_W & -self.s_reflWGateWideRear_o & -self.s_reflWGateR_N_o & \
                              +self.s_reflWGateR_S_o & +self.s_reflWGateHole_bot & -self.s_reflWGateMidAxial_o & \
                              ( -self.s_reflWGateR_S_i | +self.s_reflWGateMidAxial_i | +self.s_reflWGateR_N_i )
    self.c_coreReflGateAir_N_rear = openmc.Cell(name='Air in the rear area behind the north perm refl gate', fill=self.mats['Air'])
    self.c_coreReflGateAir_S_rear = openmc.Cell(name='Air in the rear area behind the south perm refl gate', fill=self.mats['Air'])
    self.c_coreReflGateAir_W_rear = openmc.Cell(name='Air in the rear area behind the west perm refl gate', fill=self.mats['Air'])
    self.c_coreReflGateAir_N_rear.region = -self.s_reflO_N & +self.s_reflNGateWideRear_i & -self.s_reflNGateR_E_i & \
                              +self.s_reflNGateR_W_i & +self.s_reflNGateHole_bot & -self.s_reflNGateMidAxial_i
    self.c_coreReflGateAir_S_rear.region = +self.s_reflO_S & -self.s_reflSGateWideRear_i & -self.s_reflSGateR_E_i & \
                              +self.s_reflSGateR_W_i & +self.s_reflSGateHole_bot & -self.s_reflSGateMidAxial_i
    self.c_coreReflGateAir_W_rear.region = +self.s_reflO_W & -self.s_reflWGateWideRear_i & -self.s_reflWGateR_N_i & \
                              +self.s_reflWGateR_S_i & +self.s_reflWGateHole_bot & -self.s_reflWGateMidAxial_i
    self.c_coreReflGateLiner_N_back = openmc.Cell(name='Back wall of liner around the north permanent reflector gate', \
                                      fill=self.mats['Al1100'])
    self.c_coreReflGateLiner_S_back = openmc.Cell(name='Back wall of liner around the south permanent reflector gate', \
                                      fill=self.mats['Al1100'])
    self.c_coreReflGateLiner_W_back = openmc.Cell(name='Back wall of liner around the west permanent reflector gate', \
                                      fill=self.mats['Al1100'])
    self.c_coreReflGateLiner_N_back.region = -self.s_reflNGateWideRear_o & +self.s_reflNGateWideRear_i & -self.s_reflNGate_E_o & \
                              +self.s_reflNGate_W_o & +self.s_reflNGateHole_bot & -self.s_reflNGateTopAxial_o & \
                              ( -self.s_reflNGateR_W_i | +self.s_reflNGateMidAxial_i | +self.s_reflNGateR_E_i )
    self.c_coreReflGateLiner_S_back.region = +self.s_reflSGateWideRear_o & -self.s_reflSGateWideRear_i & -self.s_reflSGate_E_o & \
                              +self.s_reflSGate_W_o & +self.s_reflSGateHole_bot & -self.s_reflSGateTopAxial_o & \
                              ( -self.s_reflSGateR_W_i | +self.s_reflSGateMidAxial_i | +self.s_reflSGateR_E_i )
    self.c_coreReflGateLiner_W_back.region = +self.s_reflWGateWideRear_o & -self.s_reflWGateWideRear_i & -self.s_reflWGate_N_o & \
                              +self.s_reflWGate_S_o & +self.s_reflWGateHole_bot & -self.s_reflWGateTopAxial_o & \
                              ( -self.s_reflWGateR_S_i | +self.s_reflWGateMidAxial_i | +self.s_reflWGateR_N_i )
    self.c_coreReflGateLiner_N_E = openmc.Cell(name='East wall of liner around the north permanent reflector gate', \
                                      fill=self.mats['Al1100'])
    self.c_coreReflGateLiner_S_E = openmc.Cell(name='East wall of liner around the south permanent reflector gate', \
                                      fill=self.mats['Al1100'])
    self.c_coreReflGateLiner_W_N = openmc.Cell(name='North wall of liner around the west permanent reflector gate', \
                                      fill=self.mats['Al1100'])
    self.c_coreReflGateLiner_N_W = openmc.Cell(name='West wall of liner around the north permanent reflector gate', \
                                      fill=self.mats['Al1100'])
    self.c_coreReflGateLiner_S_W = openmc.Cell(name='West wall of liner around the south permanent reflector gate', \
                                      fill=self.mats['Al1100'])
    self.c_coreReflGateLiner_W_S = openmc.Cell(name='South wall of liner around the west permanent reflector gate', \
                                      fill=self.mats['Al1100'])
    self.c_coreReflGateLiner_N_E.region = -self.s_reflNGateWideRear_i & +self.s_reflI_N & -self.s_reflNGate_E_o & \
                              +self.s_reflNGateL_E_i & +self.s_reflNGateHole_bot & -self.s_reflNGateTopAxial_o
    self.c_coreReflGateLiner_N_W.region = -self.s_reflNGateWideRear_i & +self.s_reflI_N & -self.s_reflNGateL_W_i & \
                              +self.s_reflNGate_W_o & +self.s_reflNGateHole_bot & -self.s_reflNGateTopAxial_o
    self.c_coreReflGateLiner_S_E.region = +self.s_reflSGateWideRear_i & -self.s_reflI_S & -self.s_reflSGate_E_o & \
                              +self.s_reflSGateL_E_i & +self.s_reflSGateHole_bot & -self.s_reflSGateTopAxial_o
    self.c_coreReflGateLiner_S_W.region = +self.s_reflSGateWideRear_i & -self.s_reflI_S & -self.s_reflSGateL_W_i & \
                              +self.s_reflSGate_W_o & +self.s_reflSGateHole_bot & -self.s_reflSGateTopAxial_o
    self.c_coreReflGateLiner_W_N.region = -self.s_reflI_W & +self.s_reflWGateWideRear_i & -self.s_reflWGate_N_o & \
                              +self.s_reflWGateL_N_i & +self.s_reflWGateHole_bot & -self.s_reflWGateTopAxial_o
    self.c_coreReflGateLiner_W_S.region = -self.s_reflI_W & +self.s_reflWGateWideRear_i & -self.s_reflWGateL_S_i & \
                              +self.s_reflWGate_S_o & +self.s_reflWGateHole_bot & -self.s_reflWGateTopAxial_o
    self.c_coreReflGateLiner_N_top = openmc.Cell(name='Top wall of liner around the north permanent reflector gate', \
                                     fill=self.mats['Al1100'])
    self.c_coreReflGateLiner_S_top = openmc.Cell(name='Top wall of liner around the south permanent reflector gate', \
                                     fill=self.mats['Al1100'])
    self.c_coreReflGateLiner_W_top = openmc.Cell(name='Top wall of liner around the west permanent reflector gate', \
                                     fill=self.mats['Al1100'])
    self.c_coreReflGateLiner_N_top.region = -self.s_reflNGateWideRear_i & +self.s_reflI_N & -self.s_reflNGateL_E_i & \
                              +self.s_reflNGateL_W_i & +self.s_reflNGateTopAxial_i & -self.s_reflNGateTopAxial_o & \
                              ( -self.s_reflNGate_W_wide | +self.s_reflNGateGrphWide_rear | +self.s_reflNGate_E_wide ) & \
                              ( -self.s_reflNGate_W_thin | +self.s_reflNGateGrphThin_rear | +self.s_reflNGate_E_thin )
    self.c_coreReflGateLiner_S_top.region = +self.s_reflSGateWideRear_i & -self.s_reflI_S & -self.s_reflSGateL_E_i & \
                              +self.s_reflSGateL_W_i & +self.s_reflSGateTopAxial_i & -self.s_reflSGateTopAxial_o & \
                              ( -self.s_reflSGate_W_wide | -self.s_reflSGateGrphWide_rear | +self.s_reflSGate_E_wide ) & \
                              ( -self.s_reflSGate_W_thin | -self.s_reflSGateGrphThin_rear | +self.s_reflSGate_E_thin )
    self.c_coreReflGateLiner_W_top.region = +self.s_reflWGateWideRear_i & -self.s_reflI_W & -self.s_reflWGateL_N_i & \
                              +self.s_reflWGateL_S_i & +self.s_reflWGateTopAxial_i & -self.s_reflWGateTopAxial_o & \
                              ( -self.s_reflWGate_S_wide | -self.s_reflWGateGrphWide_rear | +self.s_reflWGate_N_wide ) & \
                              ( -self.s_reflWGate_S_thin | -self.s_reflWGateGrphThin_rear | +self.s_reflWGate_N_thin )
    self.c_coreReflGateAir_N = openmc.Cell(name='Air around the north permanent reflector gate', fill=self.mats['Air'])
    self.c_coreReflGateAir_S = openmc.Cell(name='Air around the south permanent reflector gate', fill=self.mats['Air'])
    self.c_coreReflGateAir_W = openmc.Cell(name='Air around the west permanent reflector gate', fill=self.mats['Air'])
    self.c_coreReflGateAir_N.region = -self.s_reflNGateWideRear_i & +self.s_reflI_N & -self.s_reflNGateL_E_i & \
                              +self.s_reflNGateL_W_i & +self.s_reflNGateHole_bot & -self.s_reflNGateTopAxial_i & \
                              ( -self.s_reflNGate_W_wide | +self.s_reflNGateGrphWide_rear | +self.s_reflNGate_E_wide ) & \
                              ( -self.s_reflNGate_W_thin | +self.s_reflNGateGrphThin_rear | +self.s_reflNGate_E_thin )
    self.c_coreReflGateAir_S.region = +self.s_reflSGateWideRear_i & -self.s_reflI_S & -self.s_reflSGateL_E_i & \
                              +self.s_reflSGateL_W_i & +self.s_reflSGateHole_bot & -self.s_reflSGateTopAxial_i & \
                              ( -self.s_reflSGate_W_wide | -self.s_reflSGateGrphWide_rear | +self.s_reflSGate_E_wide ) & \
                              ( -self.s_reflSGate_W_thin | -self.s_reflSGateGrphThin_rear | +self.s_reflSGate_E_thin )
    self.c_coreReflGateAir_W.region = +self.s_reflWGateWideRear_i & -self.s_reflI_W & -self.s_reflWGateL_N_i & \
                              +self.s_reflWGateL_S_i & +self.s_reflWGateHole_bot & -self.s_reflWGateTopAxial_i & \
                              ( -self.s_reflWGate_S_wide | -self.s_reflWGateGrphWide_rear | +self.s_reflWGate_N_wide ) & \
                              ( -self.s_reflWGate_S_thin | -self.s_reflWGateGrphThin_rear | +self.s_reflWGate_N_thin )
    self.c_coreReflGateAirStat_N_top = openmc.Cell(name='Stationary air above the north permanent reflector gate', fill=self.mats['Air'])
    self.c_coreReflGateAirStat_S_top = openmc.Cell(name='Stationary air above the south permanent reflector gate', fill=self.mats['Air'])
    self.c_coreReflGateAirStat_W_top = openmc.Cell(name='Stationary air above the west permanent reflector gate', fill=self.mats['Air'])
    self.c_coreReflGateCon_N_top = openmc.Cell(name='Concrete above the north permanent reflector gate', fill=self.mats['Concrete'])
    self.c_coreReflGateCon_S_top = openmc.Cell(name='Concrete above the south permanent reflector gate', fill=self.mats['Concrete'])
    self.c_coreReflGateCon_W_top = openmc.Cell(name='Concrete above the west permanent reflector gate', fill=self.mats['Concrete'])
    self.c_coreReflGateAirStat_N_top.region = -self.s_reflO_N & +self.s_reflI_N & -self.s_reflNGate_E_o & +self.s_reflNGate_W_o \
                              & +self.s_refl_top & -self.s_aboveReflRoof & \
                              ( -self.s_reflNGate_W_wide | +self.s_reflNGateGrphWide_rear | +self.s_reflNGate_E_wide ) & \
                              ( -self.s_reflNGate_W_thin | +self.s_reflNGateGrphThin_rear | +self.s_reflNGate_E_thin ) & \
                              ( +self.s_reflNGateTopAxial_o | +self.s_reflNGateWideRear_o)
    self.c_coreReflGateAirStat_S_top.region = -self.s_reflI_S & +self.s_reflO_S & -self.s_reflSGate_E_o & +self.s_reflSGate_W_o \
                              & +self.s_refl_top & -self.s_aboveReflRoof & \
                              ( -self.s_reflSGate_W_wide | -self.s_reflSGateGrphWide_rear | +self.s_reflSGate_E_wide ) & \
                              ( -self.s_reflSGate_W_thin | -self.s_reflSGateGrphThin_rear | +self.s_reflSGate_E_thin ) & \
                              ( +self.s_reflSGateTopAxial_o | -self.s_reflSGateWideRear_o)
    self.c_coreReflGateAirStat_W_top.region = -self.s_reflI_W & +self.s_reflO_W & -self.s_reflWGate_N_o & +self.s_reflWGate_S_o \
                              & +self.s_refl_top & -self.s_aboveReflRoof & \
                              ( -self.s_reflWGate_S_wide | -self.s_reflWGateGrphWide_rear | +self.s_reflWGate_N_wide ) & \
                              ( -self.s_reflWGate_S_thin | -self.s_reflWGateGrphThin_rear | +self.s_reflWGate_N_thin ) & \
                              ( +self.s_reflWGateTopAxial_o | -self.s_reflWGateWideRear_o)
    self.c_coreReflGateCon_N_top.region = -self.s_reflO_N & +self.s_reflI_N & -self.s_reflNGate_E_o & +self.s_reflNGate_W_o \
                          & +self.s_aboveReflRoof & -self.s_aboveCoreRoof & \
                          ( -self.s_reflNGate_W_wide | +self.s_reflNGateGrphWide_rear | +self.s_reflNGate_E_wide ) & \
                          ( -self.s_reflNGate_W_thin | +self.s_reflNGateGrphThin_rear | +self.s_reflNGate_E_thin ) & \
                          ( +self.s_reflNGateTopAxial_o | +self.s_reflNGateWideRear_o)
    self.c_coreReflGateCon_S_top.region = -self.s_reflI_S & +self.s_reflO_S & -self.s_reflSGate_E_o & +self.s_reflSGate_W_o \
                          & +self.s_aboveReflRoof & -self.s_aboveCoreRoof & \
                          ( -self.s_reflSGate_W_wide | -self.s_reflSGateGrphWide_rear | +self.s_reflSGate_E_wide ) & \
                          ( -self.s_reflSGate_W_thin | -self.s_reflSGateGrphThin_rear | +self.s_reflSGate_E_thin ) & \
                          ( +self.s_reflSGateTopAxial_o | -self.s_reflSGateWideRear_o)
    self.c_coreReflGateCon_W_top.region = -self.s_reflI_W & +self.s_reflO_W & -self.s_reflWGate_N_o & +self.s_reflWGate_S_o \
                          & +self.s_aboveReflRoof & -self.s_aboveCoreRoof & \
                          ( -self.s_reflWGate_S_wide | -self.s_reflWGateGrphWide_rear | +self.s_reflWGate_N_wide ) & \
                          ( -self.s_reflWGate_S_thin | -self.s_reflWGateGrphThin_rear | +self.s_reflWGate_N_thin ) & \
                          ( +self.s_reflWGateTopAxial_o | -self.s_reflWGateWideRear_o)
    # Now start working on the movable parts of the gate
    # If the gates are raised by any amount, we have to generate an air cell beneath the gate
    if self.core.NBlockPos > 0.0: # The north gate is open
      # Generate an air cell below the gate
      self.c_coreReflGateAir_N_bot = openmc.Cell(name='Air below the north permanent reflector gate', fill=self.mats['Air'])
      self.c_coreReflGateAir_N_bot.region = -self.s_reflNGateGrphThin_rear & +self.s_reflI_N & -self.s_reflNGate_E_wide & \
                              +self.s_reflNGate_W_wide & +self.s_reflNGateHole_bot & -self.s_reflNGate_bot & \
                              ( +self.s_reflNGate_W_thin | -self.s_reflNGateGrphWide_rear ) & \
                              ( -self.s_reflNGate_E_thin | -self.s_reflNGateGrphWide_rear )
    if self.core.SBlockPos > 0.0: # The south gate is open
      # Generate an air cell below the gate
      self.c_coreReflGateAir_S_bot = openmc.Cell(name='Air below the south permanent reflector gate', fill=self.mats['Air'])
      self.c_coreReflGateAir_S_bot.region = +self.s_reflSGateGrphThin_rear & -self.s_reflI_S & -self.s_reflSGate_E_wide & \
                              +self.s_reflSGate_W_wide & +self.s_reflSGateHole_bot & -self.s_reflSGate_bot & \
                              ( +self.s_reflSGate_W_thin | +self.s_reflSGateGrphWide_rear ) & \
                              ( -self.s_reflSGate_E_thin | +self.s_reflSGateGrphWide_rear )
    if self.core.WBlockPos > 0.0: # The west gate is open
      # Generate an air cell below the gate
      self.c_coreReflGateAir_W_bot = openmc.Cell(name='Air below the west permanent reflector gate', fill=self.mats['Air'])
      self.c_coreReflGateAir_W_bot.region = +self.s_reflWGateGrphThin_rear & -self.s_reflI_W & -self.s_reflWGate_N_wide & \
                              +self.s_reflWGate_S_wide & +self.s_reflWGateHole_bot & -self.s_reflWGate_bot & \
                              ( +self.s_reflWGate_S_thin | +self.s_reflWGateGrphWide_rear ) & \
                              ( -self.s_reflWGate_N_thin | +self.s_reflWGateGrphWide_rear )
    # Create the actual physical graphite gates
    self.c_coreReflGate_N = openmc.Cell(name='North permanent reflector graphite gate', fill=self.mats['Graphite'])
    self.c_coreReflGate_S = openmc.Cell(name='South permanent reflector graphite gate', fill=self.mats['Graphite'])
    self.c_coreReflGate_W = openmc.Cell(name='West permanent reflector graphite gate', fill=self.mats['Graphite'])
    self.c_coreReflGate_N.region = -self.s_reflNGateGrphThin_rear & +self.s_reflI_N & -self.s_reflNGate_E_wide & \
                         +self.s_reflNGate_W_wide & +self.s_reflNGate_bot & -self.s_reflNGate_top & \
                         ( +self.s_reflNGate_W_thin | -self.s_reflNGateGrphWide_rear ) & \
                         ( -self.s_reflNGate_E_thin | -self.s_reflNGateGrphWide_rear )
    self.c_coreReflGate_S.region = +self.s_reflSGateGrphThin_rear & -self.s_reflI_S & -self.s_reflSGate_E_wide & \
                         +self.s_reflSGate_W_wide & +self.s_reflSGate_bot & -self.s_reflSGate_top & \
                         ( +self.s_reflSGate_W_thin | +self.s_reflSGateGrphWide_rear ) & \
                         ( -self.s_reflSGate_E_thin | +self.s_reflSGateGrphWide_rear )
    self.c_coreReflGate_W.region = +self.s_reflWGateGrphThin_rear & -self.s_reflI_W & -self.s_reflWGate_N_wide & \
                         +self.s_reflWGate_S_wide & +self.s_reflWGate_bot & -self.s_reflWGate_top & \
                         ( +self.s_reflWGate_S_thin | +self.s_reflWGateGrphWide_rear ) & \
                         ( -self.s_reflWGate_N_thin | +self.s_reflWGateGrphWide_rear )
    # Now the air directly above the gates TODO the handles should be included here somehow
    self.c_coreReflGateAir_N_top = openmc.Cell(name='Air directly above the north permanent reflector gate', fill=self.mats['Air'])
    self.c_coreReflGateAir_S_top = openmc.Cell(name='Air directly above the south permanent reflector gate', fill=self.mats['Air'])
    self.c_coreReflGateAir_W_top = openmc.Cell(name='Air directly above the west permanent reflector gate', fill=self.mats['Air'])
    self.c_coreReflGateAir_N_top.region = -self.s_reflNGateGrphThin_rear & +self.s_reflI_N & -self.s_reflNGate_E_wide & \
                         +self.s_reflNGate_W_wide & +self.s_reflNGate_top & -self.s_aboveCoreRoof & \
                         ( +self.s_reflNGate_W_thin | -self.s_reflNGateGrphWide_rear ) & \
                         ( -self.s_reflNGate_E_thin | -self.s_reflNGateGrphWide_rear )
    self.c_coreReflGateAir_S_top.region = +self.s_reflSGateGrphThin_rear & -self.s_reflI_S & -self.s_reflSGate_E_wide & \
                         +self.s_reflSGate_W_wide & +self.s_reflSGate_top & -self.s_aboveCoreRoof & \
                         ( +self.s_reflSGate_W_thin | +self.s_reflSGateGrphWide_rear ) & \
                         ( -self.s_reflSGate_E_thin | +self.s_reflSGateGrphWide_rear )
    self.c_coreReflGateAir_W_top.region = +self.s_reflWGateGrphThin_rear & -self.s_reflI_W & -self.s_reflWGate_N_wide & \
                         +self.s_reflWGate_S_wide & +self.s_reflWGate_top & -self.s_aboveCoreRoof & \
                         ( +self.s_reflWGate_S_thin | +self.s_reflWGateGrphWide_rear ) & \
                         ( -self.s_reflWGate_N_thin | +self.s_reflWGateGrphWide_rear )

    # Steel reflector liner and air gap on the outside surface of the reflector
    fill_material = self.mats['Air']
    region_name = 'Gap between permanent reflector and biological shielding'
    # Define the surfaces we'll need
    self.s_shieldI_N = openmc.YPlane(name='Biological shield inner N', y0= c.excoreRadialShieldHW_i)
    self.s_shieldI_S = openmc.YPlane(name='Biological shield inner S', y0=-c.excoreRadialShieldHW_i)
    self.s_shieldI_E = openmc.XPlane(name='Biological shield inner E', x0= c.excoreRadialShieldHW_i)
    self.s_shieldI_W = openmc.XPlane(name='Biological shield inner W', x0=-c.excoreRadialShieldHW_i)
    # Define the cells to hold the steel liner
    liner_mat = self.mats['Mild Steel']
    liner_region = +self.s_reflecFloor & -s_steel_liner_top
    above_region = +s_steel_liner_top & -self.s_aboveReflRoof
    # North
    self.c_steel_liner_N = openmc.Cell(name='North steel reflector liner', fill=liner_mat)
    north_region = +self.s_reflO_N & -s_steel_liner_N_o & \
                   +s_steel_liner_W_o & -s_steel_liner_E_o & \
                   +self.s_reflInstr_N_bot & +self.s_reflInstr_N_top
    self.c_steel_liner_N.region = north_region & liner_region
    self.c_steel_liner_above_N = openmc.Cell(name='Above the ' + self.c_steel_liner_N.name, fill=fill_material)
    self.c_steel_liner_above_N.region = north_region & above_region
    # South
    self.c_steel_liner_S = openmc.Cell(name='South steel reflector liner', fill=liner_mat)
    south_region = +s_steel_liner_S_o & -self.s_reflO_S & \
                   +s_steel_liner_W_o & -s_steel_liner_E_o & \
                   +self.s_reflInstr_S_bot & +self.s_reflInstr_S_top
    self.c_steel_liner_S.region = south_region & liner_region
    self.c_steel_liner_above_S = openmc.Cell(name='Above the ' + self.c_steel_liner_S.name, fill=fill_material)
    self.c_steel_liner_above_S.region = south_region & above_region
    # East
    self.c_steel_liner_E = openmc.Cell(name='East steel reflector liner', fill=liner_mat)
    east_region = +self.s_reflO_E & -s_steel_liner_E_o & \
                  +self.s_reflO_S & -self.s_reflO_N
    self.c_steel_liner_E.region = east_region & liner_region
    self.c_steel_liner_above_E = openmc.Cell(name='Above the ' + self.c_steel_liner_E.name, fill=fill_material)
    self.c_steel_liner_above_E.region = east_region & above_region
    # West
    self.c_steel_liner_W = openmc.Cell(name='West steel reflector liner', fill=liner_mat)
    west_region = +s_steel_liner_W_o & -self.s_reflO_W & \
                  +self.s_reflO_S & -self.s_reflO_N & \
                  +self.s_reflInstr_W_bot & +self.s_reflInstr_W_top
    self.c_steel_liner_W.region = west_region & liner_region
    self.c_steel_liner_above_W = openmc.Cell(name='Above the ' + self.c_steel_liner_W.name, fill=fill_material)
    self.c_steel_liner_above_W.region = west_region & above_region
    # Instrument tube cells (air)
    tube_mat = self.mats['Air']
    self.c_outer_instr_tube_top_N = openmc.Cell(name='North top instrument tube inside steel reflector liner',
                                                fill=tube_mat)
    self.c_outer_instr_tube_top_N.region = -self.s_reflInstr_N_top & \
                                           +self.s_reflO_N & -s_steel_liner_N_o
    self.c_outer_instr_tube_bot_N = openmc.Cell(name='North bottom instrument tube inside steel reflector liner',
                                                fill=tube_mat)
    self.c_outer_instr_tube_bot_N.region = -self.s_reflInstr_N_bot & \
                                           +self.s_reflO_N & -s_steel_liner_N_o

    self.c_outer_instr_tube_top_S = openmc.Cell(name='South top instrument tube inside steel reflector liner',
                                                fill=tube_mat)
    self.c_outer_instr_tube_top_S.region = -self.s_reflInstr_S_top & \
                                           +s_steel_liner_S_o & -self.s_reflO_S
    self.c_outer_instr_tube_bot_S = openmc.Cell(name='South bottom instrument tube inside steel reflector liner',
                                                fill=tube_mat)
    self.c_outer_instr_tube_bot_S.region = -self.s_reflInstr_S_bot & \
                                           +s_steel_liner_S_o & -self.s_reflO_S

    self.c_outer_instr_tube_top_W = openmc.Cell(name='West top instrument tube inside steel reflector liner',
                                                fill=tube_mat)
    self.c_outer_instr_tube_top_W.region = -self.s_reflInstr_W_top & \
                                           +s_steel_liner_W_o & -self.s_reflO_W
    self.c_outer_instr_tube_bot_W = openmc.Cell(name='West bottom instrument tube inside steel reflector liner',
                                                fill=tube_mat)
    self.c_outer_instr_tube_bot_W.region = -self.s_reflInstr_W_bot & \
                                           +s_steel_liner_W_o & -self.s_reflO_W
    # Window cells (air)
    window_mat = self.mats['Air']
    north_outer_window_region     = +s_outer_liner_N_window_W & -s_outer_liner_N_window_E & \
                                    +s_outer_liner_N_window_bot & -s_outer_liner_N_window_top
    north_outer_window_complement = -s_outer_liner_N_window_W | +s_outer_liner_N_window_E | \
                                    -s_outer_liner_N_window_bot | +s_outer_liner_N_window_top
    self.c_steel_liner_window_N = openmc.Cell(name="North window inside steel reflector liner",
                                              fill=window_mat)
    self.c_steel_liner_window_N.region = north_outer_window_region & \
                                         +self.s_reflO_N & -s_steel_liner_N_o
    self.c_steel_liner_N.region &= north_outer_window_complement

    south_outer_window_region =     +s_outer_liner_S_window_W & -s_outer_liner_S_window_E & \
                                    +s_outer_liner_WS_window_bot & -s_outer_liner_WS_window_top
    south_outer_window_complement = -s_outer_liner_S_window_W | +s_outer_liner_S_window_E | \
                                    -s_outer_liner_WS_window_bot | +s_outer_liner_WS_window_top
    self.c_steel_liner_window_S = openmc.Cell(name="South window inside steel reflector liner",
                                              fill=window_mat)
    self.c_steel_liner_window_S.region = south_outer_window_region & \
                                         +s_steel_liner_S_o & -self.s_reflO_S
    self.c_steel_liner_S.region &= south_outer_window_complement

    west_outer_window_region     = +s_outer_liner_W_window_S & -s_outer_liner_W_window_N & \
                                   +s_outer_liner_WS_window_bot & -s_outer_liner_WS_window_top
    west_outer_window_complement = -s_outer_liner_W_window_S | +s_outer_liner_W_window_N | \
                                   -s_outer_liner_WS_window_bot | +s_outer_liner_WS_window_top
    self.c_steel_liner_window_W = openmc.Cell(name="West window inside steel reflector liner",
                                              fill=window_mat)
    self.c_steel_liner_window_W.region = west_outer_window_region & \
                                         +s_steel_liner_W_o & -self.s_reflO_W
    self.c_steel_liner_W.region &= west_outer_window_complement

    east_outer_window_region     = +s_outer_liner_E_window_S & -s_outer_liner_E_window_N & \
                                   +s_outer_liner_E_window_bot & -s_outer_liner_E_window_top
    east_outer_window_complement = -s_outer_liner_E_window_S | +s_outer_liner_E_window_N | \
                                   -s_outer_liner_E_window_bot | +s_outer_liner_E_window_top
    self.c_steel_liner_window_E = openmc.Cell(name="East window inside steel reflector liner",
                                              fill=window_mat)
    self.c_steel_liner_window_E.region = east_outer_window_region & \
                                         +self.s_reflO_E & -s_steel_liner_E_o
    self.c_steel_liner_E.region &= east_outer_window_complement


    # Define the cells to hold the air
    self.c_reflAirGap_N = openmc.Cell(name=('N ' + region_name), fill=fill_material)
    self.c_reflAirGap_S = openmc.Cell(name=('S ' + region_name), fill=fill_material)
    self.c_reflAirGap_E = openmc.Cell(name=('E ' + region_name), fill=fill_material)
    self.c_reflAirGap_W = openmc.Cell(name=('W ' + region_name), fill=fill_material)
    self.c_reflAirGapLCon_N   = openmc.Cell(name='N concrete below the reflector outer air gap', fill=self.mats['Concrete'])
    self.c_reflAirGapLCon_S   = openmc.Cell(name='S concrete below the reflector outer air gap', fill=self.mats['Concrete'])
    self.c_reflAirGapLCon_E   = openmc.Cell(name='E concrete below the reflector outer air gap', fill=self.mats['Concrete'])
    self.c_reflAirGapLCon_W   = openmc.Cell(name='W concrete below the reflector outer air gap', fill=self.mats['Concrete'])
    self.c_reflAirGapUCon_N   = openmc.Cell(name='N concrete above the reflector outer air gap', fill=self.mats['Concrete'])
    self.c_reflAirGapUCon_S   = openmc.Cell(name='S concrete above the reflector outer air gap', fill=self.mats['Concrete'])
    self.c_reflAirGapUCon_E   = openmc.Cell(name='E concrete above the reflector outer air gap', fill=self.mats['Concrete'])
    self.c_reflAirGapUCon_W   = openmc.Cell(name='W concrete above the reflector outer air gap', fill=self.mats['Concrete'])
    # Go through and build the cells
    self.c_reflAirGap_N.region = +s_steel_liner_N_o & -self.s_shieldI_N & \
                                 +self.s_shieldI_W & -self.s_shieldI_E & \
                                 +self.s_reflecFloor & -self.s_aboveReflRoof
    self.c_reflAirGap_S.region = +self.s_shieldI_S & -s_steel_liner_S_o & \
                                 +self.s_shieldI_W & -self.s_shieldI_E & \
                                 +self.s_reflecFloor & -self.s_aboveReflRoof
    self.c_reflAirGap_E.region = +s_steel_liner_E_o & -self.s_shieldI_E & \
                                 +s_steel_liner_S_o & -s_steel_liner_N_o & \
                                 +self.s_reflecFloor & -self.s_aboveReflRoof
    self.c_reflAirGap_W.region = +self.s_shieldI_W & -s_steel_liner_W_o & \
                                 +s_steel_liner_S_o & -s_steel_liner_N_o & \
                                 +self.s_reflecFloor & -self.s_aboveReflRoof

    self.c_reflAirGapLCon_N.region = -self.s_shieldI_N & +self.s_reflO_N & -self.s_shieldI_E \
                                   & +self.s_shieldI_W & -self.s_reflecFloor & +self.s_lowerBound
    self.c_reflAirGapLCon_S.region = +self.s_shieldI_S & -self.s_reflO_S & -self.s_shieldI_E \
                                   & +self.s_shieldI_W & -self.s_reflecFloor & +self.s_lowerBound
    self.c_reflAirGapLCon_E.region = -self.s_reflO_N & +self.s_reflO_S & -self.s_shieldI_E \
                                   & +self.s_reflO_E & -self.s_reflecFloor & +self.s_lowerBound
    self.c_reflAirGapLCon_W.region = -self.s_reflO_N & +self.s_reflO_S & -self.s_reflO_W \
                                   & +self.s_shieldI_W & -self.s_reflecFloor & +self.s_lowerBound
    self.c_reflAirGapUCon_N.region = -self.s_shieldI_N & +self.s_reflO_N & -self.s_shieldI_E \
                                   & +self.s_shieldI_W & -self.s_upperBound & +self.s_aboveReflRoof
    self.c_reflAirGapUCon_S.region = +self.s_shieldI_S & -self.s_reflO_S & -self.s_shieldI_E \
                                   & +self.s_shieldI_W & -self.s_upperBound & +self.s_aboveReflRoof
    self.c_reflAirGapUCon_E.region = -self.s_reflO_N & +self.s_reflO_S & -self.s_shieldI_E \
                                   & +self.s_reflO_E & -self.s_upperBound & +self.s_aboveReflRoof
    self.c_reflAirGapUCon_W.region = -self.s_reflO_N & +self.s_reflO_S & -self.s_reflO_W \
                                   & +self.s_shieldI_W & -self.s_upperBound & +self.s_aboveReflRoof

  def _add_biological_shield(self):
    """ Adds the various cells that comprise the TREAT concrete biological shield """
    # Create the surfaces we will need for the main shield blocks
    self.s_shieldO_N = openmc.YPlane(name='Biological shield outer N', y0= c.excoreRadialShieldHW_o)
    self.s_shieldO_S = openmc.YPlane(name='Biological shield outer S', y0=-c.excoreRadialShieldHW_o)
    self.s_shieldO_E = openmc.XPlane(name='Biological shield outer E', x0= c.excoreRadialShieldHW_o)
    self.s_shieldO_W = openmc.XPlane(name='Biological shield outer W', x0=-c.excoreRadialShieldHW_o)
    self.s_shieldO_NE = openmc.Plane(name='Biological shield outer NE', A= 1, B=1, C=0, D= (math.sqrt(2.0)*c.shieldCornerDist))
    self.s_shieldO_NW = openmc.Plane(name='Biological shield outer NW', A=-1, B=1, C=0, D= (math.sqrt(2.0)*c.shieldCornerDist))
    self.s_shieldO_SE = openmc.Plane(name='Biological shield outer SE', A=-1, B=1, C=0, D=-(math.sqrt(2.0)*c.shieldCornerDist))
    self.s_shieldO_SW = openmc.Plane(name='Biological shield outer SW', A= 1, B=1, C=0, D=-(math.sqrt(2.0)*c.shieldCornerDist))

    # Create the surfaces for the eastern thermal column
    zSmallHW_top = c.struct_ThermColumnZorigin + c.excoreThermColumnSmallHW
    zSmallHW_bot = c.struct_ThermColumnZorigin - c.excoreThermColumnSmallHW
    zLargeHW_top = c.struct_ThermColumnZorigin + c.excoreThermColumnLargeHW
    zLargeHW_bot = c.struct_ThermColumnZorigin - c.excoreThermColumnLargeHW
    self.s_thermcol_inner_n = openmc.YPlane(name='East Thermal Column, inner half, N',
                                            y0=+c.excoreThermColumnSmallHW)
    self.s_thermcol_inner_s = openmc.YPlane(name='East Thermal Column, inner half, S',
                                            y0=-c.excoreThermColumnSmallHW)
    self.s_thermcol_inner_t = openmc.ZPlane(name='East Thermal Column, inner half, top',
                                            z0=zSmallHW_top)
    self.s_thermcol_inner_b = openmc.ZPlane(name='East Thermal Column, inner half, bot',
                                            z0=zSmallHW_bot)

    self.s_thermcol_outer_n = openmc.YPlane(name='East Thermal Column, outer half, N',
                                            y0=+c.excoreThermColumnLargeHW)
    self.s_thermcol_outer_s = openmc.YPlane(name='East Thermal Column, outer half, S',
                                            y0=-c.excoreThermColumnLargeHW)
    self.s_thermcol_outer_t = openmc.ZPlane(name='East Thermal Column, outer half, top',
                                            z0=zLargeHW_top)
    self.s_thermcol_outer_b = openmc.ZPlane(name='East Thermal Column, outer half, bot',
                                            z0=zLargeHW_bot)

    self.s_thermcol_middle = openmc.XPlane(name='East Thermal Column, midpoint',
                                           x0=c.excoreThermColumnMidpoint)

    # Create the main cells
    self.c_shield_N = openmc.Cell(name='N Biological Shield', fill=self.mats['Concrete'])
    self.c_shield_S = openmc.Cell(name='S Biological Shield', fill=self.mats['Concrete'])
    self.c_shield_E_inner = openmc.Cell(name='E Biological Shield, inner half', fill=self.mats['Concrete'])
    self.c_shield_E_outer = openmc.Cell(name='E Biological Shield, outer half', fill=self.mats['Concrete'])
    self.c_shield_W = openmc.Cell(name='W Biological Shield', fill=self.mats['Concrete'])
    self.c_shield_NE = openmc.Cell(name='NE Biological Shield', fill=self.mats['Concrete'])
    self.c_shield_NW = openmc.Cell(name='NW Biological Shield', fill=self.mats['Concrete'])
    self.c_shield_SE = openmc.Cell(name='SE Biological Shield', fill=self.mats['Concrete'])
    self.c_shield_SW = openmc.Cell(name='SW Biological Shield', fill=self.mats['Concrete'])
    self.c_shieldAir_NE = openmc.Cell(name='NE Air by Biological Shield', fill=self.mats['Air'])
    self.c_shieldAir_NW = openmc.Cell(name='NW Air by Biological Shield', fill=self.mats['Air'])
    self.c_shieldAir_SE = openmc.Cell(name='SE Air by Biological Shield', fill=self.mats['Air'])
    self.c_shieldAir_SW = openmc.Cell(name='SW Air by Biological Shield', fill=self.mats['Air'])
    # Thermal column cells (CP2 graphite)
    self.c_thermcol_inner = openmc.Cell(name='East Thermal Column inner half', fill=self.mats['Graphite'])
    self.c_thermcol_outer = openmc.Cell(name='East Thermal Column outer half', fill=self.mats['Graphite'])
    # Go through and build the cells
    self.c_thermcol_inner.region = +self.s_shieldI_E & -self.s_thermcol_middle & \
                                   +self.s_thermcol_inner_s & -self.s_thermcol_inner_n & \
                                   +self.s_thermcol_inner_b & -self.s_thermcol_inner_t
    self.c_thermcol_outer.region = +self.s_thermcol_middle & - self.s_shieldO_E & \
                                   +self.s_thermcol_outer_s & -self.s_thermcol_outer_n & \
                                   +self.s_thermcol_outer_b & -self.s_thermcol_outer_t
    # Shield cell regions
    self.c_shield_N.region = -self.s_shieldO_N & +self.s_shieldI_N & -self.s_shieldI_E \
                           & +self.s_shieldI_W & -self.s_upperBound & +self.s_lowerBound
    self.c_shield_S.region = +self.s_shieldO_S & -self.s_shieldI_S & -self.s_shieldI_E \
                           & +self.s_shieldI_W & -self.s_upperBound & +self.s_lowerBound
    self.c_shield_E_inner.region = -self.s_shieldI_N & +self.s_shieldI_S & -self.s_thermcol_middle & \
                                   +self.s_shieldI_E & -self.s_upperBound & +self.s_lowerBound & \
                                   ~self.c_thermcol_inner.region

    self.c_shield_E_outer.region = -self.s_shieldI_N & +self.s_shieldI_S & -self.s_shieldO_E & \
                                   +self.s_thermcol_middle & -self.s_upperBound & +self.s_lowerBound & \
                                   ~self.c_thermcol_outer.region

    self.c_shield_W.region = -self.s_shieldI_N & +self.s_shieldI_S & -self.s_shieldI_W \
                           & +self.s_shieldO_W & -self.s_upperBound & +self.s_lowerBound
    self.c_shield_NE.region = -self.s_shieldO_N & +self.s_shieldI_N & +self.s_shieldI_E & -self.s_shieldO_NE \
                            & -self.s_shieldO_E & -self.s_upperBound & +self.s_lowerBound
    self.c_shield_NW.region = +self.s_shieldI_N & -self.s_shieldO_N & -self.s_shieldI_W & -self.s_shieldO_NW \
                            & +self.s_shieldO_W & -self.s_upperBound & +self.s_lowerBound
    self.c_shield_SE.region = -self.s_shieldI_S & +self.s_shieldO_S & -self.s_shieldO_E & +self.s_shieldO_SE \
                            & +self.s_shieldI_E & -self.s_upperBound & +self.s_lowerBound
    self.c_shield_SW.region = -self.s_shieldI_S & +self.s_shieldO_S & -self.s_shieldI_W & +self.s_shieldO_SW \
                            & +self.s_shieldO_W & -self.s_upperBound & +self.s_lowerBound
    self.c_shieldAir_NE.region = -self.s_shieldO_N & +self.s_shieldO_NE & -self.s_shieldO_E & -self.s_upperBound & +self.s_lowerBound
    self.c_shieldAir_NW.region = -self.s_shieldO_N & +self.s_shieldO_NW & +self.s_shieldO_W & -self.s_upperBound & +self.s_lowerBound
    self.c_shieldAir_SE.region = +self.s_shieldO_S & -self.s_shieldO_E & -self.s_shieldO_SE & -self.s_upperBound & +self.s_lowerBound
    self.c_shieldAir_SW.region = +self.s_shieldO_S & -self.s_shieldO_SW & +self.s_shieldO_W & -self.s_upperBound & +self.s_lowerBound

  def _add_outer_universe(self):
    """ Adds TREAT air between the end of the excore contents and the vacuum boundaries """

    # Bounding radial vacuum surfaces

    fill_material = self.mats['Air']
    region_name = 'Outer Region'
    # Define the surfaces we'll need
    self.s_radialBound_N = openmc.YPlane(name='N Radial Universe Bound', y0= (c.excoreOuter+c.latticePitch), boundary_type='vacuum')
    self.s_radialBound_S = openmc.YPlane(name='S Radial Universe Bound', y0=-(c.excoreOuter+c.latticePitch), boundary_type='vacuum')
    self.s_radialBound_E = openmc.XPlane(name='E Radial Universe Bound', x0= (c.excoreOuter+c.latticePitch), boundary_type='vacuum')
    self.s_radialBound_W = openmc.XPlane(name='W Radial Universe Bound', x0=-(c.excoreOuter+c.latticePitch), boundary_type='vacuum')
    # Define the cells to hold the air for anything that we haven't assigned yet
    self.c_outerRegion_N = openmc.Cell(name=('N ' + region_name), fill=fill_material)
    self.c_outerRegion_S = openmc.Cell(name=('S ' + region_name), fill=fill_material)
    self.c_outerRegion_E = openmc.Cell(name=('E ' + region_name), fill=fill_material)
    self.c_outerRegion_W = openmc.Cell(name=('W ' + region_name), fill=fill_material)
    # Create the surfaces that will define where the ex-core content ends
    self.s_exCoreBound_N = openmc.YPlane(name='N ex core content boundary', y0= c.excoreOuter)
    self.s_exCoreBound_S = openmc.YPlane(name='S ex core content boundary', y0=-c.excoreOuter)
    self.s_exCoreBound_E = openmc.XPlane(name='E ex core content boundary', x0= c.excoreOuter)
    self.s_exCoreBound_W = openmc.XPlane(name='W ex core content boundary', x0=-c.excoreOuter)
    # Go through and construct the cells
    # North subcell
    self.c_outerRegion_N.region  = -self.s_radialBound_N # North face - outer dim
    self.c_outerRegion_N.region &= +self.s_exCoreBound_N # South face - inner dim
    self.c_outerRegion_N.region &= -self.s_exCoreBound_E # East face - inner dim
    self.c_outerRegion_N.region &= +self.s_exCoreBound_W # West face - inner dim
    self.c_outerRegion_N.region &= -self.s_upperBound # Top
    self.c_outerRegion_N.region &= +self.s_lowerBound # Bottom
    # South Subcell
    self.c_outerRegion_S.region  = -self.s_exCoreBound_S # North face - inner dim
    self.c_outerRegion_S.region &= +self.s_radialBound_S # South face - outer dim
    self.c_outerRegion_S.region &= -self.s_radialBound_E # East face - outer dim
    self.c_outerRegion_S.region &= +self.s_radialBound_W # West face - outer dim
    self.c_outerRegion_S.region &= -self.s_upperBound # Top
    self.c_outerRegion_S.region &= +self.s_lowerBound # Bottom
    # East Subcell
    self.c_outerRegion_E.region  = -self.s_radialBound_N # North face - outer dim
    self.c_outerRegion_E.region &= +self.s_exCoreBound_S # South face - inner dim
    self.c_outerRegion_E.region &= -self.s_radialBound_E # East face - outer dim
    self.c_outerRegion_E.region &= +self.s_exCoreBound_E # West face - inner dim
    self.c_outerRegion_E.region &= -self.s_upperBound # Top
    self.c_outerRegion_E.region &= +self.s_lowerBound # Bottom
    # West Subcell
    self.c_outerRegion_W.region  = -self.s_radialBound_N # North face - outer dim
    self.c_outerRegion_W.region &= +self.s_exCoreBound_S # South face - inner dim
    self.c_outerRegion_W.region &= -self.s_exCoreBound_W # East face - inner dim
    self.c_outerRegion_W.region &= +self.s_radialBound_W # West face - outer dim
    self.c_outerRegion_W.region &= -self.s_upperBound # Top
    self.c_outerRegion_W.region &= +self.s_lowerBound # Bottom

  def _add_core(self):
    """ Adds TREAT single fuel element """

    # Core lattice

    self.c_core = openmc.Cell(name="Full core element lattice", fill=self.core.u_coreLattice)
    self.c_core.region  = -self.s_coreBound_N # North face
    self.c_core.region &= +self.s_coreBound_S # South face
    self.c_core.region &= -self.s_coreBound_E # East face
    self.c_core.region &= +self.s_coreBound_W # West face
    self.c_core.region &= -self.s_aboveCoreRoof
    self.c_core.region &= +self.s_belowCoreFloor


    # If we have an experiment vessel to include, cut out that part of the core lattice
    if self.core.has_experiment:
      self.c_expVessel = openmc.Cell(name="Experiment vessel", fill=self.core.vessel.u_vessel)
      self.c_expVessel.region = self.core.r_experiment
      self.c_core.region &= ~self.core.r_experiment

    # Cells above and below

    # Surfaces for the top plug assembly
    s_plug_cyl = openmc.ZCylinder(name='Top plug outer radius', R=c.excoreTopPlugRadius)
    s_plug_slotN = openmc.YPlane(name='Top plug slot, N', y0=+c.excoreTopPlugSlotHW)
    s_plug_slotS = openmc.YPlane(name='Top plug slot, S', y0=-c.excoreTopPlugSlotHW)
    s_plug_slotE = openmc.XPlane(name='Top plug slot, E', x0=c.excoreTopPlugShortEdge)
    s_plug_lower_boral_top = openmc.ZPlane(name='Top plug, lower boral top', z0=c.struct_excore_lower_boral_top)
    s_plug_steel_top = openmc.ZPlane(name='Top plug, steel layer, top', z0=c.struct_excore_steel_top)
    s_plug_upper_boral_top = openmc.ZPlane(name='Top plug, upper boral top', z0=c.struct_excore_upper_boral_top)
    s_plug_top = openmc.ZPlane(name='Top plug, top', z0=c.struct_excore_plug_top)
    slot_region = -s_plug_cyl &  +s_plug_slotS & -s_plug_slotN & -s_plug_slotE
    plug_region = -s_plug_cyl & (-s_plug_slotS | +s_plug_slotN | +s_plug_slotE)
    # Cells for the top plug assembly
    self.c_plug_lower_boral = openmc.Cell(name='Top plug, lower boral layer', fill=self.mats["Boral"])
    self.c_plug_lower_boral.region = plug_region & +self.s_aboveCoreRoof & -s_plug_lower_boral_top
    self.c_plug_steel = openmc.Cell(name='Top plug, steel layer', fill=self.mats["Mild Steel"])
    self.c_plug_steel.region = plug_region & +s_plug_lower_boral_top & -s_plug_steel_top
    self.c_plug_upper_boral = openmc.Cell(name='Top plug, upper boral layer', fill=self.mats["Boral"])
    self.c_plug_upper_boral.region = plug_region & +s_plug_steel_top & -s_plug_upper_boral_top
    self.c_plug_checker_plate = openmc.Cell(name='Top plug, steel checker plate', fill=self.mats["Mild Steel"])
    self.c_plug_checker_plate.region = plug_region & +s_plug_upper_boral_top & -s_plug_top
    self.c_plug_slot = openmc.Cell(name='Top plug, slot', fill=self.mats["Boron Steel"])
    self.c_plug_slot.region = slot_region & +self.s_aboveCoreRoof & -s_plug_top

    # The core
    self.c_coreFloor = openmc.Cell(name="Concrete floor beneath the core", fill=self.mats['Concrete'])
    self.c_coreFloor.region = -self.s_coreBound_N & +self.s_coreBound_S & -self.s_coreBound_E & +self.s_coreBound_W \
                            & +self.s_lowerBound & -self.s_belowCoreFloor
    self.c_lower_coreRoof = openmc.Cell(name="Concrete roof above the core", fill=self.mats['Concrete'])
    self.c_lower_coreRoof.region = -self.s_reflO_N & +self.s_reflO_S & -self.s_reflO_E & +self.s_reflO_W \
                                   & +self.s_aboveCoreRoof & -s_plug_top & +s_plug_cyl
    self.c_upper_coreRoof = openmc.Cell(name="Concrete roof above the core", fill=self.mats['Concrete'])
    self.c_upper_coreRoof.region = -self.s_reflO_N & +self.s_reflO_S & -self.s_reflO_E & +self.s_reflO_W \
                                   & +s_plug_top & -self.s_upperBound


  def _create_main_universe(self):
    """ Creates the main TREAT infinite lattice universe """

    # Add the core itself
    self.add_cell(self.c_core)
    if self.core.has_experiment:
      self.add_cell(self.c_expVessel)
    # Add core associated cells
    self.add_cells((self.c_coreFloor, self.c_lower_coreRoof, self.c_upper_coreRoof))
    self.add_cells((self.c_plug_lower_boral, self.c_plug_steel, self.c_plug_upper_boral,
                    self.c_plug_checker_plate, self.c_plug_slot))
    # Outer universe
    self.add_cell(self.c_outerRegion_N)
    self.add_cell(self.c_outerRegion_S)
    self.add_cell(self.c_outerRegion_E)
    self.add_cell(self.c_outerRegion_W)
    # Air gap between the core and the inner aluminum liner
    self.add_cell(self.c_coreAirGap_N)
    self.add_cell(self.c_coreAirGap_S)
    self.add_cell(self.c_coreAirGap_E)
    self.add_cell(self.c_coreAirGap_W)
    # Inner aluminum liner
    self.add_cell(self.c_coreLinerUAir_N)
    self.add_cell(self.c_coreLinerLCon_N)
    self.add_cell(self.c_coreLinerUAir_S)
    self.add_cell(self.c_coreLinerLCon_S)
    self.add_cell(self.c_coreLinerUAir_E)
    self.add_cell(self.c_coreLinerLCon_E)
    self.add_cell(self.c_coreLinerUAir_W)
    self.add_cell(self.c_coreLinerLCon_W)
    self.add_cell(self.c_coreLinerN_E)
    self.add_cell(self.c_coreLinerN_W)
    self.add_cell(self.c_coreLinerN_top)
    self.add_cell(self.c_coreLinerN_bot)
    self.add_cell(self.c_coreLinerN_win)
    self.add_cell(self.c_coreLinerS_E)
    self.add_cell(self.c_coreLinerS_W)
    self.add_cell(self.c_coreLinerS_top)
    self.add_cell(self.c_coreLinerS_bot)
    self.add_cell(self.c_coreLinerS_win)
    self.add_cell(self.c_coreLinerE_N)
    self.add_cell(self.c_coreLinerE_S)
    self.add_cell(self.c_coreLinerE_top)
    self.add_cell(self.c_coreLinerE_bot)
    self.add_cell(self.c_coreLinerE_win)
    self.add_cell(self.c_coreLinerW_N)
    self.add_cell(self.c_coreLinerW_S)
    self.add_cell(self.c_coreLinerW_top)
    self.add_cell(self.c_coreLinerW_bot)
    self.add_cell(self.c_coreLinerW_win)
    # Outer steel liner
    self.add_cells((self.c_steel_liner_N, self.c_steel_liner_S, self.c_steel_liner_E, self.c_steel_liner_W))
    self.add_cells((self.c_steel_liner_above_N, self.c_steel_liner_above_S,
                    self.c_steel_liner_above_E, self.c_steel_liner_above_W))
    self.add_cells((self.c_outer_instr_tube_top_N, self.c_outer_instr_tube_bot_N,
                    self.c_outer_instr_tube_top_S, self.c_outer_instr_tube_bot_S,
                    self.c_outer_instr_tube_top_W, self.c_outer_instr_tube_bot_W))
    self.add_cells((self.c_steel_liner_window_N, self.c_steel_liner_window_S,
                    self.c_steel_liner_window_E, self.c_steel_liner_window_W))
    # Permanent Reflector Cells
    self.add_cell(self.c_coreReflUAir_NNE)
    self.add_cell(self.c_coreReflUAir_NNW)
    self.add_cell(self.c_coreReflLCon_N)
    self.add_cell(self.c_coreReflUAir_SSE)
    self.add_cell(self.c_coreReflUAir_SSW)
    self.add_cell(self.c_coreReflLCon_S)
    self.add_cell(self.c_coreReflUAir_E)
    self.add_cell(self.c_coreReflLCon_E)
    self.add_cell(self.c_coreReflUAir_WNW)
    self.add_cell(self.c_coreReflUAir_WSW)
    self.add_cell(self.c_coreReflLCon_W)
    self.add_cells((self.c_coreReflUCon_NNE, self.c_coreReflUCon_NNW, self.c_coreReflUCon_SSE, self.c_coreReflUCon_SSW, \
                    self.c_coreReflUCon_E, self.c_coreReflUCon_WNW, self.c_coreReflUCon_WSW))
    self.add_cell(self.c_coreRefl_NE)
    self.add_cell(self.c_coreRefl_NW)
    self.add_cell(self.c_coreRefl_SE)
    self.add_cell(self.c_coreRefl_SW)
    self.add_cell(self.c_coreRefl_E_i)
    self.add_cell(self.c_coreRefl_E_o)
    self.add_cells((self.c_coreReflTP_E_i_FN_bot,self.c_coreReflTP_E_o_FN_bot,self.c_coreReflTP_E_i_FN_mid, \
                    self.c_coreReflTP_E_o_FN_mid,self.c_coreReflTP_E_i_FN_top,self.c_coreReflTP_E_o_FN_top, \
                    self.c_coreReflTP_E_i_FS_bot,self.c_coreReflTP_E_o_FS_bot,self.c_coreReflTP_E_i_FS_mid, \
                    self.c_coreReflTP_E_o_FS_mid,self.c_coreReflTP_E_i_FS_top,self.c_coreReflTP_E_o_FS_top, \
                    self.c_coreReflTP_E_i_CN_bot,self.c_coreReflTP_E_o_CN_bot,self.c_coreReflTP_E_i_CN_top, \
                    self.c_coreReflTP_E_o_CN_top,self.c_coreReflTP_E_i_CS_bot,self.c_coreReflTP_E_o_CS_bot, \
                    self.c_coreReflTP_E_i_CS_top,self.c_coreReflTP_E_o_CS_top))
    self.add_cell(self.c_coreRefl_N_i_E)
    self.add_cell(self.c_coreRefl_N_o_E)
    self.add_cell(self.c_coreRefl_N_i_W)
    self.add_cell(self.c_coreRefl_N_o_W)
    self.add_cells((self.c_coreReflTP_N_i_FE_bot,self.c_coreReflTP_N_o_FE_bot,self.c_coreReflTP_N_i_FE_mid, \
                    self.c_coreReflTP_N_o_FE_mid,self.c_coreReflTP_N_i_FE_top,self.c_coreReflTP_N_o_FE_top, \
                    self.c_coreReflTP_N_i_FW_bot,self.c_coreReflTP_N_o_FW_bot,self.c_coreReflTP_N_i_FW_mid, \
                    self.c_coreReflTP_N_o_FW_mid,self.c_coreReflTP_N_i_FW_top,self.c_coreReflTP_N_o_FW_top, \
                    self.c_coreReflTP_N_i_CE_bot,self.c_coreReflTP_N_o_CE_bot,self.c_coreReflTP_N_i_CE_mid, \
                    self.c_coreReflTP_N_o_CE_mid,self.c_coreReflTP_N_i_CE_top,self.c_coreReflTP_N_o_CE_top, \
                    self.c_coreReflTP_N_i_CW_bot,self.c_coreReflTP_N_o_CW_bot,self.c_coreReflTP_N_i_CW_mid, \
                    self.c_coreReflTP_N_o_CW_mid,self.c_coreReflTP_N_i_CW_top,self.c_coreReflTP_N_o_CW_top))
    self.add_cells((self.c_coreReflInstr_N_bot, self.c_coreReflInstr_N_top))
    self.add_cell(self.c_coreRefl_S_i_E)
    self.add_cell(self.c_coreRefl_S_o_E)
    self.add_cell(self.c_coreRefl_S_i_W)
    self.add_cell(self.c_coreRefl_S_o_W)
    self.add_cells((self.c_coreReflTP_S_i_FE_bot,self.c_coreReflTP_S_o_FE_bot,self.c_coreReflTP_S_i_FE_mid, \
                    self.c_coreReflTP_S_o_FE_mid,self.c_coreReflTP_S_i_FE_top,self.c_coreReflTP_S_o_FE_top, \
                    self.c_coreReflTP_S_i_FW_bot,self.c_coreReflTP_S_o_FW_bot,self.c_coreReflTP_S_i_FW_mid, \
                    self.c_coreReflTP_S_o_FW_mid,self.c_coreReflTP_S_i_FW_top,self.c_coreReflTP_S_o_FW_top, \
                    self.c_coreReflTP_S_i_CE_bot,self.c_coreReflTP_S_o_CE_bot,self.c_coreReflTP_S_i_CE_mid, \
                    self.c_coreReflTP_S_o_CE_mid,self.c_coreReflTP_S_i_CE_top,self.c_coreReflTP_S_o_CE_top, \
                    self.c_coreReflTP_S_i_CW_bot,self.c_coreReflTP_S_o_CW_bot,self.c_coreReflTP_S_i_CW_mid, \
                    self.c_coreReflTP_S_o_CW_mid,self.c_coreReflTP_S_i_CW_top,self.c_coreReflTP_S_o_CW_top))
    self.add_cells((self.c_coreReflInstr_S_bot, self.c_coreReflInstr_S_top))
    self.add_cell(self.c_coreRefl_W_i_N)
    self.add_cell(self.c_coreRefl_W_o_N)
    self.add_cell(self.c_coreRefl_W_i_S)
    self.add_cell(self.c_coreRefl_W_o_S)
    self.add_cells((self.c_coreReflTP_W_i_FN_bot,self.c_coreReflTP_W_o_FN_bot,self.c_coreReflTP_W_i_FN_mid, \
                    self.c_coreReflTP_W_o_FN_mid,self.c_coreReflTP_W_i_FN_top,self.c_coreReflTP_W_o_FN_top, \
                    self.c_coreReflTP_W_i_FS_bot,self.c_coreReflTP_W_o_FS_bot,self.c_coreReflTP_W_i_FS_mid, \
                    self.c_coreReflTP_W_o_FS_mid,self.c_coreReflTP_W_i_FS_top,self.c_coreReflTP_W_o_FS_top, \
                    self.c_coreReflTP_W_i_CN_bot,self.c_coreReflTP_W_o_CN_bot,self.c_coreReflTP_W_i_CN_mid, \
                    self.c_coreReflTP_W_o_CN_mid,self.c_coreReflTP_W_i_CN_top,self.c_coreReflTP_W_o_CN_top, \
                    self.c_coreReflTP_W_i_CS_bot,self.c_coreReflTP_W_o_CS_bot,self.c_coreReflTP_W_i_CS_mid, \
                    self.c_coreReflTP_W_o_CS_mid,self.c_coreReflTP_W_i_CS_top,self.c_coreReflTP_W_o_CS_top))
    self.add_cells((self.c_coreReflInstr_W_bot, self.c_coreReflInstr_W_top))
    self.add_cells((self.c_coreReflGate_N_bot, self.c_coreReflGate_S_bot, self.c_coreReflGate_W_bot))
    self.add_cells((self.c_coreReflGateAirStat_N_top, self.c_coreReflGateAirStat_S_top, self.c_coreReflGateAirStat_W_top))
    self.add_cells((self.c_coreReflGateCon_N_top, self.c_coreReflGateCon_S_top, self.c_coreReflGateCon_W_top))
    self.add_cells((self.c_coreReflGateGrph_N_rear, self.c_coreReflGateGrph_S_rear, self.c_coreReflGateGrph_W_rear))
    self.add_cells((self.c_coreReflGateLiner_N_rear, self.c_coreReflGateLiner_S_rear, self.c_coreReflGateLiner_W_rear))
    self.add_cells((self.c_coreReflGateAir_N_rear, self.c_coreReflGateAir_S_rear, self.c_coreReflGateAir_W_rear))
    self.add_cells((self.c_coreReflGateLiner_N_back, self.c_coreReflGateLiner_S_back, self.c_coreReflGateLiner_W_back, \
                    self.c_coreReflGateLiner_N_E, self.c_coreReflGateLiner_S_E, self.c_coreReflGateLiner_W_N, \
                    self.c_coreReflGateLiner_N_W, self.c_coreReflGateLiner_S_W, self.c_coreReflGateLiner_W_S, \
                    self.c_coreReflGateLiner_N_top, self.c_coreReflGateLiner_S_top, self.c_coreReflGateLiner_W_top))
    self.add_cells((self.c_coreReflGateAir_N, self.c_coreReflGateAir_S, self.c_coreReflGateAir_W))
    if self.core.NBlockPos > 0.0: # The north gate is open
      self.add_cell(self.c_coreReflGateAir_N_bot)
    if self.core.SBlockPos > 0.0: # The south gate is open
      self.add_cell(self.c_coreReflGateAir_S_bot)
    if self.core.WBlockPos > 0.0: # The west gate is open
      self.add_cell(self.c_coreReflGateAir_W_bot)
    self.add_cells((self.c_coreReflGate_N, self.c_coreReflGate_S, self.c_coreReflGate_W))
    self.add_cells((self.c_coreReflGateAir_N_top, self.c_coreReflGateAir_S_top, self.c_coreReflGateAir_W_top))
    # Air gap between the permanent reflector and the outer biological shielding
    self.add_cells((self.c_reflAirGap_N, self.c_reflAirGap_E, self.c_reflAirGap_S, self.c_reflAirGap_W,
                    self.c_reflAirGapLCon_N, self.c_reflAirGapLCon_E, self.c_reflAirGapLCon_S, self.c_reflAirGapLCon_W,
                    self.c_reflAirGapUCon_N, self.c_reflAirGapUCon_E, self.c_reflAirGapUCon_S, self.c_reflAirGapUCon_W))
    # Main excore shield blocks
    self.add_cells((self.c_shield_N, self.c_shield_S, self.c_shield_W, self.c_shield_NE, self.c_shield_NW,
                    self.c_shield_E_inner, self.c_shield_E_outer, self.c_thermcol_inner, self.c_thermcol_outer,
                    self.c_shield_SE, self.c_shield_SW, self.c_shieldAir_NE, self.c_shieldAir_NW, self.c_shieldAir_SE,
                    self.c_shieldAir_SW))




