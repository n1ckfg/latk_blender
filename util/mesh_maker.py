from latk import *
gpMesh(_bakeMesh=True, _subd=1, _remesh=True)
bpy.ops.wm.save_as_mainfile(filepath="C:\\tmp\\render_test-nobake.blend")