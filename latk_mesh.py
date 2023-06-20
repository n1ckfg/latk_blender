# MESHES / GEOMETRY

import bpy
import bmesh
from scipy.spatial.distance import cdist

from . latk import *
from . latk_tools import *
from . latk_rw import *
from . latk_mtl import *
from . latk_draw import *

def simpleClean(target=None):
    if not target:
        target = s()
    for obj in target:
        setObjectMode()
        setActiveObject(obj)
        setEditMode()
        bpy.ops.mesh.face_make_planar()
        bpy.ops.mesh.tris_convert_to_quads()
        bpy.ops.mesh.delete_loose()

def getBmesh(target=None, update=True):
    if not target:
        target = ss()
    bm = bmesh.new()
    bm.from_mesh(target.data)
    if (update==True):
        bm.verts.ensure_lookup_table()
        bm.faces.ensure_lookup_table()
    return bm

'''
def setBmesh(bm, target=None, update=True)
    if not target:
        target = ss()
    if (update==True):
        bm.verts.ensure_lookup_table()
        bm.faces.ensure_lookup_table()
    bm.to_mesh(target.data)
'''

def updateBmesh(target=None):
    if not target:
        target = getBmesh()
    target.verts.ensure_lookup_table()
    target.faces.ensure_lookup_table()

def getBmeshVertColors(target=None):
    returnVerts = []
    returnColors = []
    if not target:
        target = getBmesh(update=True)
    color_layer = None
    #~
    if not target.loops.layers.color:
        color_layer = target.loops.layers.color.new("color")
    else:
        color_layer = target.loops.layers.color[0]
    #~
    for face in target.faces:
        for loop in face.loops:
            returnVerts.append(loop.vert.co)
            returnColors.append(loop[color_layer])
    return returnVerts, returnColors

def bmeshOp(op="hull", target=None):
    op = op.lower()
    if not target:
        target = ss()
    bm = getBmesh(target)
    if (op == "triangulate"):
        bmesh.ops.triangulate(bm, faces=bm.faces)
    elif (op == "hull"):
        bmesh.ops.convex_hull(bm, input=bm.verts, use_existing_faces=True)
    bm.to_mesh(target.data)

def getVerts(target=None, useWorldSpace=True, useColors=True, useBmesh=False, useModifiers=True):
    if not target:
        target = bpy.context.view_layer.objects.active 
    mesh = None
    if (useModifiers==True):
        #mesh = target.to_mesh(scene=bpy.context.scene, apply_modifiers=True, settings='PREVIEW')
        # https://devtalk.blender.org/t/obj-to-mesh-error-add-corrective-shape-key-py/4020/4
        mesh = target.to_mesh(preserve_all_data_layers=False, depsgraph=None)
    else:
        mesh = target.data
    mat = target.matrix_world
    #~
    if (useBmesh==True):
        bm = bmesh.new()
        bm.from_mesh(mesh)
        return bm.verts
    else:
        verts = []
        #~
        for face in mesh.polygons:
            for idx in face.vertices:
                pointsFace = []
                pointsFace.append(mesh.vertices[idx].co)
            point = Vector((0,0,0))
            for vert in pointsFace:
                point += vert
            point /= len(pointsFace)
            if (useWorldSpace == True):
                # https://blender.stackexchange.com/questions/129473/typeerror-element-wise-multiplication-not-supported-between-matrix-and-vect
                #point = mat * point
                point = mat @ point
            verts.append((point.x, point.z, point.y))
        #~
        if (useColors==True):
            colors = []
            try:
                for i in range(0, len(mesh.vertex_colors[0].data), int(len(mesh.vertex_colors[0].data) / len(verts))):
                    colors.append(mesh.vertex_colors[0].data[i].color)
                return verts, colors
            except:
                return verts, None
        else:
            return verts

getVertices = getVerts

def countVerts(target=None):
    if not target:
        target = bpy.context.view_layer.objects.active 
    return len(getVerts(target)[0])

