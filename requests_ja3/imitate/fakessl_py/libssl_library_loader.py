import sys, pickle, ctypes

shitter = sys.argv [1]
library = ctypes.cdll.LoadLibrary (shitter)

pickle.dump (library, sys.stdout.buffer)