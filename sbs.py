
# imports
import os, glob, subprocess, time

# constants
DEFAULT_COMPILER = 'cc'
BIN_DIR = '.sbs/objs/'

# move a file path to a bin dir path
def bin_path(path: str) -> str:
	return os.path.realpath(BIN_DIR + path)

# an object
class CompilerObject():

	# properties
	name: str
	file: str
	compiler: str
	
	# create the object
	def __init__(self: 'CompilerObject', name: str, file: str, compiler: str | None) -> 'CompilerObject':
		self.name = name.replace(' ', '\\ ')
		self.file = file.replace(' ', '\\ ')
		self.compiler = compiler if compiler is not None else DEFAULT_COMPILER
	
	# compile the object
	def compile(self: 'CompilerObject', opts: str = '') -> bool:
		os.makedirs(os.path.dirname(self.name), exist_ok=True)

		# get last edited timestamp
		last_edited_code = 0 if not os.path.exists(self.file) else os.path.getmtime(self.file)
		last_edited_object = 0 if not os.path.exists(self.name) else os.path.getmtime(self.name)

		# stop compiling if it is already up to date
		if last_edited_code <= last_edited_object:
			print(f'[OBJ] {self.name} already compiled!')
			return
		
		# run the command
		cmd = f'{self.compiler} -o {self.name} {self.file} -c {' '.join(opts)}'
		print(f'[OBJ] Compiling: {self.name}')
		p = subprocess.Popen(cmd, shell=True)
		p.wait()
	
	# string version
	def __str__(self):
		return self.name

# A single executable to compile
class Executable():
	
	# properties
	name: str
	compiler: str
	objects: list[CompilerObject]
	opts: list[str]

	# initialize the executable
	def __init__(self: 'Executable', name: str) -> 'Executable':
		self.name = name
		self.compiler = DEFAULT_COMPILER
		self.objects = []
		self.opts = []

	# add src files
	def add_srcs(self: 'Executable', *srcs: str, recursive: bool = False) -> 'Executable':
		for src in srcs:
			self.add_src(src, recursive=recursive)
		
		return self
	
	# add a single source
	def add_src(self: 'Executable', src: str, recursive: bool = False) -> 'Executable':
		files = glob.glob(src, recursive=recursive)

		for file in files:
			obj_name = os.path.splitext(file)[0] + '.o'
			obj_name = bin_path(obj_name)
			self.objects.append(CompilerObject(obj_name, file, self.compiler))
		
		return self
	
	# add flags
	def add_flags(self: 'Executable', flags: str) -> 'Executable':
		for flag in flags.split(' '):
			self.opts.append(flag)
		return self

	# compile 
	def compile(self: 'Executable') -> 'Executable':

		# remove duplicates
		objects = list(dict.fromkeys(self.objects))

		# assert the final dir
		dn = os.path.dirname(self.name)
		if not dn == '':
			os.makedirs(dn, exist_ok=True)

		# compile each object
		for obj in objects:
			obj.compile(self.opts)
		
		# compile self
		cmd = f'{self.compiler} -o {self.name} {' '.join(map(str, objects))} {' '.join(self.opts)}'
		print(f'[EXE] Compiling {self.name}')
		p = subprocess.Popen(cmd, shell=True)
		p.wait()

		# return self
		return self
