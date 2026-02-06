# sbs

## What is this?
This is a system that lets you quickly and easily build a C program.
It is specifically meant for hobby programs and probably isn't suitable for
large or commercial projects.

## How do I use this?
1. copy the `sbs.py` file over into your code
2. create a `build.py` file
3. put the following code into your `build.py` file:
```py
import sbs

exec = sbs.Executable('main')
exec.add_src('path/to/your/src/files') # set "recursive = True" to allow recursive search
                                       # for globbing with * and **.
exec.add_flags('-Wall -Werror') # optional; any flags you want

exec.compile()
```

## Example builds

### A simple one-file program
```py
import sbs

exec = sbs.Executable('main')\
	.add_src('src/main.c')\
	.add_flags('-Wall -Werror')

exec.compile()
```

### Compile a large folder structure that links Cocoa, and changes the compiler
```py
import sbs
DEFAULT_COMPILER = 'clang'

exec = sbs.Executable('cocoa_example')\
	.add_src('src/**/*.c', recursive=True)\
	.add_flags('-Wall -Werror -framework Cocoa')

exec.compile()
```