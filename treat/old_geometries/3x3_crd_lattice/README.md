# 3x3_crd_lattice

Runs a simulation of the a TREAT control rod fuel element surrounded by 8 other regular TREAT fuel elements. Reflective boundary
conditions are set at the core universe edges. Set to be void axially. Currently, the benchmark can be set to use either transient
or shutdown type rods from either the pre-1960 era (TREAT initial operation) or from the post-1967 era (later TREAT experiments
and presumably future TREAT operations after DOE restart) by altering the treat/core.py file's self.rcca_bank_types parameter. Control
rod insertion level can be set anywhere from fully inserted to fully withdrawn by setting the treat/core.py file's 
self.rcca_bank_locations parameter to match one of the insertion levels defined in the common_files/treat/constants.py file via the 
rcca_bank_steps_withdrawn parameter. Run by executing the make_3x3_crd_lattice.py script.