# TODO decimate does not work, context error
def bakeAllCurvesToMesh(_decimate=0.1):
    start, end = getStartEnd()
    target = matchName("latk_")
    for obj in target:
        applyModifiers(obj)   

def joinObjects(target=None, center=False):
    if not target:
        target = s()
    #~
    bpy.ops.object.select_all(action='DESELECT') 
    target[0].select_set(True)
    bpy.context.view_layer.objects.active = target[0]
    for i in range(1, len(target)):
        target[i].select_set(True)
    #~
    bpy.ops.object.join()
    #~
    #for i in range(1, len(target)):
        #scn.objects.unlink(target[i])
    #~
    gc.collect()
    if (center==True):
        centerOrigin(target[0])
    return target[0]

j = joinObjects

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
    gp = getActiveGp()
    palette = getActivePalette()
    #~
    for b, layer in enumerate(gp.data.layers):
        url = origFileName + "_layer_" + layer.info
        masterGroupList.append(getLayerInfo(layer))
        masterUrlList.append(url)
    #~
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

def gpMesh(_thickness=0.1, _resolution=1, _bevelResolution=0, _bakeMesh=True, _decimate = 0.1, _curveType="nurbs", _useColors=True, _saveLayers=False, _singleFrame=False, _vertexColors=True, _vertexColorName="rgba", _animateFrames=True, _remesh="none", _consolidateMtl=True, _caps=True, _joinMesh=True, _uvStroke=True, _uvFill=True, _usePressure=True, _useHull=True, _solidify=False):
    _remesh = _remesh.lower()
    _curveType = _curveType.lower()
    #~
    if (_joinMesh==True or _remesh != "none"):
        _bakeMesh=True
    #~
    if (_saveLayers==True):
        dn()
    #~    
    origFileName = getFileName()
    masterUrlList = []
    masterGroupList = []
    #masterParentList = []
    #~
    totalStrokes = str(len(getAllStrokes()))
    totalCounter = 0
    start, end = getStartEnd()
    #~
    gp = getActiveGp()
    palette = getActivePalette()
    #~
    '''
    capsObj = None
    if (_caps==True):
        if (_curveType == "nurbs"):
            bpy.ops.curve.primitive_nurbs_circle_add(radius=_thickness)
        else:
            bpy.ops.curve.primitive_bezier_circle_add(radius=_thickness)
        capsObj = ss()
        capsObj.name = "caps_ob"
        capsObj.data.resolution_u = _bevelResolution
    '''
    #~
    for b, layer in enumerate(gp.data.layers):
        checkStrokes = getLayerStrokes(layer.info)
        if (len(checkStrokes) < 1):
            continue
        url = origFileName + "_layer_" + layer.info
        if (layer.lock==False):
            rangeStart = 0
            rangeEnd = len(layer.frames)
            if (_singleFrame==True):
                rangeStart = getActiveFrameNum(layer)
                rangeEnd = rangeStart + 1
            for c in range(rangeStart, rangeEnd):
                frame = layer.frames[c]
                print("\n" + "*** gp layer " + layer.info + "(" + str(b+1) + " of " + str(len(gp.data.layers)) + ") | gp frame " + str(c+1) + " of " + str(rangeEnd) + " ***")
                frameList = []
                for d, stroke in enumerate(frame.strokes):
                    '''
                    origParent = None
                    if (layer.parent):
                        origParent = layer.parent
                        layer.parent = None
                        masterParentList.append(origParent.name)
                    else:
                        masterParentList.append(None)
                    '''
                    #~
                    latk_ob = None
                    thisIsAFill = getStrokeFillAlpha(stroke) > 0.001 or _remesh == "hull" or _remesh == "plane"
                    if (thisIsAFill == True):
                        doHull = False
                        if (_remesh == "hull"):
                            doHull = True
                        latk_ob = createFill(name="latk_" + getLayerInfo(layer) + "_" + str(layer.frames[c].frame_number), useHull=doHull, useUvs=_uvStroke, inputVerts=stroke.points)                        
                    else:
                        coords = getStrokeCoords(stroke)
                        pressures = getStrokePressures(stroke)
                        latk_ob = makeCurve(bake=_bakeMesh, name="latk_" + getLayerInfo(layer) + "_" + str(layer.frames[c].frame_number), coords=coords, pressures=pressures, curveType=_curveType, resolution=_resolution, thickness=_thickness, bevelResolution=_bevelResolution, caps=_caps, useUvs=_uvStroke, usePressure=_usePressure)
                    #centerOrigin(latk_ob)
                    strokeColor = (0.5,0.5,0.5)
                    if (_useColors==True):
                        strokeColor = getStrokeColor(stroke)
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
                    latk_ob.data.materials.append(mat)
                    # ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ 
                    #~   
                    bpy.context.view_layer.objects.active = latk_ob
                    #~
                    if (_bakeMesh == True):
                        if (_caps == False and _solidify == True):
                            bpy.ops.object.modifier_add(type='SOLIDIFY')
                            latk_ob = applyModifiers(latk_ob)
                        if (thisIsAFill == False and _remesh != "hull" and _remesh != "plane"):
                            if (_decimate < 0.999):
                                bpy.ops.object.modifier_add(type='DECIMATE')
                                bpy.context.object.modifiers["Decimate"].ratio = _decimate     
                                latk_ob = applyModifiers(latk_ob)
                            #~
                            if (_remesh != "none" and _remesh != "hull" and _remesh != "plane"):
                                latk_ob = remesher(latk_ob, mode=_remesh)
                            #~
                            #if (getStrokeFillAlpha(stroke) > 0.001):
                                #fill_ob = createFill(stroke.points, useUvs=_uvFill, useHull=_useHull)
                                #joinObjects([latk_ob, fill_ob])
                        #~
                        if (_vertexColors == True):
                            colorVertices(latk_ob, strokeColor, colorName=_vertexColorName) 
                        #~ 
                    frameList.append(latk_ob) 
                    #~
                    if (layer.parent != None):
                        #makeParent([frameList[len(frameList)-1], origParent])
                        makeParent([frameList[len(frameList)-1], layer.parent])
                        #layer.parent = origParent
                    else:
                        makeParent([frameList[len(frameList)-1], gp])
                    # * * * * * * * * * * * * * *
                    bpy.ops.object.select_all(action='DESELECT')

                #~
                for i in range(0, len(frameList)):
                    totalCounter += 1
                    print(frameList[i].name + " | " + str(totalCounter) + " of " + totalStrokes + " total")
                    if (_animateFrames==True):
                        hideFrame(frameList[i], start, True)
                        #~
                        for j in range(start, end):
                            if (j == layer.frames[c].frame_number):
                                hideFrame(frameList[i], j, False)
                                keyTransform(frameList[i], j)
                            elif (c < len(layer.frames)-1 and j > layer.frames[c].frame_number and j < layer.frames[c+1].frame_number):
                                hideFrame(frameList[i], j, False)
                            elif (c != len(layer.frames)-1):
                                hideFrame(frameList[i], j, True)
                #~
                if (_joinMesh==True): 
                    target = matchName("latk_" + getLayerInfo(layer))
                    for i in range(start, end):
                        strokesToJoin = []
                        if (i == layer.frames[c].frame_number):
                            goToFrame(i)
                            for j in range(0, len(target)):
                                if (target[j].hide_get()==False):
                                    strokesToJoin.append(target[j])
                        if (len(strokesToJoin) > 1):
                            print("~ ~ ~ ~ ~ ~ ~ ~ ~")
                            print("* joining " + str(len(strokesToJoin))  + " strokes")
                            joinObjects(strokesToJoin)
                            print("~ ~ ~ ~ ~ ~ ~ ~ ~")
            #~
            if (_saveLayers==True):
                deselect()
                target = matchName("latk_" + getLayerInfo(layer))
                for tt in range(0, len(target)):
                    target[tt].select = True
                print("* baking")
                # * * * * *
                bakeParentToChildByName("latk_" + getLayerInfo(layer))
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
    if (_caps==True):
        try:
            delete(capsObj)
        except:
            pass
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

