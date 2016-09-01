# https://gist.github.com/pcote/1307658
# http://blender.stackexchange.com/questions/7578/extruding-multiple-curves-at-once
# http://blender.stackexchange.com/questions/24694/query-grease-pencil-strokes-from-python
# https://wiki.blender.org/index.php/Dev:Py/Scripts/Cookbook/Code_snippets/Materials_and_textures
# http://blender.stackexchange.com/questions/58676/add-modifier-to-selected-and-another-to-active-object
# http://blenderscripting.blogspot.ca/2011/05/blender-25-python-bezier-from-list-of.html
# http://blender.stackexchange.com/questions/6750/poly-bezier-curve-from-a-list-of-coordinates
# http://blender.stackexchange.com/questions/7047/apply-transforms-to-linked-objects

def gpMesh(_thickness=0.0125, _resolution=1, _bevelResolution=0, _bakeMesh=False, _curveType="nurbs", _useModifiers=False, _useColors=False, _animateFrames=True, _minDistance = 0.0001, _subd=1, _decimate=0.02):
    start = bpy.context.scene.frame_start
    end = bpy.context.scene.frame_end + 1
    #~
    pencil = getActiveGp()
    #~
    for b in range(0, len(pencil.layers)):
        layer = pencil.layers[b]
        for c in range(0, len(layer.frames)):
            frameList = []
            for stroke in layer.frames[c].strokes:
                stroke_points = stroke.points
                coordsOrig = [ (point.co.x, point.co.y, point.co.z) for point in stroke_points ]
                coords = []
                if (_minDistance > 0.0):
                    for pp in range(0, len(coordsOrig)):
                        if (pp > 0 and getDistance(coordsOrig[pp], coordsOrig[pp-1]) >= _minDistance):
                            coords.append(coordsOrig[pp])
                else:
                    coords = coordsOrig
                # * * * * * * * * * * * * * *
                # TODO fix parenting. Here's where the initial transform corrections go.
                #if (layer.parent):
                    #for coord in coords:
                        #coord = layer.parent.matrix_world * Vector(coord)
                # * * * * * * * * * * * * * *                         
                #~
                crv_ob = makeCurve(coords=coords, curveType=_curveType, resolution=_resolution, thickness=_thickness, bevelResolution=_bevelResolution, parent=layer.parent)
                #crv_ob.data.extrude = _extrude
                strokeColor = (0.5,0.5,0.5)
                if (_useColors==True):
                    try:
                        strokeColor = stroke.color.color
                    except:
                        strokeColor = (0.5,0.5,0.5)
                        print ("error reading color")
                mat = bpy.data.materials.new("new_mtl")
                crv_ob.data.materials.append(mat)
                crv_ob.data.materials[0].diffuse_color = strokeColor
                # TODO fix vertex colors
                #colorVertices(meshObj, strokeColor, True)                        
                #~   
                bpy.context.scene.objects.active = crv_ob
                #~
                if (_useModifiers):
                    # solidify replaced by curve bevel
                    #bpy.ops.object.modifier_add(type='SOLIDIFY')
                    #bpy.context.object.modifiers["Solidify"].thickness = _extrude * 2
                    #bpy.context.object.modifiers["Solidify"].offset = 0
                    #~
                    # *** IMPORTANT: huge speed hit here.
                    if (_subd > 0):
                        bpy.ops.object.modifier_add(type='SUBSURF')
                        bpy.context.object.modifiers["Subsurf"].levels = _subd
                        bpy.context.object.modifiers["Subsurf"].render_levels = _subd
                        try:
                            bpy.context.object.modifiers["Subsurf"].use_opensubdiv = 1 # GPU if supported
                        except:
                            pass
                    #~
                    if (_decimate < 1.0):
                        bpy.ops.object.modifier_add(type='DECIMATE')
                        bpy.context.object.modifiers["Decimate"].ratio = _decimate  
                    #~  
                if (_bakeMesh==True):
                    meshObj = applyModifiers(crv_ob)       
                    frameList.append(meshObj)
                else:
                    frameList.append(crv_ob)
                # * * * * * * * * * * * * * *
                # TODO fix parenting. Here's where the output gets parented to the layer's parent.
                #if (layer.parent):
                    #index = len(frameList)-1
                    #frameList[index].parent = layer.parent
                # * * * * * * * * * * * * * *
            #~
            for i in range(0, len(frameList)):
                print(frameList[i])
                if (_animateFrames==True):
                    hideFrame(frameList[i], 0, True)
                    for j in range(start, end):
                        if (j == layer.frames[c].frame_number):
                            hideFrame(frameList[i], j, False)
                            keyTransform(frameList[i], j) 
                            #matchWithParent(frameList[i], layer.parent, j) 
                        elif (c < len(layer.frames)-1 and j > layer.frames[c].frame_number and j < layer.frames[c+1].frame_number):
                            hideFrame(frameList[i], j, False)
                            #keyTransform(frameList[i], j) 
                        #else:
                        elif (c != len(layer.frames)-1):
                            hideFrame(frameList[i], j, True)

