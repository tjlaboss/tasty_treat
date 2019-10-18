
import itertools
from openmoc import checkvalue as cv
from collections import Iterable, OrderedDict
from .executor import Executor


MUST_SET = ("nazim", "dazim", "ngroups", "geneity", "cmfdmesh", "divmesh")


class Automator:
	"""Automate the creation of Executors
	
	Parameter:
	----------
	enforce:    Iterable of str, optional; variable names to ensure are present
	            [Default: `MUST_SET` tuple from the header]
	"""
	def __init__(self, enforce=MUST_SET):
		self._variables = OrderedDict()
		self._constants = {}
		self.enforce = enforce
		
	@property
	def all_available(self):
		return self._variables.keys() | self._constants.keys()
	
	def add_variable(self, var, values):
		"""Add a variable with multiple values
		
		If a Constant already exists with the name `var`,
		it will get overwritten.
		
		Parameters:
		-----------
		var:        str; name of the variable
		values:     Iterable; all values. Must be of len() >= 2
		"""
		cv.check_type("values", values, Iterable)
		cv.check_length("values", values, 2, 1000)
		if var in self._constants:
			del self._constants[var]
		# TODO: Verify value types. And that values is iterable.
		self._variables[var] = values
	
	def add_constant(self, con, value):
		"""Add a constant with a single value
		
		If a Variable already exists with the name `con`,
		it will throw an error.

		Parameters:
		-----------
		con:        str; name of the variable
		value:      <anything>; whatever value the constant holds
		"""
		if con in self._variables:
			errstr = "{} cannot be a Constant. It is already a Variable."
			raise ValueError(errstr.format(con))
		self._constants[con] = value
	
	def is_ready(self):
		"""Check if all the enforced variables are set.
		If Automator.enforce is False, it is always ready.
		
		Returns:
		--------
		bool
		"""
		if self.enforce:
			for it in self.enforce:
				if it not in self.all_available:
					return False
		return True

	def create_jobs(self, workdir, script_file, minutes, execute=False):
		"""Create, and optionally execute, the job scripts
		
		The default run mode for `create_jobs(...)` is a dry run. Automator will write
		the qsub scripts to disk if possible, but will not execute them.
		Calling `create_jobs(..., execute=True)` will execute qsub.
		
		Parameters:
		-----------
		workdir:        str; directory the script_file is in
		script_file:    str; Python script to call inside the qsub script
		minutes:        int; number of minutes to request on the cluster
		execute:        bool, optional; whether to execute the script after creating.
		                [Default: False]
		
		"""
		if not self.is_ready():
			missing = set(self.enforce) - self.all_available
			errstr = "Some enforced variables are not set:\n{}".format(missing)
			raise ValueError(errstr)
		all_var_dicts = {}
		keys = tuple(self._variables.keys())
		n = len(keys)
		combos = itertools.product(*(val for v, val in self._variables.items()))
		for ck in combos:
			vkeys = [None]*n
			vdict = {}
			for i in range(n):
				var = keys[i]
				val = ck[i]
				vdict[var] = val
				vkeys[i] = "{}{}".format(keys[i], ck[i])
			vstr = "_".join(vkeys)
			all_var_dicts[vstr] = vdict
		
		for case_name, var_dict in all_var_dicts.items():
			case_vars = dict(self._constants)
			case_vars.update(var_dict)
			ex = Executor(script_file, minutes, case_vars["geneity"],
			              case_vars["ngroups"], case_vars["divmesh"])
			ex.job_name = case_name
			ex.postsuffix = case_name
			ex.load_template()
			shell_script = "{}/run_{}.sh".format(workdir, case_name)
			ex.write_script(shell_script, **case_vars)
			if execute:
				ex.execute_script(shell_script)

