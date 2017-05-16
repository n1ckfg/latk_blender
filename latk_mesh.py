# 5 of 8. MESHES / GEOMETRY

def joinObjects(target=None, center=False):
    if not target:
        target = s()
    #~
    bpy.ops.object.select_all(action='DESELECT') 
    target[0].select = True
    bpy.context.scene.objects.active = target[0]
    for i in range(1, len(target)):
        #print("****** " + str(bpy.context.scene.objects.active))
        #bpy.context.scene.objects.active.select = True
        target[i].select = True
        #bpy.ops.object.join()
        #bpy.context.scene.objects.unlink(strokesToJoin[sj-1])
    #~
    bpy.ops.object.join()
    #~
    for i in range(1, len(target)):
        try:
            scn.objects.unlink(target[i])
        except:
            pass
        #try:
            #removeObj(target[i].name)
        #except:
            #pass
        #try:
            #target[i].select = True
        #except:
            #pass
    #~
    gc.collect()
    if (center==True):
        centerOrigin(target[0])
    return target[0]

'''
161013
Tried an all-baking approach but it didn't seem to work. 
Going back to parenting with baking for single objects, less elegant but seems to be OK
'''
# https://gist.github.com/pcote/1307658
# http://blender.stackexchange.com/questions/7578/extruding-multiple-curves-at-once
# http://blender.stackexchange.com/questions/24694/query-grease-pencil-strokes-from-python
# https://wiki.blender.org/index.php/Dev:Py/Scripts/Cookbook/Code_snippets/Materials_and_textures
# http://blender.stackexchange.com/questions/58676/add-modifier-to-selected-and-another-to-active-object
# http://blenderscripting.blogspot.ca/2011/05/blender-25-python-bezier-from-list-of.html
# http://blender.stackexchange.com/questions/6750/poly-bezier-curve-from-a-list-of-coordinates
# http://blender.stackexchange.com/questions/7047/apply-transforms-to-linked-objects

def assembleMesh(export=False, createPalette=True):
    origFileName = getFileName()
    masterUrlList = []
    masterGroupList = []
    #~
    #start = bpy.context.scene.frame_start
    #end = bpy.context.scene.frame_end + 1
    #~
    pencil = getActiveGp()
    palette = getActivePalette()
    #~
    for b in range(0, len(pencil.layers)):
        layer = pencil.layers[b]
        #url = origFileName + "_layer" + str(b+1) + "_" + layer.info
        url = origFileName + "_layer_" + layer.info
        masterGroupList.append(getLayerInfo(layer))
        masterUrlList.append(url)
    #~
    #openFile(origFileName)
    readyToSave = True
    for i in range(0, len(masterUrlList)):
        if (export==True):
            dn()
        #~
        try:
            importGroup(getFilePath() + masterUrlList[i] + ".blend", masterGroupList[i], winDir=True)
            print("Imported group " + masterGroupList[i] + ", " + str(i+1) + " of " + str(len(masterGroupList)))
        except:
            readyToSave = False
            print("Error importing group " + masterGroupList[i] + ", " + str(i+1) + " of " + str(len(masterGroupList)))
    #~
    if (createPalette==True):
        createMtlPalette()
    #~
    consolidateGroups()
    #~
    if (readyToSave==True):
        if (export==True):
            exportForUnity()
            print(origFileName + " FBXs exported.")
        else:
            saveFile(origFileName + "_ASSEMBLY")
            print(origFileName + "_ASSEMBLY.blend" + " saved.")
    else:
        if (export==True):
            exportForUnity()
            print(origFileName + " FBXs exported but some groups were missing.")
        else:
            saveFile(origFileName + "_ASSEMBLY")
            print(origFileName + "_ASSEMBLY.blend" + " was saved but some groups were missing.")

