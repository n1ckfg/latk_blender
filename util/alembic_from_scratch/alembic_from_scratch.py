import sys
import bpy
from latk_blender import *
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
latk_settings=bpy.context.scene.latk_settings
gpMesh(_saveLayers=True, _thickness=latk_settings.thickness, _remesh=latk_settings.remesh_mode.lower(), _resolution=latk_settings.resolution, _bevelResolution=latk_settings.bevelResolution, _decimate=latk_settings.decimate, _vertexColorName=latk_settings.vertexColorName)

name4 = name3 + "_ASSEMBLY"

openFile(getFilePath() + name4)

exportAlembic(name4 + ".abc")
