# 4 of 10. MATERIALS / RENDERING

# http://blender.stackexchange.com/questions/17738/how-to-uv-unwrap-object-with-python
def planarUvProject():
    for area in bpy.context.screen.areas:
        if area.type == 'VIEW_3D':
            for region in area.regions:
                if region.type == 'WINDOW':
                    override = {'area': area, 'region': region, 'edit_object': bpy.context.edit_object}
                    bpy.ops.uv.smart_project(override)
                    
def colorVertexCyclesMat(obj):
    # http://blender.stackexchange.com/questions/6084/use-python-to-add-multiple-colors-to-a-nurbs-curve
    # http://blender.stackexchange.com/questions/5668/add-nodes-to-material-with-python
    # this will fail if you don't have Cycles Render enabled
    mesh = obj.data 
    #~    
    obj.active_material = bpy.data.materials.new('material')
    obj.active_material.use_vertex_color_paint = True
    #~
    obj.active_material.use_nodes = True
    nodes = obj.active_material.node_tree.nodes
    material_output = nodes.get('Diffuse BSDF')
    nodeAttr = nodes.new("ShaderNodeAttribute")
    nodeAttr.attribute_name = "Cd"
    obj.active_material.node_tree.links.new(material_output.inputs[0], nodeAttr.outputs[0])

def colorVertexAlt(obj, vert, color=[1,0,0]):
    mesh = obj.data 
    scn = bpy.context.scene
    # check if our mesh already has Vertex Colors, and if not add some... (first we need to make sure it's the active object)
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
        # 1-3. Creating palette of all materials
        for mtl in bpy.data.materials:
            foundNewMtl = True
            for palMtl in palette:
                if (compareTuple(getDiffuseColor(mtl), getDiffuseColor(palMtl), numPlaces=numPlaces)==True):
                    foundNewMtl = False
                    break
            if (foundNewMtl==True):
                palette.append(mtl)
        for i, mtl in enumerate(palette):
            mtl.name = "Palette_" + str(i+1)
        # 2-3. Matching palette colors for all objects
        for obj in bpy.context.scene.objects:
            try:
                for i, mtl in enumerate(obj.data.materials):
                    for palMtl in palette:
                        if (compareTuple(getDiffuseColor(mtl), getDiffuseColor(palMtl), numPlaces=numPlaces)==True):
                            obj.data.materials[i] = palMtl
            except:
                pass
        # 3-3. Removing unused materials
        removeUnusedMtl()
    #~
    print ("Created palette of " + str(len(palette)) + " materials.")
    return palette

def removeUnusedMtl():
    # http://blender.stackexchange.com/questions/5300/how-can-i-remove-all-unused-materials-from-a-file/35637#35637
    for mtl in bpy.data.materials:
        if not mtl.users:
            bpy.data.materials.remove(mtl)

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
def searchMtl(color=None, name="latk"):
    returns = []
    if not color:
        color = getActiveColor().color
    curves = matchName(name)
    for curve in curves:
        if (compareTuple(curve.data.materials[0].diffuse_color, color)):
            returns.append(curve)
    return returns

# TODO handle multiple materials on one mesh
def changeMtl(color=(1,1,0), searchColor=None, name="latk"):
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
            try:
                for i, mat in enumerate(obj.data.materials):
                    if (compareTuple((color.color[0],color.color[1],color.color[2]), getDiffuseColor(mat)) == True):
                        if (matchMat == None):
                            matchMat = mat
                        else:
                            obj.data.materials[i] = matchMat
            except:
                pass

# old version, can't handle multiple materials on one mesh
def consolidateMtlAlt(name="latk"):
    palette = getActivePalette()
    for color in palette.colors:
        curves = searchMtl(color=color.color, name=name)
        for i in range(1, len(curves)):
            curves[i].data.materials[0] = curves[0].data.materials[0]

def getActiveMtl():
    return bpy.context.scene.objects.active.data.materials[bpy.context.scene.objects.active.active_material_index]

