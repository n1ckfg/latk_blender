# http://blender.stackexchange.com/questions/17738/how-to-uv-unwrap-object-with-python
def planarUvProject():
    for area in bpy.context.screen.areas:
        if area.type == 'VIEW_3D':
            for region in area.regions:
                if region.type == 'WINDOW':
                    override = {'area': area, 'region': region, 'edit_object': bpy.context.edit_object}
                    bpy.ops.uv.smart_project(override)
                    
#def colorVertexCyclesMat(obj, color=(1,0,0), newMaterial=True):
def colorVertexCyclesMat(obj):
    # http://blender.stackexchange.com/questions/6084/use-python-to-add-multiple-colors-to-a-nurbs-curve
    # http://blender.stackexchange.com/questions/5668/add-nodes-to-material-with-python
    # this will fail if you don't have Cycles Render enabled
    mesh = obj.data 
    #~    
    #if len(mesh.vertex_colors) == 0:
        #bpy.ops.mesh.vertex_color_add()
    #~
    #if (newMaterial==True):
    obj.active_material = bpy.data.materials.new('material')
    obj.active_material.use_vertex_color_paint = True
    #~
    obj.active_material.use_nodes = True
    nodes = obj.active_material.node_tree.nodes
    material_output = nodes.get('Diffuse BSDF')
    nodeAttr = nodes.new("ShaderNodeAttribute")
    nodeAttr.attribute_name = "Col"
    obj.active_material.node_tree.links.new(material_output.inputs[0], nodeAttr.outputs[0])
    #~
    #loop through each vertex
    #num_verts = len(mesh.vertices)
    #for vert_i in range(num_verts):
        #colorVertex(obj, vert_i, color)
        #print("Finished vertex: " + str(vert_i) + "/" + str(num_verts))

def colorVertexAlt(obj, vert, color=[1,0,0]):
    mesh = obj.data 
    scn = bpy.context.scene
    #check if our mesh already has Vertex Colors, and if not add some... (first we need to make sure it's the active object)
    scn.objects.active = obj
    obj.select = True
    if len(mesh.vertex_colors) == 0:
        bpy.ops.mesh.vertex_color_add()
    i=0
    for poly in mesh.polygons:
        for vert_side in poly.loop_indices:
            global_vert_num = poly.vertices[vert_side-min(poly.loop_indices)] 
            if vert == global_vert_num:
                mesh.vertex_colors[0].data[i].color = color
            i += 1

def createMtlPalette(numPlaces=5, numReps = 1):
    palette = None
    removeUnusedMtl()
    for h in range(0, numReps):
        palette = []
        #print("1-3. Creating palette of all materials...")
        for mtl in bpy.data.materials:
            foundNewMtl = True
            for palMtl in palette:
                if (compareTuple(getDiffuseColor(mtl), getDiffuseColor(palMtl), numPlaces=numPlaces)==True):
                    foundNewMtl = False
                    break
            if (foundNewMtl==True):
                #print("Found " + mtl.name)
                palette.append(mtl)
        for i, mtl in enumerate(palette):
            mtl.name = "Palette_" + str(i+1)
        #print("2-3. Matching palette colors for all objects...")
        for obj in bpy.context.scene.objects:
            try:
                for i, mtl in enumerate(obj.data.materials):
                    for palMtl in palette:
                        if (compareTuple(getDiffuseColor(mtl), getDiffuseColor(palMtl), numPlaces=numPlaces)==True):
                            obj.data.materials[i] = palMtl
            except:
                pass
        #print("3-3. Removing unused materials...")
        removeUnusedMtl()
    #~
    print ("Created palette of " + str(len(palette)) + " materials.")
    return palette

def removeUnusedMtl():
    # http://blender.stackexchange.com/questions/5300/how-can-i-remove-all-unused-materials-from-a-file/35637#35637
    for mtl in bpy.data.materials:
        if not mtl.users:
            bpy.data.materials.remove(mtl)

'''
def sortLists(list1, list2):
    list1.sort(key=lambda x: x[0])
    ind = [i[0] for i in sorted(enumerate(list2),key=lambda x: x[1])]
    list1 = [i[0] for i in sorted(zip(list1, ind),key=lambda x: x[1])]
    return list1
'''

