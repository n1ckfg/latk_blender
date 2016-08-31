# https://gist.github.com/pcote/1307658
# http://blender.stackexchange.com/questions/7578/extruding-multiple-curves-at-once
# http://blender.stackexchange.com/questions/24694/query-grease-pencil-strokes-from-python
# https://wiki.blender.org/index.php/Dev:Py/Scripts/Cookbook/Code_snippets/Materials_and_textures
# http://blender.stackexchange.com/questions/58676/add-modifier-to-selected-and-another-to-active-object
# http://blenderscripting.blogspot.ca/2011/05/blender-25-python-bezier-from-list-of.html
# http://blender.stackexchange.com/questions/6750/poly-bezier-curve-from-a-list-of-coordinates
# http://blender.stackexchange.com/questions/7047/apply-transforms-to-linked-objects

from math import sqrt

def getDistance(v1, v2):
    return sqrt( (v1[0] - v2[0])**2 + (v1[1] - v2[1])**2 + (v1[2] - v2[2])**2)

def gpMesh(_extrude=0.025, _subd=0, _bakeMesh=False, _animateFrames=True, _remesh=False, _minDistance=0.01):
    scnobs = bpy.context.scene.objects
    start = bpy.context.scene.frame_start
    end = bpy.context.scene.frame_end + 1
    #~
    #goToFrame(1)
    #TODO: option for multiple GP blocks
    for a in range(0, 1):#len(bpy.data.grease_pencil)):
        pencil = bpy.context.scene.grease_pencil#bpy.data.grease_pencil[a]
        #~
        for b in range(0, len(pencil.layers)):
            layer = pencil.layers[b]
            for c in range(0, len(layer.frames)):
                frameList = []
                for i, stroke in enumerate(layer.frames[c].strokes):
                    crv, crv_ob = make_basic_curve()
                    scnobs.link(crv_ob)
                    #~
                    stroke_points = pencil.layers[b].frames[c].strokes[i].points
                    temp_data_list = [ (point.co.x, point.co.y, point.co.z) for point in stroke_points ]
                    #~
                    data_list = []
                    for pp in range(0, len(temp_data_list)):
                        if (pp > 0 and getDistance(temp_data_list[pp], temp_data_list[pp-1]) >= _minDistance):
                            data_list.append(temp_data_list[pp])
                    #~
                    points_to_add = len(data_list)-1
                    #~  
                    flat_list = []
                    for point in data_list: 
                        flat_list.extend(point)
                    #~
                    spline = crv.splines.new(type="BEZIER")
                    spline.bezier_points.add(points_to_add)
                    spline.bezier_points.foreach_set("co", flat_list)
                    #~
                    for point in spline.bezier_points:
                        # * * * * * * * * * * * * * *
                        if (layer.parent):
                            point.co = (layer.parent.matrix_world.inverted() * Vector(point.co)) - layer.parent.location
                        # * * * * * * * * * * * * * *                         
                        point.handle_left = point.handle_right = point.co
                        #point.handle_left_type="AUTO"
                        #point.handle_right_type="AUTO"
                    #~
                    crv_ob.data.extrude = _extrude
                    strokeColor = (0,0,0)
                    try:
                        strokeColor = pencil.layers[b].frames[c].strokes[i].color.color
                    except:
                        strokeColor = (0,0,0)
                        print ("error reading color")
                    mat = bpy.data.materials.new("new_mtl")
                    crv_ob.data.materials.append(mat)
                    crv_ob.data.materials[0].diffuse_color = strokeColor
                    #~
                    bpy.context.scene.objects.active = crv_ob
                    bpy.ops.object.modifier_add(type='SOLIDIFY')
                    bpy.context.object.modifiers["Solidify"].thickness = _extrude * 2
                    bpy.context.object.modifiers["Solidify"].offset = 0
                    #~
                    if (_subd > 0):
                        bpy.ops.object.modifier_add(type='SUBSURF')
                        bpy.context.object.modifiers["Subsurf"].levels = _subd
                        bpy.context.object.modifiers["Subsurf"].render_levels = _subd
                        bpy.context.object.modifiers["Subsurf"].use_opensubdiv = 1
                    #~
                    if (_remesh==True):
                        bpy.ops.object.modifier_add(type="REMESH")
                        bpy.context.object.modifiers["Remesh"].mode = "SMOOTH" #sharp, smooth, blocks
                        bpy.context.object.modifiers["Remesh"].octree_depth = 6
                        bpy.context.object.modifiers["Remesh"].threshold = 0.1                       
                    #~
                    if (_bakeMesh==True):
                        mesh = crv_ob.to_mesh(scene = bpy.context.scene, apply_modifiers = True, settings = 'PREVIEW')
                        meshObj = bpy.data.objects.new(crv_ob.name + "_mesh", mesh)
                        bpy.context.scene.objects.link(meshObj)
                        # TODO fix vertex colors
                        #colorVertices(meshObj, strokeColor, True)                        
                        delete(crv_ob)
                        frameList.append(meshObj)
                    else:
                        frameList.append(crv_ob)
                    if (layer.parent):
                        index = len(frameList)-1
                        frameList[index].parent = layer.parent
                        #~
                    bpy.context.scene.update()
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
    bpy.context.scene.update()

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
        bpy.context.scene.update()
        _child.parent = _parent
        keyTransform(_child, _index)   

def getDistance(v1, v2):
    return sqrt((v1[0] - v2[0])**2 + (v1[1] - v2[1])**2 + (v1[2] - v2[2])**2)

def make_basic_curve():
    crv = bpy.data.curves.new("crv", type="CURVE")
    crv_ob = bpy.data.objects.new("crv_ob", crv)
    return crv, crv_ob

'''
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
        bpy.context.scene.update()
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

