import sys
import bpy
from latk import *
#~
argv = sys.argv
argv = argv[argv.index("--") + 1:]  # get all args after "--"

bpy.context.scene.frame_start = 0
readBrushStrokes(argv[0])
splf()

name1 = argv[0].split("/")
name2 = name1[len(name1)-1].split("\\")
name3 = name2[len(name2)-1].split(".")[0]

saveFile(name3)
gpMesh(_resolution=1, _decimate=0.02, _thickness=0.02, _saveLayers=True, _usePressure=True)

name4 = name3 + "_ASSEMBLY"

openFile(getFilePath() + name4)

exportAlembic(name4 + ".abc")