# https://blender.stackexchange.com/questions/5668/add-nodes-to-material-with-python
def texAllMtl(filePath="D://Asset Collections//Images//Element maps 2K//Plaster_maps//plaster_wall_distressed_04_normal.jpg", strength=1.0, colorData=False):
    for mtl in bpy.data.materials:
        mtl.use_nodes = True
        nodes = mtl.node_tree.nodes
        links = mtl.node_tree.links
        #~
        shaderNode = nodes["Diffuse BSDF"]
        texNode = None
        mapNode = None
        try:
            texNode = nodes["Image Texture"]
        except:
            texNode = nodes.new("ShaderNodeTexImage")
        try:
            mapNode = nodes["Normal Map"]
        except:
            mapNode = nodes.new("ShaderNodeNormalMap")
        #~
        links.new(texNode.outputs[0], mapNode.inputs[1])
        links.new(mapNode.outputs[0], shaderNode.inputs[2])
        #~
        texNode.image = bpy.data.images.load(filePath)
        if (colorData==True):
            texNode.color_space = "COLOR"
        else:
            texNode.color_space = "NONE"
        mapNode.inputs[0].default_value = strength
        #~
        mapNode.location = [shaderNode.location.x - 250, shaderNode.location.y]
        texNode.location = [mapNode.location.x - 250, shaderNode.location.y]

# TODO handle multiple materials on one mesh
def searchMtl(color=None, name="crv"):
    returns = []
    if not color:
        color = getActiveColor().color
    curves = matchName(name)
    for curve in curves:
        if (compareTuple(curve.data.materials[0].diffuse_color, color)):
            returns.append(curve)
    #print ("found: " + str(returns))
    return returns

# TODO handle multiple materials on one mesh
def changeMtl(color=(1,1,0), searchColor=None, name="crv"):
    if not searchColor:
        searchColor = getActiveColor().color       
    curves = searchMtl(color=searchColor, name=name)
    print("changed: " + str(curves))
    for curve in curves:
        curve.data.materials[0].diffuse_color = color

def consolidateMtl():
    palette = getActivePalette()
    for color in palette.colors:
        matchMat = None
        for obj in bpy.context.scene.objects:
            #print(obj.name)
            try:
                for i, mat in enumerate(obj.data.materials):
                    #print(str(color.color) + " " + str(getDiffuseColor(mat)))
                    if (compareTuple((color.color[0],color.color[1],color.color[2]), getDiffuseColor(mat)) == True):
                        if (matchMat == None):
                            matchMat = mat
                        else:
                            obj.data.materials[i] = matchMat
            except:
                pass

# old version, can't handle multiple materials on one mesh
def consolidateMtlAlt(name="crv"):
    palette = getActivePalette()
    for color in palette.colors:
        curves = searchMtl(color=color.color, name=name)
        for i in range(1, len(curves)):
            curves[i].data.materials[0] = curves[0].data.materials[0]

def getActiveMtl():
    return bpy.context.scene.objects.active.data.materials[bpy.context.scene.objects.active.active_material_index]

def getMtlColor(node="Diffuse BSDF", mtl=None):
    if not mtl:
        mtl = getActiveMtl()
    try:
        colorRaw = mtl.node_tree.nodes[node].inputs["Color"].default_value
        color = (colorRaw[0], colorRaw[1], colorRaw[2])
        return color
    except:
        return None

def getEmissionColor(mtl=None):
    if not mtl:
        mtl = getActiveMtl()
    return getMtlColor("Emission", mtl)

def getDiffuseColor(mtl=None):
    if not mtl:
        mtl = getActiveMtl()
    col = getMtlColor("Diffuse BSDF", mtl)
    if (col==None):
        col = mtl.diffuse_color
    return col
    #return getMtlColor("Diffuse BSDF", mtl)

def makeEmissionMtl():
    mtl = getActiveMtl()
    color = getEmissionColor()
    #print("source color: " + str(color))
    for obj in bpy.context.scene.objects:
        try:
            for j in range(0, len(obj.data.materials)):
                destColor = getDiffuseColor(obj.data.materials[j])
                #print("dest color: " + str(destColor))
                if (compareTuple(destColor, color) == True):
                    obj.data.materials[j] = mtl
        except:
            pass

