import sys
from latk import *
#~
argv = sys.argv
argv = argv[argv.index("--") + 1:]  # get all args after "--"

readBrushStrokes(argv[0])
splf()
gpMesh(_resolution=1, _decimate=0.02, _thickness=0.02, _saveLayers=True, _usePressure=True)
#~
