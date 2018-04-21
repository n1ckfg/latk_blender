import sys
import bpy
from latk import *
#~
argv = sys.argv
argv = argv[argv.index("--") + 1:]  # get all args after "--"

bpy.context.scene.frame_start = 0
readBrushStrokes(argv[0])
splf()

getName1 = argv[0].split("/")
getName2 = getName1[len(getName1)-1].split("\\")
getName3 = getName2[len(getName2)-1].split(".")[0]

saveFile(getName3)
gpMesh(_resolution=1, _decimate=0.02, _thickness=0.02, _saveLayers=True, _usePressure=True)
#~
