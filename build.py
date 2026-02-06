
# Import the build system
import sbs

# Create the executable
exec = sbs.Executable('./main')\
	.add_srcs('./src/**/*.c', recursive=True)\
	.add_flags('-Wall -Wextra')

# Compile the program
exec.compile()