def gpMesh(_thickness=0.1, _resolution=1, _bevelResolution=0, _bakeMesh=False, _decimate = 0.1, _curveType="nurbs", _useColors=True, _saveLayers=False, _singleFrame=False, _vertexColors=False, _animateFrames=True, _solidify=False, _subd=0, _remesh=False, _consolidateMtl=True, _caps=True, _joinMesh=True, _uvStroke=False, _uvFill=False):
    if (_joinMesh==True or _remesh==True):
        _bakeMesh=True
    #~
    if (_saveLayers==True):
        dn()
    #~    
    origFileName = getFileName()
    masterUrlList = []
    masterGroupList = []
    masterParentList = []
    #~
    totalStrokes = str(len(getAllStrokes()))
    totalCounter = 0
    start = bpy.context.scene.frame_start
    end = bpy.context.scene.frame_end + 1
    #~
    pencil = getActiveGp()
    palette = getActivePalette()
    #~
    capsObj = None
    if (_caps==True):
        if (_curveType=="nurbs"):
            bpy.ops.curve.primitive_nurbs_circle_add(radius=_thickness)
        else:
            bpy.ops.curve.primitive_bezier_circle_add(radius=_thickness)
        capsObj = ss()
        capsObj.name="caps_ob"
        capsObj.data.resolution_u = _bevelResolution
    #~
    for b in range(0, len(pencil.layers)):
        layer = pencil.layers[b]
        #url = origFileName + "_layer" + str(b+1) + "_" + layer.info
        url = origFileName + "_layer_" + layer.info
        if (layer.lock==False):
            rangeStart = 0
            rangeEnd = len(layer.frames)
            if (_singleFrame==True):
                rangeStart = getActiveFrameNum(layer)
                rangeEnd = rangeStart + 1
            for c in range(rangeStart, rangeEnd):
                print("\n" + "*** gp layer " + str(b+1) + " of " + str(len(pencil.layers)) + " | gp frame " + str(c+1) + " of " + str(rangeEnd) + " ***")
                frameList = []
                for stroke in layer.frames[c].strokes:
                    origParent = None
                    if (layer.parent):
                        origParent = layer.parent
                        layer.parent = None
                        masterParentList.append(origParent.name)
                    else:
                        masterParentList.append(None)
                    #~
                    stroke_points = stroke.points
                    coords = [ (point.co.x, point.co.y, point.co.z) for point in stroke_points ]
                    pressures = [ point.pressure for point in stroke_points ]
                    '''
                    coords = []
                    if (_minDistance > 0.0):
                        for pp in range(0, len(coordsOrig)):
                            if (pp > 0 and getDistance(coordsOrig[pp], coordsOrig[pp-1]) >= _minDistance):
                                coords.append(coordsOrig[pp])
                    else:
                        coords = coordsOrig
                    '''
                    #~
                    crv_ob = makeCurve(name="crv_" + getLayerInfo(layer) + "_" + str(layer.frames[c].frame_number), coords=coords, pressures=pressures, curveType=_curveType, resolution=_resolution, thickness=_thickness, bevelResolution=_bevelResolution, parent=layer.parent, capsObj=capsObj, useUvs=_uvStroke)
                    strokeColor = (0.5,0.5,0.5)
                    if (_useColors==True):
                        strokeColor = palette.colors[stroke.colorname].color
                    # ~ ~ ~ ~ ~ ~ ~ ~ ~ ~
                    mat = None
                    if (_consolidateMtl==False):
                       mat = bpy.data.materials.new("new_mtl")
                       mat.diffuse_color = strokeColor
                    else:
                        for oldMat in bpy.data.materials:
                            if (compareTuple(strokeColor, oldMat.diffuse_color) == True):
                                mat = oldMat
                                break
                        if (mat == None):
                            mat = bpy.data.materials.new("share_mtl")
                            mat.diffuse_color = strokeColor  
                    crv_ob.data.materials.append(mat)
                    # ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ 
                    #~   
                    bpy.context.scene.objects.active = crv_ob
                    #~
                    # solidify replaced by curve bevel
                    if (_solidify==True):
                        bpy.ops.object.modifier_add(type='SOLIDIFY')
                        bpy.context.object.modifiers["Solidify"].thickness = _extrude * 2
                        bpy.context.object.modifiers["Solidify"].offset = 0
                    #~
                    # *** careful, huge speed hit here.
                    if (_subd > 0):
                        bpy.ops.object.modifier_add(type='SUBSURF')
                        bpy.context.object.modifiers["Subsurf"].levels = _subd
                        bpy.context.object.modifiers["Subsurf"].render_levels = _subd
                        try:
                            bpy.context.object.modifiers["Subsurf"].use_opensubdiv = 1 # GPU if supported
                        except:
                            pass
                    #~  
                    if (_bakeMesh==True): #or _remesh==True):
                        bpy.ops.object.modifier_add(type='DECIMATE')
                        bpy.context.object.modifiers["Decimate"].ratio = _decimate     
                        meshObj = applyModifiers(crv_ob)
                        #~
                        if (_remesh==True):
                            meshObj = remesher(meshObj)
                        #~
                        # + + + + + + +
                        if (palette.colors[stroke.colorname].fill_alpha > 0.001):
                            fill_ob = createFill(stroke.points, useUvs=_uvFill)
                            joinObjects([meshObj, fill_ob])
                        # + + + + + + +
                        #~
                        if (_vertexColors==True):
                            colorVertices(meshObj, strokeColor) 
                        #~ 
                        frameList.append(meshObj) 
                    else:
                        frameList.append(crv_ob)    
                    # * * * * * * * * * * * * * *
                    if (origParent != None):
                        makeParent([frameList[len(frameList)-1], origParent])
                        layer.parent = origParent
                    # * * * * * * * * * * * * * *
                    bpy.ops.object.select_all(action='DESELECT')
                #~
                for i in range(0, len(frameList)):
                    totalCounter += 1
                    print(frameList[i].name + " | " + str(totalCounter) + " of " + totalStrokes + " total")
                    if (_animateFrames==True):
                        hideFrame(frameList[i], 0, True)
                        for j in range(start, end):
                            if (j == layer.frames[c].frame_number):
                                hideFrame(frameList[i], j, False)
                                keyTransform(frameList[i], j)
                            elif (c < len(layer.frames)-1 and j > layer.frames[c].frame_number and j < layer.frames[c+1].frame_number):
                                hideFrame(frameList[i], j, False)
                            elif (c != len(layer.frames)-1):
                                hideFrame(frameList[i], j, True)
                #~
                #if (_consolidateMtl==True):
                    #consolidateMtl()
                #~
                if (_joinMesh==True): #and _bakeMesh==True):
                    #target = matchName("crv")
                    target = matchName("crv_" + getLayerInfo(layer))
                    for i in range(start, end):
                        strokesToJoin = []
                        if (i == layer.frames[c].frame_number):
                            goToFrame(i)
                            for j in range(0, len(target)):
                                if (target[j].hide==False):
                                    strokesToJoin.append(target[j])
                        if (len(strokesToJoin) > 1):
                            print("~ ~ ~ ~ ~ ~ ~ ~ ~")
                            print("* joining " + str(len(strokesToJoin))  + " strokes")
                            joinObjects(strokesToJoin)
                            print("~ ~ ~ ~ ~ ~ ~ ~ ~")
            #~            
            '''
            deselect()
            target = matchName("crv")
            for tt in range(0, len(target)):
                target[tt].select = True
            print("* baking")
            bakeParentToChild(start, end)
            print("~ ~ ~ ~ ~ ~ ~ ~ ~")
            '''
            #~
            if (_saveLayers==True):
                deselect()
                #target = matchName("crv")
                target = matchName("crv_" + getLayerInfo(layer))
                for tt in range(0, len(target)):
                    target[tt].select = True
                print("* baking")
                # ~ ~ new ~ ~ 
                '''
                for obj in target:
                    bpy.context.scene.objects.active = obj
                    #print(bpy.context.scene.objects.active.name)
                    bakeParentToChild(start, end)
                '''
                # ~ ~ ~ ~ ~ ~
                # * * * * *
                #bakeParentToChild(start, end)
                # * * * * *
                bakeParentToChildByName("crv_" + getLayerInfo(layer))
                # * * * * *
                print("~ ~ ~ ~ ~ ~ ~ ~ ~")
                #~
                makeGroup(getLayerInfo(layer))
                #~
                masterGroupList.append(getLayerInfo(layer))
                #~
                print("saving to " + url)
                saveFile(url)
                #~
                masterUrlList.append(url)
                #~
                gpMeshCleanup(getLayerInfo(layer))
    #~
    if (_bakeMesh==True and _caps==True and _saveLayers==False):
        delete(capsObj)
    #~
    if (_saveLayers==True):
        openFile(origFileName)
        for i in range(0, len(masterUrlList)):
            importGroup(getFilePath() + masterUrlList[i] + ".blend", masterGroupList[i], winDir=True)
        #~
        if (_consolidateMtl==True):
            createMtlPalette()
        #~
        consolidateGroups()
        #~
        saveFile(origFileName + "_ASSEMBLY")