def remesher(obj, bake=True, mode="blocks", octree=6, threshold=0.0001, smoothShade=False):
        #fixContext()
        bpy.context.scene.objects.active = obj
        bpy.ops.object.modifier_add(type="REMESH")
        bpy.context.object.modifiers["Remesh"].mode = mode.upper() #sharp, smooth, blocks
        bpy.context.object.modifiers["Remesh"].octree_depth = octree
        bpy.context.object.modifiers["Remesh"].use_smooth_shade = int(smoothShade)
        bpy.context.object.modifiers["Remesh"].threshold = threshold
        if (bake==True):
            return applyModifiers(obj)     
        else:
            return obj

def applyModifiers(obj):
    mesh = obj.to_mesh(scene = bpy.context.scene, apply_modifiers=True, settings = 'PREVIEW')
    meshObj = bpy.data.objects.new(obj.name + "_mesh", mesh)
    bpy.context.scene.objects.link(meshObj)
    bpy.context.scene.objects.active = meshObj
    meshObj.matrix_world = obj.matrix_world
    delete(obj)
    return meshObj

def getGeometryCenter(obj):
    sumWCoord = [0,0,0]
    numbVert = 0
    if obj.type == 'MESH':
        for vert in obj.data.vertices:
            wmtx = obj.matrix_world
            worldCoord = vert.co * wmtx
            sumWCoord[0] += worldCoord[0]
            sumWCoord[1] += worldCoord[1]
            sumWCoord[2] += worldCoord[2]
            numbVert += 1
        sumWCoord[0] = sumWCoord[0]/numbVert
        sumWCoord[1] = sumWCoord[1]/numbVert
        sumWCoord[2] = sumWCoord[2]/numbVert
    return sumWCoord

def centerOrigin(obj):
    oldLoc = obj.location
    newLoc = getGeometryCenter(obj)
    for vert in obj.data.vertices:
        vert.co[0] -= newLoc[0] - oldLoc[0]
        vert.co[1] -= newLoc[1] - oldLoc[1]
        vert.co[2] -= newLoc[2] - oldLoc[2]
    obj.location = newLoc

# http://blender.stackexchange.com/questions/6084/use-python-to-add-multiple-colors-to-a-nurbs-curve
# http://blender.stackexchange.com/questions/5668/add-nodes-to-material-with-python
def colorVertices(obj, color=(1,0,0), newMaterial=True):
    mesh = obj.data 
    #~    
    if len(mesh.vertex_colors) == 0:
        bpy.ops.mesh.vertex_color_add()
    #~
    if (newMaterial==True):
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
    num_verts = len(mesh.vertices)
    for vert_i in range(num_verts):
        colorVertex(obj, vert_i, color)
        print("Finished vertex: " + str(vert_i) + "/" + str(num_verts))

def colorVertex(obj, vert, color=[1,0,0]):
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

def setOrigin(target, point):
    bpy.context.scene.objects.active = target
    bpy.context.scene.cursor_location = point
    bpy.ops.object.origin_set(type='ORIGIN_CURSOR')
    #bpy.context.scene.update()

def matchWithParent(_child, _parent, _index):
    if (_parent):
        #bpy.context.scene.frame_set(_index)
        #if (_index == bpy.context.scene.frame_start):
        '''
        for v in _child.data.splines.active.bezier_points:
            loc = v.co * _parent.matrix_world.inverted()
            v.co = loc
        '''
        loc, rot, scale = _parent.matrix_world.inverted().decompose()
        _child.location = loc
        #_child.rotation_quaternion = rot
        _child.scale = scale
        #bpy.context.scene.update()
        _child.parent = _parent
        keyTransform(_child, _index)   