def gpMeshQ(val = 0.1):
    gpMesh(_decimate=val, _saveLayers=True)

def applySolidify(target=None, _extrude=1):
    if not target:
        target = s()
    for obj in target:
        setActiveObject(obj)
        bpy.ops.object.modifier_add(type='SOLIDIFY')
        bpy.context.object.modifiers["Solidify"].thickness = _extrude * 2
        bpy.context.object.modifiers["Solidify"].offset = 0

def applySubdiv(target=None, _subd=1):
    if (_subd > 0):
        if not target:
            target = s()
        for obj in target:
            setActiveObject(obj)
            bpy.ops.object.modifier_add(type='SUBSURF')
            bpy.context.object.modifiers["Subsurf"].levels = _subd
            bpy.context.object.modifiers["Subsurf"].render_levels = _subd
            try:
                bpy.context.object.modifiers["Subsurf"].use_opensubdiv = 1 # GPU if supported
            except:
                pass

def gpMeshCleanup(target):
    gc.collect()
    removeGroup(target, allGroups=True)
    dn()

def decimateAndBake(target=None, _decimate=0.1):
    if not target:
        target = s()
    for obj in target:
        if (obj.type == "CURVE"):
            setActiveObject(obj)
            bpy.ops.object.modifier_add(type='DECIMATE')
            bpy.context.object.modifiers["Decimate"].ratio = _decimate     
            meshObj = applyModifiers(obj)