def gpMeshCleanup(target):
    gc.collect()
    removeGroup(target, allGroups=True)
    dn()

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

# context error
def decimator(target=None, ratio=0.1, bake=True):
    if not target:
        target = ss()
    bpy.context.scene.objects.active = target
    #ctx = fixContext
    bpy.ops.object.modifier_add(type='DECIMATE')
    #restoreContext(ctx)
    bpy.context.object.modifiers["Decimate"].ratio = ratio     
    if (bake == True):
        return applyModifiers(target)
    else:
        return target

# https://blender.stackexchange.com/questions/45004/how-to-make-boolean-modifiers-with-python
def booleanMod(target=None, op="union"):
    if not target:
        target=s()
    for i in range(1, len(target)):
            bpy.context.scene.objects.active = target[i]
            bpy.ops.object.modifier_add(type="BOOLEAN")
            bpy.context.object.modifiers["Boolean"].operation = op.upper()
            bpy.context.object.modifiers["Boolean"].object = target[i-1]
            bpy.ops.object.modifier_apply(apply_as='DATA', modifier="Boolean")
            delete(target[i-1])

def polyCube(pos=(0,0,0), scale=(1,1,1), rot=(0,0,0)):
    bpy.ops.mesh.primitive_cube_add()
    cube = s()[0]
    cube.location = pos
    cube.scale=scale
    cube.rotation_euler=rot
    return cube

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

