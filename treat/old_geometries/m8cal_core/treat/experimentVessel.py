"""experimentVessel.py

Provides a container class for TREAT M8Cal experiment vessel

"""

import common_files.treat.constants as c
import openmc
import math

class ExperimentVessel(object):

  def __init__(self, mats):
    """ Initial setup """
    
    self.mats = mats

    self._build_vessel()
    
  def _build_vessel(self):
    # Goes through and actually creates the thing
    """ Creates the TREAT M8Cal experiment vessel universes """

    # Create some surfaces that will be needed
    # Axial
    self.s_univUpperBound = openmc.ZPlane(name='M8Cal Vessel universe upper bound', z0= c.struct_UpperCoreAir_top)
    self.s_univLowerBound = openmc.ZPlane(name='M8Cal Vessel universe lower bound', z0= c.struct_CoreFloor_top)
    self.s_gridPlate_bot = openmc.ZPlane(name='M8Cal Vessel grid plate bottom', z0= c.struct_CoreGuide_top)
    self.s_gridPlate_top = openmc.ZPlane(name='M8Cal Vessel grid plate top', z0= c.struct_CoreGridPlate_top)
    self.s_bottomTkDys_bot = openmc.ZPlane(name='M8Cal Vessel lower thick dysprosium bottom', z0= c.struct_m8_dysThick_bot)
    self.s_bottomMedDys_bot = openmc.ZPlane(name='M8Cal Vessel lower medium dysprosium bottom', z0= c.struct_m8_dysMid_bot)
    self.s_bottomTnDys_bot = openmc.ZPlane(name='M8Cal Vessel lower thin dysprosium bottom', z0= c.struct_m8_dysThin_bot)
    self.s_bottomTkDys_top = openmc.ZPlane(name='M8Cal Vessel upper thick dysprosium top', z0= c.struct_m8_dysThick_top)
    self.s_bottomMedDys_top = openmc.ZPlane(name='M8Cal Vessel upper medium dysprosium top', z0= c.struct_m8_dysMid_top)
    self.s_bottomTnDys_top = openmc.ZPlane(name='M8Cal Vessel upper thin dysprosium top', z0= c.struct_m8_dysThin_top)
    self.s_bottomSSDys_bot = openmc.ZPlane(name='M8Cal Vessel dysprosium steel bottom', z0= c.struct_m8_dysBare_bot)
    self.s_bottomSSDys_top = openmc.ZPlane(name='M8Cal Vessel dysprosium steel top', z0= c.struct_m8_dysBare_top)
    self.s_pinBotFitt_bot = openmc.ZPlane(name='M8Cal Vessel experiment fuel pin bottom fitting bottom', \
                                          z0= c.struct_m8_fuelBottomFitting_bot)
    self.s_pinFuel_bot = openmc.ZPlane(name='M8Cal Vessel experiment fuel pin bottom', z0= c.struct_m8_fuelPin_bot)
    self.s_pinFuel_top = openmc.ZPlane(name='M8Cal Vessel experiment fuel pin top', z0= c.struct_m8_fuelPin_top)
    self.s_pinNa_top = openmc.ZPlane(name='M8Cal Vessel experiment fuel pin extra sodium top', z0= c.struct_m8_fuelNa_top)
    self.s_pinPlenum_top = openmc.ZPlane(name='M8Cal Vessel experiment fuel pin plenum top', z0= c.struct_m8_fuelPlenum_top)
    self.s_pinTopFitt_top = openmc.ZPlane(name='M8Cal Vessel experiment fuel pin top fitting top', z0= c.struct_m8_fuelTopFitting_top)
    # Radial
    self.s_dummyOrigin_Y = openmc.YPlane(name='M8Cal Vessel Dummy Y plane', y0= 0.0)
    self.s_boundOuter_N = openmc.YPlane(name='M8Cal Vessel universe bound N', y0= c.latticePitch)
    self.s_boundOuter_S = openmc.YPlane(name='M8Cal Vessel universe bound S', y0=-c.latticePitch)
    self.s_boundOuter_E = openmc.XPlane(name='M8Cal Vessel universe bound E', x0= c.latticePitch/2.0)
    self.s_boundOuter_W = openmc.XPlane(name='M8Cal Vessel universe bound W', x0=-c.latticePitch/2.0)
    self.s_canOuter_N = openmc.YPlane(name='M8Cal Vessel Octagonal can outer N', y0= c.m8_can_longHW_o)
    self.s_canOuter_S = openmc.YPlane(name='M8Cal Vessel Octagonal can outer S', y0=-c.m8_can_longHW_o)
    self.s_canOuter_E = openmc.XPlane(name='M8Cal Vessel Octagonal can outer E', x0= c.m8_can_shortHW_o)
    self.s_canOuter_W = openmc.XPlane(name='M8Cal Vessel Octagonal can outer W', x0=-c.m8_can_shortHW_o)
    self.s_canInner_N = openmc.YPlane(name='M8Cal Vessel Octagonal can inner N', y0= c.m8_can_longHW_i)
    self.s_canInner_S = openmc.YPlane(name='M8Cal Vessel Octagonal can inner S', y0=-c.m8_can_longHW_i)
    self.s_canInner_E = openmc.XPlane(name='M8Cal Vessel Octagonal can inner E', x0= c.m8_can_shortHW_i)
    self.s_canInner_W = openmc.XPlane(name='M8Cal Vessel Octagonal can inner W', x0=-c.m8_can_shortHW_i)
    outerSurfDist = (c.m8_can_longHW_o + (c.m8_can_shortHW_o - c.m8_can_chamf_OW / math.sqrt(2.0))) / math.sqrt(2.0)
    innerSurfDist = outerSurfDist - c.m8_can_thickness
    self.s_canOuter_NE = openmc.Plane(name='M8Cal Vessel Octagonal can outer NE', A= 1, B=1, C=0, D= math.sqrt(2.0)*outerSurfDist)
    self.s_canOuter_NW = openmc.Plane(name='M8Cal Vessel Octagonal can outer NW', A=-1, B=1, C=0, D= math.sqrt(2.0)*outerSurfDist)
    self.s_canOuter_SE = openmc.Plane(name='M8Cal Vessel Octagonal can outer SE', A=-1, B=1, C=0, D=-math.sqrt(2.0)*outerSurfDist)
    self.s_canOuter_SW = openmc.Plane(name='M8Cal Vessel Octagonal can outer SW', A= 1, B=1, C=0, D=-math.sqrt(2.0)*outerSurfDist)
    self.s_canInner_NE = openmc.Plane(name='M8Cal Vessel Octagonal can inner NE', A= 1, B=1, C=0, D= math.sqrt(2.0)*innerSurfDist)
    self.s_canInner_NW = openmc.Plane(name='M8Cal Vessel Octagonal can inner NW', A=-1, B=1, C=0, D= math.sqrt(2.0)*innerSurfDist)
    self.s_canInner_SE = openmc.Plane(name='M8Cal Vessel Octagonal can inner SE', A=-1, B=1, C=0, D=-math.sqrt(2.0)*innerSurfDist)
    self.s_canInner_SW = openmc.Plane(name='M8Cal Vessel Octagonal can inner SW', A= 1, B=1, C=0, D=-math.sqrt(2.0)*innerSurfDist)
    self.s_canOuter_R = openmc.ZCylinder(name='M8Cal Vessel Circular can outer R', R= c.m8_can_circR_o)
    self.s_canInner_R = openmc.ZCylinder(name='M8Cal Vessel Circular can inner R', R= c.m8_can_circR_i)
    self.s_expDumHeat_OR = openmc.ZCylinder(name='M8Cal Experiment Dummy Heater outer R', R= c.m8_test_dummy_OR, y0=c.latticePitch/2.0)
    # TODO: Wasn't able to find dimensions or positions for the pump leg so guessed / approximated
    self.s_expLegMetal_OR = openmc.ZCylinder(name='M8Cal pump leg metal outer R', R= c.m8_test_calTest_IR, y0=-c.latticePitch/2.0)
    self.s_expLegMetal_IR = openmc.ZCylinder(name='M8Cal pump leg metal inner R', R= c.m8_test_calTrain_IR, y0=-c.latticePitch/2.0)
    #
    self.s_expTkDys_OR = openmc.ZCylinder(name='M8Cal Experiment Thick Dysprosium outer R', R= c.m8_test_largeDys_OR, \
                         y0=c.latticePitch/2.0)
    self.s_expMedDys_OR = openmc.ZCylinder(name='M8Cal Experiment Medium Dysprosium outer R', R= c.m8_test_middleDys_OR, \
                          y0=c.latticePitch/2.0)
    self.s_expTnDys_OR = openmc.ZCylinder(name='M8Cal Experiment Thin Dysprosium outer R', R= c.m8_test_smallDys_OR, \
                         y0=c.latticePitch/2.0)
    self.s_expSSSleeve_OR = openmc.ZCylinder(name='M8Cal Experiment Stainless Steel sleeve outer R', R= c.m8_test_ssSleeve_OR, \
                         y0=c.latticePitch/2.0)
    self.s_expAlSleeve_OR = openmc.ZCylinder(name='M8Cal Experiment Aluminum sleeve outer R', R= c.m8_test_AlSleeve_OR, \
                         y0=c.latticePitch/2.0)
    self.s_expSSCalib_OR = openmc.ZCylinder(name='M8Cal Experiment stainless steel calibration loop outer R', R= c.m8_test_calTest_OR, \
                         y0=c.latticePitch/2.0)
    self.s_expSSCalib_IR = openmc.ZCylinder(name='M8Cal Experiment stainless steel calibration loop inner R', R= c.m8_test_calTest_IR, \
                         y0=c.latticePitch/2.0)
    self.s_expSSTest_OR = openmc.ZCylinder(name='M8Cal Experiment stainless steel calibration test outer R', R= c.m8_test_calTrain_OR, \
                         y0=c.latticePitch/2.0)
    self.s_expSSTest_IR = openmc.ZCylinder(name='M8Cal Experiment stainless steel calibration test inner R', R= c.m8_test_calTrain_IR, \
                         y0=c.latticePitch/2.0)
    self.s_fuelFlowE_OR = openmc.ZCylinder(name='M8Cal Experiment Eastern fuel pin flow tube Outer R', R= c.m8_fuel_flowTube_OR, \
                         y0=c.latticePitch/2.0, x0= c.m8_fuel_pin_dist)
    self.s_fuelFlowW_OR = openmc.ZCylinder(name='M8Cal Experiment Western fuel pin flow tube Outer R', R= c.m8_fuel_flowTube_OR, \
                         y0=c.latticePitch/2.0, x0=-c.m8_fuel_pin_dist)
    self.s_fuelFlowE_IR = openmc.ZCylinder(name='M8Cal Experiment Eastern fuel pin flow tube Inner R', R= c.m8_fuel_flowTube_IR, \
                         y0=c.latticePitch/2.0, x0= c.m8_fuel_pin_dist)
    self.s_fuelFlowW_IR = openmc.ZCylinder(name='M8Cal Experiment Western fuel pin flow tube Inner R', R= c.m8_fuel_flowTube_IR, \
                         y0=c.latticePitch/2.0, x0=-c.m8_fuel_pin_dist)
    self.s_fuelCladE_OR = openmc.ZCylinder(name='M8Cal Experiment Eastern fuel pin cladding Outer R', R= c.m8_fuel_pinClad_OR, \
                         y0=c.latticePitch/2.0, x0= c.m8_fuel_pin_dist)
    self.s_fuelCladW_OR = openmc.ZCylinder(name='M8Cal Experiment Western fuel pin cladding Outer R', R= c.m8_fuel_pinClad_OR, \
                         y0=c.latticePitch/2.0, x0=-c.m8_fuel_pin_dist)
    self.s_fuelBondE_OR = openmc.ZCylinder(name='M8Cal Experiment Eastern fuel pin bond Outer R', R= c.m8_fuel_pinBond_OR, \
                         y0=c.latticePitch/2.0, x0= c.m8_fuel_pin_dist)
    self.s_fuelBondW_OR = openmc.ZCylinder(name='M8Cal Experiment Western fuel pin bond Outer R', R= c.m8_fuel_pinBond_OR, \
                         y0=c.latticePitch/2.0, x0=-c.m8_fuel_pin_dist)
    self.s_fuelPinE_OR = openmc.ZCylinder(name='M8Cal Experiment Eastern fuel pin Outer R', R= c.m8_fuel_pin_R, \
                         y0=c.latticePitch/2.0, x0= c.m8_fuel_pin_dist)
    self.s_fuelPinW_OR = openmc.ZCylinder(name='M8Cal Experiment Western fuel pin Outer R', R= c.m8_fuel_pin_R, \
                         y0=c.latticePitch/2.0, x0=-c.m8_fuel_pin_dist)

    # Create the cells for the universe
    self.c_outerAir_N_top = openmc.Cell(name='M8Cal Vessel top outside air N', fill=self.mats['Air'])
    self.c_outerAir_S_top = openmc.Cell(name='M8Cal Vessel top outside air S', fill=self.mats['Air'])
    self.c_outerAir_E_top = openmc.Cell(name='M8Cal Vessel top outside air E', fill=self.mats['Air'])
    self.c_outerAir_W_top = openmc.Cell(name='M8Cal Vessel top outside air W', fill=self.mats['Air'])
    self.c_outerAir_N_top.region = -self.s_univUpperBound & +self.s_gridPlate_top & -self.s_boundOuter_N & \
                                   -self.s_boundOuter_E & +self.s_boundOuter_W & +self.s_canOuter_R &      \
                                   (-self.s_canOuter_W | +self.s_canOuter_NW | +self.s_canOuter_N |        \
                                    +self.s_canOuter_NE | +self.s_canOuter_E) & +self.s_dummyOrigin_Y
    self.c_outerAir_S_top.region = -self.s_univUpperBound & +self.s_gridPlate_top & +self.s_boundOuter_S & \
                                   -self.s_boundOuter_E & +self.s_boundOuter_W & +self.s_canOuter_R &      \
                                   (-self.s_canOuter_W | -self.s_canOuter_SW | -self.s_canOuter_S |        \
                                    -self.s_canOuter_SE | +self.s_canOuter_E) & -self.s_dummyOrigin_Y
    self.c_outerAir_E_top.region = -self.s_univUpperBound & +self.s_gridPlate_top & -self.s_canOuter_R & \
                                   -self.s_boundOuter_E & +self.s_canOuter_E
    self.c_outerAir_W_top.region = -self.s_univUpperBound & +self.s_gridPlate_top & -self.s_canOuter_R & \
                                   +self.s_boundOuter_W & -self.s_canOuter_W
    self.c_outerAir_N_mid = openmc.Cell(name='M8Cal Vessel outside steel grid plate N', fill=self.mats['Mild Steel'])
    self.c_outerAir_S_mid = openmc.Cell(name='M8Cal Vessel outside steel grid plate S', fill=self.mats['Mild Steel'])
    self.c_outerAir_E_mid = openmc.Cell(name='M8Cal Vessel outside steel grid plate E', fill=self.mats['Mild Steel'])
    self.c_outerAir_W_mid = openmc.Cell(name='M8Cal Vessel outside steel grid plate W', fill=self.mats['Mild Steel'])
    self.c_outerAir_N_mid.region = +self.s_gridPlate_bot & -self.s_gridPlate_top & -self.s_boundOuter_N & \
                                   -self.s_boundOuter_E & +self.s_boundOuter_W & +self.s_canOuter_R &      \
                                   (-self.s_canOuter_W | +self.s_canOuter_NW | +self.s_canOuter_N |        \
                                    +self.s_canOuter_NE | +self.s_canOuter_E) & +self.s_dummyOrigin_Y
    self.c_outerAir_S_mid.region = +self.s_gridPlate_bot & -self.s_gridPlate_top & +self.s_boundOuter_S & \
                                   -self.s_boundOuter_E & +self.s_boundOuter_W & +self.s_canOuter_R &      \
                                   (-self.s_canOuter_W | -self.s_canOuter_SW | -self.s_canOuter_S |        \
                                    -self.s_canOuter_SE | +self.s_canOuter_E) & -self.s_dummyOrigin_Y
    self.c_outerAir_E_mid.region = +self.s_gridPlate_bot & -self.s_gridPlate_top & -self.s_canOuter_R & \
                                   -self.s_boundOuter_E & +self.s_canOuter_E
    self.c_outerAir_W_mid.region = +self.s_gridPlate_bot & -self.s_gridPlate_top & -self.s_canOuter_R & \
                                   +self.s_boundOuter_W & -self.s_canOuter_W
    self.c_outerAir_N_bot = openmc.Cell(name='M8Cal Vessel bottom outside air N', fill=self.mats['Air'])
    self.c_outerAir_S_bot = openmc.Cell(name='M8Cal Vessel bottom outside air S', fill=self.mats['Air'])
    self.c_outerAir_E_bot = openmc.Cell(name='M8Cal Vessel bottom outside air E', fill=self.mats['Air'])
    self.c_outerAir_W_bot = openmc.Cell(name='M8Cal Vessel bottom outside air W', fill=self.mats['Air'])
    self.c_outerAir_N_bot.region = +self.s_univLowerBound & -self.s_gridPlate_bot & -self.s_boundOuter_N & \
                                   -self.s_boundOuter_E & +self.s_boundOuter_W & +self.s_canOuter_R &      \
                                   (-self.s_canOuter_W | +self.s_canOuter_NW | +self.s_canOuter_N |        \
                                    +self.s_canOuter_NE | +self.s_canOuter_E) & +self.s_dummyOrigin_Y
    self.c_outerAir_S_bot.region = +self.s_univLowerBound & -self.s_gridPlate_bot & +self.s_boundOuter_S & \
                                   -self.s_boundOuter_E & +self.s_boundOuter_W & +self.s_canOuter_R &      \
                                   (-self.s_canOuter_W | -self.s_canOuter_SW | -self.s_canOuter_S |        \
                                    -self.s_canOuter_SE | +self.s_canOuter_E) & -self.s_dummyOrigin_Y
    self.c_outerAir_E_bot.region = +self.s_univLowerBound & -self.s_gridPlate_bot & -self.s_canOuter_R & \
                                   -self.s_boundOuter_E & +self.s_canOuter_E
    self.c_outerAir_W_bot.region = +self.s_univLowerBound & -self.s_gridPlate_bot & -self.s_canOuter_R & \
                                   +self.s_boundOuter_W & -self.s_canOuter_W
    self.c_outerClad_N = openmc.Cell(name='M8Cal Vessel outside clad N', fill=self.mats['SS304'])
    self.c_outerClad_S = openmc.Cell(name='M8Cal Vessel outside clad S', fill=self.mats['SS304'])
    self.c_outerClad_E = openmc.Cell(name='M8Cal Vessel outside clad E', fill=self.mats['SS304'])
    self.c_outerClad_W = openmc.Cell(name='M8Cal Vessel outside clad W', fill=self.mats['SS304'])
    self.c_innerClad = openmc.Cell(name='M8Cal Vessel inside clad', fill=self.mats['SS304'])
    self.c_outerClad_N.region = -self.s_univUpperBound & +self.s_univLowerBound & +self.s_canOuter_W & -self.s_canOuter_NW \
                              & -self.s_canOuter_N & -self.s_canOuter_NE & -self.s_canOuter_E & +self.s_canOuter_R  & \
                              ( -self.s_canInner_W | +self.s_canInner_NW | +self.s_canInner_N | +self.s_canInner_NE | \
                                +self.s_canInner_E) & +self.s_dummyOrigin_Y
    self.c_outerClad_S.region = -self.s_univUpperBound & +self.s_univLowerBound & +self.s_canOuter_W & +self.s_canOuter_SW \
                              & +self.s_canOuter_S & +self.s_canOuter_SE & -self.s_canOuter_E & +self.s_canOuter_R  & \
                              ( -self.s_canInner_W | -self.s_canInner_SW | -self.s_canInner_S | -self.s_canInner_SE | \
                                +self.s_canInner_E) & -self.s_dummyOrigin_Y
    self.c_outerClad_E.region = -self.s_univUpperBound & +self.s_univLowerBound & -self.s_canOuter_E & +self.s_canInner_E \
                              & -self.s_canOuter_R
    self.c_outerClad_W.region = -self.s_univUpperBound & +self.s_univLowerBound & +self.s_canOuter_W & -self.s_canInner_W \
                              & -self.s_canOuter_R
    self.c_innerClad.region = -self.s_univUpperBound & +self.s_univLowerBound & +self.s_canInner_W & -self.s_canInner_E \
                            & -self.s_canOuter_R & +self.s_canInner_R
    self.c_innerAir_N = openmc.Cell(name='M8Cal Vessel inside air N', fill=self.mats['Air'])
    self.c_innerAir_S = openmc.Cell(name='M8Cal Vessel inside air S', fill=self.mats['Air'])
    self.c_innerAir = openmc.Cell(name='M8Cal Vessel inside air central', fill=self.mats['Air'])
    self.c_innerAir_N.region = +self.s_univLowerBound & -self.s_univUpperBound & +self.s_canInner_W & -self.s_canInner_NW \
                              & -self.s_canInner_N & -self.s_canInner_NE & -self.s_canInner_E & +self.s_canOuter_R  \
                              & +self.s_dummyOrigin_Y
    self.c_innerAir_S.region = +self.s_univLowerBound & -self.s_univUpperBound & +self.s_canInner_W & +self.s_canInner_SW \
                              & +self.s_canInner_S & +self.s_canInner_SE & -self.s_canInner_E & +self.s_canOuter_R  \
                              & -self.s_dummyOrigin_Y
    self.c_innerAir.region = +self.s_univLowerBound & -self.s_univUpperBound & +self.s_canInner_W & -self.s_canInner_E \
                           & -self.s_canInner_R & +self.s_expDumHeat_OR & +self.s_expLegMetal_OR
    self.c_pumpSteel = openmc.Cell(name='M8Cal Vessel pump leg steel tube', fill=self.mats['SS304'])
    self.c_pumpAir = openmc.Cell(name='M8Cal Vessel pump leg inside air', fill=self.mats['Air'])
    self.c_pumpSteel.region = +self.s_univLowerBound & -self.s_univUpperBound & -self.s_expLegMetal_OR & +self.s_expLegMetal_IR
    self.c_pumpAir.region = +self.s_univLowerBound & -self.s_univUpperBound & -self.s_expLegMetal_IR
    self.c_vessOuterSteel = openmc.Cell(name='M8Cal Vessel experiment leg outer steel dummy heater', fill=self.mats['SS304'])
    self.c_vessDysLowerSteel = openmc.Cell(name='M8Cal Vessel experiment leg dysprosium layer lower steel segment', \
                               fill=self.mats['SS304'])
    self.c_vessDysUpperSteel = openmc.Cell(name='M8Cal Vessel experiment leg dysprosium layer upper steel segment', \
                               fill=self.mats['SS304'])
    self.c_vessDysMidSteel = openmc.Cell(name='M8Cal Vessel experiment leg dysprosium layer mid steel segment', \
                             fill=self.mats['SS304'])
    self.c_vessDysLowerTkDys = openmc.Cell(name='M8Cal Vessel experiment leg dysprosium layer lower thick dysprosium segment', \
                               fill=self.mats['Dysprosium'])
    self.c_vessDysUpperTkDys = openmc.Cell(name='M8Cal Vessel experiment leg dysprosium layer upper thick dysprosium segment', \
                               fill=self.mats['Dysprosium'])
    self.c_vessDysLowerMedDys = openmc.Cell(name='M8Cal Vessel experiment leg dysprosium layer lower medium dysprosium segment, Dys', \
                                fill=self.mats['Dysprosium'])
    self.c_vessDysUpperMedDys = openmc.Cell(name='M8Cal Vessel experiment leg dysprosium layer upper medium dysprosium segment, Dys', \
                                fill=self.mats['Dysprosium'])
    self.c_vessDysLowerMedSS = openmc.Cell(name='M8Cal Vessel experiment leg dysprosium layer lower medium dysprosium segment, Steel', \
                               fill=self.mats['SS304'])
    self.c_vessDysUpperMedSS = openmc.Cell(name='M8Cal Vessel experiment leg dysprosium layer upper medium dysprosium segment, Steel', \
                               fill=self.mats['SS304'])
    self.c_vessDysLowerTnDys = openmc.Cell(name='M8Cal Vessel experiment leg dysprosium layer lower thin dysprosium segment, Dys', \
                               fill=self.mats['Dysprosium'])
    self.c_vessDysUpperTnDys = openmc.Cell(name='M8Cal Vessel experiment leg dysprosium layer upper thin dysprosium segment, Dys', \
                               fill=self.mats['Dysprosium'])
    self.c_vessDysLowerTnSS = openmc.Cell(name='M8Cal Vessel experiment leg dysprosium layer lower thin dysprosium segment, Steel', \
                              fill=self.mats['SS304'])
    self.c_vessDysUpperTnSS = openmc.Cell(name='M8Cal Vessel experiment leg dysprosium layer upper thin dysprosium segment, Steel', \
                              fill=self.mats['SS304'])
    self.c_vessOuterSteel.region = -self.s_univUpperBound & +self.s_univLowerBound & +self.s_expTkDys_OR & -self.s_expDumHeat_OR
    self.c_vessDysLowerSteel.region = +self.s_univLowerBound & -self.s_bottomTkDys_bot & +self.s_expSSSleeve_OR & -self.s_expTkDys_OR
    self.c_vessDysUpperSteel.region = -self.s_univUpperBound & +self.s_bottomTkDys_top & +self.s_expSSSleeve_OR & -self.s_expTkDys_OR
    self.c_vessDysMidSteel.region = -self.s_bottomSSDys_top & +self.s_bottomSSDys_bot & +self.s_expSSSleeve_OR & -self.s_expTkDys_OR
    self.c_vessDysLowerTkDys.region = +self.s_bottomTkDys_bot & -self.s_bottomMedDys_bot & +self.s_expSSSleeve_OR & -self.s_expTkDys_OR
    self.c_vessDysUpperTkDys.region = -self.s_bottomTkDys_top & +self.s_bottomMedDys_top & +self.s_expSSSleeve_OR & -self.s_expTkDys_OR
    self.c_vessDysLowerMedDys.region = +self.s_bottomMedDys_bot & -self.s_bottomTnDys_bot & +self.s_expSSSleeve_OR & -self.s_expMedDys_OR
    self.c_vessDysUpperMedDys.region = -self.s_bottomMedDys_top & +self.s_bottomTnDys_top & +self.s_expSSSleeve_OR & -self.s_expMedDys_OR
    self.c_vessDysLowerMedSS.region = +self.s_bottomMedDys_bot & -self.s_bottomTnDys_bot & +self.s_expMedDys_OR & -self.s_expTkDys_OR
    self.c_vessDysUpperMedSS.region = -self.s_bottomMedDys_top & +self.s_bottomTnDys_top & +self.s_expMedDys_OR & -self.s_expTkDys_OR
    self.c_vessDysLowerTnDys.region = +self.s_bottomTnDys_bot & -self.s_bottomSSDys_bot & +self.s_expSSSleeve_OR & -self.s_expTnDys_OR
    self.c_vessDysUpperTnDys.region = -self.s_bottomTnDys_top & +self.s_bottomSSDys_top & +self.s_expSSSleeve_OR & -self.s_expTnDys_OR
    self.c_vessDysLowerTnSS.region = +self.s_bottomTnDys_bot & -self.s_bottomSSDys_bot & +self.s_expTnDys_OR & -self.s_expTkDys_OR
    self.c_vessDysUpperTnSS.region = -self.s_bottomTnDys_top & +self.s_bottomSSDys_top & +self.s_expTnDys_OR & -self.s_expTkDys_OR
    self.c_vessLinerSteel = openmc.Cell(name='M8Cal Vessel experiment leg steel liner', fill=self.mats['SS304'])
    self.c_vessLinerAl = openmc.Cell(name='M8Cal Vessel experiment leg aluminum liner', fill=self.mats['Al6063'])
    self.c_vessCLoopTest = openmc.Cell(name='M8Cal Vessel experiment leg steel calibration loop test section', fill=self.mats['SS304'])
    self.c_vessOuterGap = openmc.Cell(name='M8Cal Vessel experiment leg outer air gap', fill=self.mats['Air'])
    self.c_vessOuterTube = openmc.Cell(name='M8Cal Vessel experiment leg steel calibration train outer tube', fill=self.mats['SS304'])
    self.c_vessInnerAir = openmc.Cell(name='M8Cal Vessel experiment leg inner air fill', fill=self.mats['Air'])
    self.c_vessLinerSteel.region = -self.s_univUpperBound & +self.s_univLowerBound & +self.s_expAlSleeve_OR & -self.s_expSSSleeve_OR
    self.c_vessLinerAl.region = -self.s_univUpperBound & +self.s_univLowerBound & -self.s_expAlSleeve_OR & +self.s_expSSCalib_OR
    self.c_vessCLoopTest.region = -self.s_univUpperBound & +self.s_univLowerBound & -self.s_expSSCalib_OR & +self.s_expSSCalib_IR
    self.c_vessOuterGap.region = -self.s_univUpperBound & +self.s_univLowerBound & -self.s_expSSCalib_IR & +self.s_expSSTest_OR
    self.c_vessOuterTube.region = -self.s_univUpperBound & +self.s_univLowerBound & -self.s_expSSTest_OR & +self.s_expSSTest_IR
    self.c_vessInnerAir.region = -self.s_univUpperBound & +self.s_univLowerBound & -self.s_expSSTest_IR & +self.s_fuelFlowE_OR \
                               & +self.s_fuelFlowW_OR
    self.c_pinFlowTube_E = openmc.Cell(name='M8Cal Vessel experiment leg East pin flow tube', fill=self.mats['SS304'])
    self.c_pinFlowTube_W = openmc.Cell(name='M8Cal Vessel experiment leg West pin flow tube', fill=self.mats['SS304'])
    self.c_pinFlowGap_E = openmc.Cell(name='M8Cal Vessel experiment leg East pin Helium Argon gap', fill=self.mats['HeAr'])
    self.c_pinFlowGap_W = openmc.Cell(name='M8Cal Vessel experiment leg West pin Helium Argon gap', fill=self.mats['HeAr'])
    self.c_pinFlowTube_E.region = -self.s_univUpperBound & +self.s_univLowerBound & -self.s_fuelFlowE_OR & +self.s_fuelFlowE_IR
    self.c_pinFlowTube_W.region = -self.s_univUpperBound & +self.s_univLowerBound & -self.s_fuelFlowW_OR & +self.s_fuelFlowW_IR
    self.c_pinFlowGap_E.region = -self.s_univUpperBound & +self.s_univLowerBound & -self.s_fuelFlowE_IR & +self.s_fuelCladE_OR
    self.c_pinFlowGap_W.region = -self.s_univUpperBound & +self.s_univLowerBound & -self.s_fuelFlowW_IR & +self.s_fuelCladW_OR
    self.c_pinUpperGas_E = openmc.Cell(name='M8Cal Vessel experiment leg East pin gas above pin', fill=self.mats['HeAr'])
    self.c_pinUpperGas_W = openmc.Cell(name='M8Cal Vessel experiment leg West pin gas above pin', fill=self.mats['HeAr'])
    self.c_pinLowerGas_E = openmc.Cell(name='M8Cal Vessel experiment leg East pin gas below pin', fill=self.mats['HeAr'])
    self.c_pinLowerGas_W = openmc.Cell(name='M8Cal Vessel experiment leg West pin gas below pin', fill=self.mats['HeAr'])
    self.c_pinUpperFitt_E = openmc.Cell(name='M8Cal Vessel experiment leg East pin upper fuel pin fitting', fill=self.mats['Zirc4'])
    self.c_pinUpperFitt_W = openmc.Cell(name='M8Cal Vessel experiment leg West pin upper fuel pin fitting', fill=self.mats['Zirc4'])
    self.c_pinLowerFitt_E = openmc.Cell(name='M8Cal Vessel experiment leg East pin lower fuel pin fitting', fill=self.mats['Zirc4'])
    self.c_pinLowerFitt_W = openmc.Cell(name='M8Cal Vessel experiment leg West pin lower fuel pin fitting', fill=self.mats['Zirc4'])
    self.c_pinClad_E = openmc.Cell(name='M8Cal Vessel experiment leg East pin cladding', fill=self.mats['Zirc4'])
    self.c_pinClad_W = openmc.Cell(name='M8Cal Vessel experiment leg West pin cladding', fill=self.mats['Zirc4'])
    self.c_pinUpperGas_E.region = -self.s_univUpperBound & +self.s_pinTopFitt_top & -self.s_fuelCladE_OR
    self.c_pinUpperGas_W.region = -self.s_univUpperBound & +self.s_pinTopFitt_top & -self.s_fuelCladW_OR
    self.c_pinLowerGas_E.region = +self.s_univLowerBound & -self.s_pinBotFitt_bot & -self.s_fuelCladE_OR
    self.c_pinLowerGas_W.region = +self.s_univLowerBound & -self.s_pinBotFitt_bot & -self.s_fuelCladW_OR
    self.c_pinUpperFitt_E.region = -self.s_pinTopFitt_top & +self.s_pinPlenum_top & -self.s_fuelCladE_OR
    self.c_pinUpperFitt_W.region = -self.s_pinTopFitt_top & +self.s_pinPlenum_top & -self.s_fuelCladW_OR
    self.c_pinLowerFitt_E.region = +self.s_pinBotFitt_bot & -self.s_pinFuel_bot & -self.s_fuelCladE_OR
    self.c_pinLowerFitt_W.region = +self.s_pinBotFitt_bot & -self.s_pinFuel_bot & -self.s_fuelCladW_OR
    self.c_pinClad_E.region = -self.s_pinPlenum_top & +self.s_pinFuel_bot & -self.s_fuelCladE_OR & +self.s_fuelBondE_OR
    self.c_pinClad_W.region = -self.s_pinPlenum_top & +self.s_pinFuel_bot & -self.s_fuelCladW_OR & +self.s_fuelBondW_OR
    self.c_pinPlenum_E = openmc.Cell(name='M8Cal Vessel experiment leg East pin plenum', fill=self.mats['HeAr'])
    self.c_pinPlenum_W = openmc.Cell(name='M8Cal Vessel experiment leg West pin plenum', fill=self.mats['HeAr'])
    self.c_pinNaExtra_E = openmc.Cell(name='M8Cal Vessel experiment leg East pin extra sodium', fill=self.mats['Sodium'])
    self.c_pinNaExtra_W = openmc.Cell(name='M8Cal Vessel experiment leg West pin extra sodium', fill=self.mats['Sodium'])
    self.c_pinNaBond_E = openmc.Cell(name='M8Cal Vessel experiment leg East pin sodium bond', fill=self.mats['Sodium'])
    self.c_pinNaBond_W = openmc.Cell(name='M8Cal Vessel experiment leg West pin sodium bond', fill=self.mats['Sodium'])
    # TODO Unsure which of the four fuel pins I should be using (there are two type 1 pins, one type 2, and one type 3)
    #      For now specify them both as type 1 - highly enriched uranium, no plutonium)
    self.c_pinFuel_E = openmc.Cell(name='M8Cal Vessel experiment leg East pin fuel', fill=self.mats['M8 Fuel 1'])
    self.c_pinFuel_W = openmc.Cell(name='M8Cal Vessel experiment leg West pin fuel', fill=self.mats['M8 Fuel 1'])
    self.c_pinPlenum_E.region = +self.s_pinNa_top & -self.s_pinPlenum_top & -self.s_fuelBondE_OR
    self.c_pinPlenum_W.region = +self.s_pinNa_top & -self.s_pinPlenum_top & -self.s_fuelBondW_OR
    self.c_pinNaExtra_E.region = +self.s_pinFuel_top & -self.s_pinNa_top & -self.s_fuelBondE_OR
    self.c_pinNaExtra_W.region = +self.s_pinFuel_top & -self.s_pinNa_top & -self.s_fuelBondW_OR
    self.c_pinNaBond_E.region = -self.s_pinFuel_top & +self.s_pinFuel_bot & -self.s_fuelBondE_OR & +self.s_fuelPinE_OR
    self.c_pinNaBond_W.region = -self.s_pinFuel_top & +self.s_pinFuel_bot & -self.s_fuelBondW_OR & +self.s_fuelPinW_OR
    self.c_pinFuel_E.region = -self.s_pinFuel_top & +self.s_pinFuel_bot & -self.s_fuelPinE_OR
    self.c_pinFuel_W.region = -self.s_pinFuel_top & +self.s_pinFuel_bot & -self.s_fuelPinW_OR

    # Create the universe we are going to be building the vessel in
    self.u_vessel = openmc.Universe(name='M8Cal Vessel')
    self.u_vessel.add_cells((self.c_outerAir_N_top, self.c_outerAir_S_top, self.c_outerAir_E_top, self.c_outerAir_W_top))
    self.u_vessel.add_cells((self.c_outerAir_N_mid, self.c_outerAir_S_mid, self.c_outerAir_E_mid, self.c_outerAir_W_mid))
    self.u_vessel.add_cells((self.c_outerAir_N_bot, self.c_outerAir_S_bot, self.c_outerAir_E_bot, self.c_outerAir_W_bot))
    self.u_vessel.add_cells((self.c_outerClad_N, self.c_outerClad_S, self.c_outerClad_E, self.c_outerClad_W, self.c_innerClad))
    self.u_vessel.add_cells((self.c_innerAir_N, self.c_innerAir_S, self.c_innerAir))
    self.u_vessel.add_cells((self.c_pumpSteel, self.c_pumpAir))
    self.u_vessel.add_cells((self.c_vessOuterSteel, self.c_vessDysLowerSteel, self.c_vessDysUpperSteel, self.c_vessDysMidSteel, \
                             self.c_vessDysLowerTkDys, self.c_vessDysUpperTkDys, self.c_vessDysLowerMedDys, self.c_vessDysUpperMedDys, \
                             self.c_vessDysLowerMedSS, self.c_vessDysUpperMedSS, self.c_vessDysLowerTnDys, self.c_vessDysUpperTnDys, \
                             self.c_vessDysLowerTnSS, self.c_vessDysUpperTnSS))
    self.u_vessel.add_cells((self.c_vessLinerSteel, self.c_vessLinerAl, self.c_vessCLoopTest, self.c_vessOuterGap, \
                             self.c_vessOuterTube, self.c_vessInnerAir))
    self.u_vessel.add_cells((self.c_pinFlowTube_E, self.c_pinFlowTube_W, self.c_pinFlowGap_E, self.c_pinFlowGap_W))
    self.u_vessel.add_cells((self.c_pinUpperGas_E, self.c_pinUpperGas_W, self.c_pinLowerGas_E, self.c_pinLowerGas_W, \
                             self.c_pinUpperFitt_E, self.c_pinUpperFitt_W, self.c_pinLowerFitt_E, self.c_pinLowerFitt_W, \
                             self.c_pinClad_E, self.c_pinClad_W))
    self.u_vessel.add_cells((self.c_pinPlenum_E, self.c_pinPlenum_W, self.c_pinNaExtra_E, self.c_pinNaExtra_W, \
                             self.c_pinNaBond_E, self.c_pinNaBond_W, self.c_pinFuel_E, self.c_pinFuel_W))