def remesher(obj, bake=True, mode="blocks", octree=6, threshold=0.0001, smoothShade=False, removeDisconnected=False):
        bpy.context.view_layer.objects.active  = obj
        bpy.ops.object.modifier_add(type="REMESH")
        bpy.context.object.modifiers["Remesh"].mode = mode.upper() #sharp, smooth, blocks, voxel
        bpy.context.object.modifiers["Remesh"].octree_depth = octree
        bpy.context.object.modifiers["Remesh"].use_smooth_shade = int(smoothShade)
        bpy.context.object.modifiers["Remesh"].use_remove_disconnected = int(removeDisconnected)
        bpy.context.object.modifiers["Remesh"].threshold = threshold
        if (bake==True):
            return applyModifiers(obj)     
        else:
            return obj

# context error
def decimator(target=None, ratio=0.1, bake=True):
    if not target:
        target = ss()
    bpy.context.view_layer.objects.active  = target
    bpy.ops.object.modifier_add(type='DECIMATE')
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
            bpy.context.view_layer.objects.active  = target[i]
            bpy.ops.object.modifier_add(type="BOOLEAN")
            bpy.context.object.modifiers["Boolean"].operation = op.upper()
            bpy.context.object.modifiers["Boolean"].object = target[i-1]
            bpy.ops.object.modifier_apply(modifier="Boolean") #apply_as='DATA', modifier="Boolean")
            delete(target[i-1])
    lastObj = target[len(target)-1]
    lastObj.select_set(True)
    return lastObj

def subsurfMod(target=None):
    if not target:
        target=s()
    returns = []
    for obj in target:
        bpy.context.view_layer.objects.active = obj
        #bpy.ops.object.modifier_add(type="SUBSURF")
        #bpy.ops.object.modifier_apply(modifier="Subsurf") #apply_as='DATA', modifier="Subsurf")

        # Note that for some reason the subdivision modifier needs this different method to successfully apply
        obj.modifiers.new(name="mysubsurf", type="SUBSURF")
        bpy.ops.object.modifier_apply(modifier="mysubsurf")
        returns.append(obj)
    return returns

def smoothMod(target=None):
    if not target:
        target=s()
    returns = []
    for obj in target:
        bpy.context.view_layer.objects.active  = obj
        bpy.ops.object.modifier_add(type="SMOOTH")
        bpy.ops.object.modifier_apply(modifier="Smooth") #apply_as='DATA', modifier="Smooth")
        returns.append(obj)
    return returns