def getActiveCurvePoints():
    target = s()[0]
    if (target.data.splines[0].type=="BEZIER"):
        return target.data.splines.active.bezier_points
    else:
        return target.data.splines.active.points      

def centerOriginAlt(obj):
    oldLoc = obj.location
    newLoc = getGeometryCenter(obj)
    for vert in obj.data.vertices:
        vert.co[0] -= newLoc[0] - oldLoc[0]
        vert.co[1] -= newLoc[1] - oldLoc[1]
        vert.co[2] -= newLoc[2] - oldLoc[2]
    obj.location = newLoc

def centerOrigin(target=None):
    if not target:
        target = ss()
    deselect()
    target.select = True
    bpy.ops.object.origin_set(type = 'ORIGIN_GEOMETRY')
    deselect()

def setOrigin(target, point):
    bpy.context.scene.objects.active = target
    bpy.context.scene.cursor_location = point
    bpy.ops.object.origin_set(type='ORIGIN_CURSOR')
    #bpy.context.scene.update()

def writeOnMesh(step=1, name="crv"):
    target = matchName(name)
    for i in range (0, len(target), step):
        if (i > len(target)-1):
            i = len(target)-1
        for j in range(i, (i+1)*step):
            if (j > len(target)-1):
                j = len(target)-1
            hideFrame(target[j], 0, True)
            hideFrame(target[j], len(target)-j, False)

def colorVertices(obj, color=(1,0,0), makeMaterial=False):
    # start in object mode
    mesh = obj.data
    #~
    if not mesh.vertex_colors:
        mesh.vertex_colors.new()
    #~
    """
    let us assume for sake of brevity that there is now 
    a vertex color map called  'Col'    
    """
    #~
    #color_layer = mesh.vertex_colors["Col"]
    #~
    # or you could avoid using the color_layer name
    color_layer = mesh.vertex_colors.active  
    #~
    i = 0
    for poly in mesh.polygons:
        for idx in poly.loop_indices:
            #rgb = [random.random() for i in range(3)]
            color_layer.data[i].color = color #rgb
            i += 1
    #~
    if (makeMaterial==True):
        colorVertexCyclesMat(obj)
    #~
    # set to vertex paint mode to see the result
    #if (vertexPaintMode==True):
        #bpy.ops.object.mode_set(mode='VERTEX_PAINT')

