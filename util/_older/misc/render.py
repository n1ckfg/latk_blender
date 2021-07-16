from latk import *
#~
name = bpy.path.basename(bpy.context.blend_data.filepath)
frameInterval = 30
start, end = getStartEnd(pad=False)
startCounter = start
endCounter = start
#~
while endCounter < end:
    startCounter = endCounter
    endCounter = startCounter + frameInterval
    if (endCounter > end):
        endCounter = end
    setStartEnd(startCounter, endCounter, pad=False)
    #~
    gpMesh(_joinMesh=True, _thickness=0.01)
    #bpy.ops.wm.save_as_mainfile(filepath="C:\\tmp\\render_test_final.blend")
    bpy.ops.wm.save_as_mainfile(filepath="/Users/nick/Desktop/" + name + "_render_final_" + str(startCounter) + "-" + str(endCounter) + ".blend")