def decimateMod(target=None, _decimate=0.1):
    if not target:
        target = s()
    returns = []
    for obj in target:
        bpy.context.view_layer.objects.active  = obj
        bpy.ops.object.modifier_add(type='DECIMATE')
        bpy.context.object.modifiers["Decimate"].ratio = _decimate     
        bpy.ops.object.modifier_apply(modifier="Decimate") #apply_as='DATA', modifier="Decimate")
        returns.append(obj)
    return returns

def polyCube(pos=(0,0,0), scale=(1,1,1), rot=(0,0,0)):
    bpy.ops.mesh.primitive_cube_add()
    cube = s()[0]
    cube.location = pos
    cube.scale=scale
    cube.rotation_euler=rot
    return cube

def applyModifiers(obj):
    bpy.ops.object.select_all(action='DESELECT')
    #bpy.data.objects[obj.name].hide_set(False)
    bpy.data.objects[obj.name].select_set(True)
    bpy.context.view_layer.objects.active = obj
    bpy.ops.object.convert(target='MESH')
    return obj

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

def curveToStroke(target=None):
    if not target:
        target = s()[0]
    for spline in target.data.splines:
        points = []
        splinePoints = None
        if (spline.type=="BEZIER"):
            splinePoints = spline.bezier_points
        else:
            splinePoints = spline.points
        for point in splinePoints:
            points.append((point.co[0], point.co[2], point.co[1]))
        try:
            drawCoords(points)
        except:
            pass

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
    setActiveObject(target)
    bpy.ops.object.origin_set(type = 'ORIGIN_GEOMETRY')
    deselect()

def setOrigin(target, point):
    bpy.context.view_layer.objects.active  = target
    bpy.context.scene.cursor_location = point
    bpy.ops.object.origin_set(type='ORIGIN_CURSOR')
    #bpy.context.scene.update()

def writeOnMesh(step=1, name="latk"):
    target = matchName(name)
    for i in range (0, len(target), step):
        if (i > len(target)-1):
            i = len(target)-1
        for j in range(i, (i+1)*step):
            if (j > len(target)-1):
                j = len(target)-1
            hideFrame(target[j], 0, True)
            hideFrame(target[j], len(target)-j, False)

def strokeGen1(obj=None, strokeLength=1, strokeGaps=10.0, shuffleOdds=1.0, spreadPoints=0.1, limitPalette=32):
    if not obj:
        obj = ss()
    mesh = obj.data
    mat = obj.matrix_world
    #~
    gp = getActiveGp()
    layer = getActiveLayer()
    if not layer:
        layer = gp.data.layers.new(name="meshToGp")
    frame = getActiveFrame()
    if not frame or frame.frame_number != currentFrame():
        frame = layer.frames.new(currentFrame())
    #~
    images = None
    try:
        images = getUvImages()
    except:
        pass
    #~
    allPoints, allColors = getVerts(target=obj, useWorldSpace=True, useColors=True, useBmesh=False)
    #~
    pointSeqsToAdd = []
    colorsToAdd = []
    for i in range(0, len(allPoints), strokeLength):
        color = None
        if not images:
            try:
                color = allColors[i]
            except:
                color = getColorExplorer(obj, i)
        else:
            try:
                color = getColorExplorer(obj, i, images)
            except:
                color = getColorExplorer(obj, i)
        colorsToAdd.append(color)
        #~
        pointSeq = []
        for j in range(0, strokeLength):
            #point = allPoints[i]
            try:
                point = allPoints[i+j]
                if (len(pointSeq) == 0 or getDistance(pointSeq[len(pointSeq)-1], point) < strokeGaps):
                    pointSeq.append(point)
            except:
                break
        if (len(pointSeq) > 0): 
            pointSeqsToAdd.append(pointSeq)
    for i, pointSeq in enumerate(pointSeqsToAdd):
        color = colorsToAdd[i]
        #createColor(color)
        if (limitPalette == 0):
            createColor(color)
        else:
            createAndMatchColorPalette(color, limitPalette, 5) # num places
        #stroke = frame.strokes.new(getActiveColor().name)
        #stroke.draw_mode = "3DSPACE"
        stroke = frame.strokes.new()
        stroke.display_mode = '3DSPACE'
        stroke.line_width = 10 # adjusted from 100 for 2.93
        stroke.material_index = gp.active_material_index

        stroke.points.add(len(pointSeq))

        if (random.random() < shuffleOdds):
            random.shuffle(pointSeq)

        for j, point in enumerate(pointSeq):    
            x = point[0] + (random.random() * 2.0 * spreadPoints) - spreadPoints
            y = point[2] + (random.random() * 2.0 * spreadPoints) - spreadPoints
            z = point[1] + (random.random() * 2.0 * spreadPoints) - spreadPoints
            pressure = 1.0
            strength = 1.0
            createPoint(stroke, j, (x, y, z), pressure, strength)