def getMtlColor(node="diffuse", mtl=None):
    if not mtl:
        mtl = getActiveMtl()
    try:
        if (node.lower() == "emission"):
            color = mtl.node_tree.nodes["Emission"].inputs["Color"].default_value
            return (color[0], color[1], color[2])
        elif (node.lower() == "principled"):
            color = mtl.node_tree.nodes["Principled BSDF"].inputs["Base Color"].default_value
            return (color[0], color[1], color[2])
        else:
            color = mtl.node_tree.nodes["Diffuse BSDF"].inputs["Color"].default_value
            return (color[0], color[1], color[2])
    except:
        return None

# assumes that we're starting with diffuse shader, the default
def setMtlShader(shader="diffuse", mtl=None):
    # https://blender.stackexchange.com/questions/23436/control-cycles-material-nodes-and-material-properties-in-python
    if not mtl:
        mtl = getActiveMtl()
    col = getUnknownColor(mtl)
    if not col:
        return None
    #~
    # https://blender.stackexchange.com/questions/33189/python-script-attribute-error-while-using-node-editor
    # clear all nodes to start clean
    mtl.use_nodes = True
    nodes = mtl.node_tree.nodes
    for node in nodes:
        nodes.remove(node)
    #~
    destNode = None
    #~
    # https://docs.blender.org/api/blender_python_api_2_78_0/bpy.types.html
    # create emission node
    if (shader.lower()=="emission"):
        destNode = nodes.new(type="ShaderNodeEmission")
        destNode.inputs[0].default_value = (col[0], col[1], col[2], 1) # RGBA
        #destNode.inputs[1].default_value = 5.0 # strength
    elif (shader.lower()=="principled"):
        destNode = nodes.new(type="ShaderNodeBsdfPrincipled")
        destNode.inputs["Base Color"].default_value = (col[0], col[1], col[2], 1) # RGBA
        destNode.inputs["Subsurface Color"].default_value = (col[0], col[1], col[2], 1) # RGBA
    else:
        destNode = nodes.new(type="ShaderNodeBsdfDiffuse")
        destNode.inputs[0].default_value = (col[0], col[1], col[2], 1) # RGBA
    #~
    destNode.location = 0,0
    #~
    # create output node
    node_output = nodes.new(type="ShaderNodeOutputMaterial")   
    node_output.location = 400,0
    #~
    # link nodes
    links = mtl.node_tree.links
    link = links.new(destNode.outputs[0], node_output.inputs[0])
    #~
    return mtl

def setAllMtlShader(shader="principled"):
    for mtl in bpy.data.materials:
        setMtlShader(shader, mtl)

def getDiffuseColor(mtl=None):
    if not mtl:
        mtl = getActiveMtl()
    col = getMtlColor("diffuse", mtl)
    if (col==None):
        col = mtl.diffuse_color
    return col

def getEmissionColor(mtl=None):
    if not mtl:
        mtl = getActiveMtl()
    return getMtlColor("emission", mtl)

def getPrincipledColor(mtl=None):
    if not mtl:
        mtl = getActiveMtl()
    return getMtlColor("principled", mtl)

def getUnknownColor(mtl=None):
    if not mtl:
        mtl = getActiveMtl()
    col = None
    if (col == None):
        col = getEmissionColor(mtl)
    if (col == None):
        col = getPrincipledColor(mtl)
    if (col == None):
        col = getDiffuseColor(mtl)
    return col

# is this obsolete now that all materials are linked by color value?
def makeEmissionMtl():
    mtl = getActiveMtl()
    color = getEmissionColor()
    for obj in bpy.context.scene.objects:
        try:
            for j in range(0, len(obj.data.materials)):
                destColor = getDiffuseColor(obj.data.materials[j])
                if (compareTuple(destColor, color) == True):
                    obj.data.materials[j] = mtl
        except:
            pass

#~ ~ ~ ~ ~ ~ ~ ~
# pixel / uv methods
#~ ~ ~ ~ ~ ~ ~ ~

# http://blender.stackexchange.com/questions/49341/how-to-get-the-uv-corresponding-to-a-vertex-via-the-python-api
# https://blenderartists.org/forum/archive/index.php/t-195230.html
# https://developer.blender.org/T28211
# http://blenderscripting.blogspot.ca/2012/08/adjusting-image-pixels-walkthrough.html
# https://www.blender.org/forum/viewtopic.php?t=25804
# https://docs.blender.org/api/blender_python_api_2_63_2/bmesh.html
# http://blender.stackexchange.com/questions/1311/how-can-i-get-vertex-positions-from-a-mesh

