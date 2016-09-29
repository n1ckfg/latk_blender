from latk import *
#~
name = getFileName() + "_render_final.blend"
gpMesh(_joinMesh=True, _thickness=0.01)
#~
#bpy.ops.wm.save_as_mainfile(filepath="C:\\tmp\\render_test_final.blend")
bpy.ops.wm.save_as_mainfile(filepath="/Users/nick/Desktop/" + name)