def group_points_into_strokes(points, radius, minPointsCount):
    strokeGroups = []
    unassigned_points = set(range(len(points)))

    while len(unassigned_points) > 0:
        strokeGroup = [next(iter(unassigned_points))]
        unassigned_points.remove(strokeGroup[0])

        for i in range(len(points)):
            if i in unassigned_points and cdist([points[i]], [points[strokeGroup[-1]]])[0][0] < radius:
                strokeGroup.append(i)
                unassigned_points.remove(i)

        if (len(strokeGroup) >= minPointsCount):
            strokeGroups.append(strokeGroup)

        print("Found " + str(len(strokeGroups)) + " strokeGroups, " + str(len(unassigned_points)) + " points remaining.")
    return strokeGroups
    
def strokeGen2(obj=None, radius=2, minPointsCount=10, limitPalette=32):
    if not obj:
        obj = ss()
    mesh = obj.data
    mat = obj.matrix_world
    #~
    gp = getActiveGp()
    layer = getActiveLayer()
    if not layer:
        layer = gp.data.layers.new(name="meshToGp")
    frame = getActiveFrame()
    if not frame or frame.frame_number != currentFrame():
        frame = layer.frames.new(currentFrame())
    #~
    images = None
    try:
        images = getUvImages()
    except:
        pass
    #~
    allPoints, allColors = getVerts(target=obj, useWorldSpace=True, useColors=True, useBmesh=False)
    #~
    strokeGroups = group_points_into_strokes(allPoints, radius, minPointsCount)

    for i, strokeGroup in enumerate(strokeGroups):
        colorIndex = strokeGroup[0]

        if not images:
            try:
                color = allColors[colorIndex]
            except:
                color = getColorExplorer(obj, colorIndex)
        else:
            try:
                color = getColorExplorer(obj, colorIndex, images)
            except:
                color = getColorExplorer(obj, colorIndex)
        color = (color[0], color[1], color[2])

        if (limitPalette == 0):
            createColor(color)
        else:
            createAndMatchColorPalette(color, limitPalette, 5) # num places
        
        stroke = frame.strokes.new()
        stroke.display_mode = '3DSPACE'
        stroke.line_width = 10 # adjusted from 100 for 2.93
        stroke.material_index = gp.active_material_index

        stroke.points.add(len(strokeGroup))

        for j, index in enumerate(strokeGroup):    
            point = allPoints[index]
            x = point[0]
            y = point[2]
            z = point[1]
            pressure = 1.0
            strength = 1.0
            createPoint(stroke, j, (x, y, z), pressure, strength)

