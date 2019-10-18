# treat_openmc

This is the temporary private repo designed to be the working location for building a OpenMC, python API version of the 
TREAT reactor core, with specific attention to the M8Cal experiment configuration. 

The common_files subdirectory contains files that are used by all of the benchmarks, such as the materials definitions, 
the geometry definitions, and generation of the element objects. 

Each of the other subdirectories contains a a separate benchmark problem. A benchmark problem is run by first navigating 
into its top directory and executing the python script by the command "python make_benchmark_name.py". The resulting OpenMC
.xml files are then generated in a "build" directory inside the top directory and can be run by executing the "openmc" 
command within the build directory.