def makeCurve(coords, pressures, resolution=2, thickness=0.1, bevelResolution=1, curveType="bezier", parent=None, capsObj=None, name="crv_ob", useUvs=True):
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
    if (capsObj != None):
        curveData.bevel_object = capsObj
        curveData.use_fill_caps = True
    #~
    # map coords to spline
    curveType=curveType.upper()
    polyline = curveData.splines.new(curveType)
    if (curveType=="NURBS"):
        polyline.points.add(len(coords)-1)
        for i, coord in enumerate(coords):
            x,y,z = coord
            polyline.points[i].co = (x, y, z, 1) 
            if (pressures != None):
                polyline.points[i].radius = pressures[i]   
    elif (curveType=="BEZIER"):
        polyline.bezier_points.add(len(coords)-1)
        #polyline.bezier_points.foreach_set("co", unpack_list(coords))
        for i, coord in enumerate(coords):
            polyline.bezier_points[i].co = coord   
            if (pressures != None):
                polyline.bezier_points[i].radius = pressures[i]  
            polyline.bezier_points[i].handle_left = polyline.bezier_points[i].handle_right = polyline.bezier_points[i].co
    #~
    # create object
    crv_ob = bpy.data.objects.new(name, curveData)
    #if (parent != None):
        #crv_ob.location = (parent.location) #object origin  
    #~
    # attach to scene and validate context
    scn = bpy.context.scene
    scn.objects.link(crv_ob)
    scn.objects.active = crv_ob
    crv_ob.select = True
    if (useUvs==True):
        crv_ob.data.use_uv_as_generated = True
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
    me.name = name +'Mesh'
    #~
    # Create mesh from given verts, faces.
    me.from_pydata(verts, [], faces)
    # Update mesh with new data
    me.update()    
    # Set object mode
    bpy.ops.object.mode_set(mode='OBJECT')
    return ob

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

def cubesToVerts(target=None, cubeScale=0.25, posScale=0.01):
    if not target:
        target = s()[0].data.vertices
    for vert in target:
        bpy.ops.mesh.primitive_cube_add()
        cube = s()[0]
        cube.location = vert.co * posScale
        cube.scale = (cubeScale,cubeScale,cubeScale)

def randomMetaballs():
    # http://blenderscripting.blogspot.com/2012/09/tripping-metaballs-python.html
    scene = bpy.context.scene
    #~
    # add metaball object
    mball = bpy.data.metaballs.new("MetaBall")
    obj = bpy.data.objects.new("MetaBallObject", mball)
    scene.objects.link(obj)
    #~
    mball.resolution = 0.2   # View resolution
    mball.render_resolution = 0.02
    #~
    for i in range(20):
        coordinate = tuple(random.uniform(-4,4) for i in range(3))
        element = mball.elements.new()
        element.co = coordinate
        element.radius = 2.0

def createFill(inputVerts, useUvs=False):
    verts = []
    #~
    # Create mesh 
    me = bpy.data.meshes.new("myMesh") 
    #~
    # Create object
    ob = bpy.data.objects.new("myObject", me) 
    #~
    #ob.location = origin
    ob.show_name = True
    #~
    # Link object to scene
    bpy.context.scene.objects.link(ob)
    #~
    # Get a BMesh representation
    bm = bmesh.new() # create an empty BMesh
    bm.from_mesh(me) # fill it in from a Mesh
    #~
    # Hot to create vertices
    for i in range(0, len(inputVerts)):
        vert = bm.verts.new((inputVerts[i].co[0], inputVerts[i].co[1], inputVerts[i].co[2]))
        verts.append(vert)
    '''
    vertex1 = bm.verts.new( (0.0, 0.0, 3.0) )
    vertex2 = bm.verts.new( (2.0, 0.0, 3.0) )
    vertex3 = bm.verts.new( (2.0, 2.0, 3.0) )
    vertex4 = bm.verts.new( (0.0, 2.0, 3.0) )
    '''
    #~
    # Initialize the index values of this sequence.
    bm.verts.index_update()
    #~
    # How to create edges 
    '''
    bm.edges.new( (vertex1, vertex2) )
    bm.edges.new( (vertex2, vertex3) )
    bm.edges.new( (vertex3, vertex4) )
    bm.edges.new( (vertex4, vertex1) )
    '''
    #~
    # How to create a face
    # it's not necessary to create the edges before, I made it only to show how create 
    # edges too
    '''
    bm.faces.new( (vertex1, vertex2, vertex3, vertex4) )
    '''
    if (len(verts) > 2):
        bm.faces.new(verts)
    #~
    # Finish up, write the bmesh back to the mesh
    bm.to_mesh(me)
    #~
    if (useUvs==True):
        ob.select = True
        bpy.context.scene.objects.active = ob
        planarUvProject()
    #~
    return ob

# * * * * * * * * * * * * * * * * * * * * * * * * * *
# * * * * * * * * * * * * * * * * * * * * * * * * * *
# * * * * * * * * * * * * * * * * * * * * * * * * * *

