# ctypes demo

## Build
	run `gcc -shared -o libctest.so ctest.c`

## Demo
	After `from ctypes import *`, `lib = CDLL('./libctest.so')`
	loads the dynamic library in Python. You need to set
	argument types and return types of each function as
	`lib.sum.restype = c_double` and `lib.sun.argtypes=POINTER(c_double), c_int)`.
	Then, you can call directly `lib.sum` as if it was a Python function

	See `test.py` for different parameter types.