def uv_from_vert_first(uv_layer, v):
    for l in v.link_loops:
        uv_data = l[uv_layer]
        return uv_data.uv
    return None


def uv_from_vert_average(uv_layer, v):
    uv_average = Vector((0.0, 0.0))
    total = 0.0
    for loop in v.link_loops:
        uv_average += loop[uv_layer].uv
        total += 1.0
    #~
    if total != 0.0:
        return uv_average * (1.0 / total)
    else:
        return None

# Example using the functions above
'''
def testUvs():
    obj = bpy.context.scene.objects.active #edit_object
    me = obj.data
    bm = bmesh.new()
    bm.from_mesh(me) #from_edit_mesh(me)
    #~
    images = getUvImages()
    #~
    uv_layer = bm.loops.layers.uv.active
    #~
    for v in bm.verts:
        uv_first = uv_from_vert_first(uv_layer, v)
        uv_average = uv_from_vert_average(uv_layer, v)
        print("Vertex: %r, uv_first=%r, uv_average=%r" % (v, uv_first, uv_average))
        #~
        pixel = getPixelFromUvArray(images[obj.active_material.texture_slots[0].texture.image.name], uv_first[0], uv_first[1])
        print("Pixel: " + str(pixel))
'''

def getVerts(target=None):
    if not target:
        target = bpy.context.scene.objects.active
    me = target.data
    bm = bmesh.new()
    bm.from_mesh(me)
    return bm.verts

def getUvImages():
    obj = bpy.context.scene.objects.active
    uv_images = {}
    #~
    #for uv_tex in obdata.uv_textures.active.data:
    for tex in obj.active_material.texture_slots:
        try:
            uv_tex = tex.texture
            if (uv_tex.image and
                uv_tex.image.name not in uv_images and
                uv_tex.image.pixels):

                uv_images[uv_tex.image.name] = (
                    uv_tex.image.size[0],
                    uv_tex.image.size[1],
                    uv_tex.image.pixels[:]
                    # Accessing pixels directly is far too slow.
                    # Copied to new array for massive performance-gain.
                )
        except:
            pass
    #~
    return uv_images

def getPixelFromImage(img, xPos, yPos):
    imgWidth = int(img.size[0])
    r = img.pixels[4 * (xPos + imgWidth * yPos) + 0]
    g = img.pixels[4 * (xPos + imgWidth * yPos) + 1]
    b = img.pixels[4 * (xPos + imgWidth * yPos) + 2]
    a = img.pixels[4 * (xPos + imgWidth * yPos) + 3]
    return [r, g, b, a]

def getPixelFromUv(img, u, v):
    imgWidth = int(img.size[0])
    imgHeight = int(img.size[1])
    pixel_x = int(u * imgWidth)
    pixel_y = int(v * imgHeight)
    return getPixelFromImage(img, pixel_x, pixel_y)

# *** these methods are much faster but don't work in all contexts
def getPixelFromImageArray(img, xPos, yPos):
    imgWidth = int(img[0]) #img.size[0]
    #r = img.pixels[4 * (xPos + imgWidth * yPos) + 0]
    r = img[2][4 * (xPos + imgWidth * yPos) + 0]
    g = img[2][4 * (xPos + imgWidth * yPos) + 1]
    b = img[2][4 * (xPos + imgWidth * yPos) + 2]
    a = img[2][4 * (xPos + imgWidth * yPos) + 3]
    return [r, g, b, a]

def getPixelFromUvArray(img, u, v):
    imgWidth = int(img[0]) #img.size[0]
    imgHeight = int(img[1]) #img.size[1]
    pixel_x = int(u * imgWidth)
    pixel_y = int(v * imgHeight)
    return getPixelFromImageArray(img, pixel_x, pixel_y)

# * * * * * * * * * * * * * * * * * * * * * * * * * *
# * * * * * * * * * * * * * * * * * * * * * * * * * *
# * * * * * * * * * * * * * * * * * * * * * * * * * *

