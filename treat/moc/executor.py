

import os
import subprocess
from warnings import warn
from datetime import timedelta


class Executor:
	"""A class that creates and executes job scripts
	
	Required Parameters:
	--------------------
	script_file:    str; name of the Python script called within the job script
	minues:         int; number of minutes of walltime to request
	geneity:        str; at least the first 2 letters of "homogeneous" or "heterogeneous"
	ngroups:        int; number of energy groups to run in
	divmesh:        int; default number of mesh divisions to use for elements
	
	Optional Parameters:
	--------------------
	crdmesh:        int; number of mesh divisions to use for crd fuel elements
	fuelmesh:       int;                      "   to use for standard fuel elements
	reflmesh:       int;                      "   to use for reflector elements
	[DEFAULT: The preceding parameters will default to `divmesh` when not provided.]
	postsuffix:     str; what to append after the usual 'mesh{divmesh}' suffix
	job_name:       str; what to call the job in the queue
	
	Attributes:
	-----------
	cmfdmesh:       int; default: 2
	solver:         str; default: "lsr"
	queue:          str; default: "treat"
	
	"""
	def __init__(self, script_file, minutes, geneity, ngroups, divmesh,
	             crdmesh=None, fuelmesh=None, reflmesh=None,
	             postsuffix="", job_name="", **kwargs):
		self.script_file = script_file
		self.timestr = str(timedelta(minutes=minutes))
		self.geneity = geneity
		self.ngroups = ngroups
		self.divmesh = divmesh
		if crdmesh is None:
			crdmesh = divmesh
		if reflmesh is None:
			reflmesh = divmesh
		if fuelmesh is None:
			fuelmesh = divmesh
		self.crdmesh = crdmesh
		self.fuelmesh = fuelmesh
		self.reflmesh = reflmesh
		self.cmfdmesh = 2
		self.solver = "lsr"
		self.queue = "treat"
		self.postsuffix = postsuffix
		self.job_name = job_name
		self._template = None
		
		
	@property
	def suffix(self):
		suf = "mesh{:02d}".format(self.divmesh)
		if self.postsuffix:
			suf += "_" + self.postsuffix
		return suf
	
	
	def load_template(self, path=None):
		"""Load a template from disk.
		
		Parameter:
		----------
		path:       str, optional; path to the text file.
		            [Default: "treat/moc/templates/qsub_template.txt"]
		"""
		if path is None:
			folder = os.path.dirname(os.path.realpath(__file__))
			folder += "/templates"
			fname = "qsub_template.txt"
			path = folder + '/' + fname
		with open(path, 'r') as f:
			self._template = f.read()
		
		
	def get_script(self, **kwargs):
		"""Get the shell script as a string
		
		You must have a template loaded. The combination of Executor's attributes,
		the key "suffix", and any additional kwargs must satisfy all the named
		variables in that template. If either of these is not the case,
		an error will be thrown.
		
		Parameters:
		-----------
		**kwargs:   dict, optional; use this to override Executor's attributes.
		
		Returns:
		--------
		str; the script with the variables filled in
		"""
		if self._template is None:
			raise ValueError("You must load a template first.")
		variables = vars(self)
		variables["suffix"] = self.suffix
		variables.update(kwargs)
		return self._template.format(**variables)
	
	
	def write_script(self, destination, **kwargs):
		"""Write the shell script to disk
		
		Parameters:
		-----------
		destination:    str; location on the filesystem to write to
		**kwargs:       dict, optional; use this to override Executor's attributes.
		
		Returns:
		--------
		int:
			  0 if OK
			!=0 if there was an error.
		"""
		script = self.get_script(**kwargs)
		try:
			fout = open(destination, 'w')
			fout.write(script)
			fout.close()
		except IOError as e:
			errstr = str(e)
			errstr += "\nCould not write script: {}".format(destination)
			warn(errstr)
			return 1
		else:
			print("Written to:", destination)
			return 0
		
	
	def execute_script(self, destination):
		"""Call 'qsub' on the shell script.
		
		Parameters:
		-----------
		destination:    str; shell script to call.
		"""
		if self.job_name:
			job_name = self.job_name
		else:
			job_name = "MOC_{ngroups}groups_div{divmesh:02d}".format(**vars(self))
		argument = ['qsub', '-N', job_name, destination]
		print(" ".join(argument))
		subprocess.Popen(argument)
