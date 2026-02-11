
import sbs

exec = sbs.Executable('main')\
	.add_src('src/**/*.c')\
	.add_flags('-Wall', '-Werror')

exec.compile()