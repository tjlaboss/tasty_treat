# Argparse
#
# Parse command line arguments

import sys
from .moc.standard import NAZIM, DAZIM


_OPTS = ("--cmfdmesh", "--fuelmesh", "--reflmesh", "--crdmesh",
         "--ngroups",  "--geneous", "--solver",   "--suffix",
         "--nazim", "--dazim",
         "--nproc", "-j",
         "--help", "-h",)


_HELP_STR = """
USAGE:
python [script].py [--options]
-----------------------------------------------------------
Options:
    --help, -h              : display this help message and exit
    --cmfdmesh [num]        : set the CMFD mesh to (num, num)
    --fuelmesh [num]        : set the fuel mesh to (num, num)
    --reflmesh [num]        : set the reflector mesh to (num, num)
    --crdfmesh [num]        : set the control rod fuel mesh to (num, num)
    --ngroups [G]           : set the number of energy groups to G
    --solver [order]        : set the solve order to "FSR" or "LSR"
    --geneous [h]           : set to "het"erogeneous or "hom"ogeneous
    --nazim [na]            : set the number of azimuthal angles to na
                                  (default: na = 32)
    --dazim [d]             : set the desired azimuthal ray spacing to d cm
                                  (default: d = 0.1 cm)
    --suffix [string]       : add a suffix to the default export path
    --nproc, -j [n]         : use n threads

"""


def _arg_val(string):
	return sys.argv[sys.argv.index(string) + 1]


def check_args():
	if "--help" in sys.argv or "-h" in sys.argv:
		print(_HELP_STR)
		raise sys.exit()
	# Check if there are erroneous options
	errs = 0
	errstr = "\nUnknown arguments:"
	for i in range(1, len(sys.argv)):
		arg = sys.argv[i]
		if arg not in _OPTS:
			if sys.argv[i - 1] not in _OPTS:
				errs += 1
				errstr += '\n' + str(arg)
	# Check for duplicate arguments
	if "-j" in sys.argv and "--nproc" in sys.argv:
		errs += 1
		errstr += "\nArguments -j and --nproc are redundant."
	if errs:
		raise ValueError(errstr)


def get_arguments(cmfdmesh=None, fuelmesh=None, reflmesh=None, crdmesh=None,
                  ngroups=None, geneous=None, solver=None, nproc=None, suffix='',
                  nazim=NAZIM, dazim=DAZIM):
	"""Get the command line arguments.
	
	Usage: Providing a parameter will set a default value for that argument.
	If that argument is not specified, the default will be used, and no error will be raised.
	When no default is provided and the argument is not specified from the command line,
	get_arguments() will raise an error.
	
	Therefore, None is not a valid default value. Other Falsey types will still work.
	
	Exception: `suffix' is an empty string by default.
	"""
	arguments = {"--cmfdmesh": cmfdmesh,
	             "--fuelmesh": fuelmesh,
	             "--reflmesh": reflmesh,
	             "--crdmesh" : crdmesh,
	             "--ngroups" : ngroups,
	             "--geneous" : geneous,
	             "--solver"  : solver,
	             "--suffix"  : suffix,
	             "--nazim"   : nazim,
	             "--dazim"   : dazim,
	             "--nproc"   : nproc}
	check_args()
	for a in arguments:
		if a in sys.argv:
			arguments[a] = _arg_val(a)
	if "-j" in sys.argv:
		arguments["--nproc"] = _arg_val("-j")
	# Make sure nothing remains unset.
	null_args = []
	for a, v in arguments.items():
		if v is None:
			null_args.append(a)
	if null_args:
		errstr = "{} required arguments are missing:\n{}".format(len(null_args), null_args)
		raise ValueError(errstr)
	arguments = validate_arguments(arguments)
	cleaned = {}
	for a, v in arguments.items():
		cleaned[a[2:]] = v
	arguments = cleaned
	return arguments


def validate_arguments(args):
	errstr = "Invalid arguments:"
	errs = 0
	# Integers
	for intlike in ("--cmfdmesh", "--fuelmesh", "--reflmesh", "--crdmesh", "--ngroups",
	                "--nazim", "--nproc"):
		try:
			v = args[intlike]
			assert int(v) == float(v), intlike + " must be an integer."
		except (AssertionError, ValueError) as e:
			errs += 1
			errstr += "\n" + str(e)
		else:
			args[intlike] = int(v)
	# Floats
	for floatlike in ("--dazim",):
		try:
			v = args[floatlike]
			assert float(v) > 0
		except (AssertionError, ValueError) as e:
			errs += 1
			errstr += "\n" + floatlike + " must be a number > 0." + str(e)
		else:
			args[floatlike] = float(v)
	# Solver type
	try:
		v = args["--solver"].lower()
		assert v in ("fsr", "lsr"), "--solver must be 'fsr' or 'lsr'."
	except AttributeError:
		errs += 1
		errstr += "\n--solver must be a string."
	except AssertionError as e:
		errs += 1
		errstr += "\n" + str(e)
	else:
		args["--solver"] = v
	# Het vs hom
	try:
		v = args["--geneous"].lower()
		n = len(v)
		assert n > 1, "--geneous must be longer than 1 character."
		if v == "heterogeneous"[:n]:
			args["--geneous"] = False  # heterogeneous
		elif v == "homogeneous"[:n]:
			args["--geneous"] = True   # homogeneous
		else:
			raise AssertionError("--geneous must be unambiguously 'homogeneous' or 'heterogeneous'")
	except AttributeError:
		errs += 1
		errstr += "\n--solver must be a string."
	except AssertionError as e:
		errs += 1
		errstr += "\n" + str(e)
	
	if errs:
		raise ValueError(errstr)
	return args
