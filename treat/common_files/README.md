# common_files

This subdirectory contains files and data that will be used by multiple benchmark models. The goal of this approach is to avoid a
situtation where, for instance, a material definition is updated due to better future experimental examination and characterization
of a TREAT material and the change is made in some benchmarks but missed / forgotten in others.

All files are contained within the TREAT subdirectory. This directory will contain material definitions, system constants / 
physical dimension parameters, the python script for automated generation of cells in the TREAT geometry, the element / assembly
definitions, and the geometric definition for regions outside the core lattice itself.
