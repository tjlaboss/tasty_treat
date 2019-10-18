"""elements.py

Provides a container class of all TREAT fuel elements (assemblies)

"""

import openmc
import math
from copy import deepcopy
import common_files.treat.constants as c
from common_files.treat.corebuilder import AxialElement, InfiniteElement, PartialElement
from common_files.treat.materials import wBpGraphite, wBpFuels


class Elements(object):

  def __init__(self, mats):
    """ Creates TREAT element universes """

    self.mats = mats
    self.empty = self.mats['Air']  # Or change to void

    self._add_axials()
    self._add_dummy_universe()
    self._add_fuel_elements()
    self._add_rcca_elements()

  def _add_axials(self):
    """ Adds structure axial surfaces common for most elements """

    # Below the active fuel region axial surfaces
    self.s_struct_elemSupportPin_bot = openmc.ZPlane(name='Support structure bottom', z0=c.struct_Support_bot)
    self.s_struct_bff_prong_top = openmc.ZPlane(name='Bottom fuel fitting cone bottom', z0=c.struct_bff_cone_bot)
    self.s_struct_bff_cone_top = openmc.ZPlane(name='Bottom fuel fitting base bottom', z0=c.struct_bff_base_bot)
    self.s_struct_bff_base_top = openmc.ZPlane(name='Support structure top', z0=c.struct_bff_base_top)
    self.s_struct_lowerReflec_bot = openmc.ZPlane(name='Lower reflector region bottom', z0=c.struct_LowerReflec_bot)
    self.s_struct_lowerLP_top = openmc.ZPlane(name='Lower reflector long plug top', z0=c.struct_LowerLongPlug_top)
    self.s_struct_lowerSP_mid = openmc.ZPlane(name='Lower reflector thick short plug top', z0=c.struct_LowerShortPlug_mid)
    self.s_struct_lowerSP_top = openmc.ZPlane(name='Lower reflector thin short plug top', z0=c.struct_LowerShortPlug_top)
    self.s_struct_lowerAlSpace_top = openmc.ZPlane(name='Lower Aluminum spacer region top', z0=c.struct_LowerAlSpace_top)
    self.s_struct_lowerGap_top = openmc.ZPlane(name='Lower divotted gap region top', z0=c.struct_LowerGap_top)
    self.s_struct_lowerZrSpace_top = openmc.ZPlane(name='Lower Zirc spacer region top', z0=c.struct_LowerZrSpace_top)
    # Half-width
    self.s_struct_hw_bff_tip_top = openmc.ZPlane(name='Half-width bottom fuel fitting tip top',
                                                 z0=c.struct_hw_bff_sphere_top)
    self.s_struct_hw_bff_prong_top = openmc.ZPlane(name='Half-width bottom fuel fitting prong top',
                                                   z0=c.struct_hw_bff_prong_top)
    self.s_struct_hw_bff_cone_top = openmc.ZPlane(name='Half-width bottom fuel fitting cone top',
                                                  z0=c.struct_hw_bff_cone_top)

    # Fuel axial surfaces
    self.s_fuel_activeFuel_bot = openmc.ZPlane(name='Fuel active region bottom', z0=c.fuel_ActiveFuel_bot)
    self.s_fuel_activeFuel_top = openmc.ZPlane(name='Fuel active region top', z0=c.fuel_ActiveFuel_top)

    # Above the active fuel region axial surfaces
    self.s_struct_upperZrSpace_bot = openmc.ZPlane(name='Upper Zirc spacer region bottom', z0=c.struct_UpperZrSpace_bot)
    self.s_struct_upperZrSpace_top = openmc.ZPlane(name='Upper Zirc spacer region top', z0=c.struct_UpperZrSpace_top)
    self.s_struct_upperGap_top = openmc.ZPlane(name='Upper Zirc divotted gap region top', z0=c.struct_UpperGap_top)
    self.s_struct_upperAlSpace_top = openmc.ZPlane(name='Upper Aluminum spacer region top', z0=c.struct_UpperAlSpace_top)
    self.s_struct_upperOffGas_top = openmc.ZPlane(name='Upper off gas tube top', z0=c.struct_OffGas_top)
    self.s_struct_upperCrimp_top = openmc.ZPlane(name='Upper off gas crimping top', z0=c.struct_UpperCrimp_top)
    self.s_struct_upperSP_mid = openmc.ZPlane(name='Upper reflector thin short plug top', z0=c.struct_UpperShortPlug_mid)
    self.s_struct_upperSP_top = openmc.ZPlane(name='Upper reflector thick short plug top', z0=c.struct_UpperShortPlug_top)
    self.s_struct_upperLP_top = openmc.ZPlane(name='Upper reflector long plug top', z0=c.struct_UpperLongPlug_top)
    self.s_struct_tff_bot = openmc.ZPlane(name='Top fuel fitting bottom', z0=c.struct_upper_head_bot)
    self.s_struct_tff_base_top = openmc.ZPlane(name='Top fuel fitting base top', z0=c.struct_tff_base_top)
    self.s_struct_tff_mid_top = openmc.ZPlane(name='Top fuel fitting middle cone top', z0=c.struct_tff_mid_top)
    self.s_struct_tff_neck_top = openmc.ZPlane(name='Top fuel fitting neck top', z0=c.struct_tff_neck_top)
    self.s_struct_tff_top = openmc.ZPlane(name='Top fuel fitting top', z0=c.struct_upper_head_top)

    # Some extra axial surfaces we need to fully define the control rod elements
    self.s_struct_lowerCrdTube_bot = openmc.ZPlane(name='Lower Zirc CRD Tube Lowest Extent', z0=c.struct_lowerCrdTube_bot)
    self.s_struct_lowerCrdBase_bot = openmc.ZPlane(name='Lower CRD support structure bottom', z0=c.struct_lowerCrdBase_bot)
    self.s_struct_crdElem_top = openmc.ZPlane(name='Upper axial CRD Zr / Al tube overlap top', z0=c.struct_crdElemTube_top)
    self.s_struct_crdBearThin_top = openmc.ZPlane(name='Thin bearing tube top', z0=c.struct_crdBearThin_top)
    self.s_struct_crdBushRet_top = openmc.ZPlane(name='Top of the bushing retainer tube fixture', z0=c.struct_crdBushRet_top)
    self.s_struct_crdOffGasTube_top = openmc.ZPlane(name='Top of the main offgas tube section', z0=c.struct_crdOffGasTube_top)
    self.s_struct_crdOffGasCrimp_top = openmc.ZPlane(name='Top of the offgas tube crimp', z0=c.struct_crdOffGasCrimp_top)
    self.s_struct_crdOffGasDrill_top = openmc.ZPlane(name='Top of the offgas drill hole', z0=c.struct_crdOffGasDrillHole_top)
    self.s_struct_crdBush_top = openmc.ZPlane(name='Top of the graphitar bushing', z0=c.struct_crdBush_top)
    self.s_struct_upperCrdHead_mid = openmc.ZPlane(name='Upper CRD head structure top', z0=c.struct_upperCrdHead_mid)
    self.s_struct_upperCrdHead_top = openmc.ZPlane(name='Upper CRD head structure top', z0=c.struct_upperCrdHead_top)
    self.s_struct_upperCrdTube_top = openmc.ZPlane(name='Upper Aluminum CRD Tube Highest Extent', z0=c.struct_upperCrdTube_top)

    # Some axial surfaces for the access hole dummy elements
    self.s_struct_accLowerLead_top = openmc.ZPlane(name='Lower access lead plug top', z0=c.struct_accessLowerLead_top)
    self.s_struct_accLowerDummy_top = openmc.ZPlane(name='Lower access dummy plug top', z0=c.struct_accessLowerDummy_top)
    self.s_struct_accLowerSP_mid = openmc.ZPlane(name='Lower access short plug unmachined top', z0=c.struct_accessLowerSP_mid)
    self.s_struct_accLowerSPAl_top = openmc.ZPlane(name='Lower access short plug machined Al clad top', z0=c.struct_accessLowerSP_upper)
    self.s_struct_accLowerSPZr_top = openmc.ZPlane(name='Lower access short plug machined Zr clad top', z0=c.struct_accessLowerSP_top)
    self.s_struct_accLowerZrSpace_top = openmc.ZPlane(name='Lower access Zr spacer top', z0=c.struct_accessLowerZr_top)
    self.s_struct_accWindow_bot = openmc.ZPlane(name='Access window bottom', z0=c.struct_accessWindow_bot)
    # Now we have some diverging surfaces for the 48, 48.5, and 49.5 inch access hole elements.
    self.s_struct_accWindow48_top = openmc.ZPlane(name='48 inch access window top', z0=c.struct_accessWindow48_top)
    self.s_struct_accWindow485_top = openmc.ZPlane(name='48.5 inch access window top', z0=c.struct_accessWindow485_top)
    self.s_struct_accWindow495_top = openmc.ZPlane(name='49.5 inch access window top', z0=c.struct_accessWindow495_top)
    self.s_struct_accWindow50_top = openmc.ZPlane(name='50 inch access window top', z0=c.struct_accessWindow50_top)
    self.s_struct_accTube48_top = openmc.ZPlane(name='48 inch access upper tubing top', z0=c.struct_accessTube48_top)
    self.s_struct_accTube485_top = openmc.ZPlane(name='48.5 inch access upper tubing top', z0=c.struct_accessTube485_top)
    self.s_struct_accTube495_top = openmc.ZPlane(name='49.5 inch access upper tubing top', z0=c.struct_accessTube495_top)
    self.s_struct_accTube50_top = openmc.ZPlane(name='48 inch access upper tubing top', z0=c.struct_accessTube50_top)
    self.s_struct_accZrSpace48_top = openmc.ZPlane(name='48 inch access upper Zr spacer top', z0=c.struct_accessZr48_top)
    self.s_struct_accZrSpace485_top = openmc.ZPlane(name='48.5 inch access upper Zr spacer top', z0=c.struct_accessZr485_top)
    self.s_struct_accZrSpace495_top = openmc.ZPlane(name='49.5 inch access upper Zr spacer top', z0=c.struct_accessZr495_top)
    self.s_struct_accZrSpace50_top = openmc.ZPlane(name='48 inch access upper Zr spacer top', z0=c.struct_accessZr50_top)
    self.s_struct_accUpperSPZr48_top = openmc.ZPlane(name='48 inch access upper short plug Zr clad top',
                                                     z0=c.struct_accessUpperSP48_lower)
    self.s_struct_accUpperSPZr485_top = openmc.ZPlane(name='48.5 inch access upper short plug Zr clad top',
                                                     z0=c.struct_accessUpperSP485_lower)
    self.s_struct_accUpperSPZr495_top = openmc.ZPlane(name='49.5 inch access upper short plug Zr clad top',
                                                     z0=c.struct_accessUpperSP495_lower)
    self.s_struct_accUpperSPZr50_top = openmc.ZPlane(name='50 inch access upper short plug Zr clad top',
                                                     z0=c.struct_accessUpperSP50_lower)
    self.s_struct_accUpperSPAl48_top = openmc.ZPlane(name='48 inch access upper short plug Al clad top',
                                                     z0=c.struct_accessUpperSP48_mid)
    self.s_struct_accUpperSPAl485_top = openmc.ZPlane(name='48.5 inch access upper short plug Al clad top',
                                                     z0=c.struct_accessUpperSP485_mid)
    self.s_struct_accUpperSPAl495_top = openmc.ZPlane(name='49.5 inch access upper short plug Al clad top',
                                                     z0=c.struct_accessUpperSP495_mid)
    self.s_struct_accUpperSPAl50_top = openmc.ZPlane(name='50 inch access upper short plug Al clad top',
                                                     z0=c.struct_accessUpperSP50_mid)
    self.s_struct_accUpperSP48_top = openmc.ZPlane(name='48 inch access upper unmachined short plug top',
                                                     z0=c.struct_accessUpperSP48_mid)
    self.s_struct_accUpperSP485_top = openmc.ZPlane(name='48.5 inch access upper unmachined short plug top',
                                                     z0=c.struct_accessUpperSP485_mid)
    self.s_struct_accUpperSP495_top = openmc.ZPlane(name='49.5 inch access upper unmachined short plug top',
                                                     z0=c.struct_accessUpperSP495_mid)
    self.s_struct_accUpperSP50_top = openmc.ZPlane(name='50 inch access upper unmachined short plug top',
                                                    z0=c.struct_accessUpperSP50_mid)
    # Now are back to having the same surfaces between different access hole dummy elements
    self.s_struct_accUpperDummy_top = openmc.ZPlane(name='Upper access dummy plug top', z0=c.struct_accessUpperDummy_top)
    self.s_struct_accUpperLead_top = openmc.ZPlane(name='Upper access lead plug top', z0=c.struct_accessUpperLead_top)
    self.s_struct_accUpperHead_top = openmc.ZPlane(name='Upper access head fixture top', z0=c.struct_accessUpperPlug_top)

    # Add in some axials for the support plate and other such details below the elements
    self.s_struct_excoreGridPlate_bot = openmc.ZPlane(name='Steel grid plate bottom', z0=c.struct_CoreGuide_top)
    self.s_struct_excoreElemGuide_bot = openmc.ZPlane(name='Element guide tube bottom', z0=c.struct_CoreVoid_top)
    self.s_struct_excoreFloorVoid_bot = openmc.ZPlane(name='Air below the elements bottom', z0=c.struct_CoreFloor_top)

    # half-width element surfaces
    self.s_struct_hw_base_top = openmc.ZPlane(name='Half-width bottom fitting top', z0=c.struct_hw_base_top)
    self.s_struct_hw_p2_top = openmc.ZPlane(name='Half-width P2 extension top', z0=c.struct_hw_p2_top)
    self.s_struct_hw_lower_lead_top = openmc.ZPlane(name='Half-width lower lead brick top',
                                                    z0=c.struct_hw_lower_lead_top)
    self.s_struct_hw_reg_graphite_top = openmc.ZPlane(name='Half-width regular graphite top',
                                                      z0=c.struct_hw_reg_graphite_top)
    self.s_struct_hw_p1_top = openmc.ZPlane(name='Half-width P1 extension top', z0=c.struct_hw_p1_top)
    self.s_struct_hw_tff_clad_base_top = openmc.ZPlane(name='Half-width lifting adapter clad base top',
                                                       z0=c.struct_hw_tff_clad_base_top)
    # TODO: the exposed base, if necessary
    self.s_struct_hw_mid_cone_top = openmc.ZPlane(name='Half-width lifting adapter middle cone top',
                                                  z0=c.struct_hw_tff_mid_cone_top)
    self.s_struct_hw_tff_top = openmc.ZPlane(name='Half-width lifting adapter top', z0=c.struct_hw_tff_top)

    self.s_struct_hw_acc_upper_lead_top = openmc.ZPlane(name="Half-width upper lead brick top",
                                                        z0=c.struct_hw_acc_upper_lead_top)
    self.s_struct_hw_acc_upper_graphite_top = openmc.ZPlane(name="Half-width upper graphite brick top",
                                                        z0=c.struct_hw_acc_upper_graphite_top)
    self.s_struct_hw_acc_upper_graphite_bot = openmc.ZPlane(name="Half-width upper graphite brick bottom",
                                                        z0=c.struct_hw_acc_upper_graphite_bot)


  def _add_dummy_universe(self):
    """ Adds all-air universe for empty lattice positions"""

    self.u_airElem  = openmc.Universe(name='Dummy Air Universe')
    self.c_air = openmc.Cell(name='Air', fill=self.mats['Air'])
    self.u_airElem.add_cells([self.c_air])

    self.u_void = openmc.Universe(name='Dummy Void Universe')
    self.c_void = openmc.Cell(name='Void', fill='Void')
    self.u_void.add_cell(self.c_void)

  def _add_fuel_elements(self):
    """ Adds TREAT fuel elements """

    # Fuel Weight Percents
    self.weight_percents = ['0.211%', '0.211%']
    self.graph_boron_ppms = ['CP2']
    self.al_clad_types = ['Al1100', 'Al6063']
    self.fuel_boron_ppms = []
    self.fuel_fitting_fills = ['Air', 'Lead']
    for temp_counter in range(len(wBpGraphite)):
      self.graph_boron_ppms.append(str(wBpGraphite[temp_counter] * 1.0E6) + ' ppm')
    for temp_counter in range(len(wBpFuels)):
      self.fuel_boron_ppms.append(str(wBpFuels[temp_counter] * 1.0E6) + ' ppm')

    #########################################################################################################################
    ### First, set up all the radial surfaces we will need
    #########################################################################################################################

    # Fuel radial surfaces

    # Inner surfaces in the fuel assembly for use in breaking it up into parts
    self.s_inner_n = openmc.YPlane(name='Inner Surface Y max', y0= c.mainFuelSurfHW)
    self.s_inner_s = openmc.YPlane(name='Inner Surface Y min', y0=-c.mainFuelSurfHW)
    self.s_inner_e = openmc.XPlane(name='Inner Surface X max', x0= c.mainFuelSurfHW)
    self.s_inner_w = openmc.XPlane(name='Inner Surface X min', x0=-c.mainFuelSurfHW)
    # First the outside surface of the fuel / graphite block
    self.s_fuel_n_o = openmc.YPlane(name='Fuel Outside Surface Y max', y0= c.pelletOR)
    self.s_fuel_s_o = openmc.YPlane(name='Fuel Outside Surface Y min', y0=-c.pelletOR)
    self.s_fuel_e_o = openmc.XPlane(name='Fuel Outside Surface X max', x0= c.pelletOR)
    self.s_fuel_w_o = openmc.XPlane(name='Fuel Outside Surface X min', x0=-c.pelletOR)
    self.s_fuel_ne_o = openmc.Plane(name='Fuel Outside Surface NE', A= 1, B=1, C=0, D= (math.sqrt(2.0)*c.fuelChamfDist))
    self.s_fuel_nw_o = openmc.Plane(name='Fuel Outside Surface NW', A=-1, B=1, C=0, D= (math.sqrt(2.0)*c.fuelChamfDist))
    self.s_fuel_se_o = openmc.Plane(name='Fuel Outside Surface SE', A=-1, B=1, C=0, D=-(math.sqrt(2.0)*c.fuelChamfDist))
    self.s_fuel_sw_o = openmc.Plane(name='Fuel Outside Surface SW', A= 1, B=1, C=0, D=-(math.sqrt(2.0)*c.fuelChamfDist))
    fuel_surfs_o = {
      'N': self.s_fuel_n_o,
      'S': self.s_fuel_s_o,
      'E': self.s_fuel_e_o,
      'W': self.s_fuel_w_o,
      'NE': self.s_fuel_ne_o,
      'NW': self.s_fuel_nw_o,
      'SE': self.s_fuel_se_o,
      'SW': self.s_fuel_sw_o,
      'IN': self.s_inner_n,
      'IS': self.s_inner_s,
      'IE': self.s_inner_e,
      'IW': self.s_inner_w,
    } # There are different possibilities for the interior surfs. The groups will be set up at the end of radial surf definition
    # Then the inside surface of the cladding
    self.s_clad_n_i = openmc.YPlane(name='Clad Inside Surface Y max', y0= c.cladIR)
    self.s_clad_s_i = openmc.YPlane(name='Clad Inside Surface Y min', y0=-c.cladIR)
    self.s_clad_e_i = openmc.XPlane(name='Clad Inside Surface X max', x0= c.cladIR)
    self.s_clad_w_i = openmc.XPlane(name='Clad Inside Surface X min', x0=-c.cladIR)
    self.s_clad_ne_i = openmc.Plane(name='Clad Inside Surface NE', A= 1, B=1, C=0, D= (math.sqrt(2.0)*c.cladChamfDistI))
    self.s_clad_nw_i = openmc.Plane(name='Clad Inside Surface NW', A=-1, B=1, C=0, D= (math.sqrt(2.0)*c.cladChamfDistI))
    self.s_clad_se_i = openmc.Plane(name='Clad Inside Surface SE', A=-1, B=1, C=0, D=-(math.sqrt(2.0)*c.cladChamfDistI))
    self.s_clad_sw_i = openmc.Plane(name='Clad Inside Surface SW', A= 1, B=1, C=0, D=-(math.sqrt(2.0)*c.cladChamfDistI))
    # Create some surfaces that will handle the extra material in the gap and cladding (required to keep gap and clad
    # constant thickness everywhere)
    self.s_gap_nw = openmc.Plane(name='Gap NE & SW Chamfers NW Surface', A=-1, B=1, C=0, D= math.sqrt(2.0)*c.fuelChamfOW/2.0)
    self.s_gap_se = openmc.Plane(name='Gap NE & SW Chamfers SE Surface', A=-1, B=1, C=0, D=-math.sqrt(2.0)*c.fuelChamfOW/2.0)
    self.s_gap_ne = openmc.Plane(name='Gap NW & SE Chamfers NE Surface', A= 1, B=1, C=0, D= math.sqrt(2.0)*c.fuelChamfOW/2.0)
    self.s_gap_sw = openmc.Plane(name='Gap NW & SE Chamfers SW Surface', A= 1, B=1, C=0, D=-math.sqrt(2.0)*c.fuelChamfOW/2.0)
    clad_surfs_i = {
      'N': self.s_clad_n_i,
      'S': self.s_clad_s_i,
      'E': self.s_clad_e_i,
      'W': self.s_clad_w_i,
      'NE': self.s_clad_ne_i,
      'NW': self.s_clad_nw_i,
      'SE': self.s_clad_se_i,
      'SW': self.s_clad_sw_i,
      'IN': self.s_inner_n,
      'IS': self.s_inner_s,
      'IE': self.s_inner_e,
      'IW': self.s_inner_w,
      'INW': self.s_gap_nw,
      'ISE': self.s_gap_se,
      'INE': self.s_gap_ne,
      'ISW': self.s_gap_sw,
      'prevN': self.s_fuel_n_o,  # These particular cladding inside surfaces only ever surround the fuel blocks
      'prevS': self.s_fuel_s_o,  # so those will always be our previous surfaces.
      'prevE': self.s_fuel_e_o,
      'prevW': self.s_fuel_w_o,
      'prevNE': self.s_fuel_ne_o,
      'prevNW': self.s_fuel_nw_o,
      'prevSE': self.s_fuel_se_o,
      'prevSW': self.s_fuel_sw_o,
    }
    # Then the outside surface of the cladding
    self.s_clad_n_o = openmc.YPlane(name='Clad Outside Surface Y max', y0= c.cladOR)
    self.s_clad_s_o = openmc.YPlane(name='Clad Outside Surface Y min', y0=-c.cladOR)
    self.s_clad_e_o = openmc.XPlane(name='Clad Outside Surface X max', x0= c.cladOR)
    self.s_clad_w_o = openmc.XPlane(name='Clad Outside Surface X min', x0=-c.cladOR)
    self.s_clad_ne_o = openmc.Plane(name='Clad Outside Surface NE', A= 1, B=1, C=0, D= (math.sqrt(2.0)*c.cladChamfDistO))
    self.s_clad_nw_o = openmc.Plane(name='Clad Outside Surface NW', A=-1, B=1, C=0, D= (math.sqrt(2.0)*c.cladChamfDistO))
    self.s_clad_se_o = openmc.Plane(name='Clad Outside Surface SE', A=-1, B=1, C=0, D=-(math.sqrt(2.0)*c.cladChamfDistO))
    self.s_clad_sw_o = openmc.Plane(name='Clad Outside Surface SW', A= 1, B=1, C=0, D=-(math.sqrt(2.0)*c.cladChamfDistO))
    # Create some surfaces that will handle the extra material in the gap and cladding (required to keep gap and clad
    # constant thickness everywhere)
    clad_chamf_dist = c.fuelChamfOW/2.0 + c.TANPI8 * (c.cladIR - c.pelletOR)
    clad_long_dist = c.mainFuelSurfHW + c.TANPI8 * (c.cladIR - c.pelletOR)
    self.s_clad_nw = openmc.Plane(name='Clad NE & SW Chamfers NW Surface', A=-1, B=1, C=0, D= math.sqrt(2.0)*clad_chamf_dist)
    self.s_clad_se = openmc.Plane(name='Clad NE & SW Chamfers SE Surface', A=-1, B=1, C=0, D=-math.sqrt(2.0)*clad_chamf_dist)
    self.s_clad_ne = openmc.Plane(name='Clad NW & SE Chamfers NE Surface', A= 1, B=1, C=0, D= math.sqrt(2.0)*clad_chamf_dist)
    self.s_clad_sw = openmc.Plane(name='Clad NW & SE Chamfers SW Surface', A= 1, B=1, C=0, D=-math.sqrt(2.0)*clad_chamf_dist)
    self.s_c_inner_n = openmc.YPlane(name='Inner Surface Y max', y0= clad_long_dist)
    self.s_c_inner_s = openmc.YPlane(name='Inner Surface Y min', y0=-clad_long_dist)
    self.s_c_inner_e = openmc.XPlane(name='Inner Surface X max', x0= clad_long_dist)
    self.s_c_inner_w = openmc.XPlane(name='Inner Surface X min', x0=-clad_long_dist)
    clad_surfs_o = {
      'N': self.s_clad_n_o,
      'S': self.s_clad_s_o,
      'E': self.s_clad_e_o,
      'W': self.s_clad_w_o,
      'NE': self.s_clad_ne_o,
      'NW': self.s_clad_nw_o,
      'SE': self.s_clad_se_o,
      'SW': self.s_clad_sw_o,
      'IN': self.s_c_inner_n,
      'IS': self.s_c_inner_s,
      'IE': self.s_c_inner_e,
      'IW': self.s_c_inner_w,
      'INW': self.s_clad_nw,
      'ISE': self.s_clad_se,
      'INE': self.s_clad_ne,
      'ISW': self.s_clad_sw,
      'prevN': self.s_clad_n_i, # These particular cladding exterior surfaces only ever surround the cladding interior surfaces
      'prevS': self.s_clad_s_i, # so those will always be our previous surfaces.
      'prevE': self.s_clad_e_i,
      'prevW': self.s_clad_w_i,
      'prevNE': self.s_clad_ne_i,
      'prevNW': self.s_clad_nw_i,
      'prevSE': self.s_clad_se_i,
      'prevSW': self.s_clad_sw_i,
    }

    # Radial surfaces for solid blocks of material that still have the chamfered corners (e.g. Zr and Al spacers)
    # Inner surfaces for use in breaking it up into parts
    self.s_block_inner_n = openmc.YPlane(name='Inner Surface Y max', y0= c.mainCladSurfHW)
    self.s_block_inner_s = openmc.YPlane(name='Inner Surface Y min', y0=-c.mainCladSurfHW)
    self.s_block_inner_e = openmc.XPlane(name='Inner Surface X max', x0= c.mainCladSurfHW)
    self.s_block_inner_w = openmc.XPlane(name='Inner Surface X min', x0=-c.mainCladSurfHW)
    # The outside surface of the material
    self.s_block_n_o = openmc.YPlane(name='Outside Surface Y max', y0= c.cladOR)
    self.s_block_s_o = openmc.YPlane(name='Outside Surface Y min', y0=-c.cladOR)
    self.s_block_e_o = openmc.XPlane(name='Outside Surface X max', x0= c.cladOR)
    self.s_block_w_o = openmc.XPlane(name='Outside Surface X min', x0=-c.cladOR)
    self.s_block_ne_o = openmc.Plane(name='Outside Surface NE', A= 1, B=1, C=0, D= (math.sqrt(2.0)*c.cladChamfDistO))
    self.s_block_nw_o = openmc.Plane(name='Outside Surface NW', A=-1, B=1, C=0, D= (math.sqrt(2.0)*c.cladChamfDistO))
    self.s_block_se_o = openmc.Plane(name='Outside Surface SE', A=-1, B=1, C=0, D=-(math.sqrt(2.0)*c.cladChamfDistO))
    self.s_block_sw_o = openmc.Plane(name='Outside Surface SW', A= 1, B=1, C=0, D=-(math.sqrt(2.0)*c.cladChamfDistO))
    block_surfs_o = {
      'N': self.s_block_n_o,
      'S': self.s_block_s_o,
      'E': self.s_block_e_o,
      'W': self.s_block_w_o,
      'NE': self.s_block_ne_o,
      'NW': self.s_block_nw_o,
      'SE': self.s_block_se_o,
      'SW': self.s_block_sw_o,
      'IN': self.s_block_inner_n,
      'IS': self.s_block_inner_s,
      'IE': self.s_block_inner_e,
      'IW': self.s_block_inner_w,
    } # There are different possibilities for the interior surfs. The groups will be set up at the end of radial surf definition

    # Set of radial surfaces for cladding with only one material inside, with no separate gap (currently will only be used
    # for empty air inside clad)
    # First, do thin cladding (i.e. that around the fuel region)
    # Inner surfaces in the material for use in breaking it up into parts
    self.s_tn_cld_inner_n = openmc.YPlane(name='Inner Surface Y max', y0= c.thinCladSurfInnerHW)
    self.s_tn_cld_inner_s = openmc.YPlane(name='Inner Surface Y min', y0=-c.thinCladSurfInnerHW)
    self.s_tn_cld_inner_e = openmc.XPlane(name='Inner Surface X max', x0= c.thinCladSurfInnerHW)
    self.s_tn_cld_inner_w = openmc.XPlane(name='Inner Surface X min', x0=-c.thinCladSurfInnerHW)
    # First the inside surface of the clad
    self.s_tn_cld_n_i = openmc.YPlane(name='Clad Inside Surface Y max', y0= c.cladIR)
    self.s_tn_cld_s_i = openmc.YPlane(name='Clad Inside Surface Y min', y0=-c.cladIR)
    self.s_tn_cld_e_i = openmc.XPlane(name='Clad Inside Surface X max', x0= c.cladIR)
    self.s_tn_cld_w_i = openmc.XPlane(name='Clad Inside Surface X min', x0=-c.cladIR)
    self.s_tn_cld_ne_i = openmc.Plane(name='Clad Inside Surface NE', A= 1, B=1, C=0, D= (math.sqrt(2.0)*c.cladChamfDistI))
    self.s_tn_cld_nw_i = openmc.Plane(name='Clad Inside Surface NW', A=-1, B=1, C=0, D= (math.sqrt(2.0)*c.cladChamfDistI))
    self.s_tn_cld_se_i = openmc.Plane(name='Clad Inside Surface SE', A=-1, B=1, C=0, D=-(math.sqrt(2.0)*c.cladChamfDistI))
    self.s_tn_cld_sw_i = openmc.Plane(name='Clad Inside Surface SW', A= 1, B=1, C=0, D=-(math.sqrt(2.0)*c.cladChamfDistI))
    tn_cld_surfs_i = {
      'N': self.s_tn_cld_n_i,
      'S': self.s_tn_cld_s_i,
      'E': self.s_tn_cld_e_i,
      'W': self.s_tn_cld_w_i,
      'NE': self.s_tn_cld_ne_i,
      'NW': self.s_tn_cld_nw_i,
      'SE': self.s_tn_cld_se_i,
      'SW': self.s_tn_cld_sw_i,
      'IN': self.s_tn_cld_inner_n,
      'IS': self.s_tn_cld_inner_s,
      'IE': self.s_tn_cld_inner_e,
      'IW': self.s_tn_cld_inner_w,
    } # There are different possibilities for the interior surfs. The groups will be set up at the end of radial surf definition
    # Then the outside surface of the cladding
    self.s_tn_cld_n_o = openmc.YPlane(name='Clad Outside Surface Y max', y0= c.cladOR)
    self.s_tn_cld_s_o = openmc.YPlane(name='Clad Outside Surface Y min', y0=-c.cladOR)
    self.s_tn_cld_e_o = openmc.XPlane(name='Clad Outside Surface X max', x0= c.cladOR)
    self.s_tn_cld_w_o = openmc.XPlane(name='Clad Outside Surface X min', x0=-c.cladOR)
    self.s_tn_cld_ne_o = openmc.Plane(name='Clad Outside Surface NE', A= 1, B=1, C=0, D= (math.sqrt(2.0)*c.cladChamfDistO))
    self.s_tn_cld_nw_o = openmc.Plane(name='Clad Outside Surface NW', A=-1, B=1, C=0, D= (math.sqrt(2.0)*c.cladChamfDistO))
    self.s_tn_cld_se_o = openmc.Plane(name='Clad Outside Surface SE', A=-1, B=1, C=0, D=-(math.sqrt(2.0)*c.cladChamfDistO))
    self.s_tn_cld_sw_o = openmc.Plane(name='Clad Outside Surface SW', A= 1, B=1, C=0, D=-(math.sqrt(2.0)*c.cladChamfDistO))
    # Create some surfaces that will handle the extra material in the cladding (required to keep clad
    # constant thickness everywhere)
    self.s_tn_cld_gap_nw = openmc.Plane(name='NE & SW Chamfers NW Surface', A=-1, B=1, C=0, D= math.sqrt(2.0)*c.thinCladChamfIW/2.0)
    self.s_tn_cld_gap_se = openmc.Plane(name='NE & SW Chamfers SE Surface', A=-1, B=1, C=0, D=-math.sqrt(2.0)*c.thinCladChamfIW/2.0)
    self.s_tn_cld_gap_ne = openmc.Plane(name='NW & SE Chamfers NE Surface', A= 1, B=1, C=0, D= math.sqrt(2.0)*c.thinCladChamfIW/2.0)
    self.s_tn_cld_gap_sw = openmc.Plane(name='NW & SE Chamfers SW Surface', A= 1, B=1, C=0, D=-math.sqrt(2.0)*c.thinCladChamfIW/2.0)
    tn_cld_surfs_o = {
      'N': self.s_tn_cld_n_o,
      'S': self.s_tn_cld_s_o,
      'E': self.s_tn_cld_e_o,
      'W': self.s_tn_cld_w_o,
      'NE': self.s_tn_cld_ne_o,
      'NW': self.s_tn_cld_nw_o,
      'SE': self.s_tn_cld_se_o,
      'SW': self.s_tn_cld_sw_o,
      'IN': self.s_tn_cld_inner_n,
      'IS': self.s_tn_cld_inner_s,
      'IE': self.s_tn_cld_inner_e,
      'IW': self.s_tn_cld_inner_w,
      'INW': self.s_tn_cld_gap_nw,
      'ISE': self.s_tn_cld_gap_se,
      'INE': self.s_tn_cld_gap_ne,
      'ISW': self.s_tn_cld_gap_sw,
      'prevN': self.s_tn_cld_n_i, # These particular cladding exterior surfaces only ever surround the cladding interior surfaces
      'prevS': self.s_tn_cld_s_i, # so those will always be our previous surfaces.
      'prevE': self.s_tn_cld_e_i,
      'prevW': self.s_tn_cld_w_i,
      'prevNE': self.s_tn_cld_ne_i,
      'prevNW': self.s_tn_cld_nw_i,
      'prevSE': self.s_tn_cld_se_i,
      'prevSW': self.s_tn_cld_sw_i,
    }
    # Now generate the same surfaces for the thicker cladding (i.e. around the reflector region)
    # Inner surfaces in the material for use in breaking it up into parts
    self.s_tk_cld_inner_n = openmc.YPlane(name='Inner Surface Y max', y0= c.thickCladSurfInnerHW)
    self.s_tk_cld_inner_s = openmc.YPlane(name='Inner Surface Y min', y0=-c.thickCladSurfInnerHW)
    self.s_tk_cld_inner_e = openmc.XPlane(name='Inner Surface X max', x0= c.thickCladSurfInnerHW)
    self.s_tk_cld_inner_w = openmc.XPlane(name='Inner Surface X min', x0=-c.thickCladSurfInnerHW)
    # First the inside surface of the clad
    self.s_tk_cld_n_i = openmc.YPlane(name='Clad Inside Surface Y max', y0= c.thickCladIR)
    self.s_tk_cld_s_i = openmc.YPlane(name='Clad Inside Surface Y min', y0=-c.thickCladIR)
    self.s_tk_cld_e_i = openmc.XPlane(name='Clad Inside Surface X max', x0= c.thickCladIR)
    self.s_tk_cld_w_i = openmc.XPlane(name='Clad Inside Surface X min', x0=-c.thickCladIR)
    self.s_tk_cld_ne_i = openmc.Plane(name='Clad Inside Surface NE', A= 1, B=1, C=0, D= (math.sqrt(2.0)*c.thickCladChamfDistI))
    self.s_tk_cld_nw_i = openmc.Plane(name='Clad Inside Surface NW', A=-1, B=1, C=0, D= (math.sqrt(2.0)*c.thickCladChamfDistI))
    self.s_tk_cld_se_i = openmc.Plane(name='Clad Inside Surface SE', A=-1, B=1, C=0, D=-(math.sqrt(2.0)*c.thickCladChamfDistI))
    self.s_tk_cld_sw_i = openmc.Plane(name='Clad Inside Surface SW', A= 1, B=1, C=0, D=-(math.sqrt(2.0)*c.thickCladChamfDistI))
    tk_cld_surfs_i = {
      'N': self.s_tk_cld_n_i,
      'S': self.s_tk_cld_s_i,
      'E': self.s_tk_cld_e_i,
      'W': self.s_tk_cld_w_i,
      'NE': self.s_tk_cld_ne_i,
      'NW': self.s_tk_cld_nw_i,
      'SE': self.s_tk_cld_se_i,
      'SW': self.s_tk_cld_sw_i,
      'IN': self.s_tk_cld_inner_n,
      'IS': self.s_tk_cld_inner_s,
      'IE': self.s_tk_cld_inner_e,
      'IW': self.s_tk_cld_inner_w,
    } # Surface currently only used in one case, has no interior surfaces
    # Then the outside surface of the cladding
    self.s_tk_cld_n_o = openmc.YPlane(name='Clad Outside Surface Y max', y0= c.cladOR)
    self.s_tk_cld_s_o = openmc.YPlane(name='Clad Outside Surface Y min', y0=-c.cladOR)
    self.s_tk_cld_e_o = openmc.XPlane(name='Clad Outside Surface X max', x0= c.cladOR)
    self.s_tk_cld_w_o = openmc.XPlane(name='Clad Outside Surface X min', x0=-c.cladOR)
    self.s_tk_cld_ne_o = openmc.Plane(name='Clad Outside Surface NE', A= 1, B=1, C=0, D= (math.sqrt(2.0)*c.cladChamfDistO))
    self.s_tk_cld_nw_o = openmc.Plane(name='Clad Outside Surface NW', A=-1, B=1, C=0, D= (math.sqrt(2.0)*c.cladChamfDistO))
    self.s_tk_cld_se_o = openmc.Plane(name='Clad Outside Surface SE', A=-1, B=1, C=0, D=-(math.sqrt(2.0)*c.cladChamfDistO))
    self.s_tk_cld_sw_o = openmc.Plane(name='Clad Outside Surface SW', A= 1, B=1, C=0, D=-(math.sqrt(2.0)*c.cladChamfDistO))
    # Create some surfaces that will handle the extra material in the cladding (required to keep clad
    # constant thickness everywhere)
    self.s_tk_cld_gap_nw = openmc.Plane(name='NE & SW Chamfers NW Surface', A=-1, B=1, C=0, D= math.sqrt(2.0)*c.thickCladChamfIW/2.0)
    self.s_tk_cld_gap_se = openmc.Plane(name='NE & SW Chamfers SE Surface', A=-1, B=1, C=0, D=-math.sqrt(2.0)*c.thickCladChamfIW/2.0)
    self.s_tk_cld_gap_ne = openmc.Plane(name='NW & SE Chamfers NE Surface', A= 1, B=1, C=0, D= math.sqrt(2.0)*c.thickCladChamfIW/2.0)
    self.s_tk_cld_gap_sw = openmc.Plane(name='NW & SE Chamfers SW Surface', A= 1, B=1, C=0, D=-math.sqrt(2.0)*c.thickCladChamfIW/2.0)
    tk_cld_surfs_o = {
      'N': self.s_tk_cld_n_o,
      'S': self.s_tk_cld_s_o,
      'E': self.s_tk_cld_e_o,
      'W': self.s_tk_cld_w_o,
      'NE': self.s_tk_cld_ne_o,
      'NW': self.s_tk_cld_nw_o,
      'SE': self.s_tk_cld_se_o,
      'SW': self.s_tk_cld_sw_o,
      'IN': self.s_tk_cld_inner_n,
      'IS': self.s_tk_cld_inner_s,
      'IE': self.s_tk_cld_inner_e,
      'IW': self.s_tk_cld_inner_w,
      'INW': self.s_tk_cld_gap_nw,
      'ISE': self.s_tk_cld_gap_se,
      'INE': self.s_tk_cld_gap_ne,
      'ISW': self.s_tk_cld_gap_sw,
      'prevN': self.s_tk_cld_n_i, # These particular cladding exterior surfaces only ever surround the cladding interior surfaces
      'prevS': self.s_tk_cld_s_i, # so those will always be our previous surfaces.
      'prevE': self.s_tk_cld_e_i,
      'prevW': self.s_tk_cld_w_i,
      'prevNE': self.s_tk_cld_ne_i,
      'prevNW': self.s_tk_cld_nw_i,
      'prevSE': self.s_tk_cld_se_i,
      'prevSW': self.s_tk_cld_sw_i,
    }

    # Start generating surfaces for the reflector region
    # First the thick, chamfered region of the reflector block
    # Inner surfaces in the fuel assembly for use in breaking it up into parts
    self.s_plug_ref_inner_n = openmc.YPlane(name='Inner Surface Y max', y0= c.mainPlugSurfHW)
    self.s_plug_ref_inner_s = openmc.YPlane(name='Inner Surface Y min', y0=-c.mainPlugSurfHW)
    self.s_plug_ref_inner_e = openmc.XPlane(name='Inner Surface X max', x0= c.mainPlugSurfHW)
    self.s_plug_ref_inner_w = openmc.XPlane(name='Inner Surface X min', x0=-c.mainPlugSurfHW)
    # First the outside surface of the graphite block
    self.s_plug_ref_n_o = openmc.YPlane(name='Refl Plug Outside Surface Y max', y0= c.PlugHW)
    self.s_plug_ref_s_o = openmc.YPlane(name='Refl Plug Outside Surface Y min', y0=-c.PlugHW)
    self.s_plug_ref_e_o = openmc.XPlane(name='Refl Plug Outside Surface X max', x0= c.PlugHW)
    self.s_plug_ref_w_o = openmc.XPlane(name='Refl Plug Outside Surface X min', x0=-c.PlugHW)
    self.s_plug_ref_ne_o = openmc.Plane(name='Refl Plug Outside Surface NE', A= 1, B=1, C=0, D= (math.sqrt(2.0)*c.plugChamfDist))
    self.s_plug_ref_nw_o = openmc.Plane(name='Refl Plug Outside Surface NW', A=-1, B=1, C=0, D= (math.sqrt(2.0)*c.plugChamfDist))
    self.s_plug_ref_se_o = openmc.Plane(name='Refl Plug Outside Surface SE', A=-1, B=1, C=0, D=-(math.sqrt(2.0)*c.plugChamfDist))
    self.s_plug_ref_sw_o = openmc.Plane(name='Refl Plug Outside Surface SW', A= 1, B=1, C=0, D=-(math.sqrt(2.0)*c.plugChamfDist))
    plug_ref_surfs_o = {
      'N': self.s_plug_ref_n_o,
      'S': self.s_plug_ref_s_o,
      'E': self.s_plug_ref_e_o,
      'W': self.s_plug_ref_w_o,
      'NE': self.s_plug_ref_ne_o,
      'NW': self.s_plug_ref_nw_o,
      'SE': self.s_plug_ref_se_o,
      'SW': self.s_plug_ref_sw_o,
      'IN': self.s_plug_ref_inner_n,
      'IS': self.s_plug_ref_inner_s,
      'IE': self.s_plug_ref_inner_e,
      'IW': self.s_plug_ref_inner_w,
    } # There are different possibilities for the interior surfs. The groups will be set up at the end of radial surf definition
    # Then the inside surface of the cladding
    self.s_plug_clad_n_i = openmc.YPlane(name='Tk Clad Inside Surface Y max', y0= c.thickCladIR)
    self.s_plug_clad_s_i = openmc.YPlane(name='Tk Clad Inside Surface Y min', y0=-c.thickCladIR)
    self.s_plug_clad_e_i = openmc.XPlane(name='Tk Clad Inside Surface X max', x0= c.thickCladIR)
    self.s_plug_clad_w_i = openmc.XPlane(name='Tk Clad Inside Surface X min', x0=-c.thickCladIR)
    self.s_plug_clad_ne_i = openmc.Plane(name='Tk Clad Inside Surface NE', A= 1, B=1, C=0, D= (math.sqrt(2.0)*c.thickCladChamfDistI))
    self.s_plug_clad_nw_i = openmc.Plane(name='Tk Clad Inside Surface NW', A=-1, B=1, C=0, D= (math.sqrt(2.0)*c.thickCladChamfDistI))
    self.s_plug_clad_se_i = openmc.Plane(name='Tk Clad Inside Surface SE', A=-1, B=1, C=0, D=-(math.sqrt(2.0)*c.thickCladChamfDistI))
    self.s_plug_clad_sw_i = openmc.Plane(name='Tk Clad Inside Surface SW', A= 1, B=1, C=0, D=-(math.sqrt(2.0)*c.thickCladChamfDistI))
    # Create some surfaces that will handle the extra material in the gap and cladding (required to keep gap and clad
    # constant thickness everywhere)
    self.s_plug_gap_nw = openmc.Plane(name='Gap NE & SW Chamfers NW Surface', A=-1, B=1, C=0, D= math.sqrt(2.0)*c.PlugChamfOW/2.0)
    self.s_plug_gap_se = openmc.Plane(name='Gap NE & SW Chamfers SE Surface', A=-1, B=1, C=0, D=-math.sqrt(2.0)*c.PlugChamfOW/2.0)
    self.s_plug_gap_ne = openmc.Plane(name='Gap NW & SE Chamfers NE Surface', A= 1, B=1, C=0, D= math.sqrt(2.0)*c.PlugChamfOW/2.0)
    self.s_plug_gap_sw = openmc.Plane(name='Gap NW & SE Chamfers SW Surface', A= 1, B=1, C=0, D=-math.sqrt(2.0)*c.PlugChamfOW/2.0)
    plug_clad_surfs_i = {
      'N': self.s_plug_clad_n_i,
      'S': self.s_plug_clad_s_i,
      'E': self.s_plug_clad_e_i,
      'W': self.s_plug_clad_w_i,
      'NE': self.s_plug_clad_ne_i,
      'NW': self.s_plug_clad_nw_i,
      'SE': self.s_plug_clad_se_i,
      'SW': self.s_plug_clad_sw_i,
      'IN': self.s_plug_ref_inner_n,
      'IS': self.s_plug_ref_inner_s,
      'IE': self.s_plug_ref_inner_e,
      'IW': self.s_plug_ref_inner_w,
      'INW': self.s_plug_gap_nw,
      'ISE': self.s_plug_gap_se,
      'INE': self.s_plug_gap_ne,
      'ISW': self.s_plug_gap_sw,
      'prevN': self.s_plug_ref_n_o, # These particular cladding inside surfaces only ever surround the reflector plugs
      'prevS': self.s_plug_ref_s_o, # so those will always be our previous surfaces.
      'prevE': self.s_plug_ref_e_o,
      'prevW': self.s_plug_ref_w_o,
      'prevNE': self.s_plug_ref_ne_o,
      'prevNW': self.s_plug_ref_nw_o,
      'prevSE': self.s_plug_ref_se_o,
      'prevSW': self.s_plug_ref_sw_o,
    }
    # Then the outside surface of the cladding
    self.s_plug_clad_n_o = openmc.YPlane(name='Clad Outside Surface Y max', y0= c.cladOR)
    self.s_plug_clad_s_o = openmc.YPlane(name='Clad Outside Surface Y min', y0=-c.cladOR)
    self.s_plug_clad_e_o = openmc.XPlane(name='Clad Outside Surface X max', x0= c.cladOR)
    self.s_plug_clad_w_o = openmc.XPlane(name='Clad Outside Surface X min', x0=-c.cladOR)
    self.s_plug_clad_ne_o = openmc.Plane(name='Clad Outside Surface NE', A= 1, B=1, C=0, D= (math.sqrt(2.0)*c.cladChamfDistO))
    self.s_plug_clad_nw_o = openmc.Plane(name='Clad Outside Surface NW', A=-1, B=1, C=0, D= (math.sqrt(2.0)*c.cladChamfDistO))
    self.s_plug_clad_se_o = openmc.Plane(name='Clad Outside Surface SE', A=-1, B=1, C=0, D=-(math.sqrt(2.0)*c.cladChamfDistO))
    self.s_plug_clad_sw_o = openmc.Plane(name='Clad Outside Surface SW', A= 1, B=1, C=0, D=-(math.sqrt(2.0)*c.cladChamfDistO))
    # Create some surfaces that will handle the extra material in the gap and cladding (required to keep gap and clad
    # constant thickness everywhere)
    clad_chamf_dist = c.PlugChamfOW/2.0 + c.TANPI8 * (c.thickCladIR - c.PlugHW)
    clad_long_dist = c.mainPlugSurfHW + c.TANPI8 * (c.thickCladIR - c.PlugHW)
    self.s_plug_clad_nw = openmc.Plane(name='Clad NE & SW Chamfers NW Surface', A=-1, B=1, C=0, D= math.sqrt(2.0)*clad_chamf_dist)
    self.s_plug_clad_se = openmc.Plane(name='Clad NE & SW Chamfers SE Surface', A=-1, B=1, C=0, D=-math.sqrt(2.0)*clad_chamf_dist)
    self.s_plug_clad_ne = openmc.Plane(name='Clad NW & SE Chamfers NE Surface', A= 1, B=1, C=0, D= math.sqrt(2.0)*clad_chamf_dist)
    self.s_plug_clad_sw = openmc.Plane(name='Clad NW & SE Chamfers SW Surface', A= 1, B=1, C=0, D=-math.sqrt(2.0)*clad_chamf_dist)
    self.s_plug_c_inner_n = openmc.YPlane(name='Inner Surface Y max', y0= clad_long_dist)
    self.s_plug_c_inner_s = openmc.YPlane(name='Inner Surface Y min', y0=-clad_long_dist)
    self.s_plug_c_inner_e = openmc.XPlane(name='Inner Surface X max', x0= clad_long_dist)
    self.s_plug_c_inner_w = openmc.XPlane(name='Inner Surface X min', x0=-clad_long_dist)
    plug_clad_surfs_o = {
      'N': self.s_plug_clad_n_o,
      'S': self.s_plug_clad_s_o,
      'E': self.s_plug_clad_e_o,
      'W': self.s_plug_clad_w_o,
      'NE': self.s_plug_clad_ne_o,
      'NW': self.s_plug_clad_nw_o,
      'SE': self.s_plug_clad_se_o,
      'SW': self.s_plug_clad_sw_o,
      'IN': self.s_plug_c_inner_n,
      'IS': self.s_plug_c_inner_s,
      'IE': self.s_plug_c_inner_e,
      'IW': self.s_plug_c_inner_w,
      'INW': self.s_plug_clad_nw,
      'ISE': self.s_plug_clad_se,
      'INE': self.s_plug_clad_ne,
      'ISW': self.s_plug_clad_sw,
      'prevN': self.s_plug_clad_n_i, # While the outer plug clad surfaces two different groups of interior clad surfaces
      'prevS': self.s_plug_clad_s_i, # (plug_clad_surfs_i & Mplug_clad_surfs_i), the key N/E/S/W/NE/SE/SW/NW surfaces are
      'prevE': self.s_plug_clad_e_i, # the same, so we don't need to generate multiple groups of surfaces for this base
      'prevW': self.s_plug_clad_w_i,
      'prevNE': self.s_plug_clad_ne_i,
      'prevNW': self.s_plug_clad_nw_i,
      'prevSE': self.s_plug_clad_se_i,
      'prevSW': self.s_plug_clad_sw_i,
    }
    # Interior cylindrical hole through the top reflector segment
    self.s_ref_element_IR = openmc.ZCylinder(name='Top Reflector Interior Hole IR', R=c.topShortPlugIR)
    # Outgas tube surfaces
    self.s_offgas_tube_IR = openmc.ZCylinder(name='Offgas tube IR', R=c.offGasTubeIR)
    self.s_offgas_tube_OR = openmc.ZCylinder(name='Offgas tube OR', R=c.offGasTubeOR)
    self.s_offgas_crimp_OR = openmc.ZCylinder(name='Offgas tube crimped top OR', R=c.offGasCladW)
    # Create the surfaces for the square machined part of the short plug
    self.s_Mplug_n = openmc.YPlane(name='Machined Short Plug Outside Surface Y max', y0= c.plugMachinedHW)
    self.s_Mplug_s = openmc.YPlane(name='Machined Short Plug Outside Surface Y min', y0=-c.plugMachinedHW)
    self.s_Mplug_e = openmc.XPlane(name='Machined Short Plug Outside Surface X max', x0= c.plugMachinedHW)
    self.s_Mplug_w = openmc.XPlane(name='Machined Short Plug Outside Surface X min', x0=-c.plugMachinedHW)
    Mplug_surfs = {
      'N': self.s_Mplug_n,
      'S': self.s_Mplug_s,
      'E': self.s_Mplug_e,
      'W': self.s_Mplug_w,
    } # There are different possibilities for the interior surfs. The groups will be set up at the end of radial surf definition
    # The following is a dummy surface used solely as a hack to check which of the two cases we are working with
    # when building the surfaces for the space between an inner box and an outer octagon. The key part is that it
    # is an x, y, or z plane with x0 / y0 / z0 = -1.0 * full_width_of_the_chamfered_surface_of_the_outer_octagon
    self.s_Mplug_dummy_chamf_width = openmc.XPlane(name='Dummy Surface for Case Check', x0=c.thickCladChamfIW)
    # Now pack up the other surfaces we need for the outer cladding
    Mplug_clad_surfs_i = {
      'N': self.s_plug_clad_n_i,
      'S': self.s_plug_clad_s_i,
      'E': self.s_plug_clad_e_i,
      'W': self.s_plug_clad_w_i,
      'NE': self.s_plug_clad_ne_i,
      'NW': self.s_plug_clad_nw_i,
      'SE': self.s_plug_clad_se_i,
      'SW': self.s_plug_clad_sw_i,
      'IN': self.s_plug_c_inner_n,
      'IS': self.s_plug_c_inner_s,
      'IE': self.s_plug_c_inner_e,
      'IW': self.s_plug_c_inner_w,
      'Dummy': self.s_Mplug_dummy_chamf_width,
      'prevN': self.s_Mplug_n, # These particular cladding inside surfaces only ever surround the machined reflector plugs
      'prevS': self.s_Mplug_s, # so those will always be our previous surfaces.
      'prevE': self.s_Mplug_e,
      'prevW': self.s_Mplug_w,
    }

    # Set up some radial surfaces for the access hole dummy elements
    # First, the center box section
    self.s_accessCenter_n = openmc.YPlane(name='Access Element Central Region Surface Y max', y0= c.cladIR)
    self.s_accessCenter_s = openmc.YPlane(name='Access Element Central Region Surface Y min', y0=-c.cladIR)
    self.s_accessCenter_e = openmc.XPlane(name='Access Element Central Region Surface X max', x0= c.accessWindowHW)
    self.s_accessCenter_w = openmc.XPlane(name='Access Element Central Region Surface X min', x0=-c.accessWindowHW)
    accessCenter_surfs = {
      'N': self.s_accessCenter_n,
      'S': self.s_accessCenter_s,
      'E': self.s_accessCenter_e,
      'W': self.s_accessCenter_w,
    }
    # The north window section
    self.s_accessWindowN_n = openmc.YPlane(name='Access Element North Window Surface Y max', y0= c.cladOR)
    accessWindowN_surfs = {
      'N': self.s_accessWindowN_n,
      'S': self.s_accessCenter_n,
      'E': self.s_accessCenter_e,
      'W': self.s_accessCenter_w,
    }
    # The south window section
    self.s_accessWindowS_s = openmc.YPlane(name='Access Element South Window Surface Y min', y0=-c.cladOR)
    accessWindowS_surfs = {
      'N': self.s_accessCenter_s,
      'S': self.s_accessWindowS_s,
      'E': self.s_accessCenter_e,
      'W': self.s_accessCenter_w,
    }
    # Create the surfaces that will allow us to build our exterior cladding
    accessClad_surfs_o = deepcopy(clad_surfs_o)
    accessClad_surfs_o['windowE'] = self.s_accessCenter_e
    accessClad_surfs_o['windowW'] = self.s_accessCenter_w
    # Begin creating the monstrosity that are the surfaces that will define the parts of the interior of the access hole
    # dummy element that contains the stiffener component.
    accessStiff_surfs = deepcopy(tn_cld_surfs_i)
    accessStiff_surfs['windowE'] = self.s_accessCenter_e
    accessStiff_surfs['windowW'] = self.s_accessCenter_w
    self.s_accessStiffWall_n = openmc.YPlane(name='Access Element Stiffener Wall Section Y max', y0= c.accessStiffHW)
    self.s_accessStiffWall_s = openmc.YPlane(name='Access Element Stiffener Wall Section Y min', y0=-c.accessStiffHW)
    accessStiff_surfs['stiffWallN'] = self.s_accessStiffWall_n
    accessStiff_surfs['stiffWallS'] = self.s_accessStiffWall_s
    self.s_accessStiffWall_e = openmc.XPlane(name='Access Element East Stiffener Wall Section X min', x0= c.accessStiffWallDist)
    self.s_accessStiffWall_w = openmc.XPlane(name='Access Element West Stiffener Wall Section X max', x0=-c.accessStiffWallDist)
    accessStiff_surfs['stiffWallE'] = self.s_accessStiffWall_e
    accessStiff_surfs['stiffWallW'] = self.s_accessStiffWall_w
    self.s_accessStiffMainInner_e = openmc.XPlane(name='Access Element East Stiffener Main Section, Wall Facing Surface X',
                                                  x0= c.accessStiffMainInnerDist)
    self.s_accessStiffMainInner_w = openmc.XPlane(name='Access Element West Stiffener Main Section, Wall Facing Surface X',
                                                  x0=-c.accessStiffMainInnerDist)
    self.s_accessStiffMainOuter_e = openmc.XPlane(name='Access Element East Stiffener Main Section, Center Facing Surface X',
                                                  x0= c.accessStiffMainOuterDist)
    self.s_accessStiffMainOuter_w = openmc.XPlane(name='Access Element West Stiffener Main Section, Center Facing Surface X',
                                                  x0=-c.accessStiffMainOuterDist)
    accessStiff_surfs['stiffMainCenterE'] = self.s_accessStiffMainOuter_e
    accessStiff_surfs['stiffMainCenterW'] = self.s_accessStiffMainOuter_w
    accessStiff_surfs['stiffMainWallE'] = self.s_accessStiffMainInner_e
    accessStiff_surfs['stiffMainWallW'] = self.s_accessStiffMainInner_w
    self.s_accessStiffAngled_ne_o = openmc.Plane(name='Access Element Stiffener Angled Section, Center Facing Surface NE',
                                                 A= 1, B=1, C=0, D= (math.sqrt(2.0)*c.accessStiffAngleCenterDist))
    self.s_accessStiffAngled_nw_o = openmc.Plane(name='Access Element Stiffener Angled Section, Center Facing Surface NW',
                                                 A=-1, B=1, C=0, D= (math.sqrt(2.0)*c.accessStiffAngleCenterDist))
    self.s_accessStiffAngled_se_o = openmc.Plane(name='Access Element Stiffener Angled Section, Center Facing Surface SE',
                                                 A=-1, B=1, C=0, D=-(math.sqrt(2.0)*c.accessStiffAngleCenterDist))
    self.s_accessStiffAngled_sw_o = openmc.Plane(name='Access Element Stiffener Angled Section, Center Facing Surface SW',
                                                 A= 1, B=1, C=0, D=-(math.sqrt(2.0)*c.accessStiffAngleCenterDist))
    self.s_accessStiffAngled_ne_i = openmc.Plane(name='Access Element Stiffener Angled Section, Wall Facing Surface NE',
                                                 A= 1, B=1, C=0, D= (math.sqrt(2.0)*c.accessStiffAngleWallDist))
    self.s_accessStiffAngled_nw_i = openmc.Plane(name='Access Element Stiffener Angled Section, Wall Facing Surface NW',
                                                 A=-1, B=1, C=0, D= (math.sqrt(2.0)*c.accessStiffAngleWallDist))
    self.s_accessStiffAngled_se_i = openmc.Plane(name='Access Element Stiffener Angled Section, Wall Facing Surface SE',
                                                 A=-1, B=1, C=0, D=-(math.sqrt(2.0)*c.accessStiffAngleWallDist))
    self.s_accessStiffAngled_sw_i = openmc.Plane(name='Access Element Stiffener Angled Section, Wall Facing Surface SW',
                                                 A= 1, B=1, C=0, D=-(math.sqrt(2.0)*c.accessStiffAngleWallDist))
    accessStiff_surfs['stiffCenterNE'] = self.s_accessStiffAngled_ne_o
    accessStiff_surfs['stiffCenterNW'] = self.s_accessStiffAngled_nw_o
    accessStiff_surfs['stiffCenterSE'] = self.s_accessStiffAngled_se_o
    accessStiff_surfs['stiffCenterSW'] = self.s_accessStiffAngled_sw_o
    accessStiff_surfs['stiffWallNE'] = self.s_accessStiffAngled_ne_i
    accessStiff_surfs['stiffWallNW'] = self.s_accessStiffAngled_nw_i
    accessStiff_surfs['stiffWallSE'] = self.s_accessStiffAngled_se_i
    accessStiff_surfs['stiffWallSW'] = self.s_accessStiffAngled_sw_i

    # Radial surfaces for the top fuel fitting
    # Innermost octagon
    d = math.sqrt(2)*(c.tff_base_origin_to_outer_edge - c.tff_base_thick)
    self.s_reg_tff_base_n_i = openmc.YPlane(name='Top fuel fitting Base Inside Surface Y max', y0=+c.tff_base_radius_i)
    self.s_reg_tff_base_s_i = openmc.YPlane(name='Top fuel fitting Base Inside Surface Y min', y0=-c.tff_base_radius_i)
    self.s_reg_tff_base_e_i = openmc.XPlane(name='Top fuel fitting Base Inside Surface X max', x0=+c.tff_base_radius_i)
    self.s_reg_tff_base_w_i = openmc.XPlane(name='Top fuel fitting Base Inside Surface X min', x0=-c.tff_base_radius_i)
    self.s_reg_tff_base_ne_i = openmc.Plane(name='Top fuel fitting Base Inside Surface NE', A=1, B=1, C=0, D=d)
    self.s_reg_tff_base_nw_i = openmc.Plane(name='Top fuel fitting Base Inside Surface NW', A=-1, B=1, C=0, D=d)
    self.s_reg_tff_base_se_i = openmc.Plane(name='Top fuel fitting Base Inside Surface SE', A=-1, B=1, C=0, D=-d)
    self.s_reg_tff_base_sw_i = openmc.Plane(name='Top fuel fitting Base Inside Surface SW', A=1, B=1, C=0, D=-d)

    base_long_dist = c.tff_base_radius_i - c.tff_base_corner_length_i/math.sqrt(2)
    self.s_reg_tff_base_inner_n = openmc.YPlane(name='Top fuel fitting Base Inner Square Y max', y0=+base_long_dist)
    self.s_reg_tff_base_inner_s = openmc.YPlane(name='Top fuel fitting Base Inner Square Y min', y0=-base_long_dist)
    self.s_reg_tff_base_inner_e = openmc.XPlane(name='Top fuel fitting Base Inner Square X max', x0=+base_long_dist)
    self.s_reg_tff_base_inner_w = openmc.XPlane(name='Top fuel fitting Base Inner Square X min', x0=-base_long_dist)

    reg_tff_base_surfs_i = {
      'N': self.s_reg_tff_base_n_i,
      'S': self.s_reg_tff_base_s_i,
      'E': self.s_reg_tff_base_e_i,
      'W': self.s_reg_tff_base_w_i,
      'NE': self.s_reg_tff_base_ne_i,
      'NW': self.s_reg_tff_base_nw_i,
      'SE': self.s_reg_tff_base_se_i,
      'SW': self.s_reg_tff_base_sw_i,
      'IN': self.s_reg_tff_base_inner_n,
      'IS': self.s_reg_tff_base_inner_s,
      'IE': self.s_reg_tff_base_inner_e,
      'IW': self.s_reg_tff_base_inner_w,
    }

    # Outermost octagon
    d = math.sqrt(2)*c.tff_base_origin_to_outer_edge
    self.s_reg_tff_base_n_o = openmc.YPlane(name='Top fuel fitting Base Outside Surface Y max', y0=+c.tff_base_radius_o)
    self.s_reg_tff_base_s_o = openmc.YPlane(name='Top fuel fitting Base Outside Surface Y min', y0=-c.tff_base_radius_o)
    self.s_reg_tff_base_e_o = openmc.XPlane(name='Top fuel fitting Base Outside Surface X max', x0=+c.tff_base_radius_o)
    self.s_reg_tff_base_w_o = openmc.XPlane(name='Top fuel fitting Base Outside Surface X min', x0=-c.tff_base_radius_o)
    self.s_reg_tff_base_ne_o = openmc.Plane(name='Top fuel fitting Base Outside Surface NE', A=1, B=1, C=0, D=d)
    self.s_reg_tff_base_nw_o = openmc.Plane(name='Top fuel fitting Base Outside Surface NW', A=-1, B=1, C=0, D=d)
    self.s_reg_tff_base_se_o = openmc.Plane(name='Top fuel fitting Base Outside Surface SE', A=-1, B=1, C=0, D=-d)
    self.s_reg_tff_base_sw_o = openmc.Plane(name='Top fuel fitting Base Outside Surface SW', A=1, B=1, C=0, D=-d)
    # Create some surfaces that will handle the extra material in the gap and cladding (required to keep gap and clad
    # constant thickness everywhere)
    d = c.tff_base_corner_length_i/math.sqrt(2)
    self.s_reg_tff_base_nw = openmc.Plane(name='Top fuel fittingNE & SW Chamfers NW Surface', A=-1, B=1, C=0, D=d)
    self.s_reg_tff_base_se = openmc.Plane(name='Top fuel fittingNE & SW Chamfers SE Surface', A=-1, B=1, C=0, D=-d)
    self.s_reg_tff_base_ne = openmc.Plane(name='Top fuel fittingNW & SE Chamfers NE Surface', A=1, B=1, C=0, D=d)
    self.s_reg_tff_base_sw = openmc.Plane(name='Top fuel fittingNW & SE Chamfers SW Surface', A=1, B=1, C=0, D=-d)

    reg_tff_base_surfs_o = {'N': self.s_reg_tff_base_n_o,
                            'S': self.s_reg_tff_base_s_o,
                            'E': self.s_reg_tff_base_e_o,
                            'W': self.s_reg_tff_base_w_o,
                            'NE': self.s_reg_tff_base_ne_o,
                            'NW': self.s_reg_tff_base_nw_o,
                            'SE': self.s_reg_tff_base_se_o,
                            'SW': self.s_reg_tff_base_sw_o,
                            'IN': self.s_reg_tff_base_inner_n,
                            'IS': self.s_reg_tff_base_inner_s,
                            'IE': self.s_reg_tff_base_inner_e,
                            'IW': self.s_reg_tff_base_inner_w,
                            'INW': self.s_reg_tff_base_nw,
                            'ISE': self.s_reg_tff_base_se,
                            'INE': self.s_reg_tff_base_ne,
                            'ISW': self.s_reg_tff_base_sw,
                            'prevN': self.s_reg_tff_base_n_i,
                            'prevS': self.s_reg_tff_base_s_i,
                            'prevE': self.s_reg_tff_base_e_i,
                            'prevW': self.s_reg_tff_base_w_i,
                            'prevNE': self.s_reg_tff_base_ne_i,
                            'prevNW': self.s_reg_tff_base_nw_i,
                            'prevSE': self.s_reg_tff_base_se_i,
                            'prevSW': self.s_reg_tff_base_sw_i,
                            }

    # Next region: cone-mid (or pyra-mid :P)
    # Use the average thickness across the sloped region
    # Innermost octagon
    d = math.sqrt(2)*(c.tff_mid_origin_to_outer_edge - c.tff_mid_thick)
    self.s_reg_tff_mid_n_i = openmc.YPlane(name='Top fuel fitting Middle Cone Inside Surface Y max', y0=+c.tff_mid_radius_i)
    self.s_reg_tff_mid_s_i = openmc.YPlane(name='Top fuel fitting Middle Cone Inside Surface Y min', y0=-c.tff_mid_radius_i)
    self.s_reg_tff_mid_e_i = openmc.XPlane(name='Top fuel fitting Middle Cone Inside Surface X max', x0=+c.tff_mid_radius_i)
    self.s_reg_tff_mid_w_i = openmc.XPlane(name='Top fuel fitting Middle Cone Inside Surface X min', x0=-c.tff_mid_radius_i)
    self.s_reg_tff_mid_ne_i = openmc.Plane(name='Top fuel fitting Middle Cone Inside Surface NE', A=1, B=1, C=0, D=d)
    self.s_reg_tff_mid_nw_i = openmc.Plane(name='Top fuel fitting Middle Cone Inside Surface NW', A=-1, B=1, C=0, D=d)
    self.s_reg_tff_mid_se_i = openmc.Plane(name='Top fuel fitting Middle Cone Inside Surface SE', A=-1, B=1, C=0, D=-d)
    self.s_reg_tff_mid_sw_i = openmc.Plane(name='Top fuel fitting Middle Cone Inside Surface SW', A=1, B=1, C=0, D=-d)

    mid_long_dist = c.tff_mid_radius_i - c.tff_mid_corner_length_i/math.sqrt(2)
    self.s_reg_tff_mid_inner_n = openmc.YPlane(name='mid Inner Square Y max', y0=+mid_long_dist)
    self.s_reg_tff_mid_inner_s = openmc.YPlane(name='mid Inner Square Y min', y0=-mid_long_dist)
    self.s_reg_tff_mid_inner_e = openmc.XPlane(name='mid Inner Square X max', x0=+mid_long_dist)
    self.s_reg_tff_mid_inner_w = openmc.XPlane(name='mid Inner Square X min', x0=-mid_long_dist)

    reg_tff_mid_surfs_i = {
      'N': self.s_reg_tff_mid_n_i,
      'S': self.s_reg_tff_mid_s_i,
      'E': self.s_reg_tff_mid_e_i,
      'W': self.s_reg_tff_mid_w_i,
      'NE': self.s_reg_tff_mid_ne_i,
      'NW': self.s_reg_tff_mid_nw_i,
      'SE': self.s_reg_tff_mid_se_i,
      'SW': self.s_reg_tff_mid_sw_i,
      'IN': self.s_reg_tff_mid_inner_n,
      'IS': self.s_reg_tff_mid_inner_s,
      'IE': self.s_reg_tff_mid_inner_e,
      'IW': self.s_reg_tff_mid_inner_w,
    }

    # Outermost octagon
    d = math.sqrt(2)*c.tff_mid_origin_to_outer_edge
    self.s_reg_tff_mid_n_o = openmc.YPlane(name='Top fuel fitting Middle Cone Outside Surface Y max', y0=+c.tff_mid_radius_o)
    self.s_reg_tff_mid_s_o = openmc.YPlane(name='Top fuel fitting Middle Cone Outside Surface Y min', y0=-c.tff_mid_radius_o)
    self.s_reg_tff_mid_e_o = openmc.XPlane(name='Top fuel fitting Middle Cone Outside Surface X max', x0=+c.tff_mid_radius_o)
    self.s_reg_tff_mid_w_o = openmc.XPlane(name='Top fuel fitting Middle Cone Outside Surface X min', x0=-c.tff_mid_radius_o)
    self.s_reg_tff_mid_ne_o = openmc.Plane(name='Top fuel fitting Middle Cone Outside Surface NE', A=1, B=1, C=0, D=d)
    self.s_reg_tff_mid_nw_o = openmc.Plane(name='Top fuel fitting Middle Cone Outside Surface NW', A=-1, B=1, C=0, D=d)
    self.s_reg_tff_mid_se_o = openmc.Plane(name='Top fuel fitting Middle Cone Outside Surface SE', A=-1, B=1, C=0, D=-d)
    self.s_reg_tff_mid_sw_o = openmc.Plane(name='Top fuel fitting Middle Cone Outside Surface SW', A=1, B=1, C=0, D=-d)
    # Create some surfaces that will handle the extra material in the gap and cladding (required to keep gap and clad
    # constant thickness everywhere)
    d = c.tff_mid_corner_length_i/math.sqrt(2)
    self.s_reg_tff_mid_nw = openmc.Plane(name='Top fuel fitting NE & SW Chamfers NW Surface', A=-1, B=1, C=0, D=d)
    self.s_reg_tff_mid_se = openmc.Plane(name='Top fuel fitting NE & SW Chamfers SE Surface', A=-1, B=1, C=0, D=-d)
    self.s_reg_tff_mid_ne = openmc.Plane(name='Top fuel fitting NW & SE Chamfers NE Surface', A=1, B=1, C=0, D=d)
    self.s_reg_tff_mid_sw = openmc.Plane(name='Top fuel fitting NW & SE Chamfers SW Surface', A=1, B=1, C=0, D=-d)

    reg_tff_mid_surfs_o = {'N': self.s_reg_tff_mid_n_o,
                           'S': self.s_reg_tff_mid_s_o,
                           'E': self.s_reg_tff_mid_e_o,
                           'W': self.s_reg_tff_mid_w_o,
                           'NE': self.s_reg_tff_mid_ne_o,
                           'NW': self.s_reg_tff_mid_nw_o,
                           'SE': self.s_reg_tff_mid_se_o,
                           'SW': self.s_reg_tff_mid_sw_o,
                           'IN': self.s_reg_tff_mid_inner_n,
                           'IS': self.s_reg_tff_mid_inner_s,
                           'IE': self.s_reg_tff_mid_inner_e,
                           'IW': self.s_reg_tff_mid_inner_w,
                           'INW': self.s_reg_tff_mid_nw,
                           'ISE': self.s_reg_tff_mid_se,
                           'INE': self.s_reg_tff_mid_ne,
                           'ISW': self.s_reg_tff_mid_sw,
                           'prevN': self.s_reg_tff_mid_n_i,
                           'prevS': self.s_reg_tff_mid_s_i,
                           'prevE': self.s_reg_tff_mid_e_i,
                           'prevW': self.s_reg_tff_mid_w_i,
                           'prevNE': self.s_reg_tff_mid_ne_i,
                           'prevNW': self.s_reg_tff_mid_nw_i,
                           'prevSE': self.s_reg_tff_mid_se_i,
                           'prevSW': self.s_reg_tff_mid_sw_i,
                           }

    # Cylinder
    self.s_reg_tff_neck_i = openmc.ZCylinder(name="Top fuel fitting neck IR", R=c.tff_neck_radius_i)
    self.s_reg_tff_neck_o = openmc.ZCylinder(name="Top fuel fitting neck OR", R=c.tff_neck_radius_o)
    reg_tff_neck_surfs = {'R': self.s_reg_tff_neck_o, 'prevR': self.s_reg_tff_neck_i}
    # Innermost cylinder
    self.s_reg_tff_cone_top_i = openmc.ZCylinder(name="Top fuel top cone IR", R=c.tff_cone_top_radius_i)
    self.s_reg_tff_cone_top_o = openmc.ZCylinder(name="Top fuel top cone OR", R=c.tff_cone_top_radius_o)
    reg_tff_cone_top_surfs = {'R': self.s_reg_tff_cone_top_o, 'prevR': self.s_reg_tff_cone_top_i}


    # Radial surfaces for the bottom fuel fitting
    # Base (octagon)
    d = math.sqrt(2)*c.bff_base_origin_to_outer_edge
    self.s_reg_bff_base_n = openmc.YPlane(name='Bottom fuel fitting Base Outside Surface Y max', y0=+c.bff_base_radius)
    self.s_reg_bff_base_s = openmc.YPlane(name='Bottom fuel fitting Base Outside Surface Y min', y0=-c.bff_base_radius)
    self.s_reg_bff_base_e = openmc.XPlane(name='Bottom fuel fitting Base Outside Surface X max', x0=+c.bff_base_radius)
    self.s_reg_bff_base_w = openmc.XPlane(name='Bottom fuel fitting Base Outside Surface X min', x0=-c.bff_base_radius)
    self.s_reg_bff_base_ne = openmc.Plane(name='Bottom fuel fitting Base Outside Surface NE', A=1, B=1, C=0, D=d)
    self.s_reg_bff_base_nw = openmc.Plane(name='Bottom fuel fitting Base Outside Surface NW', A=-1, B=1, C=0, D=d)
    self.s_reg_bff_base_se = openmc.Plane(name='Bottom fuel fitting Base Outside Surface SE', A=-1, B=1, C=0, D=-d)
    self.s_reg_bff_base_sw = openmc.Plane(name='Bottom fuel fitting Base Outside Surface SW', A=1, B=1, C=0, D=-d)

    base_long_dist = c.bff_base_radius - c.bff_base_corner_length/math.sqrt(2)
    self.s_reg_bffbase_inner_n = openmc.YPlane(name='Bottom fuel fitting Base Inner Square Y max', y0=+base_long_dist)
    self.s_reg_bffbase_inner_s = openmc.YPlane(name='Bottom fuel fitting Base Inner Square Y min', y0=-base_long_dist)
    self.s_reg_bffbase_inner_e = openmc.XPlane(name='Bottom fuel fitting Base Inner Square X max', x0=+base_long_dist)
    self.s_reg_bffbase_inner_w = openmc.XPlane(name='Bottom fuel fitting Base Inner Square X min', x0=-base_long_dist)

    reg_bff_base_surfs = {
      'N': self.s_reg_bff_base_n,
      'S': self.s_reg_bff_base_s,
      'E': self.s_reg_bff_base_e,
      'W': self.s_reg_bff_base_w,
      'NE': self.s_reg_bff_base_ne,
      'NW': self.s_reg_bff_base_nw,
      'SE': self.s_reg_bff_base_se,
      'SW': self.s_reg_bff_base_sw,
      'IN': self.s_reg_bffbase_inner_n,
      'IS': self.s_reg_bffbase_inner_s,
      'IE': self.s_reg_bffbase_inner_e,
      'IW': self.s_reg_bffbase_inner_w,
    }

    # Cone (cylinder)
    self.s_reg_bff_cone = openmc.ZCylinder(name="Bottom fuel fitting cone (avg.)", R=c.bff_cone_radius)
    # Prong (cylinder), ignoring the narrowing at the tip
    self.s_reg_bff_prong = openmc.ZCylinder(name="Bottom fuel fitting prong", R=c.bff_prong_radius)

    # Half-width bottom fuel fitting dimensions
    # Cone (cylinder)
    self.s_hw_bff_cone = openmc.ZCylinder(name="Half-width bottom fuel fitting cone (avg.)",
                                          R=c.hw_bff_cone_radius)
    # Prong (cylinder)
    self.s_hw_bff_prong = openmc.ZCylinder(name="Half-width bottom fuel fitting prong",
                                           R=c.hw_bff_prong_radius)
    # Tip (sphere)
    self.s_hw_bff_tip = openmc.Sphere(name="Half-width bottom fuel fitting tip",
                                      R=c.hw_support_pin_bff_r, z0=c.struct_hw_bff_sphere_top)


    # Radial surfaces for the Half-width lead brick
    # Innermost octagon
    d = math.sqrt(2)*c.hw_lead_origin_to_outer_edge
    self.s_hw_lead_n_i = openmc.YPlane(name='Lead brick Inside Surface Y max', y0=+c.hw_lead_radius)
    self.s_hw_lead_s_i = openmc.YPlane(name='Lead brick Inside Surface Y min', y0=-c.hw_lead_radius)
    self.s_hw_lead_e_i = openmc.XPlane(name='Lead brick Inside Surface X max', x0=+c.hw_lead_radius)
    self.s_hw_lead_w_i = openmc.XPlane(name='Lead brick Inside Surface X min', x0=-c.hw_lead_radius)
    self.s_hw_lead_ne_i = openmc.Plane(name='Lead brick Inside Surface NE', A=1, B=1, C=0, D=d)
    self.s_hw_lead_nw_i = openmc.Plane(name='Lead brick Inside Surface NW', A=-1, B=1, C=0, D=d)
    self.s_hw_lead_se_i = openmc.Plane(name='Lead brick Inside Surface SE', A=-1, B=1, C=0, D=-d)
    self.s_hw_lead_sw_i = openmc.Plane(name='Lead brick Inside Surface SW', A=1, B=1, C=0, D=-d)

    lead_long_dist = c.hw_lead_radius - c.hw_lead_short_dist
    self.s_hw_lead_inner_n = openmc.YPlane(name='Lead brick Inner Square Y max', y0=+lead_long_dist)
    self.s_hw_lead_inner_s = openmc.YPlane(name='Lead brick Inner Square Y min', y0=-lead_long_dist)
    self.s_hw_lead_inner_e = openmc.XPlane(name='Lead brick Inner Square X max', x0=+lead_long_dist)
    self.s_hw_lead_inner_w = openmc.XPlane(name='Lead brick Inner Square X min', x0=-lead_long_dist)

    hw_innermost_surfs = {
      'N': self.s_hw_lead_n_i,
      'S': self.s_hw_lead_s_i,
      'E': self.s_hw_lead_e_i,
      'W': self.s_hw_lead_w_i,
      'NE': self.s_hw_lead_ne_i,
      'NW': self.s_hw_lead_nw_i,
      'SE': self.s_hw_lead_se_i,
      'SW': self.s_hw_lead_sw_i,
      'IN': self.s_hw_lead_inner_n,
      'IS': self.s_hw_lead_inner_s,
      'IE': self.s_hw_lead_inner_e,
      'IW': self.s_hw_lead_inner_w,
    }

    # Air gap / clad inner
    # Middle octagon
    d = math.sqrt(2)*c.hw_gap_origin_to_outer_edge
    self.s_hw_can_n_i = openmc.YPlane(name='Half-width clad inner Outside Surface Y max', y0=+c.hw_can_radius_i)
    self.s_hw_can_s_i = openmc.YPlane(name='Half-width clad inner Outside Surface Y min', y0=-c.hw_can_radius_i)
    self.s_hw_can_e_i = openmc.XPlane(name='Half-width clad inner Outside Surface X max', x0=+c.hw_can_radius_i)
    self.s_hw_can_w_i = openmc.XPlane(name='Half-width clad inner Outside Surface X min', x0=-c.hw_can_radius_i)
    self.s_hw_can_ne_i = openmc.Plane(name='Half-width clad inner Outside Surface NE', A=1, B=1, C=0, D=d)
    self.s_hw_can_nw_i = openmc.Plane(name='Half-width clad inner Outside Surface NW', A=-1, B=1, C=0, D=d)
    self.s_hw_can_se_i = openmc.Plane(name='Half-width clad inner Outside Surface SE', A=-1, B=1, C=0, D=-d)
    self.s_hw_can_sw_i = openmc.Plane(name='Half-width clad inner Outside Surface SW', A=1, B=1, C=0, D=-d)
    # Create some surfaces that will handle the extra material in the gap and cladding (required to keep gap and clad
    # constant thickness everywhere)
    d = c.hw_lead_corner_length/math.sqrt(2)
    self.s_hw_gap_nw = openmc.Plane(name='Half-width clad inner NE & SW Chamfers NW Surface', A=-1, B=1, C=0, D=d)
    self.s_hw_gap_se = openmc.Plane(name='Half-width clad inner NE & SW Chamfers SE Surface', A=-1, B=1, C=0, D=-d)
    self.s_hw_gap_ne = openmc.Plane(name='Half-width clad inner NW & SE Chamfers NE Surface', A=1, B=1, C=0, D=d)
    self.s_hw_gap_sw = openmc.Plane(name='Half-width clad inner NW & SE Chamfers SW Surface', A=1, B=1, C=0, D=-d)

    hw_can_surfs_i = {
      'N': self.s_hw_can_n_i,
      'S': self.s_hw_can_s_i,
      'E': self.s_hw_can_e_i,
      'W': self.s_hw_can_w_i,
      'NE': self.s_hw_can_ne_i,
      'NW': self.s_hw_can_nw_i,
      'SE': self.s_hw_can_se_i,
      'SW': self.s_hw_can_sw_i,
      'IN': self.s_hw_lead_inner_n,
      'IS': self.s_hw_lead_inner_s,
      'IE': self.s_hw_lead_inner_e,
      'IW': self.s_hw_lead_inner_w,
      'INW': self.s_hw_gap_nw,
      'ISE': self.s_hw_gap_se,
      'INE': self.s_hw_gap_ne,
      'ISW': self.s_hw_gap_sw,
      'prevN': self.s_hw_lead_n_i,
      'prevS': self.s_hw_lead_s_i,
      'prevE': self.s_hw_lead_e_i,
      'prevW': self.s_hw_lead_w_i,
      'prevNE': self.s_hw_lead_ne_i,
      'prevNW': self.s_hw_lead_nw_i,
      'prevSE': self.s_hw_lead_se_i,
      'prevSW': self.s_hw_lead_sw_i
    }

    # Clad outer
    # Outermost octagon
    d = math.sqrt(2)*c.hw_can_origin_to_outer_edge
    self.s_hw_can_n_o = openmc.YPlane(name='Half-width outer clad Outside Surface Y max', y0=+c.hw_can_radius_o)
    self.s_hw_can_s_o = openmc.YPlane(name='Half-width outer clad Outside Surface Y min', y0=-c.hw_can_radius_o)
    self.s_hw_can_e_o = openmc.XPlane(name='Half-width outer clad Outside Surface X max', x0=+c.hw_can_radius_o)
    self.s_hw_can_w_o = openmc.XPlane(name='Half-width outer clad Outside Surface X min', x0=-c.hw_can_radius_o)
    self.s_hw_can_ne_o = openmc.Plane(name='Half-width outer clad Outside Surface NE', A=1, B=1, C=0, D=d)
    self.s_hw_can_nw_o = openmc.Plane(name='Half-width outer clad Outside Surface NW', A=-1, B=1, C=0, D=d)
    self.s_hw_can_se_o = openmc.Plane(name='Half-width outer clad Outside Surface SE', A=-1, B=1, C=0, D=-d)
    self.s_hw_can_sw_o = openmc.Plane(name='Half-width outer clad Outside Surface SW', A=1, B=1, C=0, D=-d)
    # Inner surfaces in the material for use in breaking it up into parts
    can_long_dist = lead_long_dist + c.TANPI8*c.hw_gap_thick
    self.s_hw_can_inner_n = openmc.YPlane(name='Half-width outer clad Inner Y max', y0=+can_long_dist)
    self.s_hw_can_inner_s = openmc.YPlane(name='Half-width outer clad Inner Y min', y0=-can_long_dist)
    self.s_hw_can_inner_e = openmc.XPlane(name='Half-width outer clad Inner X max', x0=+can_long_dist)
    self.s_hw_can_inner_w = openmc.XPlane(name='Half-width outer clad Inner X min', x0=-can_long_dist)
    # Create some surfaces that will handle the extra material in the gap and cladding
    # (required to keep gap and clad constant thickness everywhere)
    d = c.hw_lead_corner_length/math.sqrt(2.0) + math.sqrt(2)*c.TANPI8*c.hw_gap_thick
    self.s_hw_can_nw = openmc.Plane(name='Half-width outer clad NE & SW Chamfers NW Surface', A=-1, B=1, C=0, D=d)
    self.s_hw_can_se = openmc.Plane(name='Half-width outer clad NE & SW Chamfers SE Surface', A=-1, B=1, C=0, D=-d)
    self.s_hw_can_ne = openmc.Plane(name='Half-width outer clad NW & SE Chamfers NE Surface', A=1, B=1, C=0, D=d)
    self.s_hw_can_sw = openmc.Plane(name='Half-width outer clad NW & SE Chamfers SW Surface', A=1, B=1, C=0, D=-d)

    hw_can_surfs_o = {
      'N': self.s_hw_can_n_o,
      'S': self.s_hw_can_s_o,
      'E': self.s_hw_can_e_o,
      'W': self.s_hw_can_w_o,
      'NE': self.s_hw_can_ne_o,
      'NW': self.s_hw_can_nw_o,
      'SE': self.s_hw_can_se_o,
      'SW': self.s_hw_can_sw_o,
      'IN': self.s_hw_can_inner_n,
      'IS': self.s_hw_can_inner_s,
      'IE': self.s_hw_can_inner_e,
      'IW': self.s_hw_can_inner_w,
      'INW': self.s_hw_can_nw,
      'ISE': self.s_hw_can_se,
      'INE': self.s_hw_can_ne,
      'ISW': self.s_hw_can_sw,
      'prevN': self.s_hw_can_n_i,
      'prevS': self.s_hw_can_s_i,
      'prevE': self.s_hw_can_e_i,
      'prevW': self.s_hw_can_w_i,
      'prevNE': self.s_hw_can_ne_i,
      'prevNW': self.s_hw_can_nw_i,
      'prevSE': self.s_hw_can_se_i,
      'prevSW': self.s_hw_can_sw_i
    }

    # Surfaces to make the interior bricks into half-width elements
    self.s_hw_half_innermost_o = openmc.YPlane(name="Fill outer edge (short side)",
                                               y0=c.hw_origin_to_half_lead)
    self.s_hw_half_can_i = openmc.YPlane(name="Can inner edge (short side)",
                                         y0=c.hw_origin_to_half_can_i)
    self.s_hw_half_can_o = openmc.YPlane(name="Can outer edge (short side)",
                                         y0=c.hw_origin_to_half_can_o)
    half_element_dict = {'clad': self.s_hw_half_can_o,
                         'gap':  self.s_hw_half_can_i,
                         'fill': self.s_hw_half_innermost_o}
    bare_half_element_dict = {'fill': self.s_hw_half_innermost_o}

    # Radial surfaces for the Half-width lifting adapter (tff) middle cone
    # Innermost octagon
    d = math.sqrt(2)*c.hw_tff_mid_origin_to_outer_edge
    self.s_hw_tff_mid_n_i = openmc.YPlane(name='Lifting Adapter middle cone Inside Surface Y max', y0=+c.hw_tff_mid_radius)
    self.s_hw_tff_mid_s_i = openmc.YPlane(name='Lifting Adapter middle cone Inside Surface Y min', y0=-c.hw_tff_mid_radius)
    self.s_hw_tff_mid_e_i = openmc.XPlane(name='Lifting Adapter middle cone Inside Surface X max', x0=+c.hw_tff_mid_radius)
    self.s_hw_tff_mid_w_i = openmc.XPlane(name='Lifting Adapter middle cone Inside Surface X min', x0=-c.hw_tff_mid_radius)
    self.s_hw_tff_mid_ne_i = openmc.Plane(name='Lifting Adapter middle cone Inside Surface NE', A=1, B=1, C=0, D=d)
    self.s_hw_tff_mid_nw_i = openmc.Plane(name='Lifting Adapter middle cone Inside Surface NW', A=-1, B=1, C=0, D=d)
    self.s_hw_tff_mid_se_i = openmc.Plane(name='Lifting Adapter middle cone Inside Surface SE', A=-1, B=1, C=0, D=-d)
    self.s_hw_tff_mid_sw_i = openmc.Plane(name='Lifting Adapter middle cone Inside Surface SW', A=1, B=1, C=0, D=-d)

    hw_mid_long_dist = c.hw_tff_mid_radius - c.hw_tff_mid_corner_length/math.sqrt(2)
    self.s_hw_tff_mid_inner_n = openmc.YPlane(name='Lifting Adapter middle cone Inner Square Y max', y0=+hw_mid_long_dist)
    self.s_hw_tff_mid_inner_s = openmc.YPlane(name='Lifting Adapter middle cone Inner Square Y min', y0=-hw_mid_long_dist)
    self.s_hw_tff_mid_inner_e = openmc.XPlane(name='Lifting Adapter middle cone Inner Square X max', x0=+hw_mid_long_dist)
    self.s_hw_tff_mid_inner_w = openmc.XPlane(name='Lifting Adapter middle cone Inner Square X min', x0=-hw_mid_long_dist)

    hw_mid_surfs = {
      'N': self.s_hw_tff_mid_n_i,
      'S': self.s_hw_tff_mid_s_i,
      'E': self.s_hw_tff_mid_e_i,
      'W': self.s_hw_tff_mid_w_i,
      'NE': self.s_hw_tff_mid_ne_i,
      'NW': self.s_hw_tff_mid_nw_i,
      'SE': self.s_hw_tff_mid_se_i,
      'SW': self.s_hw_tff_mid_sw_i,
      'IN': self.s_hw_tff_mid_inner_n,
      'IS': self.s_hw_tff_mid_inner_s,
      'IE': self.s_hw_tff_mid_inner_e,
      'IW': self.s_hw_tff_mid_inner_w,
    }

    # Radial surfaces for the Half-width lifting adapter (tff) head
    # Innermost octagon
    d = math.sqrt(2)*c.hw_tff_head_origin_to_outer_edge
    self.s_hw_tff_head_n_i = openmc.YPlane(name='Lifting Adapter Head Inside Surface Y max', y0=+c.hw_tff_head_radius)
    self.s_hw_tff_head_s_i = openmc.YPlane(name='Lifting Adapter Head Inside Surface Y min', y0=-c.hw_tff_head_radius)
    self.s_hw_tff_head_e_i = openmc.XPlane(name='Lifting Adapter Head Inside Surface X max', x0=+c.hw_tff_head_radius)
    self.s_hw_tff_head_w_i = openmc.XPlane(name='Lifting Adapter Head Inside Surface X min', x0=-c.hw_tff_head_radius)
    self.s_hw_tff_head_ne_i = openmc.Plane(name='Lifting Adapter Head Inside Surface NE', A=1, B=1, C=0, D=d)
    self.s_hw_tff_head_nw_i = openmc.Plane(name='Lifting Adapter Head Inside Surface NW', A=-1, B=1, C=0, D=d)
    self.s_hw_tff_head_se_i = openmc.Plane(name='Lifting Adapter Head Inside Surface SE', A=-1, B=1, C=0, D=-d)
    self.s_hw_tff_head_sw_i = openmc.Plane(name='Lifting Adapter Head Inside Surface SW', A=1, B=1, C=0, D=-d)

    hw_head_long_dist = c.hw_tff_head_radius - c.hw_tff_head_corner_length/math.sqrt(2)
    self.s_hw_tff_head_inner_n = openmc.YPlane(name='Lifting Adapter Head Inner Square Y max', y0=+hw_head_long_dist)
    self.s_hw_tff_head_inner_s = openmc.YPlane(name='Lifting Adapter Head Inner Square Y min', y0=-hw_head_long_dist)
    self.s_hw_tff_head_inner_e = openmc.XPlane(name='Lifting Adapter Head Inner Square X max', x0=+hw_head_long_dist)
    self.s_hw_tff_head_inner_w = openmc.XPlane(name='Lifting Adapter Head Inner Square X min', x0=-hw_head_long_dist)

    hw_head_surfs = {
      'N': self.s_hw_tff_head_n_i,
      'S': self.s_hw_tff_head_s_i,
      'E': self.s_hw_tff_head_e_i,
      'W': self.s_hw_tff_head_w_i,
      'NE': self.s_hw_tff_head_ne_i,
      'NW': self.s_hw_tff_head_nw_i,
      'SE': self.s_hw_tff_head_se_i,
      'SW': self.s_hw_tff_head_sw_i,
      'IN': self.s_hw_tff_head_inner_n,
      'IS': self.s_hw_tff_head_inner_s,
      'IE': self.s_hw_tff_head_inner_e,
      'IW': self.s_hw_tff_head_inner_w,
    }


    # Radial surfaces for the inside of the control rod elements
    self.s_crd_fuel_IR = openmc.ZCylinder(name='Control Rod Fuel Element IR', R=c.crdCenterR)
    self.s_crd_upperRefl_IR = openmc.ZCylinder(name='Control Rod Upper Axial Reflector IR', R=c.crdUpperCenterR)
    self.s_crd_upperSPOffGas_IR = openmc.ZCylinder(name='Control Rod Upper Short Plug Off Gas Drill Hole IR',
                                  R=c.crdUpperOffgasR, x0=c.crdDrillCardDist, y0=c.crdDrillCardDist)
    self.s_crd_lowerRefl_IR = openmc.ZCylinder(name='Control Rod Lower Axial Reflector IR', R=c.crdLowerCenterR)
    self.s_crd_bear_OR = openmc.ZCylinder(name='Control Rod Bearing OR', R=c.crdBearOR)
    self.s_crd_bearThin_IR = openmc.ZCylinder(name='Control Rod Thin Bearing IR', R=c.crdBearThinIR)
    self.s_crd_bearThick_IR = openmc.ZCylinder(name='Control Rod Thick Bearing IR', R=c.crdBearThickIR)
    self.s_crd_bush_OR = openmc.ZCylinder(name='Control Rod Bushing OR', R=c.crdBushOR)
    self.s_crd_bush_IR = openmc.ZCylinder(name='Control Rod Bushing IR', R=c.crdBushIR)
    self.s_crd_bushRet_OR = openmc.ZCylinder(name='Control Rod Bushing Retainer OR', R=c.crdBushRetainOR)
    self.s_crd_bushRet_IR = openmc.ZCylinder(name='Control Rod Bushing Retainer IR', R=c.crdBushRetainIR)
    self.s_crd_SPOffGasClad_IR = openmc.ZCylinder(name='Control Rod Upper Short Plug Off Gas Clad IR',
                                 R=c.offGasTubeIR, x0=c.crdDrillCardDist, y0=c.crdDrillCardDist)
    self.s_crd_SPOffGasClad_OR = openmc.ZCylinder(name='Control Rod Upper Short Plug Off Gas Clad OR',
                                 R=c.offGasTubeOR, x0=c.crdDrillCardDist, y0=c.crdDrillCardDist)
    self.s_crd_SPOffGasCrimp_R = openmc.ZCylinder(name='Control Rod Upper Short Plug Off Gas Crimp R',
                                 R=c.offGasCladW, x0=c.crdDrillCardDist, y0=c.crdDrillCardDist)
    self.s_crd_elem_OR = openmc.ZCylinder(name='Control Rod Zr Element Tube OR', R=c.crdElemOR)
    self.s_crd_elem_IR = openmc.ZCylinder(name='Control Rod Zr Element Tube IR', R=c.crdElemIR)

    # In previous versions of the builder, when not working on the first ring, we pulled interior surfaces from previous rings.
    # This unfortunately causes difficulty for off center cells, and complicates generating the more complex element surfaces.
    # Here, go through and add in specific interior surfaces for the various specialized cases we need.
    fuel_crd_surfs_o = deepcopy(fuel_surfs_o) # For the control rod active fuel region
    fuel_crd_surfs_o['prevR'] = self.s_crd_fuel_IR
    fuel_crd_zrSpacer_surfs_o = deepcopy(fuel_surfs_o) # For the zirc spacer above and below the control rod active fuel region
    fuel_crd_zrSpacer_surfs_o['prevR'] = self.s_crd_elem_OR
    block_alSpacer_surfs_o = deepcopy(block_surfs_o) # For the top aluminum spacer in regular elements
    block_alSpacer_surfs_o['prevR'] = self.s_offgas_tube_IR
    block_crdSpacer_surfs_o = deepcopy(block_surfs_o) # For the aluminum spacers in control rod elements
    block_crdSpacer_surfs_o['prevR'] = self.s_crd_elem_OR
    block_crdSpacerOG_surfs_o = deepcopy(block_crdSpacer_surfs_o) # For the aluminum spacers in control rod elements
    block_crdSpacerOG_surfs_o['Enclave1'] = self.s_crd_SPOffGasClad_IR
    tn_cldCrd_surfs_i = deepcopy(tn_cld_surfs_i) # For the zr divotted gap spacers in control rod elements
    tn_cldCrd_surfs_i['prevR'] = self.s_crd_elem_OR
    plug_refUpper_surfs_o = deepcopy(plug_ref_surfs_o) # For the drilled hole in the upper unmachined short plug, regular element
    plug_refUpper_surfs_o['prevR'] = self.s_ref_element_IR
    plug_refCrdLower_surfs_o = deepcopy(plug_ref_surfs_o) # For the control rod element lower reflector plugs
    plug_refCrdLower_surfs_o['prevR'] = self.s_crd_lowerRefl_IR
    plug_refCrdUpper_surfs_o = deepcopy(plug_ref_surfs_o) # For the control rod element upper reflector plugs
    plug_refCrdUpper_surfs_o['prevR'] = self.s_crd_upperRefl_IR
    plug_refCrdUpperOG_surfs_o = deepcopy(plug_refCrdUpper_surfs_o) # For the control rod element reflector plugs with offgas tube
    plug_refCrdUpperOG_surfs_o['Enclave1'] = self.s_crd_upperSPOffGas_IR
    Mplug_refUpper_surfs_o = deepcopy(Mplug_surfs) # For the machined upper short plug region in regular elements
    Mplug_refUpper_surfs_o['prevR'] = self.s_ref_element_IR
    Mplug_refCrdLower_surfs_o = deepcopy(Mplug_surfs) # For the machined lower short plug in control rod elements
    Mplug_refCrdLower_surfs_o['prevR'] = self.s_crd_lowerRefl_IR
    Mplug_refCrdUpper_surfs_o = deepcopy(Mplug_surfs) # For the machined upper short plug in control rod elements
    Mplug_refCrdUpper_surfs_o['prevR'] = self.s_crd_upperRefl_IR
    Mplug_refCrdUpper_surfs_o['Enclave1'] = self.s_crd_upperSPOffGas_IR
    # Create surface pairs for the case of a cylinder inside a cylinder
    offgas_tube_surfs_o = {'R': self.s_offgas_tube_OR, 'prevR': self.s_offgas_tube_IR}
    ref_element_surfs_i = {'R': self.s_ref_element_IR, 'prevR': self.s_offgas_tube_OR}
    offgas_crimp_gap_surfs_o = {'R': self.s_ref_element_IR, 'prevR': self.s_offgas_crimp_OR}
    crd_elem_surfs_o = {'R': self.s_crd_elem_OR, 'prevR': self.s_crd_elem_IR}
    crd_fuel_surfs_i = {'R': self.s_crd_fuel_IR, 'prevR': self.s_crd_elem_OR}
    crd_lowerRefl_surfs_i = {'R': self.s_crd_lowerRefl_IR, 'prevR': self.s_crd_elem_OR}
    crd_tkBear_surfs_o = {'R': self.s_crd_bear_OR, 'prevR': self.s_crd_bearThick_IR}
    crd_upperRefl_surfs_i = {'R': self.s_crd_upperRefl_IR, 'prevR': self.s_crd_bear_OR}
    crd_bushBear_surfs_o = {'R': self.s_crd_bear_OR, 'prevR': self.s_crd_bush_OR}
    crd_bush_surfs_o = {'R': self.s_crd_bush_OR, 'prevR': self.s_crd_bush_IR}
    crd_bushRetBear_surfs_o = {'R': self.s_crd_bear_OR, 'prevR': self.s_crd_bushRet_OR}
    crd_bushRet_surfs_o = {'R': self.s_crd_bushRet_OR, 'prevR': self.s_crd_bushRet_IR}
    crd_tnBear_surfs_o = {'R': self.s_crd_bear_OR, 'prevR': self.s_crd_bearThin_IR}
    crd_tnBear_surfs_i = {'R': self.s_crd_bearThin_IR, 'prevR': self.s_crd_elem_OR}
    # Create surface pairs for the control rod offgas tubes
    crd_offgas_surfs_o = {'R': self.s_crd_SPOffGasClad_OR, 'prevR': self.s_crd_SPOffGasClad_IR}
    crd_offgasHole_surfs_i = {'R': self.s_crd_upperSPOffGas_IR, 'prevR': self.s_crd_SPOffGasClad_OR}
    crd_crimpGap_surfs_i = {'R': self.s_crd_upperSPOffGas_IR, 'prevR': self.s_crd_SPOffGasCrimp_R}

    # TODO Remove duplicate surfaces to clean things up

    # Radial surfaces for the upper crd head fitting
    # Base level: octagon
    d = math.sqrt(2)*c.crd_head_base_origin_to_outer_edge
    self.s_crd_head_base_n_o = openmc.YPlane(name='Crd Base Outside Surface Y max', y0=+c.crd_head_base_radius_o)
    self.s_crd_head_base_s_o = openmc.YPlane(name='Crd Base Outside Surface Y min', y0=-c.crd_head_base_radius_o)
    self.s_crd_head_base_e_o = openmc.XPlane(name='Crd Base Outside Surface X max', x0=+c.crd_head_base_radius_o)
    self.s_crd_head_base_w_o = openmc.XPlane(name='Crd Base Outside Surface X min', x0=-c.crd_head_base_radius_o)
    self.s_crd_head_base_ne_o = openmc.Plane(name='Crd Base Outside Surface NE', A=1, B=1, C=0, D=d)
    self.s_crd_head_base_nw_o = openmc.Plane(name='Crd Base Outside Surface NW', A=-1, B=1, C=0, D=d)
    self.s_crd_head_base_se_o = openmc.Plane(name='Crd Base Outside Surface SE', A=-1, B=1, C=0, D=-d)
    self.s_crd_head_base_sw_o = openmc.Plane(name='Crd Base Outside Surface SW', A=1, B=1, C=0, D=-d)
    # Inner surfaces
    base_long_dist = c.crd_head_base_radius_o - c.crd_head_base_corner_length_o/math.sqrt(2)
    self.s_crd_head_base_inner_n = openmc.YPlane(name='Crd upper head Base Inner Square Y max', y0=+base_long_dist)
    self.s_crd_head_base_inner_s = openmc.YPlane(name='Crd upper head Base Inner Square Y min', y0=-base_long_dist)
    self.s_crd_head_base_inner_e = openmc.XPlane(name='Crd upper head Base Inner Square X max', x0=+base_long_dist)
    self.s_crd_head_base_inner_w = openmc.XPlane(name='Crd upper head Base Inner Square X min', x0=-base_long_dist)

    crd_head_base_surfs_o = {
      'N': self.s_crd_head_base_n_o,
      'S': self.s_crd_head_base_s_o,
      'E': self.s_crd_head_base_e_o,
      'W': self.s_crd_head_base_w_o,
      'NE': self.s_crd_head_base_ne_o,
      'NW': self.s_crd_head_base_nw_o,
      'SE': self.s_crd_head_base_se_o,
      'SW': self.s_crd_head_base_sw_o,
      'IN': self.s_crd_head_base_inner_n,
      'IS': self.s_crd_head_base_inner_s,
      'IE': self.s_crd_head_base_inner_e,
      'IW': self.s_crd_head_base_inner_w,
      'prevR': self.s_crd_bear_OR
    }

    # Top level: octagon
    d = math.sqrt(2)*c.crd_head_top_origin_to_outer_edge
    self.s_crd_head_top_n_o = openmc.YPlane(name='Crd top Outside Surface Y max', y0=+c.crd_head_top_radius_o)
    self.s_crd_head_top_s_o = openmc.YPlane(name='Crd top Outside Surface Y min', y0=-c.crd_head_top_radius_o)
    self.s_crd_head_top_e_o = openmc.XPlane(name='Crd top Outside Surface X max', x0=+c.crd_head_top_radius_o)
    self.s_crd_head_top_w_o = openmc.XPlane(name='Crd top Outside Surface X min', x0=-c.crd_head_top_radius_o)
    self.s_crd_head_top_ne_o = openmc.Plane(name='Crd top Outside Surface NE', A=1, B=1, C=0, D=d)
    self.s_crd_head_top_nw_o = openmc.Plane(name='Crd top Outside Surface NW', A=-1, B=1, C=0, D=d)
    self.s_crd_head_top_se_o = openmc.Plane(name='Crd top Outside Surface SE', A=-1, B=1, C=0, D=-d)
    self.s_crd_head_top_sw_o = openmc.Plane(name='Crd top Outside Surface SW', A=1, B=1, C=0, D=-d)
    # Inner surfaces
    top_long_dist = c.crd_head_top_radius_o - c.crd_head_top_corner_length_o/math.sqrt(2)
    self.s_crd_head_top_inner_n = openmc.YPlane(name='Crd upper head top Inner Square Y max', y0=+top_long_dist)
    self.s_crd_head_top_inner_s = openmc.YPlane(name='Crd upper head top Inner Square Y min', y0=-top_long_dist)
    self.s_crd_head_top_inner_e = openmc.XPlane(name='Crd upper head top Inner Square X max', x0=+top_long_dist)
    self.s_crd_head_top_inner_w = openmc.XPlane(name='Crd upper head top Inner Square X min', x0=-top_long_dist)

    crd_head_top_surfs_o = {
      'N': self.s_crd_head_top_n_o,
      'S': self.s_crd_head_top_s_o,
      'E': self.s_crd_head_top_e_o,
      'W': self.s_crd_head_top_w_o,
      'NE': self.s_crd_head_top_ne_o,
      'NW': self.s_crd_head_top_nw_o,
      'SE': self.s_crd_head_top_se_o,
      'SW': self.s_crd_head_top_sw_o,
      'IN': self.s_crd_head_top_inner_n,
      'IS': self.s_crd_head_top_inner_s,
      'IE': self.s_crd_head_top_inner_e,
      'IW': self.s_crd_head_top_inner_w,
      'prevR': self.s_crd_bear_OR
    }

    # Define some radial surfaces to handle the guide tubes below the elements
    self.s_elemGuide_OR = openmc.ZCylinder(name='Element Support Guide Tube OR', R=c.excoreElemGuideOR)
    guide_thick = c.excoreElemGuideOR - c.bff_prong_radius
    self.s_hwGuide_OR = openmc.ZCylinder(name='Half-width Support Guide Tube OR',
                                         R=c.hw_bff_prong_radius + guide_thick)
    self.s_crdGuide_OR = openmc.ZCylinder(name='Control Rod Support Guide Tube OR', R=c.excoreCrdGuideOR)
    reg_support_elemGuide_surfs_o = {'R': self.s_elemGuide_OR, 'prevR': self.s_reg_bff_prong}
    hw_support_elemGuide_surfs_o = {'R': self.s_hwGuide_OR, 'prevR': self.s_hw_bff_prong}
    crd_supportGuide_surfs_o = {'R': self.s_crdGuide_OR, 'prevR': self.s_crd_elem_OR}

    #########################################################################################################################
    ### Now go through and generate the radial universes (still axially infinite at this point)
    #########################################################################################################################

    # Fuel element universes

    ### Regular assembly sections

    # Pure graphite elements
    # The aluminum clad parts of the reflector region containing the
    # long plug and the non-machined parts of the lower short plug
    self.u_graph_ref_al = {}
    for boron in self.graph_boron_ppms:
      for altype in self.al_clad_types:
        self.u_graph_ref_al[boron, altype] = InfiniteElement(name='Non-machined lower axial graphite reflector & Upper long plug region')
        if boron == 'CP2':
          # Using the basic CP2 graphite material
          self.u_graph_ref_al[boron, altype].add_ring(self.mats['Graphite'], plug_ref_surfs_o, octagon=True, first=True)
        else:
          # Creating a graphite element segment with a specified boron impurity
          # This is an option arising from an early misunderstanding about the
          # axial reflector composition and will likely not be needed for
          # most applications
          self.u_graph_ref_al[boron, altype].add_ring(self.mats['Graphite {0}'.format(boron)],
                                                      plug_ref_surfs_o, octagon=True, first=True)
        self.u_graph_ref_al[boron, altype].add_ring(self.mats['Air'], plug_clad_surfs_i, octagon=True, prevOctagon=True)
        self.u_graph_ref_al[boron, altype].add_ring(self.mats[altype], plug_clad_surfs_o, octagon=True, prevOctagon=True)
        self.u_graph_ref_al[boron, altype].add_last_ring(self.mats['Air'])
        self.u_graph_ref_al[boron, altype].finalize()
    # The zirconium clad parts of the un-fuelled elements with dummy graphite blocks at the fuelled region height.
    # These will typically be used only for dummy elements directly adjacent to the fuel elements
    self.u_graph_dummy_zr = {}
    for boron in self.graph_boron_ppms:
      self.u_graph_dummy_zr[boron] = InfiniteElement(name='Zr clad dummy graphite element, active region')
      if boron == 'CP2': # Using the basic CP2 graphite material
        # Using the basic CP2 graphite material
        self.u_graph_dummy_zr[boron].add_ring(     self.mats['Graphite'], fuel_surfs_o, octagon=True, first=True)
      else:
        # Creating a graphite element segment with a specified boron impurity
        # This is an option arising from an early misunderstanding about the
        # axial reflector composition and will likely not be needed for
        # most applications
        self.u_graph_dummy_zr[boron].add_ring(     self.mats['Graphite {0}'.format(boron)], fuel_surfs_o, octagon=True, first=True)
      self.u_graph_dummy_zr[boron].add_ring(     self.mats['Air'], clad_surfs_i, octagon=True, prevOctagon=True)
      self.u_graph_dummy_zr[boron].add_ring(     self.mats['Zirc3'], clad_surfs_o, octagon=True, prevOctagon=True)
      self.u_graph_dummy_zr[boron].add_last_ring(self.mats['Air'])
      self.u_graph_dummy_zr[boron].finalize()
    # The aluminum clad parts of the reflector region containing the non-machined parts of the upper short plug
    self.u_graph_ref_Usp_al = {}
    for boron in self.graph_boron_ppms:
      for altype in self.al_clad_types:
        self.u_graph_ref_Usp_al[boron, altype] = InfiniteElement(name='Non-machined upper short plug region')
        self.u_graph_ref_Usp_al[boron, altype].add_ring(     self.mats['Air'],   self.s_ref_element_IR, first=True)
        if boron == 'CP2':
          # Using the basic CP2 graphite material
          self.u_graph_ref_Usp_al[boron, altype].add_ring(     self.mats['Graphite'], plug_refUpper_surfs_o, octagon=True)
        else:
          # Creating a graphite element segment with a specified boron impurity
          # This is an option arising from an early misunderstanding about the
          # axial reflector composition and will likely not be needed for
          # most applications
          self.u_graph_ref_Usp_al[boron, altype].add_ring(     self.mats['Graphite {0}'.format(boron)], plug_refUpper_surfs_o, octagon=True)
        self.u_graph_ref_Usp_al[boron, altype].add_ring(     self.mats['Air'], plug_clad_surfs_i, octagon=True, prevOctagon=True)
        self.u_graph_ref_Usp_al[boron, altype].add_ring(     self.mats[altype], plug_clad_surfs_o, octagon=True, prevOctagon=True)
        self.u_graph_ref_Usp_al[boron, altype].add_last_ring(self.mats['Air'])
        self.u_graph_ref_Usp_al[boron, altype].finalize()
    # The aluminum clad parts of the reflector region containing the machined parts of the lower short plug
    self.u_graph_ref_mLsp_al = {}
    for boron in self.graph_boron_ppms:
      for altype in self.al_clad_types:
        self.u_graph_ref_mLsp_al[boron, altype] = InfiniteElement(name='Machined lower axial graphite reflector region')
        if boron == 'CP2':
          # Using the basic CP2 graphite material
          self.u_graph_ref_mLsp_al[boron, altype].add_ring(     self.mats['Graphite'], Mplug_surfs, box=True, first=True)
        else:
          # Creating a graphite element segment with a specified boron impurity
          # This is an option arising from an early misunderstanding about the
          # axial reflector composition and will likely not be needed for
          # most applications
          self.u_graph_ref_mLsp_al[boron, altype].add_ring(     self.mats['Graphite {0}'.format(boron)], Mplug_surfs, box=True, first=True)
        self.u_graph_ref_mLsp_al[boron, altype].add_ring(     self.mats['Air'], Mplug_clad_surfs_i, octagon=True, prevBox=True)
        self.u_graph_ref_mLsp_al[boron, altype].add_ring(     self.mats[altype], plug_clad_surfs_o, octagon=True, prevOctagon=True)
        self.u_graph_ref_mLsp_al[boron, altype].add_last_ring(self.mats['Air'])
        self.u_graph_ref_mLsp_al[boron, altype].finalize()
    # The aluminum clad parts of the reflector region containing the machined parts of the upper short plug with no offgas tube
    self.u_graph_ref_mUsp_al = {}
    for boron in self.graph_boron_ppms:
      for altype in self.al_clad_types:
        self.u_graph_ref_mUsp_al[boron, altype] = InfiniteElement(name='Machined upper short plug region')
        self.u_graph_ref_mUsp_al[boron, altype].add_ring(     self.mats['Air'],   self.s_ref_element_IR, first=True)
        if boron == 'CP2':
          # Using the basic CP2 graphite material
          self.u_graph_ref_mUsp_al[boron, altype].add_ring(     self.mats['Graphite'], Mplug_refUpper_surfs_o, box=True)
        else:
          # Creating a graphite element segment with a specified boron impurity
          # This is an option arising from an early misunderstanding about the
          # axial reflector composition and will likely not be needed for
          # most applications
          self.u_graph_ref_mUsp_al[boron, altype].add_ring(     self.mats['Graphite {0}'.format(boron)], Mplug_refUpper_surfs_o, box=True)
        self.u_graph_ref_mUsp_al[boron, altype].add_ring(     self.mats['Air'], Mplug_clad_surfs_i, octagon=True, prevBox=True)
        self.u_graph_ref_mUsp_al[boron, altype].add_ring(     self.mats[altype], plug_clad_surfs_o, octagon=True, prevOctagon=True)
        self.u_graph_ref_mUsp_al[boron, altype].add_last_ring(self.mats['Air'])
        self.u_graph_ref_mUsp_al[boron, altype].finalize()
    # The aluminum clad parts of the reflector region containing the
    # machined parts of the upper short plug with offgas tube
    self.u_graph_ref_mUspG_al = {}
    for boron in self.graph_boron_ppms:
      for altype in self.al_clad_types:
        self.u_graph_ref_mUspG_al[boron, altype] = InfiniteElement(name='Machined upper short plug with offgas tube region')
        self.u_graph_ref_mUspG_al[boron, altype].add_ring(     self.mats['Air'],   self.s_offgas_tube_IR, first=True)
        self.u_graph_ref_mUspG_al[boron, altype].add_ring(     self.mats['Al1100'],  offgas_tube_surfs_o)
        self.u_graph_ref_mUspG_al[boron, altype].add_ring(     self.mats['Air'],       ref_element_surfs_i)
        if boron == 'CP2':
          # Using the basic CP2 graphite material
          self.u_graph_ref_mUspG_al[boron, altype].add_ring(     self.mats['Graphite'], Mplug_refUpper_surfs_o, box=True)
        else:
          # Creating a graphite element segment with a specified boron impurity
          # This is an option arising from an early misunderstanding about the
          # axial reflector composition and will likely not be needed for
          # most applications
          self.u_graph_ref_mUspG_al[boron, altype].add_ring(     self.mats['Graphite {0}'.format(boron)], Mplug_refUpper_surfs_o, box=True)
        self.u_graph_ref_mUspG_al[boron, altype].add_ring(     self.mats['Air'], Mplug_clad_surfs_i, octagon=True, prevBox=True)
        self.u_graph_ref_mUspG_al[boron, altype].add_ring(     self.mats[altype], plug_clad_surfs_o, octagon=True, prevOctagon=True)
        self.u_graph_ref_mUspG_al[boron, altype].add_last_ring(self.mats['Air'])
        self.u_graph_ref_mUspG_al[boron, altype].finalize()
    # The aluminum clad parts of the reflector region containing the
    # machined parts of the upper short plug with offgas tube crimp
    self.u_graph_ref_mUspC_al = {}
    for boron in self.graph_boron_ppms:
      for altype in self.al_clad_types:
        self.u_graph_ref_mUspC_al[boron, altype] = InfiniteElement(name='Machined upper long plug with offgas tube crimp region')
        self.u_graph_ref_mUspC_al[boron, altype].add_ring(     self.mats['Al1100'],   self.s_offgas_crimp_OR, first=True)
        self.u_graph_ref_mUspC_al[boron, altype].add_ring(     self.mats['Air'],   offgas_crimp_gap_surfs_o)
        if boron == 'CP2':
          # Using the basic CP2 graphite material
          self.u_graph_ref_mUspC_al[boron, altype].add_ring(     self.mats['Graphite'], Mplug_refUpper_surfs_o, box=True)
        else:
          # Creating a graphite element segment with a specified boron impurity
          # This is an option arising from an early misunderstanding about the
          # axial reflector composition and will likely not be needed for
          # most applications
          self.u_graph_ref_mUspC_al[boron, altype].add_ring(     self.mats['Graphite {0}'.format(boron)], Mplug_refUpper_surfs_o, box=True)
        self.u_graph_ref_mUspC_al[boron, altype].add_ring(     self.mats['Air'], Mplug_clad_surfs_i, octagon=True, prevBox=True)
        self.u_graph_ref_mUspC_al[boron, altype].add_ring(     self.mats[altype], plug_clad_surfs_o, octagon=True, prevOctagon=True)
        self.u_graph_ref_mUspC_al[boron, altype].add_last_ring(self.mats['Air'])
        self.u_graph_ref_mUspC_al[boron, altype].finalize()

    # Regular fuel elements
    self.u_fuel_active_pin = {}
    for wgt, boron in zip(self.weight_percents, self.fuel_boron_ppms):
      self.u_fuel_active_pin[wgt, boron] = InfiniteElement(name='Fuel rod active region - {0} wgt, {1}'.format(wgt,boron))
      self.u_fuel_active_pin[wgt, boron].add_ring(     self.mats['Fuel {0}'.format(boron)], fuel_surfs_o, octagon=True, first=True)
      self.u_fuel_active_pin[wgt, boron].add_ring(     self.mats['Air'],               clad_surfs_i, octagon=True, prevOctagon=True)
      self.u_fuel_active_pin[wgt, boron].add_ring(     self.mats['Zirc3'],                 clad_surfs_o, octagon=True, prevOctagon=True)
      self.u_fuel_active_pin[wgt, boron].add_last_ring(self.mats['Air'])
      self.u_fuel_active_pin[wgt, boron].finalize()

    ### Control rod element radial universes

    # Control rod elements
    self.u_crd_active = {}
    for wgt, boron in zip(self.weight_percents, self.fuel_boron_ppms):
      self.u_crd_active[wgt, boron] = InfiniteElement(name='Fuel rod with control active region - {0} wgt, {1}'.format(wgt,boron))
      self.u_crd_active[wgt, boron].add_ring(     self.mats['Air'],               self.s_crd_elem_IR, first=True)
      self.u_crd_active[wgt, boron].add_ring(     self.mats['Zirc3'],              crd_elem_surfs_o)
      self.u_crd_active[wgt, boron].add_ring(     self.mats['Air'],               crd_fuel_surfs_i)
      self.u_crd_active[wgt, boron].add_ring(     self.mats['Fuel {0}'.format(boron)], fuel_crd_surfs_o, octagon=True)
      self.u_crd_active[wgt, boron].add_ring(     self.mats['Air'],               clad_surfs_i, octagon=True, prevOctagon=True)
      self.u_crd_active[wgt, boron].add_ring(     self.mats['Zirc3'],             clad_surfs_o, octagon=True, prevOctagon=True)
      self.u_crd_active[wgt, boron].add_last_ring(self.mats['Air'])
      self.u_crd_active[wgt, boron].finalize()

    # Pure graphite for control rods
    # Part of the element containing the lower long plug and the unmachined short plug
    self.u_crd_grphLower = {}
    for boron in self.graph_boron_ppms:
      self.u_crd_grphLower[boron] = InfiniteElement(name='Control rod element basic lower axial reflector region')
      self.u_crd_grphLower[boron].add_ring(     self.mats['Air'],   self.s_crd_elem_IR, first=True)
      self.u_crd_grphLower[boron].add_ring(     self.mats['Zirc3'],  crd_elem_surfs_o)
      self.u_crd_grphLower[boron].add_ring(     self.mats['Air'],   crd_lowerRefl_surfs_i)
      if boron == 'CP2':
        # Using the basic CP2 graphite material
        self.u_crd_grphLower[boron].add_ring(     self.mats['Graphite'], plug_refCrdLower_surfs_o, octagon=True)
      else:
        # Creating a graphite element segment with a specified boron impurity
        # This is an option arising from an early misunderstanding about the
        # axial reflector composition and will likely not be needed for
        # most applications
        self.u_crd_grphLower[boron].add_ring(     self.mats['Graphite {0}'.format(boron)], plug_refCrdLower_surfs_o, octagon=True)
      self.u_crd_grphLower[boron].add_ring(     self.mats['Air'],  plug_clad_surfs_i, octagon=True, prevOctagon=True)
      self.u_crd_grphLower[boron].add_ring(     self.mats['Al6063'],    plug_clad_surfs_o, octagon=True, prevOctagon=True)
      self.u_crd_grphLower[boron].add_last_ring(self.mats['Air'])
      self.u_crd_grphLower[boron].finalize()
    # Part of the element containing the lower machined short plug
    self.u_crd_grphLowerMsp = {}
    for boron in self.graph_boron_ppms:
      self.u_crd_grphLowerMsp[boron] = InfiniteElement(name='Control rod element machined short plug lower axial reflector region')
      self.u_crd_grphLowerMsp[boron].add_ring(     self.mats['Air'],   self.s_crd_elem_IR, first=True)
      self.u_crd_grphLowerMsp[boron].add_ring(     self.mats['Zirc3'],  crd_elem_surfs_o)
      self.u_crd_grphLowerMsp[boron].add_ring(     self.mats['Air'],   crd_lowerRefl_surfs_i)
      if boron == 'CP2':
        # Using the basic CP2 graphite material
        self.u_crd_grphLowerMsp[boron].add_ring(     self.mats['Graphite'], Mplug_refCrdLower_surfs_o, box=True)
      else:
        # Creating a graphite element segment with a specified boron impurity
        # This is an option arising from an early misunderstanding about the
        # axial reflector composition and will likely not be needed for
        # most applications
        self.u_crd_grphLowerMsp[boron].add_ring(     self.mats['Graphite {0}'.format(boron)], Mplug_refCrdLower_surfs_o, box=True)
      self.u_crd_grphLowerMsp[boron].add_ring(     self.mats['Air'],  Mplug_clad_surfs_i, octagon=True, prevBox=True)
      self.u_crd_grphLowerMsp[boron].add_ring(     self.mats['Al6063'],    plug_clad_surfs_o, octagon=True, prevOctagon=True)
      self.u_crd_grphLowerMsp[boron].add_last_ring(self.mats['Air'])
      self.u_crd_grphLowerMsp[boron].finalize()
    # Part of the element containing the upper long plug and the unmachined short plug with thick clad
    self.u_crd_grphUpper = {}
    for boron in self.graph_boron_ppms:
      self.u_crd_grphUpper[boron] = InfiniteElement(name='Control rod element basic upper axial reflector region')
      self.u_crd_grphUpper[boron].add_ring(     self.mats['Air'],    self.s_crd_bearThick_IR, first=True)
      self.u_crd_grphUpper[boron].add_ring(     self.mats['Al1100'], crd_tkBear_surfs_o)
      self.u_crd_grphUpper[boron].add_ring(     self.mats['Air'],    crd_upperRefl_surfs_i)
      if boron == 'CP2':
        # Using the basic CP2 graphite material
        self.u_crd_grphUpper[boron].add_ring(     self.mats['Graphite'], plug_refCrdUpper_surfs_o, octagon=True)
      else:
        # Creating a graphite element segment with a specified boron impurity
        # This is an option arising from an early misunderstanding about the
        # axial reflector composition and will likely not be needed for
        # most applications
        self.u_crd_grphUpper[boron].add_ring(     self.mats['Graphite {0}'.format(boron)], plug_refCrdUpper_surfs_o, octagon=True)
      self.u_crd_grphUpper[boron].add_ring(     self.mats['Air'],  plug_clad_surfs_i, octagon=True, prevOctagon=True)
      self.u_crd_grphUpper[boron].add_ring(     self.mats['Al6063'],    plug_clad_surfs_o, octagon=True, prevOctagon=True)
      self.u_crd_grphUpper[boron].add_last_ring(self.mats['Air'])
      self.u_crd_grphUpper[boron].finalize()
    # Part of the element containing the upper unmachined short plug with graphitar bushing, no offgas hole
    self.u_crd_grphUpperBush = {}
    for boron in self.graph_boron_ppms:
      self.u_crd_grphUpperBush[boron] = InfiniteElement(name='Control rod element upper region with graphitar bushing, no offgas')
      self.u_crd_grphUpperBush[boron].add_ring(     self.mats['Air'],      self.s_crd_bush_IR, first=True)
      # TODO should really have this material be graphitar and not graphite
      self.u_crd_grphUpperBush[boron].add_ring(     self.mats['Graphite'], crd_bush_surfs_o)
      self.u_crd_grphUpperBush[boron].add_ring(     self.mats['Al1100'],   crd_bushBear_surfs_o)
      self.u_crd_grphUpperBush[boron].add_ring(     self.mats['Air'],      crd_upperRefl_surfs_i)
      if boron == 'CP2':
        # Using the basic CP2 graphite material
        self.u_crd_grphUpperBush[boron].add_ring(     self.mats['Graphite'], plug_refCrdUpper_surfs_o, octagon=True)
      else:
        # Creating a graphite element segment with a specified boron impurity
        # This is an option arising from an early misunderstanding about the
        # axial reflector composition and will likely not be needed for
        # most applications
        self.u_crd_grphUpperBush[boron].add_ring(   self.mats['Graphite {0}'.format(boron)], plug_refCrdUpper_surfs_o, octagon=True)
      self.u_crd_grphUpperBush[boron].add_ring(     self.mats['Air'],    plug_clad_surfs_i, octagon=True, prevOctagon=True)
      self.u_crd_grphUpperBush[boron].add_ring(     self.mats['Al6063'], plug_clad_surfs_o, octagon=True, prevOctagon=True)
      self.u_crd_grphUpperBush[boron].add_last_ring(self.mats['Air'])
      self.u_crd_grphUpperBush[boron].finalize()
    # Part of the element containing the upper unmachined short plug with graphitar bushing, with offgas drill hole
    self.u_crd_grphUpperBushOGD = {}
    for boron in self.graph_boron_ppms:
      self.u_crd_grphUpperBushOGD[boron] = InfiniteElement(name='Crd element upper region with graphitar bushing, offgas drill')
      self.u_crd_grphUpperBushOGD[boron].add_ring(     self.mats['Air'],       self.s_crd_bush_IR, first=True)
      # TODO should really have this material be graphitar and not graphite
      self.u_crd_grphUpperBushOGD[boron].add_ring(     self.mats['Graphite'], crd_bush_surfs_o)
      self.u_crd_grphUpperBushOGD[boron].add_ring(     self.mats['Al1100'],   crd_bushBear_surfs_o)
      self.u_crd_grphUpperBushOGD[boron].add_ring(     self.mats['Air'],      crd_upperRefl_surfs_i)
      if boron == 'CP2':
        # Using the basic CP2 graphite material
        self.u_crd_grphUpperBushOGD[boron].add_ring(     self.mats['Graphite'], plug_refCrdUpperOG_surfs_o, octagon=True, nEnclaves=1)
      else:
        # Creating a graphite element segment with a specified boron impurity
        # This is an option arising from an early misunderstanding about the
        # axial reflector composition and will likely not be needed for
        # most applications
        self.u_crd_grphUpperBushOGD[boron].add_ring(     self.mats['Graphite {0}'.format(boron)], plug_refCrdUpperOG_surfs_o,
                                                         octagon=True, nEnclaves=1)
      self.u_crd_grphUpperBushOGD[boron].add_ring(     self.mats['Air'],       self.s_crd_upperSPOffGas_IR, first=True)
      self.u_crd_grphUpperBushOGD[boron].add_ring(     self.mats['Air'],       plug_clad_surfs_i, octagon=True, prevOctagon=True)
      self.u_crd_grphUpperBushOGD[boron].add_ring(     self.mats['Al6063'],    plug_clad_surfs_o, octagon=True, prevOctagon=True)
      self.u_crd_grphUpperBushOGD[boron].add_last_ring(self.mats['Air'])
      self.u_crd_grphUpperBushOGD[boron].finalize()
    # Part of the element containing the upper unmachined short plug with graphitar bushing, with offgas crimp
    self.u_crd_grphUpperBushOGC = {}
    for boron in self.graph_boron_ppms:
      self.u_crd_grphUpperBushOGC[boron] = InfiniteElement(name='Crd element upper region with graphitar bushing, offgas crimp')
      self.u_crd_grphUpperBushOGC[boron].add_ring(     self.mats['Air'],       self.s_crd_bush_IR, first=True)
      # TODO should really have this material be graphitar and not graphite
      self.u_crd_grphUpperBushOGC[boron].add_ring(     self.mats['Graphite'],  crd_bush_surfs_o)
      self.u_crd_grphUpperBushOGC[boron].add_ring(     self.mats['Al1100'],  crd_bushBear_surfs_o)
      self.u_crd_grphUpperBushOGC[boron].add_ring(     self.mats['Air'],       crd_upperRefl_surfs_i)
      if boron == 'CP2':
        # Using the basic CP2 graphite material
        self.u_crd_grphUpperBushOGC[boron].add_ring(     self.mats['Graphite'], plug_refCrdUpperOG_surfs_o, octagon=True, nEnclaves=1)
      else:
        # Creating a graphite element segment with a specified boron impurity
        # This is an option arising from an early misunderstanding about the
        # axial reflector composition and will likely not be needed for
        # most applications
        self.u_crd_grphUpperBushOGC[boron].add_ring(     self.mats['Graphite {0}'.format(boron)], plug_refCrdUpperOG_surfs_o,
                                                         octagon=True, nEnclaves=1)
      self.u_crd_grphUpperBushOGC[boron].add_ring(     self.mats['Al1100'],  self.s_crd_SPOffGasCrimp_R, first=True)
      self.u_crd_grphUpperBushOGC[boron].add_ring(     self.mats['Air'],       crd_crimpGap_surfs_i)
      self.u_crd_grphUpperBushOGC[boron].add_ring(     self.mats['Air'],       plug_clad_surfs_i, octagon=True, prevOctagon=True)
      self.u_crd_grphUpperBushOGC[boron].add_ring(     self.mats['Al6063'],  plug_clad_surfs_o, octagon=True, prevOctagon=True)
      self.u_crd_grphUpperBushOGC[boron].add_last_ring(self.mats['Air'])
      self.u_crd_grphUpperBushOGC[boron].finalize()
    # Part of the element containing the upper unmachined short plug with graphitar bushing, with offgas tube
    self.u_crd_grphUpperBushOGT = {}
    for boron in self.graph_boron_ppms:
      self.u_crd_grphUpperBushOGT[boron] = InfiniteElement(name='Crd element upper region with graphitar bushing, offgas tube')
      self.u_crd_grphUpperBushOGT[boron].add_ring(     self.mats['Air'],       self.s_crd_bush_IR, first=True)
      # TODO should really have this material be graphitar and not graphite
      self.u_crd_grphUpperBushOGT[boron].add_ring(     self.mats['Graphite'],  crd_bush_surfs_o)
      self.u_crd_grphUpperBushOGT[boron].add_ring(     self.mats['Al1100'],  crd_bushBear_surfs_o)
      self.u_crd_grphUpperBushOGT[boron].add_ring(     self.mats['Air'],       crd_upperRefl_surfs_i)
      if boron == 'CP2':
        # Using the basic CP2 graphite material
        self.u_crd_grphUpperBushOGT[boron].add_ring(     self.mats['Graphite'], plug_refCrdUpperOG_surfs_o, octagon=True, nEnclaves=1)
      else:
        # Creating a graphite element segment with a specified boron impurity
        # This is an option arising from an early misunderstanding about the
        # axial reflector composition and will likely not be needed for
        # most applications
        self.u_crd_grphUpperBushOGT[boron].add_ring(     self.mats['Graphite {0}'.format(boron)],
                                                         plug_refCrdUpperOG_surfs_o, octagon=True, nEnclaves=1)
      self.u_crd_grphUpperBushOGT[boron].add_ring(     self.mats['Air'],       self.s_crd_SPOffGasClad_IR, first=True)
      self.u_crd_grphUpperBushOGT[boron].add_ring(     self.mats['Al1100'],  crd_offgas_surfs_o)
      self.u_crd_grphUpperBushOGT[boron].add_ring(     self.mats['Air'],       crd_offgasHole_surfs_i)
      self.u_crd_grphUpperBushOGT[boron].add_ring(     self.mats['Air'],       plug_clad_surfs_i, octagon=True, prevOctagon=True)
      self.u_crd_grphUpperBushOGT[boron].add_ring(     self.mats['Al6063'],  plug_clad_surfs_o, octagon=True, prevOctagon=True)
      self.u_crd_grphUpperBushOGT[boron].add_last_ring(self.mats['Air'])
      self.u_crd_grphUpperBushOGT[boron].finalize()
    # Part of the element containing the upper unmachined short plug with graphitar bushing retainer
    self.u_crd_grphUpperRet = {}
    for boron in self.graph_boron_ppms:
      self.u_crd_grphUpperRet[boron] = InfiniteElement(name='Control rod element upper unmachined region with bushing retainer')
      self.u_crd_grphUpperRet[boron].add_ring(     self.mats['Air'],       self.s_crd_bushRet_IR, first=True)
      self.u_crd_grphUpperRet[boron].add_ring(     self.mats['Al1100'],  crd_bushRet_surfs_o)
      self.u_crd_grphUpperRet[boron].add_ring(     self.mats['Al1100'],  crd_bushRetBear_surfs_o)
      self.u_crd_grphUpperRet[boron].add_ring(     self.mats['Air'],       crd_upperRefl_surfs_i)
      if boron == 'CP2':
        # Using the basic CP2 graphite material
        self.u_crd_grphUpperRet[boron].add_ring(     self.mats['Graphite'],
                                                     plug_refCrdUpperOG_surfs_o, octagon=True, nEnclaves=1)
      else:
        # Creating a graphite element segment with a specified boron impurity
        # This is an option arising from an early misunderstanding about the
        # axial reflector composition and will likely not be needed for
        # most applications
        self.u_crd_grphUpperRet[boron].add_ring(     self.mats['Graphite {0}'.format(boron)],
                                                     plug_refCrdUpperOG_surfs_o, octagon=True, nEnclaves=1)
      self.u_crd_grphUpperRet[boron].add_ring(     self.mats['Air'],       self.s_crd_SPOffGasClad_IR, first=True)
      self.u_crd_grphUpperRet[boron].add_ring(     self.mats['Al1100'],  crd_offgas_surfs_o)
      self.u_crd_grphUpperRet[boron].add_ring(     self.mats['Air'],       crd_offgasHole_surfs_i)
      self.u_crd_grphUpperRet[boron].add_ring(     self.mats['Air'],       plug_clad_surfs_i, octagon=True, prevOctagon=True)
      self.u_crd_grphUpperRet[boron].add_ring(     self.mats['Al6063'],  plug_clad_surfs_o, octagon=True, prevOctagon=True)
      self.u_crd_grphUpperRet[boron].add_last_ring(self.mats['Air'])
      self.u_crd_grphUpperRet[boron].finalize()
    # Part of the element containing the upper machined short plug with graphitar bushing retainer
    self.u_crd_grphUpperRetMsp = {}
    for boron in self.graph_boron_ppms:
      self.u_crd_grphUpperRetMsp[boron] = InfiniteElement(name='Control rod element upper machined region with bushing retainer')
      self.u_crd_grphUpperRetMsp[boron].add_ring(     self.mats['Air'],       self.s_crd_bushRet_IR, first=True)
      self.u_crd_grphUpperRetMsp[boron].add_ring(     self.mats['Al1100'],  crd_bushRet_surfs_o)
      self.u_crd_grphUpperRetMsp[boron].add_ring(     self.mats['Al1100'],  crd_bushRetBear_surfs_o)
      self.u_crd_grphUpperRetMsp[boron].add_ring(     self.mats['Air'],       crd_upperRefl_surfs_i)
      if boron == 'CP2':
        # Using the basic CP2 graphite material
        self.u_crd_grphUpperRetMsp[boron].add_ring(     self.mats['Graphite'], Mplug_refCrdUpper_surfs_o, box=True, nEnclaves=1)
      else:
        # Creating a graphite element segment with a specified boron impurity
        # This is an option arising from an early misunderstanding about the
        # axial reflector composition and will likely not be needed for
        # most applications
        self.u_crd_grphUpperRetMsp[boron].add_ring(     self.mats['Graphite {0}'.format(boron)], Mplug_refCrdUpper_surfs_o,
                                                        box=True, nEnclaves=1)
      self.u_crd_grphUpperRetMsp[boron].add_ring(     self.mats['Air'],       self.s_crd_SPOffGasClad_IR, first=True)
      self.u_crd_grphUpperRetMsp[boron].add_ring(     self.mats['Al1100'],  crd_offgas_surfs_o)
      self.u_crd_grphUpperRetMsp[boron].add_ring(     self.mats['Air'],       crd_offgasHole_surfs_i)
      self.u_crd_grphUpperRetMsp[boron].add_ring(     self.mats['Air'],       Mplug_clad_surfs_i, octagon=True, prevBox=True)
      self.u_crd_grphUpperRetMsp[boron].add_ring(     self.mats['Al6063'],  plug_clad_surfs_o, octagon=True, prevOctagon=True)
      self.u_crd_grphUpperRetMsp[boron].add_last_ring(self.mats['Air'])
      self.u_crd_grphUpperRetMsp[boron].finalize()
    # Part of the element containing the upper machined short plug with only the thin bearing component
    self.u_crd_grphUpperBearMsp = {}
    for boron in self.graph_boron_ppms:
      self.u_crd_grphUpperBearMsp[boron] = InfiniteElement(name='Control rod element upper machined region with thin bearing')
      self.u_crd_grphUpperBearMsp[boron].add_ring(     self.mats['Air'],       self.s_crd_bearThin_IR, first=True)
      self.u_crd_grphUpperBearMsp[boron].add_ring(     self.mats['Al1100'],  crd_tnBear_surfs_o)
      self.u_crd_grphUpperBearMsp[boron].add_ring(     self.mats['Air'],       crd_upperRefl_surfs_i)
      if boron == 'CP2':
        # Using the basic CP2 graphite material
        self.u_crd_grphUpperBearMsp[boron].add_ring(     self.mats['Graphite'], Mplug_refCrdUpper_surfs_o, box=True, nEnclaves=1)
      else:
        # Creating a graphite element segment with a specified boron impurity
        # This is an option arising from an early misunderstanding about the
        # axial reflector composition and will likely not be needed for
        # most applications
        self.u_crd_grphUpperBearMsp[boron].add_ring(     self.mats['Graphite {0}'.format(boron)],
                                                         Mplug_refCrdUpper_surfs_o, box=True, nEnclaves=1)
      self.u_crd_grphUpperBearMsp[boron].add_ring(     self.mats['Air'],       self.s_crd_SPOffGasClad_IR, first=True)
      self.u_crd_grphUpperBearMsp[boron].add_ring(     self.mats['Al1100'],    crd_offgas_surfs_o)
      self.u_crd_grphUpperBearMsp[boron].add_ring(     self.mats['Air'],       crd_offgasHole_surfs_i)
      self.u_crd_grphUpperBearMsp[boron].add_ring(     self.mats['Air'],       Mplug_clad_surfs_i, octagon=True, prevBox=True)
      self.u_crd_grphUpperBearMsp[boron].add_ring(     self.mats['Al6063'],    plug_clad_surfs_o, octagon=True, prevOctagon=True)
      self.u_crd_grphUpperBearMsp[boron].add_last_ring(self.mats['Air'])
      self.u_crd_grphUpperBearMsp[boron].finalize()
    # Part of the element containing the upper machined short plug with the thin bearing component and zirc element tube
    self.u_crd_grphUpperTubeMsp = {}
    for boron in self.graph_boron_ppms:
      self.u_crd_grphUpperTubeMsp[boron] = InfiniteElement(name='Control rod element upper machined with thin bearing and Zr tube')
      self.u_crd_grphUpperTubeMsp[boron].add_ring(     self.mats['Air'],       self.s_crd_elem_IR, first=True)
      self.u_crd_grphUpperTubeMsp[boron].add_ring(     self.mats['Zirc3'],     crd_elem_surfs_o)
      self.u_crd_grphUpperTubeMsp[boron].add_ring(     self.mats['Air'],       crd_tnBear_surfs_i)
      self.u_crd_grphUpperTubeMsp[boron].add_ring(     self.mats['Al1100'],    crd_tnBear_surfs_o)
      self.u_crd_grphUpperTubeMsp[boron].add_ring(     self.mats['Air'],       crd_upperRefl_surfs_i)
      if boron == 'CP2':
        # Using the basic CP2 graphite material
        self.u_crd_grphUpperTubeMsp[boron].add_ring(     self.mats['Graphite'], Mplug_refCrdUpper_surfs_o, box=True, nEnclaves=1)
      else:
        # Creating a graphite element segment with a specified boron impurity
        # This is an option arising from an early misunderstanding about the
        # axial reflector composition and will likely not be needed for
        # most applications
        self.u_crd_grphUpperTubeMsp[boron].add_ring(     self.mats['Graphite {0}'.format(boron)], Mplug_refCrdUpper_surfs_o,
                                                         box=True, nEnclaves=1)
      self.u_crd_grphUpperTubeMsp[boron].add_ring(     self.mats['Air'],     self.s_crd_SPOffGasClad_IR, first=True)
      self.u_crd_grphUpperTubeMsp[boron].add_ring(     self.mats['Al1100'],  crd_offgas_surfs_o)
      self.u_crd_grphUpperTubeMsp[boron].add_ring(     self.mats['Air'],     crd_offgasHole_surfs_i)
      self.u_crd_grphUpperTubeMsp[boron].add_ring(     self.mats['Air'],     Mplug_clad_surfs_i, octagon=True, prevBox=True)
      self.u_crd_grphUpperTubeMsp[boron].add_ring(     self.mats['Al6063'],  plug_clad_surfs_o, octagon=True, prevOctagon=True)
      self.u_crd_grphUpperTubeMsp[boron].add_last_ring(self.mats['Air'])
      self.u_crd_grphUpperTubeMsp[boron].finalize()

    # Create a handful of radial universes for the access hole dummy elements
    # First the machined short plug with zirc cladding
    self.u_accessMSP_zr = {}
    for boron in self.graph_boron_ppms:
      self.u_accessMSP_zr[boron] = InfiniteElement(name='Access hole dummy element machined short plug with Zirc clad')
      if boron == 'CP2':
        # Using the basic CP2 graphite material
        self.u_accessMSP_zr[boron].add_ring(     self.mats['Graphite'], Mplug_surfs, box=True, first=True)
      else:
        # Creating a graphite element segment with a specified boron impurity
        # This is an option arising from an early misunderstanding about the
        # axial reflector composition and will likely not be needed for
        # most applications
        self.u_accessMSP_zr[boron].add_ring(     self.mats['Graphite {0}'.format(boron)], Mplug_surfs, box=True, first=True)
      self.u_accessMSP_zr[boron].add_ring(     self.mats['Air'], Mplug_clad_surfs_i, octagon=True, prevBox=True)
      self.u_accessMSP_zr[boron].add_ring(     self.mats['Zirc3'], plug_clad_surfs_o, octagon=True, prevOctagon=True)
      self.u_accessMSP_zr[boron].add_last_ring(self.mats['Air'])
      self.u_accessMSP_zr[boron].finalize()
    # Component of the access hole dummy element central region with no window
    self.u_accessCentral = InfiniteElement(name='Access hole dummy element central region, no window')
    # NOTE the zirconium in this component is currently set to Zirc 3 because the BATMAN report seems to indicate that comprises
    #      the overwhelming majority of Zirc in TREAT, however, the BATMAN report says that this Zirc is "Zr-3 or Zr-4"
    self.u_accessCentral.add_ring(     self.mats['Air'],   accessStiff_surfs, octagon=True, first=True, stiffener=True)
    self.u_accessCentral.add_ring(     self.mats['Zirc3'], accessStiff_surfs, stiffener=True, first=True)
    self.u_accessCentral.add_ring(     self.mats['Zirc3'], accessClad_surfs_o, octagon=True, prevOctagon=True)
    self.u_accessCentral.add_last_ring(self.mats['Air'])
    self.u_accessCentral.finalize()
    # Component of the access hole dummy element central region with the window
    self.u_accessWindow = InfiniteElement(name='Access hole dummy element central region with window')
    # NOTE the zirconium in this component is currently set to Zirc 3 because the BATMAN report seems to indicate that comprises
    #      the overwhelming majority of Zirc in TREAT, however, the BATMAN report says that this Zirc is "Zr-3 or Zr-4"
    self.u_accessWindow.add_ring(     self.mats['Air'],  accessStiff_surfs, octagon=True, first=True, window=True, stiffener=True)
    self.u_accessWindow.add_ring(     self.mats['Zirc3'],  accessStiff_surfs, stiffener=True, first=True)
    self.u_accessWindow.add_ring(     self.mats['Air'],  accessCenter_surfs, box=True, first=True)
    self.u_accessWindow.add_ring(     self.mats['Air'],  accessWindowN_surfs, box=True, first=True)
    self.u_accessWindow.add_ring(     self.mats['Air'],  accessWindowS_surfs, box=True, first=True)
    self.u_accessWindow.add_ring(     self.mats['Zirc3'], accessClad_surfs_o, octagon=True, prevOctagon=True, window=True)
    self.u_accessWindow.add_last_ring(self.mats['Air'])
    self.u_accessWindow.finalize()

    ### Structural radial surfaces (e.g. spacers, fittings, supports, etc)

    # Regular fuel and dummy elements first
    # Zirc spacer regions between fueled region and top / bottom reflector regions
    self.u_reg_zr_spacer = InfiniteElement(name='Regular Zirc spacer')
    self.u_reg_zr_spacer.add_ring(     self.mats['Zirc3'], fuel_surfs_o, octagon=True, first=True)
    self.u_reg_zr_spacer.add_ring(     self.mats['Air'],  clad_surfs_i, octagon=True, prevOctagon=True)
    self.u_reg_zr_spacer.add_ring(     self.mats['Zirc3'], clad_surfs_o, octagon=True, prevOctagon=True)
    self.u_reg_zr_spacer.add_last_ring(self.mats['Air'])
    self.u_reg_zr_spacer.finalize()
    # Aluminum spacer region between fueled region and bottom reflector region
    self.u_reg_al_spacer_bot = InfiniteElement(name='Regular bottom Aluminum spacer')
    self.u_reg_al_spacer_bot.add_ring(     self.mats['Al6063'], block_surfs_o, octagon=True, first=True)
    self.u_reg_al_spacer_bot.add_last_ring(self.mats['Air'])
    self.u_reg_al_spacer_bot.finalize()
    # Aluminum spacer region between fueled region and top reflector region
    self.u_reg_al_spacer_top = InfiniteElement(name='Regular top Aluminum spacer')
    self.u_reg_al_spacer_top.add_ring(     self.mats['Air'],   self.s_offgas_tube_IR, first=True)
    self.u_reg_al_spacer_top.add_ring(     self.mats['Al6063'], block_alSpacer_surfs_o, octagon=True)
    self.u_reg_al_spacer_top.add_last_ring(self.mats['Air'])
    self.u_reg_al_spacer_top.finalize()
    # Gap region between Zr and Al spacers. NOTE: in reality, this has 4 small Zr divots that are neglected here
    self.u_reg_gap_spacer = InfiniteElement(name='Regular gap spacer')
    self.u_reg_gap_spacer.add_ring(     self.mats['Air'],  tn_cld_surfs_i, octagon=True, first=True)
    self.u_reg_gap_spacer.add_ring(     self.mats['Zirc3'], tn_cld_surfs_o, octagon=True, prevOctagon=True)
    self.u_reg_gap_spacer.add_last_ring(self.mats['Air'])
    self.u_reg_gap_spacer.finalize()

    # The next several universes are the top fuel fitting
    # Gap region between axial reflector blocks and support plate / end fitting
    self.u_reg_tff_base = {}
    self.u_reg_tff_mid = {}
    self.u_reg_tff_neck = {}
    self.u_reg_tff_top_cone = {}

    for fill in self.fuel_fitting_fills:
      self.u_reg_tff_base[fill] = InfiniteElement(name='Regular top fuel fitting, base')
      # First ring: 3" diameter = 3.81 cm radius (hollow)
      self.u_reg_tff_base[fill].add_ring(self.mats[fill], reg_tff_base_surfs_i, octagon=True, first=True)
      # Second ring: 4" diameter = 5.08 cm radius (aluminum)
      self.u_reg_tff_base[fill].add_ring(self.mats['Al1100'], reg_tff_base_surfs_o, octagon=True, prevOctagon=True)
      # Third ring: outside/air
      self.u_reg_tff_base[fill].add_last_ring(self.mats['Air'])
      self.u_reg_tff_base[fill].finalize()
      #
      # The middle slanted/cone portion--approximated as an average-diameter cylinder
      self.u_reg_tff_mid[fill] = InfiniteElement(name="Regular top fuel fitting, cone (mid)")
      # First ring: 2.5" diameter = 3.175 cm radius (hollow) -- average
      self.u_reg_tff_mid[fill].add_ring(self.mats[fill], reg_tff_mid_surfs_i, octagon=True, first=True)
      # Second ring: 3" diameter = 3.81 cm radius (aluminum) --average
      self.u_reg_tff_mid[fill].add_ring(self.mats['Al1100'], reg_tff_mid_surfs_o, octagon=True, prevOctagon=True)
      # Third ring: outside/air
      self.u_reg_tff_mid[fill].add_last_ring(self.mats['Air'])
      self.u_reg_tff_mid[fill].finalize()
      #
      # The necked portion
      self.u_reg_tff_neck[fill] = InfiniteElement(name="Regular top fuel fitting, neck")
      # First ring; 2" diameter = 2.54 cm radius (hollow)
      self.u_reg_tff_neck[fill].add_ring(self.mats[fill], self.s_reg_tff_neck_i, octagon=False, first=True)
      # Second ring: 2.5" diameter = 3.175 cm radius (aluminum)
      self.u_reg_tff_neck[fill].add_ring(self.mats['Al1100'], reg_tff_neck_surfs, octagon=False, prevOctagon=False)
      # Third ring: outside/air
      self.u_reg_tff_neck[fill].add_last_ring(self.mats['Air'])
      self.u_reg_tff_neck[fill].finalize()
      #
      # The top slanted/cone portion--approximated as an average-diameter cylinder
      self.u_reg_tff_top_cone[fill] = InfiniteElement(name="Regular top fuel fitting, cone (top)")
      # First ring: 2" diameter = 2.54 cm radius (hollow) -- exact
      self.u_reg_tff_top_cone[fill].add_ring(self.mats[fill], self.s_reg_tff_cone_top_i, octagon=False, first=True)
      # Second ring: 2.75" diameter = 3.493 cm radius (aluminum) -- average
      self.u_reg_tff_top_cone[fill].add_ring(self.mats['Al1100'], reg_tff_cone_top_surfs, octagon=False, prevOctagon=False)
      # Third ring: outside/air
      self.u_reg_tff_top_cone[fill].add_last_ring(self.mats['Air'])
      self.u_reg_tff_top_cone[fill].finalize()
    
    # The next several universes are the bottom fuel fitting
    # The octagonal base
    self.u_reg_bff_base = InfiniteElement(name="Regular bottom fuel fitting, base")
    self.u_reg_bff_base.add_ring(self.mats['Al1100'], reg_bff_base_surfs, octagon=True, first=True)
    self.u_reg_bff_base.add_last_ring(self.mats['Air'])
    self.u_reg_bff_base.finalize()
    # The middle cone portion--approximated as an average-diameter cylinder
    self.u_reg_bff_cone = InfiniteElement(name="Regular bottom fuel fitting, cone")
    self.u_reg_bff_cone.add_ring(self.mats['Al1100'], self.s_reg_bff_cone, first=True)
    self.u_reg_bff_cone.add_last_ring(self.mats['Mild Steel'])
    self.u_reg_bff_cone.finalize()
    # The bottom prong portion, part inside the grid plate
    self.u_reg_bff_prong_top = InfiniteElement(name="Regular bottom fuel fitting, prong in the grid plate")
    self.u_reg_bff_prong_top.add_ring(self.mats['Al1100'], self.s_reg_bff_prong, first=True)
    self.u_reg_bff_prong_top.add_last_ring(self.mats['Mild Steel'])
    self.u_reg_bff_prong_top.finalize()
    # The bottom prong portion, part inside the guide tube
    self.u_reg_bff_prong_mid = InfiniteElement(name="Regular bottom fuel fitting, prong in the guide tube")
    self.u_reg_bff_prong_mid.add_ring(self.mats['Al1100'], self.s_reg_bff_prong, first=True)
    self.u_reg_bff_prong_mid.add_ring(self.mats['Mild Steel'], reg_support_elemGuide_surfs_o)
    self.u_reg_bff_prong_mid.add_last_ring(self.mats['Air'])
    self.u_reg_bff_prong_mid.finalize()
    # The bottom prong portion, part in air, ignoring the slightly narrowed tip
    self.u_reg_bff_prong_bot = InfiniteElement(name="Regular bottom fuel fitting, prong in air")
    self.u_reg_bff_prong_bot.add_ring(self.mats['Al1100'], self.s_reg_bff_prong, first=True)
    self.u_reg_bff_prong_bot.add_last_ring(self.mats['Air'])
    self.u_reg_bff_prong_bot.finalize()

    # The next several universes are for the half-width bottom fuel fitting
    translation_vector = [0, -c.hw_bff_offset_y, 0]
    # The cone portion--approximated as an average-diameter cylinder, in the grid plate
    u_hw_bff_cone_t = InfiniteElement(name="Half-width bottom fuel fitting, cone")
    u_hw_bff_cone_t.add_ring(self.mats['Al6061'], self.s_hw_bff_cone, first=True)
    u_hw_bff_cone_t.add_last_ring(self.mats['Mild Steel'])
    u_hw_bff_cone_t.finalize()
    self.u_hw_bff_cone = u_hw_bff_cone_t.translate_rotate(t_vector=translation_vector)
    # The prong portion
    # Top portion, in the grid plate
    u_hw_bff_prong_top_t = InfiniteElement(name="Half-width bottom fuel fitting, prong in the grid plate")
    u_hw_bff_prong_top_t.add_ring(self.mats['Al6061'], self.s_hw_bff_prong, first=True)
    u_hw_bff_prong_top_t.add_last_ring(self.mats['Mild Steel'])
    u_hw_bff_prong_top_t.finalize()
    self.u_hw_bff_prong_top = u_hw_bff_prong_top_t.translate_rotate(t_vector=translation_vector)
    # Middle portion, in the guide ring
    # The element guide ring is not quite right--but its actual dimensions are not in BATMAN
    u_hw_bff_prong_mid_t = InfiniteElement(name="Half-width bottom fuel fitting, prong in guide tube")
    u_hw_bff_prong_mid_t.add_ring(self.mats['Al6061'], self.s_hw_bff_prong, first=True)
    u_hw_bff_prong_mid_t.add_ring(self.mats['Mild Steel'], hw_support_elemGuide_surfs_o)
    u_hw_bff_prong_mid_t.add_last_ring(self.mats['Air'])
    u_hw_bff_prong_mid_t.finalize()
    self.u_hw_bff_prong_mid = u_hw_bff_prong_mid_t.translate_rotate(t_vector=translation_vector)
    # Bottom of the prong, bare in air
    u_hw_bff_prong_bot_t = InfiniteElement(name="Half-width bottom fuel fitting, prong in air")
    u_hw_bff_prong_bot_t.add_ring(self.mats['Al6061'], self.s_hw_bff_prong, first=True)
    u_hw_bff_prong_bot_t.add_last_ring(self.mats['Air'])
    u_hw_bff_prong_bot_t.finalize()
    self.u_hw_bff_prong_bot = u_hw_bff_prong_bot_t.translate_rotate(t_vector=translation_vector)
    # Just the hemispherical tip
    u_hw_bff_tip_t = InfiniteElement(name="Half-width bottom fuel fitting, tip")
    u_hw_bff_tip_t.add_ring(self.mats['Al6061'], self.s_hw_bff_tip, first=True)
    u_hw_bff_tip_t.add_last_ring(self.mats['Air'])
    u_hw_bff_tip_t.finalize()
    self.u_hw_bff_tip = u_hw_bff_tip_t.translate_rotate(t_vector=translation_vector)

    # Most of the half-width elements will be of the same geometric shape
    # Create the full octagonal universe for the lead brick
    self.u_lead_brick = InfiniteElement(name="Full lead brick")
    self.u_lead_brick.add_ring(self.mats['Lead'],  hw_innermost_surfs, octagon=True, first=True)
    self.u_lead_brick.add_ring(self.mats['Air'],   hw_can_surfs_i, octagon=True, prevOctagon=True)
    self.u_lead_brick.add_ring(self.mats['Zirc3'], hw_can_surfs_o, octagon=True, prevOctagon=True)
    self.u_lead_brick.add_last_ring(self.mats['Air'])
    self.u_lead_brick.finalize()
    # There is a class in corebuilder that allows us to adapt
    self.u_half_lead_brick = PartialElement(name="Half lead brick (partial element)",
                                            full_element=self.u_lead_brick, outer_fill=self.empty,
                                            gap_fill=self.mats['Air'], clad_fill=self.mats['Zirc3'],
                                            clad_o_surfs=hw_can_surfs_o, clad_i_surfs=hw_can_surfs_i,
                                            y_surfs=half_element_dict)
    self.u_half_lead_brick.finalize()

    # Create the universes for the the bff base, tff base, and P1/P2 extensions
    self.u_al_brick = InfiniteElement(name="Full Aluminum brick")
    self.u_al_brick.add_ring(self.mats['Al6061'], hw_innermost_surfs, octagon=True, first=True)
    self.u_al_brick.add_ring(self.mats['Air'], hw_can_surfs_i, octagon=True, prevOctagon=True)
    self.u_al_brick.add_ring(self.mats['Zirc3'], hw_can_surfs_o, octagon=True, prevOctagon=True)
    self.u_al_brick.add_last_ring(self.mats['Air'])
    self.u_al_brick.finalize()

    self.u_half_al_brick = PartialElement(name="Half aluminum brick (partial element)",
                                          full_element=self.u_al_brick, outer_fill=self.empty,
                                          clad_fill=self.mats['Zirc3'], gap_fill=self.mats['Air'],
                                          y_surfs=half_element_dict)
    self.u_half_al_brick.clad_i_surfs = hw_can_surfs_i
    self.u_half_al_brick.clad_o_surfs = hw_can_surfs_o
    self.u_half_al_brick.finalize()

    # Create the universes for the graphite block
    self.u_graph3 = {}
    self.u_half_graph3 = {}
    for boron in self.graph_boron_ppms:
      if boron == "CP2":
        borname = ""
      else:
        borname = " " + boron
      self.u_graph3[boron] = InfiniteElement(name='Full Mk-III graphite {} block'.format(boron))
      self.u_graph3[boron].add_ring(self.mats['Graphite{}'.format(borname)],
                                    hw_innermost_surfs, octagon=True, first=True)
      self.u_graph3[boron].add_ring(self.mats['Air'], hw_can_surfs_i, octagon=True, prevOctagon=True)
      self.u_graph3[boron].add_ring(self.mats['Zirc3'], hw_can_surfs_o, octagon=True, prevOctagon=True)
      self.u_graph3[boron].add_last_ring(self.mats['Air'])
      self.u_graph3[boron].finalize()

      self.u_half_graph3[boron] = PartialElement(name="Half Mk-III graphite {} block (partial element)".format(boron),
                                                 full_element=self.u_graph3[boron], outer_fill=self.empty,
                                                 clad_fill=self.mats['Zirc3'], gap_fill=self.mats['Air'],
                                                 y_surfs=half_element_dict)
      self.u_half_graph3[boron].clad_i_surfs = hw_can_surfs_i
      self.u_half_graph3[boron].clad_o_surfs = hw_can_surfs_o
      self.u_half_graph3[boron].finalize()

    # FIXME: Modeling these all as solid; but it looks like there could be a hole drilled?

    # TODO: Create the universes for the exposed base of the lifting adapter, if necessary

    # Create the universes for the sloped portion of the lifting adapter
    self.u_tff3_mid = InfiniteElement(name="Full lifting adapter, middle cone")
    self.u_tff3_mid.add_ring(self.mats['Al6061'], hw_mid_surfs, octagon=True, first=True)
    self.u_tff3_mid.add_last_ring(self.mats['Air'])
    self.u_tff3_mid.finalize()

    self.u_half_tff_mid = PartialElement(name="Half lifting adapter, middle cone (partial element)",
                                         full_element=self.u_tff3_mid, outer_fill=self.empty,
                                         y_surfs=bare_half_element_dict)
    self.u_half_tff_mid.finalize()

    # Create the universes for the top portion/head of the lifting adapter
    self.u_tff3_head = InfiniteElement(name="Full lifting adapter, head")
    self.u_tff3_head.add_ring(self.mats['Al6061'], hw_head_surfs, octagon=True, first=True)
    self.u_tff3_head.add_last_ring(self.mats['Air'])
    self.u_tff3_head.finalize()

    self.u_half_tff_head = PartialElement(name="Half lifting adapter, head (partial element)",
                                     full_element=self.u_tff3_head, outer_fill=self.empty,
                                     y_surfs=bare_half_element_dict)
    self.u_half_tff_head.finalize()

    

    # Now do the same for the spacers on the control rod assemblies
    # The zirc spacers directly above and below the fuel
    self.u_crd_zr_spacer = InfiniteElement(name='Zirc fuel region crd spacer')
    self.u_crd_zr_spacer.add_ring(     self.mats['Air'],   self.s_crd_elem_IR, first=True)
    self.u_crd_zr_spacer.add_ring(     self.mats['Zirc3'], crd_elem_surfs_o)
    self.u_crd_zr_spacer.add_ring(     self.mats['Zirc3'], fuel_crd_zrSpacer_surfs_o, octagon=True)
    self.u_crd_zr_spacer.add_ring(     self.mats['Air'],   clad_surfs_i, octagon=True, prevOctagon=True)
    self.u_crd_zr_spacer.add_ring(     self.mats['Zirc3'], clad_surfs_o, octagon=True, prevOctagon=True)
    self.u_crd_zr_spacer.add_last_ring(self.mats['Air'])
    self.u_crd_zr_spacer.finalize()
    # Aluminum spacer region between the fuel region and the lower axial reflector
    self.u_crd_al_spacer_bot = InfiniteElement(name='Lower Axial Reflector Aluminum crd spacer')
    self.u_crd_al_spacer_bot.add_ring(     self.mats['Air'],    self.s_crd_elem_IR, first=True)
    self.u_crd_al_spacer_bot.add_ring(     self.mats['Zirc3'],  crd_elem_surfs_o)
    self.u_crd_al_spacer_bot.add_ring(     self.mats['Al6063'], block_crdSpacer_surfs_o, octagon=True)
    self.u_crd_al_spacer_bot.add_last_ring(self.mats['Air'])
    self.u_crd_al_spacer_bot.finalize()
    # Aluminum spacer region between the fuel region and the upper axial reflector
    self.u_crd_al_spacer_top = InfiniteElement(name='Upper Axial Reflector Aluminum crd spacer')
    self.u_crd_al_spacer_top.add_ring(     self.mats['Air'],    self.s_crd_elem_IR, first=True)
    self.u_crd_al_spacer_top.add_ring(     self.mats['Zirc3'],  crd_elem_surfs_o)
    # Needs to be before the aluminum octagon due to some implicit assumptions on how the last ring material is filled
    self.u_crd_al_spacer_top.add_ring(     self.mats['Air'],    self.s_crd_SPOffGasClad_IR, first=True)
    self.u_crd_al_spacer_top.add_ring(     self.mats['Al6063'], block_crdSpacerOG_surfs_o, octagon=True, nEnclaves=1)
    self.u_crd_al_spacer_top.add_last_ring(self.mats['Air'])
    self.u_crd_al_spacer_top.finalize()
    # The divotted gaps between the zirc and aluminum spacers
    self.u_crd_gap_spacer = InfiniteElement(name='Crd gap spacer')
    self.u_crd_gap_spacer.add_ring(     self.mats['Air'],   self.s_crd_elem_IR, first=True)
    self.u_crd_gap_spacer.add_ring(     self.mats['Zirc3'], crd_elem_surfs_o)
    self.u_crd_gap_spacer.add_ring(     self.mats['Air'],   tn_cldCrd_surfs_i, octagon=True)
    self.u_crd_gap_spacer.add_ring(     self.mats['Zirc3'], tn_cld_surfs_o, octagon=True, prevOctagon=True)
    self.u_crd_gap_spacer.add_last_ring(self.mats['Air'])
    self.u_crd_gap_spacer.finalize()
    # The base fitting for the control rod element
    self.u_crd_base = InfiniteElement(name='Crd lower base')
    self.u_crd_base.add_ring(     self.mats['Air'],    self.s_crd_elem_IR, first=True)
    self.u_crd_base.add_ring(     self.mats['Zirc3'],  crd_elem_surfs_o)
    self.u_crd_base.add_ring(     self.mats['Al1100'], block_crdSpacer_surfs_o, octagon=True)
    self.u_crd_base.add_last_ring(self.mats['Air'])
    self.u_crd_base.finalize()
    # The extended lower tube for the control rod element, part in the grid plate
    self.u_crd_tube_top = InfiniteElement(name='Crd lower tube in grid plate')
    self.u_crd_tube_top.add_ring(     self.mats['Air'],   self.s_crd_elem_IR, first=True)
    self.u_crd_tube_top.add_ring(     self.mats['Zirc3'], crd_elem_surfs_o)
    self.u_crd_tube_top.add_last_ring(self.mats['Mild Steel'])
    self.u_crd_tube_top.finalize()
    # The extended lower tube for the control rod element, part in the steel guide tube
    self.u_crd_tube_bot = InfiniteElement(name='Crd lower tube in guide tube')
    self.u_crd_tube_bot.add_ring(     self.mats['Air'],   self.s_crd_elem_IR, first=True)
    self.u_crd_tube_bot.add_ring(     self.mats['Zirc3'], crd_elem_surfs_o)
    self.u_crd_tube_bot.add_ring(     self.mats['Mild Steel'], crd_supportGuide_surfs_o)
    self.u_crd_tube_bot.add_last_ring(self.mats['Air'])
    self.u_crd_tube_bot.finalize()
    # The extended lower guide tube for the control rod element
    self.u_crd_tube_guide = InfiniteElement(name='Crd lower guide tube')
    self.u_crd_tube_guide.add_ring(     self.mats['Air'],   self.s_crd_elem_OR, first=True)
    self.u_crd_tube_guide.add_ring(     self.mats['Mild Steel'], crd_supportGuide_surfs_o)
    self.u_crd_tube_guide.add_last_ring(self.mats['Air'])
    self.u_crd_tube_guide.finalize()
    # The base of the head fitting for the control rod element
    self.u_crd_head_base = InfiniteElement(name='Crd upper head, base')
    self.u_crd_head_base.add_ring(     self.mats['Air'],    self.s_crd_bearThick_IR, first=True)
    self.u_crd_head_base.add_ring(     self.mats['Al1100'], crd_tkBear_surfs_o)
    self.u_crd_head_base.add_ring(     self.mats['Al1100'], crd_head_base_surfs_o, octagon=True)
    self.u_crd_head_base.add_last_ring(self.mats['Air'])
    self.u_crd_head_base.finalize()
    # The top of the head fitting for the control rod element
    self.u_crd_head_top = InfiniteElement(name='Crd upper head, top')
    self.u_crd_head_top.add_ring(     self.mats['Air'],    self.s_crd_bearThick_IR, first=True)
    self.u_crd_head_top.add_ring(     self.mats['Al1100'], crd_tkBear_surfs_o)
    self.u_crd_head_top.add_ring(     self.mats['Al1100'], crd_head_top_surfs_o, octagon=True)
    self.u_crd_head_top.add_last_ring(self.mats['Air'])
    self.u_crd_head_top.finalize()

    # The extended upper bearing tube for the control rod element
    self.u_crd_upperTube = InfiniteElement(name='Crd upper tube')
    self.u_crd_upperTube.add_ring(     self.mats['Air'],    self.s_crd_bearThick_IR, first=True)
    self.u_crd_upperTube.add_ring(     self.mats['Al1100'], crd_tkBear_surfs_o)
    self.u_crd_upperTube.add_last_ring(self.mats['Air'])
    self.u_crd_upperTube.finalize()

    # Access hole structural components
    # Zirc spacer between the central region and the axial plugs
    self.u_access_zr_spacer = InfiniteElement(name='Access hole dummy element Zirc spacer')
    self.u_access_zr_spacer.add_ring(     self.mats['Zirc3'], block_surfs_o, octagon=True, first=True)
    self.u_access_zr_spacer.add_last_ring(self.mats['Air'])
    self.u_access_zr_spacer.finalize()
    # Lead top and bottom plugs
    self.u_access_PbPlug = {}
    self.u_access_PbPlug = InfiniteElement(name='Access hole dummy element top and bottom lead plugs')
    self.u_access_PbPlug.add_ring(     self.mats['Lead'], plug_ref_surfs_o, octagon=True, first=True)
    self.u_access_PbPlug.add_ring(     self.mats['Air'], plug_clad_surfs_i, octagon=True, prevOctagon=True)
    self.u_access_PbPlug.add_ring(     self.mats['Al1100'], plug_clad_surfs_o, octagon=True, prevOctagon=True)
    self.u_access_PbPlug.add_last_ring(self.mats['Air'])
    self.u_access_PbPlug.finalize()

    #########################################################################################################################
    ### Fuel axial stack universes
    #########################################################################################################################

    # 2.1 Standard Fuel Assembly
    self.u_fuel_p = {}
    for wgt, boron in zip(self.weight_percents, self.fuel_boron_ppms):
      self.u_fuel_p[wgt, boron] = AxialElement(name='Fuel rod - {0} wgt, {1}'.format(wgt, boron))
      self.u_fuel_p[wgt, boron].add_axial_section(self.s_struct_elemSupportPin_bot,  self.mats['Air'])
      self.u_fuel_p[wgt, boron].add_axial_section(self.s_struct_excoreElemGuide_bot, self.u_reg_bff_prong_bot)
      self.u_fuel_p[wgt, boron].add_axial_section(self.s_struct_excoreGridPlate_bot, self.u_reg_bff_prong_mid)
      self.u_fuel_p[wgt, boron].add_axial_section(self.s_struct_bff_prong_top,       self.u_reg_bff_prong_top)
      self.u_fuel_p[wgt, boron].add_axial_section(self.s_struct_bff_cone_top,     self.u_reg_bff_cone)
      self.u_fuel_p[wgt, boron].add_axial_section(self.s_struct_bff_base_top,     self.u_reg_bff_base)
      self.u_fuel_p[wgt, boron].add_axial_section(self.s_struct_lowerLP_top,      self.u_graph_ref_al['CP2', 'Al6063'])
      self.u_fuel_p[wgt, boron].add_axial_section(self.s_struct_lowerSP_mid,      self.u_graph_ref_al['CP2', 'Al6063'])
      self.u_fuel_p[wgt, boron].add_axial_section(self.s_struct_lowerSP_top,      self.u_graph_ref_mLsp_al['CP2', 'Al6063'])
      self.u_fuel_p[wgt, boron].add_axial_section(self.s_struct_lowerAlSpace_top, self.u_reg_al_spacer_bot)
      self.u_fuel_p[wgt, boron].add_axial_section(self.s_struct_lowerGap_top,     self.u_reg_gap_spacer)
      self.u_fuel_p[wgt, boron].add_axial_section(self.s_struct_lowerZrSpace_top, self.u_reg_zr_spacer)
      self.u_fuel_p[wgt, boron].add_axial_section(self.s_fuel_activeFuel_top,     self.u_fuel_active_pin[wgt, boron])
      self.u_fuel_p[wgt, boron].add_axial_section(self.s_struct_upperZrSpace_top, self.u_reg_zr_spacer)
      self.u_fuel_p[wgt, boron].add_axial_section(self.s_struct_upperGap_top,     self.u_reg_gap_spacer)
      self.u_fuel_p[wgt, boron].add_axial_section(self.s_struct_upperAlSpace_top, self.u_reg_al_spacer_top)
      self.u_fuel_p[wgt, boron].add_axial_section(self.s_struct_upperOffGas_top,  self.u_graph_ref_mUspG_al['CP2', 'Al6063'])
      self.u_fuel_p[wgt, boron].add_axial_section(self.s_struct_upperCrimp_top,   self.u_graph_ref_mUspC_al['CP2', 'Al6063'])
      self.u_fuel_p[wgt, boron].add_axial_section(self.s_struct_upperSP_mid,      self.u_graph_ref_mUsp_al['CP2', 'Al6063'])
      self.u_fuel_p[wgt, boron].add_axial_section(self.s_struct_upperSP_top,      self.u_graph_ref_Usp_al['CP2', 'Al6063'])
      self.u_fuel_p[wgt, boron].add_axial_section(self.s_struct_upperLP_top,      self.u_graph_ref_al['CP2', 'Al6063'])
      self.u_fuel_p[wgt, boron].add_axial_section(self.s_struct_tff_base_top,     self.u_reg_tff_base['Air'])
      self.u_fuel_p[wgt, boron].add_axial_section(self.s_struct_tff_mid_top,      self.u_reg_tff_mid['Air'])
      self.u_fuel_p[wgt, boron].add_axial_section(self.s_struct_tff_neck_top,     self.u_reg_tff_neck['Air'])
      self.u_fuel_p[wgt, boron].add_axial_section(self.s_struct_tff_top,          self.u_reg_tff_top_cone['Air'])
      self.u_fuel_p[wgt, boron].add_last_axial_section(                           self.mats['Air'])
      self.u_fuel_p[wgt, boron].finalize()

    # 2.2 Control Rod Fuel Assembly
    self.u_crd_p = {}
    for wgt, boron in zip(self.weight_percents, self.fuel_boron_ppms):
      self.u_crd_p[wgt, boron] = AxialElement(name='Control rod bank assembly - {0} wgt, {1}'.format(wgt,boron))
      self.u_crd_p[wgt, boron].add_axial_section(self.s_struct_lowerCrdTube_bot,    self.u_crd_tube_guide)
      self.u_crd_p[wgt, boron].add_axial_section(self.s_struct_excoreGridPlate_bot, self.u_crd_tube_bot)
      self.u_crd_p[wgt, boron].add_axial_section(self.s_struct_lowerCrdBase_bot,    self.u_crd_tube_top)
      self.u_crd_p[wgt, boron].add_axial_section(self.s_struct_lowerReflec_bot,     self.u_crd_base)
      self.u_crd_p[wgt, boron].add_axial_section(self.s_struct_lowerLP_top,         self.u_crd_grphLower['CP2'])
      self.u_crd_p[wgt, boron].add_axial_section(self.s_struct_lowerSP_mid,         self.u_crd_grphLower['CP2'])
      self.u_crd_p[wgt, boron].add_axial_section(self.s_struct_lowerSP_top,         self.u_crd_grphLowerMsp['CP2'])
      self.u_crd_p[wgt, boron].add_axial_section(self.s_struct_lowerAlSpace_top,    self.u_crd_al_spacer_bot)
      self.u_crd_p[wgt, boron].add_axial_section(self.s_struct_lowerGap_top,        self.u_crd_gap_spacer)
      self.u_crd_p[wgt, boron].add_axial_section(self.s_struct_lowerZrSpace_top,    self.u_crd_zr_spacer)
      self.u_crd_p[wgt, boron].add_axial_section(self.s_fuel_activeFuel_top,        self.u_crd_active[wgt, boron])
      self.u_crd_p[wgt, boron].add_axial_section(self.s_struct_upperZrSpace_top,    self.u_crd_zr_spacer)
      self.u_crd_p[wgt, boron].add_axial_section(self.s_struct_upperGap_top,        self.u_crd_gap_spacer)
      self.u_crd_p[wgt, boron].add_axial_section(self.s_struct_upperAlSpace_top,    self.u_crd_al_spacer_top)
      self.u_crd_p[wgt, boron].add_axial_section(self.s_struct_crdElem_top,         self.u_crd_grphUpperTubeMsp['CP2'])
      self.u_crd_p[wgt, boron].add_axial_section(self.s_struct_crdBearThin_top,     self.u_crd_grphUpperBearMsp['CP2'])
      self.u_crd_p[wgt, boron].add_axial_section(self.s_struct_upperSP_mid,         self.u_crd_grphUpperRetMsp['CP2'])
      self.u_crd_p[wgt, boron].add_axial_section(self.s_struct_crdBushRet_top,      self.u_crd_grphUpperRet['CP2'])
      self.u_crd_p[wgt, boron].add_axial_section(self.s_struct_crdOffGasTube_top,   self.u_crd_grphUpperBushOGT['CP2'])
      self.u_crd_p[wgt, boron].add_axial_section(self.s_struct_crdOffGasCrimp_top,  self.u_crd_grphUpperBushOGC['CP2'])
      self.u_crd_p[wgt, boron].add_axial_section(self.s_struct_crdOffGasDrill_top,  self.u_crd_grphUpperBushOGD['CP2'])
      self.u_crd_p[wgt, boron].add_axial_section(self.s_struct_crdBush_top,         self.u_crd_grphUpperBush['CP2'])
      self.u_crd_p[wgt, boron].add_axial_section(self.s_struct_upperSP_top,         self.u_crd_grphUpper['CP2'])
      self.u_crd_p[wgt, boron].add_axial_section(self.s_struct_upperLP_top,         self.u_crd_grphUpper['CP2'])
      self.u_crd_p[wgt, boron].add_axial_section(self.s_struct_upperCrdHead_mid,    self.u_crd_head_base)
      self.u_crd_p[wgt, boron].add_axial_section(self.s_struct_upperCrdHead_top,    self.u_crd_head_top)
      self.u_crd_p[wgt, boron].add_axial_section(self.s_struct_upperCrdTube_top,    self.u_crd_upperTube)
      self.u_crd_p[wgt, boron].add_last_axial_section(                              self.mats['Air'])
      self.u_crd_p[wgt, boron].finalize()

    # 2.5 Aluminum-Clad Dummy Fuel Assembly
    self.u_null_al_p = {}
    for boron in self.graph_boron_ppms:
      self.u_null_al_p[boron] = AxialElement(name='Blank Graphite Assembly - {0}'.format(boron))
      self.u_null_al_p[boron].add_axial_section(self.s_struct_elemSupportPin_bot,  self.mats['Air'])
      self.u_null_al_p[boron].add_axial_section(self.s_struct_excoreElemGuide_bot, self.u_reg_bff_prong_bot)
      self.u_null_al_p[boron].add_axial_section(self.s_struct_excoreGridPlate_bot, self.u_reg_bff_prong_mid)
      self.u_null_al_p[boron].add_axial_section(self.s_struct_bff_prong_top,       self.u_reg_bff_prong_top)
      self.u_null_al_p[boron].add_axial_section(self.s_struct_bff_cone_top,     self.u_reg_bff_cone)
      self.u_null_al_p[boron].add_axial_section(self.s_struct_bff_base_top,     self.u_reg_bff_base)
      self.u_null_al_p[boron].add_axial_section(self.s_struct_lowerZrSpace_top, self.u_graph_ref_al[boron, 'Al1100'])
      self.u_null_al_p[boron].add_axial_section(self.s_fuel_activeFuel_top,     self.u_graph_ref_al[boron, 'Al1100'])
      self.u_null_al_p[boron].add_axial_section(self.s_struct_upperLP_top,      self.u_graph_ref_al[boron, 'Al1100'])
      self.u_null_al_p[boron].add_axial_section(self.s_struct_tff_base_top,     self.u_reg_tff_base['Air'])
      self.u_null_al_p[boron].add_axial_section(self.s_struct_tff_mid_top,      self.u_reg_tff_mid['Air'])
      self.u_null_al_p[boron].add_axial_section(self.s_struct_tff_neck_top,     self.u_reg_tff_neck['Air'])
      self.u_null_al_p[boron].add_axial_section(self.s_struct_tff_top,          self.u_reg_tff_top_cone['Air'])
      self.u_null_al_p[boron].add_last_axial_section(                           self.mats['Air'])
      self.u_null_al_p[boron].finalize()

    # 2.6 Zircaloy-Clad Dummy Fuel Assemblies
    self.u_null_zr_p = {}
    for boron in self.graph_boron_ppms:
      self.u_null_zr_p[boron] = AxialElement(name='Blank Zr Clad Graphite Assembly - {0}'.format(boron))
      self.u_null_zr_p[boron].add_axial_section(self.s_struct_elemSupportPin_bot,  self.mats['Air'])
      self.u_null_zr_p[boron].add_axial_section(self.s_struct_excoreElemGuide_bot, self.u_reg_bff_prong_bot)
      self.u_null_zr_p[boron].add_axial_section(self.s_struct_excoreGridPlate_bot, self.u_reg_bff_prong_mid)
      self.u_null_zr_p[boron].add_axial_section(self.s_struct_bff_prong_top,    self.u_reg_bff_prong_top)
      self.u_null_zr_p[boron].add_axial_section(self.s_struct_bff_cone_top,     self.u_reg_bff_cone)
      self.u_null_zr_p[boron].add_axial_section(self.s_struct_bff_base_top,     self.u_reg_bff_base)
      self.u_null_zr_p[boron].add_axial_section(self.s_struct_lowerLP_top,      self.u_graph_ref_al[boron, 'Al6063'])
      self.u_null_zr_p[boron].add_axial_section(self.s_struct_lowerSP_mid,      self.u_graph_ref_al[boron, 'Al6063'])
      self.u_null_zr_p[boron].add_axial_section(self.s_struct_lowerSP_top,      self.u_graph_ref_mLsp_al[boron, 'Al6063'])
      self.u_null_zr_p[boron].add_axial_section(self.s_struct_lowerAlSpace_top, self.u_reg_al_spacer_bot)
      self.u_null_zr_p[boron].add_axial_section(self.s_struct_lowerGap_top,     self.u_reg_gap_spacer)
      self.u_null_zr_p[boron].add_axial_section(self.s_struct_lowerZrSpace_top, self.u_reg_zr_spacer)
      self.u_null_zr_p[boron].add_axial_section(self.s_fuel_activeFuel_top,     self.u_graph_dummy_zr[boron])
      self.u_null_zr_p[boron].add_axial_section(self.s_struct_upperZrSpace_top, self.u_reg_zr_spacer)
      self.u_null_zr_p[boron].add_axial_section(self.s_struct_upperGap_top,     self.u_reg_gap_spacer)
      self.u_null_zr_p[boron].add_axial_section(self.s_struct_upperAlSpace_top, self.u_reg_al_spacer_bot)
      self.u_null_zr_p[boron].add_axial_section(self.s_struct_upperSP_mid,      self.u_graph_ref_mLsp_al[boron, 'Al6063'])
      self.u_null_zr_p[boron].add_axial_section(self.s_struct_upperSP_top,      self.u_graph_ref_al[boron, 'Al6063'])
      self.u_null_zr_p[boron].add_axial_section(self.s_struct_upperLP_top,      self.u_graph_ref_al[boron, 'Al6063'])
      self.u_null_zr_p[boron].add_axial_section(self.s_struct_tff_base_top,     self.u_reg_tff_base['Air'])
      self.u_null_zr_p[boron].add_axial_section(self.s_struct_tff_mid_top,      self.u_reg_tff_mid['Air'])
      self.u_null_zr_p[boron].add_axial_section(self.s_struct_tff_neck_top,     self.u_reg_tff_neck['Air'])
      self.u_null_zr_p[boron].add_axial_section(self.s_struct_tff_top,          self.u_reg_tff_top_cone['Air'])
      self.u_null_zr_p[boron].add_last_axial_section(                           self.mats['Air'])
      self.u_null_zr_p[boron].finalize()

    # 2.6.2 Half Assembly
    self.u_hw_zr_p = {}
    for boron in self.graph_boron_ppms:
      self.u_hw_zr_p[boron] = AxialElement(name="Half-width Zr Clad Element - {}".format(boron))
      self.u_hw_zr_p[boron].add_axial_section(self.s_struct_hw_bff_tip_top, self.u_hw_bff_tip)
      self.u_hw_zr_p[boron].add_axial_section(self.s_struct_excoreElemGuide_bot, self.u_hw_bff_prong_bot)
      self.u_hw_zr_p[boron].add_axial_section(self.s_struct_excoreGridPlate_bot, self.u_hw_bff_prong_mid)
      self.u_hw_zr_p[boron].add_axial_section(self.s_struct_bff_prong_top, self.u_hw_bff_prong_top)
      self.u_hw_zr_p[boron].add_axial_section(self.s_struct_hw_bff_cone_top, self.u_hw_bff_cone)
      self.u_hw_zr_p[boron].add_axial_section(self.s_struct_hw_p2_top, self.u_half_al_brick)
      self.u_hw_zr_p[boron].add_axial_section(self.s_struct_hw_lower_lead_top, self.u_half_lead_brick)
      self.u_hw_zr_p[boron].add_axial_section(self.s_struct_hw_reg_graphite_top, self.u_half_graph3[boron])
      self.u_hw_zr_p[boron].add_axial_section(self.s_struct_hw_tff_clad_base_top, self.u_half_al_brick)
      self.u_hw_zr_p[boron].add_axial_section(self.s_struct_hw_mid_cone_top, self.u_half_tff_mid)
      self.u_hw_zr_p[boron].add_axial_section(self.s_struct_hw_tff_top, self.u_half_tff_head)
      self.u_hw_zr_p[boron].add_last_axial_section(self.mats['Air'])
      self.u_hw_zr_p[boron].finalize()

    # 2.6.7 Access Hole (50 inch) Half Assembly
    self.u_hw_ahole = {}
    for boron in self.graph_boron_ppms:
      self.u_hw_ahole[boron] = AxialElement(name="Half-width access hole Element - {}".format(boron))
      self.u_hw_ahole[boron].add_axial_section(self.s_struct_hw_bff_tip_top, self.u_hw_bff_tip)
      self.u_hw_ahole[boron].add_axial_section(self.s_struct_excoreElemGuide_bot, self.u_hw_bff_prong_bot)
      self.u_hw_ahole[boron].add_axial_section(self.s_struct_excoreGridPlate_bot, self.u_hw_bff_prong_mid)
      self.u_hw_ahole[boron].add_axial_section(self.s_struct_hw_bff_prong_top, self.u_hw_bff_prong_top)
      self.u_hw_ahole[boron].add_axial_section(self.s_struct_hw_bff_cone_top, self.u_hw_bff_cone)
      self.u_hw_ahole[boron].add_axial_section(self.s_struct_hw_p2_top, self.u_half_al_brick)
      self.u_hw_ahole[boron].add_axial_section(self.s_struct_hw_lower_lead_top, self.u_half_lead_brick)
      self.u_hw_ahole[boron].add_axial_section(self.s_struct_accLowerSP_mid, self.u_half_graph3[boron])

      full_window_level = AxialElement(name="Half-width access hole Window - {}".format(boron))
      full_window_level.add_axial_section(self.s_struct_accLowerSPAl_top, self.u_graph_ref_mLsp_al[boron, 'Al1100'])
      full_window_level.add_axial_section(self.s_struct_accLowerSPZr_top, self.u_accessMSP_zr[boron])
      full_window_level.add_axial_section(self.s_struct_accLowerZrSpace_top, self.u_access_zr_spacer)
      full_window_level.add_axial_section(self.s_struct_accWindow_bot, self.u_accessCentral)
      full_window_level.add_axial_section(self.s_struct_accWindow50_top, self.u_accessWindow)
      full_window_level.add_axial_section(self.s_struct_accTube50_top, self.u_accessCentral)
      full_window_level.add_axial_section(self.s_struct_accZrSpace50_top, self.u_access_zr_spacer)
      full_window_level.finalize()

      half_window_level = PartialElement(full_element=full_window_level, y_surfs=half_element_dict,
                                         outer_fill=self.empty, clad_fill=self.mats['Zirc3'], gap_fill=self.mats['Air'],
                                         clad_o_surfs=hw_can_surfs_o, clad_i_surfs=hw_can_surfs_i,
                                         window_width=c.hw_acc_window_width)
      half_window_level.finalize()
      self.u_hw_ahole[boron].add_axial_section(self.s_struct_hw_acc_upper_graphite_bot, half_window_level)

      self.u_hw_ahole[boron].add_axial_section(self.s_struct_hw_acc_upper_graphite_top, self.u_half_graph3[boron])
      self.u_hw_ahole[boron].add_axial_section(self.s_struct_hw_acc_upper_lead_top, self.u_half_lead_brick)
      self.u_hw_ahole[boron].add_axial_section(self.s_struct_hw_tff_clad_base_top, self.u_half_al_brick)
      self.u_hw_ahole[boron].add_axial_section(self.s_struct_hw_mid_cone_top, self.u_half_tff_mid)
      self.u_hw_ahole[boron].add_axial_section(self.s_struct_hw_tff_top, self.u_half_tff_head)
      self.u_hw_ahole[boron].add_last_axial_section(self.mats['Air'])
      self.u_hw_ahole[boron].finalize()

    # Access hole dummy element
    self.dummy_window_heights = ['48 inch', '48.5 inch', '49.5 inch']
    self.u_access_dummy_p = {}
    for hgt in self.dummy_window_heights:
      for boron in self.graph_boron_ppms:
        self.u_access_dummy_p[hgt,boron] = AxialElement(name='Access Window Dummy Element, {0} Window Height - {1}'.format(hgt,boron))
        self.u_access_dummy_p[hgt,boron].add_axial_section(self.s_struct_elemSupportPin_bot,  self.mats['Air'])
        self.u_access_dummy_p[hgt,boron].add_axial_section(self.s_struct_excoreElemGuide_bot, self.u_reg_bff_prong_bot)
        self.u_access_dummy_p[hgt,boron].add_axial_section(self.s_struct_excoreGridPlate_bot, self.u_reg_bff_prong_mid)
        self.u_access_dummy_p[hgt,boron].add_axial_section(self.s_struct_bff_prong_top,       self.u_reg_bff_prong_top)
        self.u_access_dummy_p[hgt,boron].add_axial_section(self.s_struct_bff_cone_top,        self.u_reg_bff_cone)
        self.u_access_dummy_p[hgt,boron].add_axial_section(self.s_struct_bff_base_top,        self.u_reg_bff_base)
        self.u_access_dummy_p[hgt,boron].add_axial_section(self.s_struct_accLowerLead_top,    self.u_access_PbPlug)
        self.u_access_dummy_p[hgt,boron].add_axial_section(self.s_struct_accLowerDummy_top,   self.u_graph_ref_al[boron, 'Al1100'])
        self.u_access_dummy_p[hgt,boron].add_axial_section(self.s_struct_accLowerSP_mid,      self.u_graph_ref_al[boron, 'Al1100'])
        self.u_access_dummy_p[hgt,boron].add_axial_section(self.s_struct_accLowerSPAl_top,    self.u_graph_ref_mLsp_al[boron, 'Al1100'])
        self.u_access_dummy_p[hgt,boron].add_axial_section(self.s_struct_accLowerSPZr_top,    self.u_accessMSP_zr[boron])
        self.u_access_dummy_p[hgt,boron].add_axial_section(self.s_struct_accLowerZrSpace_top, self.u_access_zr_spacer)
        self.u_access_dummy_p[hgt,boron].add_axial_section(self.s_struct_accWindow_bot,       self.u_accessCentral)
        # This is where we have a divergence of different segment lengths based on how tall the element access hole is
        if hgt == '48 inch':
          self.u_access_dummy_p[hgt,boron].add_axial_section(self.s_struct_accWindow48_top,     self.u_accessWindow)
          self.u_access_dummy_p[hgt,boron].add_axial_section(self.s_struct_accTube48_top,       self.u_accessCentral)
          self.u_access_dummy_p[hgt,boron].add_axial_section(self.s_struct_accZrSpace48_top,    self.u_access_zr_spacer)
          self.u_access_dummy_p[hgt,boron].add_axial_section(self.s_struct_accUpperSPZr48_top,  self.u_accessMSP_zr[boron])
          self.u_access_dummy_p[hgt,boron].add_axial_section(self.s_struct_accUpperSPAl48_top,  self.u_graph_ref_mLsp_al[boron, 'Al1100'])
          self.u_access_dummy_p[hgt, boron].add_axial_section(self.s_struct_accUpperSP48_top,   self.u_graph_ref_al[boron, 'Al1100'])
        elif hgt == '48.5 inch':
          self.u_access_dummy_p[hgt,boron].add_axial_section(self.s_struct_accWindow485_top,    self.u_accessWindow)
          self.u_access_dummy_p[hgt,boron].add_axial_section(self.s_struct_accTube485_top,      self.u_accessCentral)
          self.u_access_dummy_p[hgt,boron].add_axial_section(self.s_struct_accZrSpace485_top,   self.u_access_zr_spacer)
          self.u_access_dummy_p[hgt,boron].add_axial_section(self.s_struct_accUpperSPZr485_top, self.u_accessMSP_zr[boron])
          self.u_access_dummy_p[hgt,boron].add_axial_section(self.s_struct_accUpperSPAl485_top, self.u_graph_ref_mLsp_al[boron, 'Al1100'])
          self.u_access_dummy_p[hgt, boron].add_axial_section(self.s_struct_accUpperSP485_top,  self.u_graph_ref_al[boron, 'Al1100'])
        elif hgt == '49.5 inch':
          self.u_access_dummy_p[hgt,boron].add_axial_section(self.s_struct_accWindow495_top,    self.u_accessWindow)
          self.u_access_dummy_p[hgt,boron].add_axial_section(self.s_struct_accTube495_top,      self.u_accessCentral)
          self.u_access_dummy_p[hgt,boron].add_axial_section(self.s_struct_accZrSpace495_top,   self.u_access_zr_spacer)
          self.u_access_dummy_p[hgt,boron].add_axial_section(self.s_struct_accUpperSPZr495_top, self.u_accessMSP_zr[boron])
          self.u_access_dummy_p[hgt,boron].add_axial_section(self.s_struct_accUpperSPAl495_top, self.u_graph_ref_mLsp_al[boron, 'Al1100'])
          self.u_access_dummy_p[hgt, boron].add_axial_section(self.s_struct_accUpperSP495_top,  self.u_graph_ref_al[boron, 'Al1100'])
        # At the top of the short plug, or surfaces are at a constant height again
        self.u_access_dummy_p[hgt,boron].add_axial_section(self.s_struct_accUpperDummy_top,      self.u_graph_ref_al[boron, 'Al1100'])
        self.u_access_dummy_p[hgt,boron].add_axial_section(self.s_struct_accUpperLead_top,       self.u_access_PbPlug)
        self.u_access_dummy_p[hgt, boron].add_axial_section(self.s_struct_tff_base_top,          self.u_reg_tff_base['Lead'])
        self.u_access_dummy_p[hgt, boron].add_axial_section(self.s_struct_tff_mid_top,           self.u_reg_tff_mid['Lead'])
        self.u_access_dummy_p[hgt, boron].add_axial_section(self.s_struct_tff_neck_top,          self.u_reg_tff_neck['Lead'])
        self.u_access_dummy_p[hgt, boron].add_axial_section(self.s_struct_tff_top,               self.u_reg_tff_top_cone['Lead'])
        self.u_access_dummy_p[hgt,boron].add_last_axial_section(                                 self.mats['Air'])
        self.u_access_dummy_p[hgt,boron].finalize()

  def _add_rcca_elements(self):
    """ Adds TREAT RCCA elements """

    # First define the different types of control rods that exist in the TREAT reactor model
    # NOTE Shutdown type rods are equivalent to control and compensation rods
    self.crd_types = ['Shutdown Type I','Shutdown Type II','Transient Type I','Transient Type II']

    # RCCA rod radial surfaces
    self.s_rcca_OR = openmc.ZCylinder(name='RCCA rod OR', R=c.rcca_OR)
    self.s_rcca_clad_IR = openmc.ZCylinder(name='RCCA rod clad IR', R=c.rcca_clad_IR)
    self.s_rcca_active_OR = openmc.ZCylinder(name='RCCA rod active OR', R=c.rcca_active_OR)
    self.s_rcca_adapter_OR = openmc.ZCylinder(name='RCCA rod adapter OR', R=c.rcca_adapter_OR)
    self.s_rcca_stock_OR = openmc.ZCylinder(name='RCCA rod stock OR', R=c.rcca_stock_OR)
    rcca_clad_surfs_o = {'R': self.s_rcca_OR, 'prevR': self.s_rcca_active_OR}

    # RCCA rod axial surfaces
    # This is done in a loop over bank since each bank will have a different insertion level, and thus the axial surfaces will be
    # located in different places
    self.s_rcca_Adapt_bot = {}
    self.s_rcca_Adapt_top = {}
    self.s_rcca_FollowAct_top = {}
    self.s_rcca_FollowUpperPlug_top = {}
    self.s_rcca_UpFollowLowerPlug_top = {}
    self.s_rcca_UpFollowAct_top = {}
    self.s_rcca_UpFollowUpperPlug_top = {}
    self.s_rcca_ZrFollowLowerPlug_top = {}
    self.s_rcca_ZrFollowAct_top = {}
    self.s_rcca_ZrFollowUpperPlug_top = {}
    self.s_rcca_B4CLowerPlug_top = {}
    self.s_rcca_B4CTypeIGraphite_top = {}
    self.s_rcca_B4CAct_top = {}
    self.s_rcca_B4CUpperPlug_top = {}
    self.s_rcca_GrappleWide_top = {}
    self.s_rcca_GrappleLowerThin_top = {}
    self.s_rcca_GrappleStock_top = {}
    self.s_rcca_GrappleUpperThin_top = {}
    for b in c.rcca_banks: # Loop over all the banks (i.e. the different insertion levels)
      for crd_type in self.crd_types: # Loop over the types of control rods that are available
        # Set up things in a certain way if this is a transient type rod
        if crd_type[:9] == 'Transient':
          d = c.rcca_bank_steps_withdrawn[b]*c.rcca_TransientStepWidth
          self.s_rcca_Adapt_bot[b,crd_type] = openmc.ZPlane(name= \
                                              'Bottom of RCCA adapter bank {0}, rod class {1}'.format(b,crd_type),
                                               z0=c.struct_rcca_transFollS_bot + d)
          self.s_rcca_Adapt_top[b,crd_type] = openmc.ZPlane(name= \
                                              'Top of RCCA adapter bank {0}, rod class {1}'.format(b,crd_type),
                                               z0=c.struct_rcca_transFolAct_bot + d)
          self.s_rcca_FollowAct_top[b,crd_type] = openmc.ZPlane(name= \
                                              'Top of RCCA lower follower active section bank {0}, rod class {1}'.format(b,crd_type),
                                               z0=c.struct_rcca_transFoluS_bot + d)
          self.s_rcca_FollowUpperPlug_top[b,crd_type] = openmc.ZPlane(name= \
                                              'Top of RCCA lower follower upper plug bank {0}, rod class {1}'.format(b,crd_type),
                                               z0=c.struct_rcca_transUpFollS_bot + d)
          self.s_rcca_UpFollowLowerPlug_top[b,crd_type] = openmc.ZPlane(name= \
                                              'Top of RCCA upper follower lower plug bank {0}, rod class {1}'.format(b,crd_type),
                                               z0=c.struct_rcca_transUpFolAct_bot + d)
          self.s_rcca_UpFollowAct_top[b,crd_type] = openmc.ZPlane(name= \
                                              'Top of RCCA upper follower active section bank {0}, rod class {1}'.format(b,crd_type),
                                               z0=c.struct_rcca_transUpFoluS_bot + d)
          self.s_rcca_UpFollowUpperPlug_top[b,crd_type] = openmc.ZPlane(name= \
                                              'Top of RCCA upper follower upper plug bank {0}, rod class {1}'.format(b,crd_type),
                                               z0=c.struct_rcca_transZrlS_bot + d)
          self.s_rcca_ZrFollowLowerPlug_top[b,crd_type] = openmc.ZPlane(name= \
                                              'Top of RCCA Zr follower lower plug bank {0}, rod class {1}'.format(b,crd_type),
                                               z0=c.struct_rcca_transZrAct_bot + d)
          self.s_rcca_ZrFollowAct_top[b,crd_type] = openmc.ZPlane(name= \
                                              'Top of RCCA Zr follower active section bank {0}, rod class {1}'.format(b,crd_type),
                                               z0=c.struct_rcca_transZruS_bot + d)
          self.s_rcca_ZrFollowUpperPlug_top[b,crd_type] = openmc.ZPlane(name= \
                                              'Top of RCCA Zr follower upper plug bank {0}, rod class {1}'.format(b,crd_type),
                                               z0=c.struct_rcca_transB4ClS_bot + d)
          self.s_rcca_B4CLowerPlug_top[b,crd_type] = openmc.ZPlane(name= \
                                              'Top of RCCA B4C poison lower plug bank {0}, rod class {1}'.format(b,crd_type),
                                               z0=c.struct_rcca_transActB4C_bot + d)
          if crd_type[-6:] == 'Type I': # We have an additional graphite section to define a surface for
              self.s_rcca_B4CTypeIGraphite_top[b,crd_type] = openmc.ZPlane(name= \
                                                'Top of RCCA B4C type I graphite section bank {0}, rod class {1}'.format(b,crd_type),
                                                 z0=c.struct_rcca_transTypeIGrph_top + d)
          self.s_rcca_B4CAct_top[b,crd_type] = openmc.ZPlane(name= \
                                              'Top of RCCA B4C poision active section bank {0}, rod class {1}'.format(b,crd_type),
                                               z0=c.struct_rcca_transActB4C_top + d)
          self.s_rcca_B4CUpperPlug_top[b,crd_type] = openmc.ZPlane(name= \
                                              'Top of RCCA B4C poison upper plug bank {0}, rod class {1}'.format(b,crd_type),
                                               z0=c.struct_rcca_transB4CuS_top + d)
          self.s_rcca_GrappleWide_top[b,crd_type] = openmc.ZPlane(name= \
                                              'Top of RCCA wide grapple section bank {0}, rod class {1}'.format(b,crd_type),
                                               z0=c.struct_rcca_transGw_top + d)
          self.s_rcca_GrappleLowerThin_top[b,crd_type] = openmc.ZPlane(name= \
                                              'Top of RCCA lower thin grapple bank {0}, rod class {1}'.format(b,crd_type),
                                               z0=c.struct_rcca_transGl_top + d)
          self.s_rcca_GrappleStock_top[b,crd_type] = openmc.ZPlane(name= \
                                              'Top of RCCA grapple stock bank {0}, rod class {1}'.format(b,crd_type),
                                               z0=c.struct_rcca_transGs_top + d)
          self.s_rcca_GrappleUpperThin_top[b,crd_type] = openmc.ZPlane(name= \
                                              'Top of RCCA upper thin grapple bank {0}, rod class {1}'.format(b,crd_type),
                                               z0=c.struct_rcca_transGu_top + d)
        # Otherwise set things up for the shutdown / control / compensation rods
        else:
          d = c.rcca_bank_steps_withdrawn[b]*c.rcca_ShutdownStepWidth
          self.s_rcca_Adapt_bot[b,crd_type] = openmc.ZPlane(name= \
                                              'Bottom of RCCA adapter bank {0}, rod class {1}'.format(b,crd_type),
                                               z0=c.struct_rcca_shutFollS_bot + d)
          self.s_rcca_Adapt_top[b,crd_type] = openmc.ZPlane(name= \
                                              'Top of RCCA adapter bank {0}, rod class {1}'.format(b,crd_type),
                                               z0=c.struct_rcca_shutFolAct_bot + d)
          self.s_rcca_FollowAct_top[b,crd_type] = openmc.ZPlane(name= \
                                              'Top of RCCA lower follower active section bank {0}, rod class {1}'.format(b,crd_type),
                                               z0=c.struct_rcca_shutFoluS_bot + d)
          self.s_rcca_FollowUpperPlug_top[b,crd_type] = openmc.ZPlane(name= \
                                              'Top of RCCA lower follower upper plug bank {0}, rod class {1}'.format(b,crd_type),
                                               z0=c.struct_rcca_shutUpFollS_bot + d)
          self.s_rcca_UpFollowLowerPlug_top[b,crd_type] = openmc.ZPlane(name= \
                                              'Top of RCCA upper follower lower plug bank {0}, rod class {1}'.format(b,crd_type),
                                               z0=c.struct_rcca_shutUpFolAct_bot + d)
          self.s_rcca_UpFollowAct_top[b,crd_type] = openmc.ZPlane(name= \
                                              'Top of RCCA upper follower active section bank {0}, rod class {1}'.format(b,crd_type),
                                               z0=c.struct_rcca_shutUpFoluS_bot + d)
          self.s_rcca_UpFollowUpperPlug_top[b,crd_type] = openmc.ZPlane(name= \
                                              'Top of RCCA upper follower upper plug bank {0}, rod class {1}'.format(b,crd_type),
                                               z0=c.struct_rcca_shutZrlS_bot + d)
          self.s_rcca_ZrFollowLowerPlug_top[b,crd_type] = openmc.ZPlane(name= \
                                              'Top of RCCA Zr follower lower plug bank {0}, rod class {1}'.format(b,crd_type),
                                               z0=c.struct_rcca_shutZrAct_bot + d)
          self.s_rcca_ZrFollowAct_top[b,crd_type] = openmc.ZPlane(name= \
                                              'Top of RCCA Zr follower active section bank {0}, rod class {1}'.format(b,crd_type),
                                               z0=c.struct_rcca_shutZruS_bot + d)
          self.s_rcca_ZrFollowUpperPlug_top[b,crd_type] = openmc.ZPlane(name= \
                                              'Top of RCCA Zr follower upper plug bank {0}, rod class {1}'.format(b,crd_type),
                                               z0=c.struct_rcca_shutB4ClS_bot + d)
          self.s_rcca_B4CLowerPlug_top[b,crd_type] = openmc.ZPlane(name= \
                                              'Top of RCCA B4C poison lower plug bank {0}, rod class {1}'.format(b,crd_type),
                                               z0=c.struct_rcca_shutActB4C_bot + d)
          if crd_type[-6:] == 'Type I': # We have an additional graphite section to define a surface for
              self.s_rcca_B4CTypeIGraphite_top[b,crd_type] = openmc.ZPlane(name= \
                                                'Top of RCCA B4C type I graphite section bank {0}, rod class {1}'.format(b,crd_type),
                                                 z0=c.struct_rcca_shutTypeIGrph_top + d)
          self.s_rcca_B4CAct_top[b,crd_type] = openmc.ZPlane(name= \
                                              'Top of RCCA B4C poision active section bank {0}, rod class {1}'.format(b,crd_type),
                                               z0=c.struct_rcca_shutActB4C_top + d)
          self.s_rcca_B4CUpperPlug_top[b,crd_type] = openmc.ZPlane(name= \
                                              'Top of RCCA B4C poison upper plug bank {0}, rod class {1}'.format(b,crd_type),
                                               z0=c.struct_rcca_shutB4CuS_top + d)
          self.s_rcca_GrappleWide_top[b,crd_type] = openmc.ZPlane(name= \
                                              'Top of RCCA wide grapple section bank {0}, rod class {1}'.format(b,crd_type),
                                               z0=c.struct_rcca_shutGw_top + d)
          self.s_rcca_GrappleLowerThin_top[b,crd_type] = openmc.ZPlane(name= \
                                              'Top of RCCA lower thin grapple bank {0}, rod class {1}'.format(b,crd_type),
                                               z0=c.struct_rcca_shutGl_top + d)
          self.s_rcca_GrappleStock_top[b,crd_type] = openmc.ZPlane(name= \
                                              'Top of RCCA grapple stock bank {0}, rod class {1}'.format(b,crd_type),
                                               z0=c.struct_rcca_shutGs_top + d)
          self.s_rcca_GrappleUpperThin_top[b,crd_type] = openmc.ZPlane(name= \
                                              'Top of RCCA upper thin grapple bank {0}, rod class {1}'.format(b,crd_type),
                                               z0=c.struct_rcca_shutGu_top + d)


    # RCCA radial universes
    # TODO Add in the nickel and chrome platings for the control rods (currently neglected because only a couple mm thick)
    # Note: The screws should technically be stainless steel.
    # First the steel sections at the top and bottom of the control rod
    self.u_rcca_adap = InfiniteElement(name='RCCA rod adapter')
    self.u_rcca_adap.add_ring(     self.mats['Mild Steel'], self.s_rcca_OR, first=True)
    self.u_rcca_adap.add_last_ring(self.mats['Air'])
    self.u_rcca_adap.finalize()
    self.u_rcca_thinAdap = InfiniteElement(name='RCCA rod thin upper adapter')
    self.u_rcca_thinAdap.add_ring(     self.mats['Mild Steel'], self.s_rcca_adapter_OR, first=True)
    self.u_rcca_thinAdap.add_last_ring(self.mats['Air'])
    self.u_rcca_thinAdap.finalize()
    self.u_rcca_stock = InfiniteElement(name='RCCA rod upper adapter stock')
    self.u_rcca_stock.add_ring(     self.mats['Mild Steel'], self.s_rcca_stock_OR, first=True)
    self.u_rcca_stock.add_last_ring(self.mats['Air'])
    self.u_rcca_stock.finalize()
    self.u_rcca_plug = InfiniteElement(name='RCCA rod plug')
    self.u_rcca_plug.add_ring(     self.mats['Mild Steel'], self.s_rcca_OR, first=True)
    self.u_rcca_plug.add_last_ring(self.mats['Air'])
    self.u_rcca_plug.finalize()
    # Now the B4C poison sections, both for the old and new types of rod
    # Old design
    self.u_rcca_b4c_old = InfiniteElement(name='RCCA B4C old design (low density B4C)')
    self.u_rcca_b4c_old.add_ring(     self.mats['B4C Rod Old'], self.s_rcca_active_OR, first=True)
    self.u_rcca_b4c_old.add_ring(     self.mats['Mild Steel'],       rcca_clad_surfs_o)
    self.u_rcca_b4c_old.add_last_ring(self.mats['Air'])
    self.u_rcca_b4c_old.finalize()
    # New design
    self.u_rcca_b4c_new = InfiniteElement(name='RCCA B4C new design (higher density B4C)')
    self.u_rcca_b4c_new.add_ring(     self.mats['B4C Rod'], self.s_rcca_active_OR, first=True)
    self.u_rcca_b4c_new.add_ring(     self.mats['Mild Steel'],   rcca_clad_surfs_o)
    self.u_rcca_b4c_new.add_last_ring(self.mats['Air'])
    self.u_rcca_b4c_new.finalize()
    # Next the zirconium clad graphite follower directly below the poison section
    self.u_rcca_ZrGrph = InfiniteElement(name='RCCA Zirc Follower')
    self.u_rcca_ZrGrph.add_ring(     self.mats['Graphite'], self.s_rcca_active_OR, first=True)
    self.u_rcca_ZrGrph.add_ring(     self.mats['Zirc3'],     rcca_clad_surfs_o)
    self.u_rcca_ZrGrph.add_last_ring(self.mats['Air'])
    self.u_rcca_ZrGrph.finalize()
    # NOTE that the way the description is written, the two plugs on either side of the Zirc follower should be zirconium
    #      clad and probably have some zirc internals as well. However, since both ends of the zirc follower are the empty
    #      ends of their respective screw joins, for simplicity, the whole plugs will be approximated as being steel
    # Finally, define the steel clad parts with graphite internal followers
    self.u_rcca_Grph = InfiniteElement(name='RCCA Steel Follower')
    self.u_rcca_Grph.add_ring(     self.mats['Graphite'], self.s_rcca_active_OR, first=True)
    self.u_rcca_Grph.add_ring(     self.mats['Mild Steel'],    rcca_clad_surfs_o)
    self.u_rcca_Grph.add_last_ring(self.mats['Air'])
    self.u_rcca_Grph.finalize()

    # RCCA rod axial stack

    self.u_rcca = {}
    for b in c.rcca_banks:
      for crd_type in self.crd_types: # Loop over the types of control rods that are available
        for wgt, boron in zip(self.weight_percents, self.fuel_boron_ppms):
          self.u_rcca[b,crd_type,wgt,boron] = AxialElement(name='RCCA bank {0}, {1}, fuel {2} wgt, {3}'.format(b,crd_type,wgt,boron))
          self.u_rcca[b,crd_type,wgt,boron].add_axial_section(self.s_rcca_Adapt_bot[b,crd_type],              self.mats['Air'])
          self.u_rcca[b,crd_type,wgt,boron].add_axial_section(self.s_rcca_Adapt_top[b,crd_type],              self.u_rcca_adap)
          self.u_rcca[b,crd_type,wgt,boron].add_axial_section(self.s_rcca_FollowAct_top[b,crd_type],          self.u_rcca_Grph)
          self.u_rcca[b,crd_type,wgt,boron].add_axial_section(self.s_rcca_FollowUpperPlug_top[b,crd_type],    self.u_rcca_plug)
          self.u_rcca[b,crd_type,wgt,boron].add_axial_section(self.s_rcca_UpFollowLowerPlug_top[b,crd_type],  self.u_rcca_plug)
          self.u_rcca[b,crd_type,wgt,boron].add_axial_section(self.s_rcca_UpFollowAct_top[b,crd_type],        self.u_rcca_Grph)
          self.u_rcca[b,crd_type,wgt,boron].add_axial_section(self.s_rcca_UpFollowUpperPlug_top[b,crd_type],  self.u_rcca_plug)
          self.u_rcca[b,crd_type,wgt,boron].add_axial_section(self.s_rcca_ZrFollowLowerPlug_top[b,crd_type],  self.u_rcca_plug)
          self.u_rcca[b,crd_type,wgt,boron].add_axial_section(self.s_rcca_ZrFollowAct_top[b,crd_type],        self.u_rcca_ZrGrph)
          self.u_rcca[b,crd_type,wgt,boron].add_axial_section(self.s_rcca_ZrFollowUpperPlug_top[b,crd_type],  self.u_rcca_plug)
          self.u_rcca[b,crd_type,wgt,boron].add_axial_section(self.s_rcca_B4CLowerPlug_top[b,crd_type],       self.u_rcca_plug)
          if crd_type[-6:] == 'Type I': # We have an additional graphite section and assume we use the old B4C material
            self.u_rcca[b,crd_type,wgt,boron].add_axial_section(self.s_rcca_B4CTypeIGraphite_top[b,crd_type], self.u_rcca_Grph)
            self.u_rcca[b,crd_type,wgt,boron].add_axial_section(self.s_rcca_B4CAct_top[b,crd_type],           self.u_rcca_b4c_old)
          else: # It is just B4C, and we use the new material
            self.u_rcca[b,crd_type,wgt,boron].add_axial_section(self.s_rcca_B4CAct_top[b,crd_type],           self.u_rcca_b4c_new)
          self.u_rcca[b,crd_type,wgt,boron].add_axial_section(self.s_rcca_B4CUpperPlug_top[b,crd_type],       self.u_rcca_plug)
          self.u_rcca[b,crd_type,wgt,boron].add_axial_section(self.s_rcca_GrappleWide_top[b,crd_type],        self.u_rcca_adap)
          self.u_rcca[b,crd_type,wgt,boron].add_axial_section(self.s_rcca_GrappleLowerThin_top[b,crd_type],   self.u_rcca_thinAdap)
          self.u_rcca[b,crd_type,wgt,boron].add_axial_section(self.s_rcca_GrappleStock_top[b,crd_type],       self.u_rcca_stock)
          self.u_rcca[b,crd_type,wgt,boron].add_axial_section(self.s_rcca_GrappleUpperThin_top[b,crd_type],   self.u_rcca_thinAdap)
          self.u_rcca[b,crd_type,wgt,boron].add_last_axial_section(                                           self.mats['Air'])
          self.u_rcca[b,crd_type,wgt,boron] = self.u_rcca[b,crd_type,wgt,boron].add_wrapper(self.u_crd_p[wgt,boron])
          self.u_rcca[b,crd_type,wgt,boron].finalize()


