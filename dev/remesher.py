def remesher(target=None, mode="smooth", octree=6, threshold=1):
    original_type = bpy.context.area.type
    print("Current context: " + original_type)
    bpy.context.area.type = "VIEW_3D"
    #~
    if not target:
        target = []
        target.append(bpy.context.scene.objects.active)
    #~
    for i in range(0, len(target)):
    	obj = bpy.ops.object.select_pattern(target[i])
        bpy.context.scene.objects.active = obj
        bpy.ops.object.modifier_add(type="REMESH")
        bpy.context.object.modifiers["Remesh"].mode = mode.upper() #sharp, smooth, blocks
        bpy.context.object.modifiers["Remesh"].octree_depth = octree
        bpy.context.object.modifiers["Remesh"].threshold = threshold
    #~
    bpy.context.area.type = original_type    

def blockify(target=None, mode="blocks", threshold=0.5):
    remesher(target, mode, threshold)

def remeshCurves(name="crv"):
    remesher(matchName(name))

def blockifyCurves(name="crv"):
    blockify(matchName(name))



