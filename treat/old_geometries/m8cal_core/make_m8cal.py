#!/usr/bin/env python

import os
from treat.builder import TREAT

try:
    os.mkdir('build')
except OSError: pass
os.chdir('build')

t = TREAT("BATMAN", backup_lib="backup", nndc_xs=True)
t.write_openmc_geometry()
t.write_openmc_materials()
t.write_openmc_plots()
t.write_openmc_settings()
t.write_openmc_tallies()