def makeCurve(coords, pressures=None, resolution=2, thickness=0.1, bevelResolution=1, curveType="bezier", caps=False, name="latk_ob", useUvs=True, usePressure=True, bake=False):
    try:
        coords.insert(0, coords[0])
        pressures.insert(0, pressures[0])
    except:
        pass
    #~
    curveData = bpy.data.curves.new('latk', type='CURVE')
    curveData.dimensions = '3D'
    curveData.fill_mode = 'FULL'
    curveData.resolution_u = resolution
    curveData.bevel_depth = thickness
    curveData.bevel_resolution = bevelResolution
    #~
    if (caps == False):
        curveData.extrude = thickness
        curveData.use_fill_caps = False
    else:
        curveData.bevel_depth = thickness
        curveData.bevel_resolution = bevelResolution
        curveData.use_fill_caps = True
    #~
    # map coords to spline
    curveType=curveType.upper()
    polyline = curveData.splines.new(curveType)
    #~
    if (curveType=="NURBS"):
        polyline.points.add(len(coords))#-1)
        for i, coord in enumerate(coords):
            x,y,z = coord
            polyline.points[i].co = (x, y, z, 1) 
            if (pressures != None and usePressure==True):
                polyline.points[i].radius = pressures[i]   
    elif (curveType=="BEZIER"):
        polyline.bezier_points.add(len(coords))#-1)
        #polyline.bezier_points.foreach_set("co", unpack_list(coords))
        for i, coord in enumerate(coords):
            polyline.bezier_points[i].co = coord   
            if (pressures != None and usePressure==True):
                polyline.bezier_points[i].radius = pressures[i]  
            polyline.bezier_points[i].handle_left = polyline.bezier_points[i].handle_right = polyline.bezier_points[i].co
    #~
    # create object
    latk_ob = bpy.data.objects.new(name, curveData)
    #~
    # attach to scene and validate context
    bpy.context.collection.objects.link(latk_ob)
    bpy.context.view_layer.objects.active = latk_ob
    latk_ob.select_set(True)
    if (useUvs==True):
        try: # 2.83 beta bug
            latk_ob.data.use_uv_as_generated = True
        except:
            pass
    if (bake==True):
        bpy.ops.object.convert(target="MESH")
    return latk_ob

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
        target = ss()
    verts = target.data.vertices
    mat = target.matrix_world
    for vert in verts:
        bpy.ops.mesh.primitive_cube_add()
        cube = ss()
        cube.scale = (cubeScale * target.scale[0],cubeScale * target.scale[1],cubeScale * target.scale[2])
        cube.rotation_euler = target.rotation_euler
        cube.location = mat * vert.co

def randomMetaballs():
    # http://blenderscripting.blogspot.com/2012/09/tripping-metaballs-python.html
    #scene = bpy.context.scene
    #~
    # add metaball object
    mball = bpy.data.metaballs.new("MetaBall")
    obj = bpy.data.objects.new("MetaBallObject", mball)
    bpy.context.collection.objects.link(obj)
    #~
    mball.resolution = 0.2   # View resolution
    mball.render_resolution = 0.02
    #~
    for i in range(20):
        coordinate = tuple(random.uniform(-4,4) for i in range(3))
        element = mball.elements.new()
        element.co = coordinate
        element.radius = 2.0

def createFill(inputVerts, useUvs=False, useHull=False, name="myObject"):
    if (len(inputVerts) < 3):
        return None
    me = bpy.data.meshes.new("myMesh") 
    ob = bpy.data.objects.new(name, me) 
    ob.show_name = True
    bpy.context.collection.objects.link(ob)
    bm = bmesh.new() # create an empty BMesh
    bm.from_mesh(me) # fill it in from a Mesh
    #~
    for vt in inputVerts:
        bm.verts.new(vt.co)
    bm.verts.index_update()
    #~
    if (useHull==False):
        targetFace = None
        if (len(bm.verts) > 2):
            targetFace = bm.faces.new(bm.verts)
        bmesh.ops.triangulate(bm, faces=[targetFace])
    else:
        bmesh.ops.convex_hull(bm, input=bm.verts, use_existing_faces=True)
    # Finish up, write the bmesh back to the mesh
    bm.to_mesh(me)
    #~
    if (useUvs==True):
        ob.select_set(True)
        bpy.context.view_layer.objects.active = ob
        planarUvProject()
    #~
    return ob

def getAlembicCurves(obj=None):
    if not obj:
        obj = ss()
    name = obj.name
    start, end = getStartEnd()
    for i in range(start, end):
        goToFrame(i)
        blankFrame()
        obj = bpy.context.view_layer.objects[obj.name] # make sure obj is still accessible
        splines = obj.data.splines
        for spline in splines:
            points = []
            for point in spline.points:
                points.append(point.co)
            drawCoords(points)
