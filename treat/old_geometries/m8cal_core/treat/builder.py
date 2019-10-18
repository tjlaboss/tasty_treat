""" builder.py

Provides a main class that facilitates construction and output of any piece of
the TREAT geometry. This is designed to be a simplified model to construct only
an infinite lattice of basic fuel elements.

"""

import warnings
import openmc
import sys; sys.path.append('..')
import common_files.treat.constants as c
from common_files.treat.elements import Elements
from common_files.treat.lat_fullCore_univzero import UniverseZero
from treat.experimentVessel import ExperimentVessel
from common_files.treat.basetreat import BaseTREAT
from treat.core import Core

# Suppress DeprecationWarnings from OpenMC's Cell.add_surface(...) method
warnings.simplefilter('once', DeprecationWarning)

class TREAT(BaseTREAT):
    """ Main TREAT class"""

    def __init__(self, material_lib, backup_lib, nndc_xs=False):
        """ We build the entire geometry in memory in the constructor """
        super(TREAT, self).__init__(material_lib, backup_lib, nndc_xs)
        # TODO: make the control rod bank insertion heights attributes
        
        self.elements = Elements(self.mats)
        self.vessel = ExperimentVessel(self.mats)
        self.core = Core(self.elements, self.vessel)
        self.main_universe = UniverseZero(self.core, self.mats)

        self.openmc_geometry = openmc.Geometry(self.main_universe)

        self.tallies = []
        
        self.settings_batches = 10
        self.settings_inactive = 5
        self.settings_particles = 10000
        core_HW = c.n_lattice_positions*c.latticePitch/2.0 
        self.settings_sourcebox = [-core_HW, -core_HW, c.fuel_ActiveFuel_bot,
                                   core_HW, core_HW, c.fuel_ActiveFuel_top]
        self.settings_output_tallies = False
        self.settings_summary = True
        self.settings_output_distribmats = False

        self.tally_meshes = []
        self.tallies = []

        self.dd_mesh_dimension = None
        self.dd_mesh_lower_left = None
        self.dd_mesh_upper_right = None
        self.dd_nodemap = None
        self.dd_truncate = False
        self.dd_interactions = False

        # These were not chosen with any application in mind: tailor them to your needs!
        self.depletion_nuclides = [
                    'Ag107', 'Ag109', 'Ag111', 'Am241', 'Am243', 'As75',
                    'Au197', 'Ba134', 'Ba135', 'Ba136', 'Ba137', 'Ba138',
                    'Ba140', 'Br79',  'Br81',  'Cd108', 'Cd110', 'Cd111',
                    'Cd112', 'Cd113', 'Cd114', 'Cd116', 'Ce140',
                    'Ce141', 'Ce142', 'Ce143', 'Ce144', 'Cm244', 'Co59',
                    'Cs133', 'Cs134', 'Cs135', 'Cs136', 'Cs137', 'Dy160',
                    'Dy161', 'Dy162', 'Dy163', 'Dy164', 'Er166', 'Er167',
                    'Eu151', 'Eu152', 'Eu153', 'Eu154', 'Eu155', 'Eu156',
                    'Eu157', 'Gd154', 'Gd155', 'Gd156', 'Gd157', 'Gd158',
                    'Gd160', 'Ge72',  'Ge73',  'Ge74',  'Ge76',  'Ho165',
                    'I127',  'I129',  'I130',  'I131',  'I135',  'In113',
                    'In115', 'Kr80',  'Kr82',  'Kr83',  'Kr84',  'Kr85',
                    'Kr86',  'La139', 'La140', 'Lu175', 'Lu176', 'Mo100',
                    'Mo94',  'Mo95',  'Mo96',  'Mo97',  'Mo98',  'Mo99',
                    'Nb93',  'Nb94',  'Nb95',  'Nd142', 'Nd143', 'Nd144',
                    'Nd145', 'Nd146', 'Nd147', 'Nd148', 'Nd150', 'Np237',
                    'Pa233', 'Pd104', 'Pd105', 'Pd106', 'Pd107', 'Pd108',
                    'Pd110', 'Pm147', 'Pm148', 'Pm149', 'Pm151', 'Pr141',
                    'Pr142', 'Pr143', 'Pu238', 'Pu239', 'Pu240', 'Pu241',
                    'Pu242', 'Rb85',  'Rb86',  'Rb87',  'Re185', 'Re187',
                    'Rh103', 'Rh105', 'Ru100', 'Ru101', 'Ru102', 'Ru103',
                    'Ru104', 'Ru105', 'Ru106', 'Ru99',  'Sb121', 'Sb123',
                    'Sb124', 'Sb125', 'Sb126', 'Se76',  'Se77',  'Se78',
                    'Se80',  'Se82',  'Sm147', 'Sm148', 'Sm149', 'Sm150',
                    'Sm151', 'Sm152', 'Sm153', 'Sm154', 'Sn115', 'Sn116',
                    'Sn117', 'Sn118', 'Sn119', 'Sn120', 'Sn122', 'Sn123',
                    'Sn124', 'Sn125', 'Sn126', 'Sr86',  'Sr87',  'Sr88',
                    'Sr89',  'Sr90',  'Ta181', 'Tb159', 'Tb160', 'Tc99',
                    'Te122', 'Te123', 'Te124', 'Te125', 'Te126',
                    'Te128', 'Te130', 'Te132', 'Th232', 'U233',
                    'U234',  'U235',  'U236',  'U238',  'W182',  'W183',
                    'W184',  'W186',  'Xe128', 'Xe129', 'Xe130', 'Xe131',
                    'Xe132', 'Xe133', 'Xe134', 'Xe135', 'Xe136', 'Y89',
                    'Y90',   'Y91',   'Zr90',  'Zr91',  'Zr92',  'Zr93', 'Zr94',
                    'Zr95',  'Zr96']
        nuclides = []
        for nuc in self.depletion_nuclides:
            nuclides.append(openmc.Nuclide(name=nuc))
        self.depletion_nuclides = nuclides

    def write_openmc_settings(self):
        settings_file = openmc.Settings()
        settings_file.batches = self.settings_batches
        settings_file.inactive = self.settings_inactive
        settings_file.particles = self.settings_particles
        if self.dd_mesh_dimension:
            settings_file.dd_mesh_dimension = self.dd_mesh_dimension
            settings_file.dd_mesh_lower_left = self.dd_mesh_lower_left
            settings_file.dd_mesh_upper_right = self.dd_mesh_upper_right
            if self.dd_nodemap:
                settings_file.dd_nodemap = self.dd_nodemap
            settings_file.dd_allow_leakage = self.dd_truncate
            settings_file.dd_count_interactions = self.dd_interactions
        settings_file.source = openmc.Source(space=openmc.stats.Box(
            self.settings_sourcebox[:3], self.settings_sourcebox[3:]))
        output = {'tallies': self.settings_output_tallies,
                  'summary': self.settings_summary}
        settings_file.output = output
        settings_file.export_to_xml()

    def set_params(self, particles=None, batches=None, inactive=None):
        if particles: self.settings_particles = particles
        if batches: self.settings_batches = batches
        if inactive: self.settings_inactive = inactive

    def set_dd_mesh(self, nx, ny, nz, nodemap=None):
        """ Sets a DD mesh that covers the whole geometry
        """
        self.dd_mesh_dimension = [nx, ny, nz]
        self.dd_mesh_lower_left = [-c.rpvOR, -c.rpvOR, c.struct_LowestExtent]
        self.dd_mesh_upper_right = [c.rpvOR, c.rpvOR, c.struct_HighestExtent]
        self.dd_nodemap = nodemap
        self.dd_truncate = False

    def set_dd_mesh_restricted(self, nx, ny, nz, nodemap=None):
        """ Sets a DD mesh that truncates tracking outside the shield panels
        """
        self.dd_mesh_dimension = [nx, ny, nz]
        self.dd_mesh_lower_left = [-c.neutronShieldOR, -c.neutronShieldOR, c.struct_LowestExtent]
        self.dd_mesh_upper_right = [c.neutronShieldOR, c.neutronShieldOR, c.struct_HighestExtent]
        self.dd_nodemap = nodemap
        self.dd_truncate = True

    def set_dd_mesh_assembly_restricted(self, nz, nodemap=None):
        """ Sets a restricted DD mesh that is assembly-sized radially, and user-specified axially
        """
        lp = c.latticePitch
        self.dd_mesh_dimension = [17, 17, nz]
        self.dd_mesh_lower_left = [-8*lp, -8*lp, c.struct_LowestExtent]
        self.dd_mesh_upper_right = [8*lp, 8*lp, c.struct_HighestExtent]
        self.dd_nodemap = nodemap
        self.dd_truncate = True

    def set_dd_mesh_3assembly_restricted(self, nz, nodemap=None):
        """ Sets a restricted DD mesh that is 3x3 assebly-sized radially, and user-specified axially
        """
        lp = c.latticePitch
        self.dd_mesh_dimension = [7, 7, nz]
        self.dd_mesh_lower_left = [-10*lp, -10*lp, c.struct_LowestExtent]
        self.dd_mesh_upper_right = [10*lp, 10*lp, c.struct_HighestExtent]
        self.dd_nodemap = nodemap
        self.dd_truncate = True

    def reset_dd(self):
        """ Undoes set_dd_mesh and set_dd_mesh_restricted
        """
        self.dd_mesh_dimension = None
        self.dd_mesh_lower_left = None
        self.dd_mesh_upper_right = None
        self.dd_nodemap = None
        self.dd_truncate = False

    def set_distributed_materials(self):
        """ Sets depletable regions to distributed materials
        """

        # Distribute fuel materials
        for enr in self.pincells.enrichments:
            self.openmc_mats['Fuel %s' % enr].set_as_distrib_comp()

        # TODO: distribute other regions as necessary (bpra pins, rcca pins, etc)

    def set_fuel_otf_files(self, files):
        """ Sets OTF material files for the specified material names
        files should be a list of file paths equal to the number of enrichments
        """
        for enr,f in zip(self.pincells.enrichments, files):
            if f:
                self.openmc_mats['Fuel %s' % enr].set_otf_mat_file(f)

    def reset_fuel_otf_files(self):
        """ Undoes set_fuel_otf_files
        """
        for enr in self.pincells.enrichments:
            self.openmc_mats['Fuel %s' % enr].set_otf_mat_file(None)

    def get_all_fuel_cells(self):
        cells = []
        universes = []
        for enr in self.pincells.enrichments[:3]:
            fuel_pin = self.pincells.u_fuel_active_pin[enr]
            name = "Fuel rod active region - {0} enr radial 0: Fuel {0}".format(enr)
            cells.append(fuel_pin.get_cell_by_name(name))
            universes.append(fuel_pin)
        return zip(cells, universes)

    def set_fuel_depletion_tallies(self):
        """ Sets up distributed tallies needed for depletion of fresh fuel
        NOTE: this was so far created only for benchmarking openmc performance,
        and is not really what we'll end up doing for depletion
        """
        scores = ["total", "absorption", "fission", "nu-fission"]

        for c,u in self.get_all_fuel_cells():

            # Instantiate tally Filter
            filter_ = openmc.DistribcellFilter(c.id)

            # Instantiate the Tally
            tally = openmc.Tally()
            tally.filters = [filter_]
            tally.scores = scores
            nuclides = self.openmc_mats[c.fill.name].nuclides
            tally.nuclides = [nuc for nuc, ao, typ in nuclides]
            self.tallies.append(tally)

    def set_fuel_distrib_tallies(self, scores):
        """ Sets up distribcell tallies on fuel pins
        NOTE: currently this only sets them up for the 1.6, 2.4, and 3.1 pins
        """

        for c,u in self.get_all_fuel_cells():

            # Instantiate tally Filter
            filter_ = openmc.DistribcellFilter(c._id)

            # Instantiate the Tally
            tally = openmc.Tally()
            tally.filters = [filter_]
            tally.scores = [scores]
            self.tallies.append(tally)

    def set_full_depletion_mats(self):
        """ Adds 207 depletion nuclides to fuel materials
        """

        for name,mat in self.openmc_mats.items():
            if not name in ['Fuel 1.6%', 'Fuel 2.4%', 'Fuel 3.1%', 'Fuel 3.2%', 'Fuel 3.4%']: continue
            for nuc in self.depletion_nuclides:
                if not nuc._name in mat._nuclides:
                   mat.add_nuclide(nuc, 1e-14)
