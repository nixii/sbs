"""
	Examples

Create a simple executable from a directory
	import sbs

	sbs.init()

	Executable("main")\
		.add_src("src/**/*.c")\
		.compile()


More advanced, many-directory build
	import sbs

	sbs.init()

	exec = Executable("main")

	exec.add_src("src/**/*.c")
	exec.add_src("game/**/*.c")

	if sbs.OS_MAC:
		exec.add_frameworks("Cocoa")
		exec.set_compiler("clang")

	exec.add_flags("-Wall -Winclude")
	exec.add_includes("-Iinclude")
	exec.add_libs("-Llib")

	exec.compile()
"""

# import all used libraries
import subprocess
import platform
import glob
import sys
import os

# get the system
_sys = platform.system()

# various settings
class Settings:
	DIR = "sbs"
	COMPILER: str = "cc"

# what os is running the command
class Os:
	MACOS =_sys.lower() == "darwin"
	WINDOWS = _sys.lower() == "windows"
	LINUX = _sys.lower() == "linux"

# make a dir if it doesn't exist
def enforce_dir(dir: str):
	os.makedirs(dir, exist_ok=True)

# turn a path into the obj file path
def binpath(p: str):

	# get the dir and filename seperately
	dir, filename = os.path.split(p)

	# get the directory locally
	reldir = os.path.relpath(dir, start=os.getcwd())

	# move the local dir path to the bin directory
	tdir = os.path.join(Settings.DIR, reldir)

	# get the final path from that new dir with the .o extension
	tf = os.path.join(tdir, os.path.splitext(filename)[0] + '.o')
	return tf

# options for the compiler
class Options:
	def __init__(self,
		flags: str="",
		includes: str="",
		libs: str="",
		frameworks: str=""):

		self.flags = flags
		self.includes = includes
		self.libs = libs
		self.frameworks = frameworks
		self.cc = Settings.COMPILER

	# duplicate it if needed
	def clone(self):
		return Options(
			flags = self.flags,
			includes = self.includes,
			libs = self.libs,
			frameworks = self.frameworks)

	# adders
	def add_flag(self, flag: str):
		self.flags += f' {flag}'
	def add_include(self, include: str):
		self.includes += f' -I{include}'
	def add_lib(self, lib: str):
		self.libs += f' -L{lib}'
	def add_framework(self, framework: str):
		self.frameworks += f'-framework {framework}'
	def set_compiler(self, compiler: str):
		self.cc = compiler

# a single object file to compile
class OFile:
	def __init__(self, name: str, src: str, options: Options | None = None):
		self.name = name
		self.src = src
		self.options = options or Options()

	# compile the object
	def compile(self):

		# create the dir if it doesn't exist
		my_dir = os.path.dirname(self.name)
		if not my_dir.isspace():
			enforce_dir(my_dir)

		# don't recompile if there is no nee
		if os.path.exists(self.name)\
			and os.path.getmtime(self.src) < os.path.getmtime(self.name):
			print(f'[OBJ] Object {self.name} already compiled!!!')
			return

		# create the command
		cmd = f'{self.options.cc} -o {self.name} -c {self.src} {self.options.flags}'
		print(f'[OBJ] Compiling {self.name}...')

		# run the command and wait to finish
		try:
			subprocess.check_call(cmd, shell=True)
		except subprocess.CalledProcessError:
			print(f'\033[31m[ERROR!]\033[m Failed to compile {self.name}')
			sys.exit(0)

		# success
		print(f'[DONE] Compiled {self.name}!')

# the final executable to compile
class Executable:
	def __init__(self, name, options: Options | None = None):
		self.name = os.path.relpath(name)
		self.srcs = {}
		self.options = options if options is not None else Options()

	# add src files, globbing enabled
	def add_src(self, *paths: str):

		# double loop so variadic args
		for path in paths:
			for p in glob.glob(path, recursive=True):

				# create the object
				new_path = binpath(p)
				o = OFile(new_path, p, self.options)
				self.srcs[new_path] = o
		return self

	# adders for thing in the options, with va args
	def add_flags(self, *flags: str):
		for flaggroup in flags:
			for flag in flaggroup.split(" "):
				self.options.add_flag(flag)
		return self
	def add_includes(self, *includes: str):
		for includegroup in includes:
			for include in includegroup.split(" "):
				self.options.add_include(include)
		return self
	def add_lib(self, *libs: str):
		for libgroup in libs:
			for lib in libgroup.split(" "):
				self.options.add_lib(lib)
		return self
	def add_frameworks(self, *frameworks: str):
		for frameworkgroup in frameworks:
			for framework in frameworkgroup.split(" "):
				self.options.add_framework(framework)
		return self
	def set_compiler(self, compiler: str):
		self.options.set_compiler(compiler)
		return self

	# compile the executable
	def compile(self):

		# compile all the object files
		for src in self.srcs.values():
			src.compile()

		# ensure the directory exists
		my_dir = os.path.dirname(self.name)
		if not my_dir.isspace() and my_dir != '':
			enforce_dir(my_dir)

		# create the command
		cmd = f'{self.options.cc} -o {self.name} {" ".join(self.srcs.keys())} {self.options.flags} {self.options.includes} {self.options.libs} {self.options.frameworks}'
		print(f'[EXE] Compiling {self.name}...')

		# run the command and wait
		try:
			subprocess.check_call(cmd, shell=True)
		except subprocess.CalledProcessError:
			print(f'\033[31m[ERROR!]\033[m Failed to compile {self.name}')
			sys.exit(0)

		# success
		print(f'[DONE] Compiled {self.name}!')