""" builder.py

Provides a main class that facilitates construction and output of any piece of
the TREAT geometry. This is designed to be a simplified model to construct only
an infinite lattice of basic fuel elements.

"""

import sys
import warnings

import openmc

sys.path.append('..')

import common_files.treat.constants as c
from common_files.treat.elements import Elements
from treat.inf_lat_univzero import UniverseZero
from common_files.treat.basetreat import BaseTREAT
import mesh
import openmc.mgxs as mgxs

# Suppress DeprecationWarnings from OpenMC's Cell.add_surface(...) method
warnings.simplefilter('once', DeprecationWarning)

class TREAT(BaseTREAT):
    """ Main TREAT class"""

    def __init__(self, material_lib, nndc_xs=False):
        """ We build the entire geometry in memory in the constructor """
        super(TREAT, self).__init__(material_lib, nndc_xs)

        self.elements = Elements(self.mats)
        self.main_universe = UniverseZero(self.elements, self.mats)

        self.openmc_geometry = openmc.Geometry(self.main_universe)

        self.tallies = []

        self.settings_batches = 100
        self.settings_inactive = 35
        self.settings_particles = int(1E7)
        core_HW = 1*c.latticePitch/2.0 # Only a single element in this model, will be more in later models
        self.settings_sourcebox = [-core_HW, -core_HW, self.main_universe.zmid - 1,
                                   core_HW, core_HW, self.main_universe.zmid + 1]
        self.settings_output_tallies = False
        self.settings_summary = True

        self.tally_meshes = []
        self.tallies = []


    def write_openmc_plots(self):
        all_plots = []
        p = c.latticePitch
        for axis in ("xy", "yz"):
            new_plot = openmc.Plot()
            new_plot.basis = axis
            new_plot.color_by = "material"
            new_plot.pixels = (400, 400)
            if axis == "xy":
                new_plot.width = [p, p]
            elif axis == "yz":
                new_plot.width = [p, 2]
            new_plot.origin = (0, 0, self.main_universe.zmid)
            all_plots.append(new_plot)
    
        plot_file = openmc.Plots(all_plots)
        plot_file.export_to_xml()

    def write_openmc_settings(self):
        settings_file = openmc.Settings()
        settings_file.batches = self.settings_batches
        settings_file.inactive = self.settings_inactive
        settings_file.particles = self.settings_particles
        settings_file.source = openmc.Source(space=openmc.stats.Box(
            self.settings_sourcebox[:3], self.settings_sourcebox[3:]))
        output = {'tallies': self.settings_output_tallies,
                  'summary': self.settings_summary}
        settings_file.output = output
        settings_file.export_to_xml()

    def write_openmc_tallies(self):
        tallies_xml = openmc.Tallies()
        # Exploit the pwr.mesh module
        low_left = [-c.latticePitch/2.0, -c.latticePitch/2.0, mesh.cuts.Z0]
        axial_mesh = mesh.MeshGroup(c.latticePitch, 1, 1, low_left)
        n = len(mesh.cuts.dzs)
        for i in range(n):
            dz = mesh.cuts.dzs[i]
            nz = mesh.cuts.n_cuts[i]
            axial_mesh.add_mesh(nz=nz, dz=dz)

        # Build the mesh library
        mesh_lib = mgxs.Library(self.openmc_geometry)
        mesh_lib.domain_type = "mesh"
        mesh_lib.domains = axial_mesh.meshes
        mesh_lib.build_library()
        mesh_lib.add_to_tallies_file(tallies_xml)
        # Wrap it up in a nice XML file
        tallies_xml.extend(axial_mesh.tallies)
        tallies_xml.export_to_xml()

    def set_params(self, particles=None, batches=None, inactive=None):
        if particles: self.settings_particles = particles
        if batches: self.settings_batches = batches
        if inactive: self.settings_inactive = inactive

    