def makeCurve(coords, resolution=2, thickness=0.1, bevelResolution=1, simplify=True, curveType="bezier", parent=None):
    # http://blender.stackexchange.com/questions/12201/bezier-spline-with-python-adds-unwanted-point
    # http://blender.stackexchange.com/questions/6750/poly-bezier-curve-from-a-list-of-coordinates
    # create the curve datablock
    # https://svn.blender.org/svnroot/bf-extensions/trunk/py/scripts/addons/curve_simplify.py
    '''
    options = [
        0,    # smooth mode
        0,    # output mode
        0,    # k_thresh
        5,    # pointsNr
        0.0,  # error
        5,    # degreeOut
        0.0]  # dis_error
    if (simplify==True):
        coordsToVec = []
        for coord in coords:
            coordsToVec.append(Vector(coord))
        coordsToVec = simplypoly(coordsToVec, options)
        print(coordsToVec)
        #coords = []
        #for vec in coordsToVec:
            #coords.append((vec.x, vec.y, vec.z))
    '''
    #~
    curveData = bpy.data.curves.new('crv', type='CURVE')
    curveData.dimensions = '3D'
    curveData.fill_mode = 'FULL'
    curveData.resolution_u = resolution
    curveData.bevel_depth = thickness
    curveData.bevel_resolution = bevelResolution
    #~
    # map coords to spline
    curveType=curveType.upper()
    polyline = curveData.splines.new(curveType)
    if (curveType=="NURBS"):
        polyline.points.add(len(coords)-1)
        for i, coord in enumerate(coords):
                x,y,z = coord
                polyline.points[i].co = (x, y, z, 1)    
    elif (curveType=="BEZIER"):
        polyline.bezier_points.add(len(coords)-1)
        #polyline.bezier_points.foreach_set("co", unpack_list(coords))
        for i, coord in enumerate(coords):
            polyline.bezier_points[i].co = coord   
            polyline.bezier_points[i].handle_left = polyline.bezier_points[i].handle_right = polyline.bezier_points[i].co
    #~
    # create object
    crv_ob = bpy.data.objects.new('crv_ob', curveData)
    #if (parent != None):
        #crv_ob.location = (parent.location) #object origin  
    #~
    # attach to scene and validate context
    scn = bpy.context.scene
    scn.objects.link(crv_ob)
    scn.objects.active = crv_ob
    crv_ob.select = True
    return crv_ob

'''
# old attempts
def make_basic_curve():
    crv = bpy.data.curves.new("crv", type="CURVE")
    crv_ob = bpy.data.objects.new("crv_ob", crv)
    return crv, crv_ob

def makePolyLine(objname, curvename, cList):  
    curvedata = bpy.data.curves.new(name=curvename, type='CURVE')  
    curvedata.dimensions = '3D'  
    #~
    objectdata = bpy.data.objects.new(objname, curvedata)  
    objectdata.location = (0,0,0) #object origin  
    bpy.context.scene.objects.link(objectdata)  
    #~  
    polyline = curvedata.splines.new('NURBS')  
    polyline.points.add(len(cList)-1)  
    for num in range(len(cList)):  
        polyline.points[num].co = (cList[num])+(w,)  
    #~  
    polyline.order_u = len(polyline.points)-1
    polyline.use_endpoint_u = True
'''

def createMesh(name, origin, verts, faces):
    bpy.ops.object.add(
        type='MESH', 
        enter_editmode=False,
        location=origin)
    ob = bpy.context.object
    ob.name = name
    ob.show_name = True
    me = ob.data
    me.name = name+'Mesh'
    #~
    # Create mesh from given verts, faces.
    me.from_pydata(verts, [], faces)
    # Update mesh with new data
    me.update()    
    # Set object mode
    bpy.ops.object.mode_set(mode='OBJECT')
    return ob

def exporter():
    for j in range(bpy.context.scene.frame_start, bpy.context.scene.frame_end + 1):
        bpy.ops.object.select_all(action='DESELECT')
        goToFrame(j)
        for i in range(0, len(bpy.data.objects)):
            if (bpy.data.objects[i].hide == False):
                bpy.data.objects[i].select = True
        #bpy.context.scene.update()
        bpy.ops.export_scene.obj(filepath="/Users/nick/Desktop/test" + str(j) + ".obj", use_selection=True)

# crashes        
def makeGpCurve(_type="PATH"):
    original_type = bpy.context.area.type
    print("Current context: " + original_type)
    bpy.context.area.type = "VIEW_3D"
    #~
    # strokes, points, frame
    bpy.ops.gpencil.convert(type=_type)
    #~
    #bpy.context.area.type = "CONSOLE"
    bpy.context.area.type = original_type

# ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~
# ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~
# shortcuts

def crv():
    deleteName("crv")
    gpMesh(0.005, 0, False, True)  

def crvStill():
    deleteName("crv")
    gpMesh(0.005, 0, False, False)

def crvAbcFat():
    deleteName("crv")
    gpMesh(0.05,0, True, True)

def crvAbcThin():
    deleteName("crv")
    gpMesh(0.005, 0, True, True)

# * * * * * * * * * * * * * * * * * * * * * * * * * *
# * * * * * * * * * * * * * * * * * * * * * * * * * *
# * * * * * * * * * * * * * * * * * * * * * * * * * *

