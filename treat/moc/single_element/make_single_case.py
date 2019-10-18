# Make Single case
#
# A manager for the infinite single element case

import sys; sys.path.append("..")
from moc_case import Case

NGROUPS = [11, 25]
DOMAINS = ["mesh"]
BASE = 40
SHAPE = (BASE*3, BASE*3)
ALL_SHAPES = [SHAPE]
RUN_MOC = False
PLOT_XS = True

single = Case(NGROUPS, DOMAINS, ALL_SHAPES)
mesh_name = single.shape_to_string(SHAPE)
single.make_montecarlo_tallies()
#single.export_to_xml()

if PLOT_XS:
	single.load_openmc_statepoint("statepoint.080.h5")
	# still need to implement this in `Case` class...
	import numpy as np
	from matplotlib import pyplot as plt
	
	num_groups = 11
	
	PITCH = 10.16
	
	x0 = -PITCH/2.0
	x1 = +PITCH/2.0
	xstype = "total"
	
	
	xsmesh = single.meshes[SHAPE]
	mesh_lib = single.mesh_libraries[num_groups]
	mesh_lib.load_from_statepoint(single.sp)
	
	xs_df = mesh_lib.get_mgxs(xsmesh, xstype).get_pandas_dataframe()
	
	# plotting params
	n = xsmesh.dimension[0]
	
	# row = int(np.ceil(n/2))
	row = SHAPE[0]//2
	xlist = np.linspace(x0, x1, n)
	xs_scale = "macro"
	plotted_sigma = False
	
	for g in range(1, num_groups+1):
		plt.figure(g)
		group_df = xs_df[xs_df["group in"] == g]
		meshy_name = "mesh {}".format(xsmesh.id)
		y_df = group_df[group_df[(meshy_name, 'y')] == row]
		yvals = y_df['mean']
		uncert = y_df['std. dev.']
		
		# 1D
		ylist = np.array(yvals)
		ulist = np.array(uncert)
		
		style = "steps"
		
		plt.grid()
		
		plt.plot(xlist, ylist, drawstyle=style, label="$\Sigma_{" + str(g) + "}$")
		if not plotted_sigma:
			plt.plot(xlist, ylist + ulist, "red", drawstyle=style, alpha=0.5, label="$\pm 1\sigma$")
		# plotted_sigma = True
		else:
			plt.plot(xlist, ylist + ulist, "red", drawstyle=style, alpha=0.5)
		plt.plot(xlist, ylist - ulist, "red", drawstyle=style, alpha=0.5)
		
		plt.legend(loc="best")
		title_string = "{} {}scopic Cross Section".format(xstype.title(), xs_scale.title())
		plt.xlabel("Radial distance (cm)")
		plt.ylabel("$\Sigma$ (cm$^{-1}$)")
		plt.title(title_string, {"fontsize": 14})
		plt.suptitle("Group {} of {}".format(g, num_groups))
		plt.tight_layout()
		plt.savefig("xs_plots/xs-{:02d}.pdf".format(g))
		plt.show()
		
		# and 2D
		plt.figure(100 + g)
		xy_at_z_df = group_df[group_df[(meshy_name, 'z')] == 1]
		xsarray = np.array(xy_at_z_df['mean'])
		xsarray[xsarray <= 1E-6] = np.NaN
		xsarray.shape = (n, n)
		
		plt.imshow(xsarray, cmap="jet")
		plt.colorbar()
		plt.title("Total (Group {} of {})".format(g, num_groups))
		plt.tight_layout()
		
		plt.savefig("xs_plots/xs-map-{:02d}.pdf".format(g))
		plt.show()


