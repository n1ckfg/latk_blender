# TOOLS

import bpy
import bpy_extras
import re
import parameter_editor
import random
import sys
import gc
import struct
import uuid
import contextlib
import numpy as np
from mathutils import Vector
from collections import defaultdict
from itertools import zip_longest
from operator import itemgetter

from . latk import *

def getFilePath(stripFileName=True):
    name = bpy.context.blend_data.filepath
    if (stripFileName==True):
        name = name[:-len(getFileName(stripExtension=False))]
    return name

def getFileName(stripExtension=True):
    name = bpy.path.basename(bpy.context.blend_data.filepath)
    if (stripExtension==True):
        name = name[:-6]
    return name
    
def showAlert(message="alert", title="Message Box", icon='INFO'):
    def draw(self, context):
        self.layout.label(message)
    bpy.context.window_manager.popup_menu(draw, title=title, icon=icon)

def setObjectMode():
    bpy.ops.object.mode_set(mode='OBJECT')

def setEditMode():
    bpy.ops.object.mode_set(mode='EDIT')

def bakeAnimConstraint(target=None, bakeType="OBJECT"):
    if not target:
        target = s()
    start, end = getStartEnd()
    for obj in target:
        deselect()
        select(obj)
        setActiveObject(obj)
        bpy.ops.nla.bake(frame_start=start, frame_end=end, only_selected=True, visual_keying=True, clear_constraints=True, bake_types={bakeType.upper()})

def scatterObjects(target=None, val=10):
    if not target:
        target = s()
    for obj in target:
        x = (2 * random.random() * val) - val
        y = (2 * random.random() * val) - val
        z = (2 * random.random() * val) - val
        obj.location = (x, y, z)

def matchFills(alpha=None):
    palette = getActivePalette()
    for mtl in palette:
        bpy.data.materials[mtl.name].grease_pencil.fill_color = bpy.data.materials[mtl.name].grease_pencil.color

def resizeToFitGp():
    least = 1
    most = 1
    #~
    gp = getActiveGp()
    for layer in gp.data.layers:
        if (layer.lock == False):
            for frame in layer.frames:
                if frame.frame_number < least:
                    least = frame.frame_number
                elif frame.frame_number > most:
                    most = frame.frame_number
    #~
    setStartEnd(least, most - 1)
    return getStartEnd()

def makeLoop():
    target = matchName("latk")
    origStart, origEnd = getStartEnd()
    setStartEnd(origStart-1, origEnd+1)
    start, end = getStartEnd()
    ctx = fixContext()
    #~
    for obj in target:
        fixContext("VIEW_3D")
        for i in range(start, end):
            goToFrame(i)
            if (obj.hide_get() == False):
                bpy.ops.object.select_all(action='DESELECT')
                obj.select_get() == True
                bpy.context.view_layer.objects.active = obj # last object will be the parent
                fixContext("GRAPH_EDITOR")
                bpy.ops.graph.extrapolation_type(type='MAKE_CYCLIC')
    #~
    returnContext(ctx)
    setStartEnd(origStart, origEnd - 2)

def breakUpStrokes():
    gp = getActiveGp()
    palette = getActivePalette()
    for layer in gp.data.layers:
        for frame in layer.frames:
            tempPoints = []
            tempColorNames = []
            for stroke in frame.strokes:
                for point in stroke.points:
                    tempPoints.append(point)
                    tempColorNames.append(stroke.colorname)
            #~
            for stroke in frame.strokes:
                frame.strokes.remove(stroke)     
            #~  
            for i, point in enumerate(tempPoints):
                stroke = frame.strokes.new(tempColorNames[i])
                #stroke.draw_mode = "3DSPACE"
                stroke.points.add(1)
                coord = point.co
                createPoint(stroke, 0, (coord[0], coord[1], coord[2]), point.pressure, point.strength)

def normalizePoints(minVal=0.0, maxVal=1.0):
    gp = getActiveGp()
    allX = []
    allY = []
    allZ = []
    for layer in gp.data.layers:
        for frame in layer.frames:
            for stroke in frame.strokes:
                for point in stroke.points:
                    coord = point.co
                    allX.append(coord[0])
                    allY.append(coord[1])
                    allZ.append(coord[2])
    allX.sort()
    allY.sort()
    allZ.sort()
    #~
    leastValArray = [ allX[0], allY[0], allZ[0] ]
    mostValArray = [ allX[len(allX)-1], allY[len(allY)-1], allZ[len(allZ)-1] ]
    leastValArray.sort()
    mostValArray.sort()
    leastVal = leastValArray[0]
    mostVal = mostValArray[2]
    valRange = mostVal - leastVal
    #~
    xRange = (allX[len(allX)-1] - allX[0]) / valRange
    yRange = (allY[len(allY)-1] - allY[0]) / valRange
    zRange = (allZ[len(allZ)-1] - allZ[0]) / valRange
    #~
    minValX = minVal * xRange
    minValY = minVal * yRange
    minValZ = minVal * zRange
    maxValX = maxVal * xRange
    maxValY = maxVal * yRange
    maxValZ = maxVal * zRange
    #~
    for layer in gp.data.layers:
        for frame in layer.frames:
            for stroke in frame.strokes:
                for point in stroke.points:  
                    coord = point.co
                    x = remap(coord[0], allX[0], allX[len(allX)-1], minValX, maxValX)
                    y = remap(coord[1], allY[0], allY[len(allY)-1], minValY, maxValY)
                    z = remap(coord[2], allZ[0], allZ[len(allZ)-1], minValZ, maxValZ)
                    point.co = (x,y,z)

def scalePoints(val=0.01):
    strokes = getAllStrokes()
    for stroke in strokes:
        for point in stroke.points:
            point.co = (point.co[0] * val, point.co[1] * val, point.co[2] * val)

def loadJson(url):
    return json.load(open(url))

def gpWorldRoot(name="Empty"):
    bpy.ops.object.empty_add(type="PLAIN_AXES")
    target = ss()
    target.name = name
    layers = getAllLayers()
    for layer in layers:
        layer.parent = target
    return target

def pressureRange(_min=0.1, _max=1.0, _mode="clamp_p"):
    gp = getActiveGp()
    if (_mode == "clamp_p"):
        for layer in gp.data.layers:
            for frame in layer.frames:
                for stroke in frame.strokes:
                    for point in stroke.points:
                        if (point.pressure < _min):
                            point.pressure = _min
                        elif (point.pressure > _max):
                            point.pressure = _max
    elif (_mode == "remap_p"):
        for layer in gp.data.layers:
            for frame in layer.frames:
                for stroke in frame.strokes:
                    for point in stroke.points:
                        point.pressure = remap(point.pressure, 0.0, 1.0, _min, _max)
    elif (_mode == "clamp_s"):
        for layer in gp.data.layers:
            for frame in layer.frames:
                for stroke in frame.strokes:
                    for point in stroke.points:
                        if (point.strength < _min):
                            point.strength = _min
                        elif (point.strength > _max):
                            point.strength = _max
    elif (_mode == "remap_s"):
        for layer in gp.data.layers:
            for frame in layer.frames:
                for stroke in frame.strokes:
                    for point in stroke.points:
                        point.strength = remap(point.strength, 0.0, 1.0, _min, _max)
    
def cameraArray(target=None, hideTarget=True, removeCameras=True, removeLayers=True): 
    if not target:
        target = ss()
    if (removeCameras == True):
        cams = matchName("Camera")
        for cam in cams:
            delete(cam)
    #~
    scene = bpy.context.scene
    render = scene.render
    render.use_multiview = True
    render.views_format = "MULTIVIEW"
    #~
    if (removeLayers == True):
        while (len(render.views) > 1): # can't delete first layer
            render.views.remove(render.views[len(render.views)-1])
        render.views[0].name = "left"
        render.views.new("right")
    render.views["left"].use = False
    render.views["right"].use = False
    #~
    coords = [(target.matrix_world @ v.co) for v in target.data.vertices]
    cams = []
    for coord in coords:
        cam = createCamera()
        cam.location = coord
        cams.append(cam)
    for i, cam in enumerate(cams):
        lookAt(cam, target)
        cam.name = "Camera_" + str(i)
        renView = render.views.new(cam.name)
        renView.camera_suffix = "_" + cam.name.split("_")[1]
        bpy.context.view_layer.objects.active = cam
    parentMultiple(cams, target)
    #~
    if (hideTarget==True):
        target.hide_set(True)
        target.hide_select = False
        target.hide_render = True

def lookAt(looker, lookee):
    deselect()
    select([looker, lookee])
    lookerPos = looker.matrix_world.to_translation()
    lookeePos = lookee.matrix_world.to_translation()
    #~
    direction = lookeePos - lookerPos
    #~
    # point the cameras '-Z' and use its 'Y' as up
    rot_quat = direction.to_track_quat('-Z', 'Y')
    #~
    # assume we're using euler rotation
    looker.rotation_euler = rot_quat.to_euler()

'''
def centerPivot(target=None):
    if not target:
        target = ss()
    bpy.ops.object.origin_set(type="ORIGIN_GEOMETRY")
'''
    
def getLayerInfo(layer):
    return layer.info.split(".")[0]

def getActiveFrameNum(layer=None):
    # assumes layer can have only one active frame
    if not layer:
        layer = getActiveLayer()
    returns = -1
    for i in range(0, len(layer.frames)):
        if (layer.frames[i] == layer.active_frame):
            returns = i
    return returns

def matchWithParent(_child, _parent, _index):
    if (_parent):
        loc, rot, scale = _parent.matrix_world.inverted().decompose()
        _child.location = loc
        #_child.rotation_quaternion = rot
        _child.scale = scale
        _child.parent = _parent
        keyTransform(_child, _index)   

def clearState():
    for ob in bpy.data.objects.values():
        try:
            ob.selected=False
        except:
            pass
    bpy.context.view_layer.objects.active = None

def onionSkin(layers=None, onion=False):
    if not layers:
        layers = getActiveGp().layers
    for layer in layers:
        layer.use_onion_skinning = onion

def bakeParentToChild(start=None, end=None):
    if (start==None and end==None):
        start, end = getStartEnd()
    # https://www.blender.org/api/blender_python_api_2_72_1/bpy.ops.nla.html
    bpy.ops.nla.bake(frame_start=start, frame_end=end, step=1, only_selected=True, visual_keying=True, clear_constraints=True, clear_parents=True, use_current_action=True, bake_types={'OBJECT'})    

def bakeParentToChildByName(name="latk"):
    start, end = getStartEnd()
    target = matchName(name)
    for obj in target:
        bpy.context.view_layer.objects.active = obj
        bakeParentToChild(start, end)

def copyTransform(source, dest):
    dest.location = source.location
    dest.rotation_euler = source.rotation_euler
    dest.scale = source.scale

def getWorldCoords(co=None, camera=None, usePixelCoords=True, useRenderScale=True, flipV=True):
    # https://blender.stackexchange.com/questions/882/how-to-find-image-coordinates-of-the-rendered-vertex
    # Test the function using the active object (which must be a camera)
    # and the 3D cursor as the location to find.
    scene = bpy.context.scene
    if not camera:
        camera = bpy.context.object
    if not co:
        co = bpy.context.scene.cursor_location
    #~
    co_2d = bpy_extras.object_utils.world_to_camera_view(scene, camera, co)
    pixel_2d = None
    #~
    if (usePixelCoords==False):
        print("2D Coords: ", co_2d)
        return co_2d
    else:
        render_size = getSceneResolution(useRenderScale)
        if (flipV==True):
            pixel_2d = (round(co_2d.x * render_size[0]), round(render_size[1] - (co_2d.y * render_size[1])))
        else:
            pixel_2d = (round(co_2d.x * render_size[0]), round(co_2d.y * render_size[1]))
        print("Pixel Coords: ", pixel_2d)
        return pixel_2d

def projectAllToCamera(usePixelCoords=False, discardDepth=False):
    strokes = getAllStrokes()
    camera = getActiveCamera()
    scene = bpy.context.scene
    render_size = getSceneResolution(True)
    #~
    for stroke in strokes:
        for point in stroke.points:
            co = bpy_extras.object_utils.world_to_camera_view(scene, camera, point.co)
            x = co[0]
            y = co[1]
            z = co[2]
            if (usePixelCoords == True):
                x *= render_size[0] * 100.0
                y *= render_size[1] * 100.0
                z *= 255.0
            else:
                if (render_size[0] > render_size[1]):
                    x *= render_size[0] / render_size[1]
                elif (render_size[1] > render_size[0]):
                    y *= render_size[1] / render_size[0]
            if (discardDepth == True):
                point.co = (x, 0, y)
            else:
                point.co = (x, z, y)

def getSceneResolution(useRenderScale=True):
    # https://blender.stackexchange.com/questions/882/how-to-find-image-coordinates-of-the-rendered-vertex
    scene = bpy.context.scene
    render_scale = scene.render.resolution_percentage / 100
    if (useRenderScale==True):
        return (int(scene.render.resolution_x * render_scale), int(scene.render.resolution_y * render_scale))
    else:
        return (int(scene.render.resolution_x), int(scene.render.resolution_y))

def setSceneResolution(width=1920, height=1080, scale=50):
    # https://blender.stackexchange.com/questions/9164/modify-render-settings-for-all-scenes-using-python
    for scene in bpy.data.scenes:
        scene.render.resolution_x = width
        scene.render.resolution_y = height
        scene.render.resolution_percentage = scale
        scene.render.use_border = False

def getSceneFps():
    return bpy.context.scene.render.fps

def setSceneFps(fps=12):
    for scene in bpy.data.scenes:
        scene.render.fps = fps

def deselect():
    bpy.ops.object.select_all(action='DESELECT')

def selectAll():
    bpy.ops.object.select_all(action='SELECT')

# TODO fix so you can find selected group regardless of active object
def getActiveGroup():
    obj = bpy.context.view_layer.objects.active
    for group in bpy.data.groups:
        for groupObj in group.objects:
            if(obj.name == groupObj.name):
                return group
    return None

def getChildren(target=None):
    if not target:
        target=s()[0]
    # https://www.blender.org/forum/viewtopic.php?t=8661
    return [ob for ob in bpy.context.scene.objects if ob.parent == target]

def groupName(name="latk", gName="myGroup"):
    deselect()
    selectName(name)
    makeGroup(gName)

def makeGroup(name="myGroup", newGroup=True):
    if (newGroup==True):
        bpy.ops.group.create(name=name)
    else:
        bpy.ops.group_link(group=name)

def deleteGroup(name="myGroup"):
    group = bpy.data.groups[name]
    for obj in group.objects:
        delete(obj)
    removeGroup(name)

def deleteGroups(name=["myGroup"]):
    for n in name:
        deleteGroup(n)

def preserveGroups(name=["myGroup"]):
    allNames = []
    for group in bpy.data.groups:
        allNames.append(group.name)
    for aN in allNames:
        doDelete = True
        for n in name:
            if (aN == n):
                doDelete = False
        if (doDelete == True):
            deleteGroup(aN)

def preserveGroupName(name="myGroup"):
    allNames = []
    for group in bpy.data.groups:
        allNames.append(group.name)
    for aN in allNames:
        doDelete = True
        for n in name:
            if re.match(r'^' + n + '', aN):
                doDelete = False
        if (doDelete == True):
            deleteGroup(aN)

def deleteGroupName(name="myGroup"):
    allNames = []
    for group in bpy.data.groups:
        allNames.append(group.name)
    for aN in allNames:
        doDelete = False
        for n in name:
            if re.match(r'^' + n + '', aN):
                doDelete = True
        if (doDelete == True):
            deleteGroup(aN)

def removeGroup(name="myGroup", allGroups=False):
    if (allGroups==False):
        group = bpy.data.groups[name]
        group.user_clear()
        bpy.data.groups.remove(group) 
        #~
    else:
        for group in bpy.data.groups:
            group.user_clear()
            bpy.data.groups.remove(group)   

def importGroup(path, name, winDir=False):
    importAppend(path, "Group", name, winDir)

def removeObj(name="myObj", allObjs=False):
    if (allObjs==False):
        obj = bpy.data.objects[name]
        obj.user_clear()
        bpy.data.objects.remove(obj) 
    else:
        for obj in bpy.data.objects:
            obj.user_clear()
            bpy.data.objects.remove(obj)  
    refresh()

def deleteDuplicateStrokes(fromAllFrames = False):
    strokes = getSelectedStrokes()
    checkPoints = []
    for i in range(0, len(strokes)):
        checkPoints.append(sumPoints(strokes[i]))
    for i in range(0, len(strokes)):
        for j in range(0, len(strokes)):
            try:
                if ( j != i and checkPoints[i] == checkPoints[j]):
                    bpy.ops.object.select_all(action='DESELECT')
                    strokes[i].select = True
                    deleteSelected()
            except:
                pass

def getEmptyStrokes(_strokes, _minPoints=0):
    returns = []
    for stroke in _strokes:
        if (len(stroke.points) <= _minPoints):
            returns.append(stroke)
    print("Found " + str(len(returns)) + " empty strokes.")
    return returns

def cleanEmptyStrokes(_strokes, _minPoints=0):
    target = getEmptyStrokes(_strokes, _minPoints)
    deleteStrokes(target)

def consolidateGroups():
    wholeNames = []
    mergeNames = []
    for group in bpy.data.groups:
        if("." in group.name):
            mergeNames.append(group.name)
        else:
            wholeNames.append(group.name)
    for sourceName in mergeNames:
        sourceGroup = bpy.data.groups[sourceName]
        destGroup = None
        for destName in wholeNames:
            if (sourceName.split(".")[0] == destName):
                destGroup = bpy.data.groups[destName]
                break
        if (destGroup==None):
            break
        else:
            for obj in sourceGroup.objects:
                try:
                    destGroup.objects.link(obj)
                except:
                    pass
            removeGroup(sourceName)
    print(mergeNames)
    print(wholeNames)


def sumPoints(stroke):
    x = 0
    y = 0
    z = 0
    for point in stroke.points:
        co = point.co
        x += co[0]
        y += co[1]
        z += co[2]
    return roundVal(x + y + z, 5)

def rename(target=None, name="Untitled"):
    if not target:
        target = ss()
    target.name = name
    return target.name

def getUniqueName(name):
    # if the name is already unique, return it
    searchNames = matchName("name")
    if (len(searchNames) == 0):
        return name
    else:
        # find the trailing digit in the name
        trailingDigit = re.sub('.*?([0-9]*)$',r'\1',name)
        
        # create default variables for newDigit and shortname
        # in case there is no trailing digit (ie: "pSphere")
        newDigit = 1
        shortname = name
        
        if(trailingDigit):
            # increment the last digit and find the shortname using the length
            # of the trailing digit as a reference for how much to trim
            newDigit = int(trailingDigit)+1
            shortname = name[:-len(trailingDigit)]
        
        # create the new name
        newName = shortname+str(newDigit)

        # recursively run through the function until a unique name is reached and returned
        return getUniqueName(newName)

def renameCurves(name="mesh", nameMesh="latk_ob_mesh", nameCurve="latk"):
    target = matchName(nameMesh)
    for i in range(0, len(target)):
        target[i].name = name + "_" + str(i)

def deleteUnparentedCurves(name="latk"):
    target = matchName(name)
    toDelete = []
    for i in range(0, len(target)):
        if (target[i].parent==None):
            toDelete.append(target[i])
    print(str(len(toDelete)) + " objects selected for deletion.")
    for i in range(0, len(toDelete)):
        delete(toDelete[i])

def currentFrame(target=None):
    if not target:
        return bpy.context.scene.frame_current
    else:
        goToFrame(target)

def getDistanceAlt(v1, v2):
    return np.sqrt( (v1[0] - v2[0])**2 + (v1[1] - v2[1])**2 + (v1[2] - v2[2])**2)

def getDistance(point1, point2):
    point1 = np.array(point1)
    point2 = np.array(point2)
    return np.linalg.norm(point1 - point2)

def hitDetect3D(p1, p2, hitbox=0.01):
    #if (p1[0] + hitbox >= p2[0] - hitbox and p1[0] - hitbox <= p2[0] + hitbox and p1[1] + hitbox >= p2[1] - hitbox and p1[1] - hitbox <= p2[1] + hitbox and p1[2] + hitbox >= p2[2] - hitbox and p1[2] - hitbox <= p2[2] + hitbox):
    if (getDistance(p1, p2) <= hitbox):
        return True
    else:
        return False

def getVertices(obj, fast=False):
    if (fast == True):
        count = len(obj.data.vertices)
        shape = (count, 3)
        verts = np.empty(count*3, dtype=np.float64)  
        obj.data.vertices.foreach_get('co', verts)  
        verts.shape = shape  
        return verts
    else:
        return np.array([v.co for v in obj.data.vertices])  

def getVertsAndColors(target=None, useWorldSpace=True, useColors=True, useBmesh=False, useModifiers=True):
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
            verts.append(point)
        '''
        verts = None
        if (useWorldSpace == True):
            verts = np.array([mat @ v.co for v in mesh.vertices])  
        else:
            verts = np.array([v.co for v in mesh.vertices])  
        '''
        #~
        if (useColors==True):
            colors = []
            try:
                for i in range(0, len(mesh.vertex_colors[0].data), int(len(mesh.vertex_colors[0].data) / len(verts))):
                #for i in range(0, len(mesh.vertex_colors[0].data)):
                    colors.append(mesh.vertex_colors[0].data[i].color)
                return verts, colors
            except:
                return verts, None
        else:
            return verts

def getEdges(obj):
    count = len(obj.data.edges)
    shape = (count, 2)
    edges = np.empty(count*2, dtype=int)  
    obj.data.edges.foreach_get('vertices', edges)  
    edges.shape = shape  
    return edges

def getFaces(obj):
    return np.array([f.vertices for f in obj.data.polygons])

def getAvgSize(obj):
    returns = (obj.dimensions.x + obj.dimensions.y + obj.dimensions.z) / 3.0
    return returns

def normalizeMesh(vertices):
    magnitudes = np.linalg.norm(vertices, axis=1)
    return vertices / magnitudes[:, np.newaxis]

def parentMultiple(target, root, fixTransforms=True):
    bpy.context.view_layer.objects.active = root # last object will be the parent
    bpy.ops.object.select_all(action='DESELECT')
    for i in range(0, len(target)):
        target[i].select_set(True)
    if (fixTransforms==True):
        bpy.ops.object.parent_set(type='OBJECT', xmirror=False, keep_transform=False) 
    else:
        bpy.ops.object.parent_set(type='OBJECT', xmirror=False, keep_transform=True)

def makeParent(target=None, unParent=False, fixTransforms=True):
    if not target:
        target = s()
    if (unParent==True):
        for obj in target:
            if (obj.parent != None):
                bpy.context.view_layer.objects.active=obj
                if (fixTransforms==True):
                    bpy.ops.object.parent_clear(type='CLEAR_KEEP_TRANSFORM')
                else:
                    bpy.ops.object.parent_clear()
    else:
        # http://blender.stackexchange.com/questions/9200/make-object-a-a-parent-of-object-b-via-python
        for i in range(0, len(target)-1):
            target[i].select_set(True)
            if (fixTransforms==True):
                copyTransform(target[len(target)-1], target[i])
        bpy.context.view_layer.objects.active = target[len(target)-1] # last object will be the parent
        #~
        if (fixTransforms==True):
            bpy.ops.object.parent_set(type='OBJECT', xmirror=False, keep_transform=False) 
        else:   
            bpy.ops.object.parent_set(type='OBJECT', xmirror=False, keep_transform=True) 

def up():
    makeParent(unParent=True)

def makeRoot():
    root = addLocator()
    target = matchName("latk")
    parentMultiple(target, root)
    return root

def makeLayerParent():
    layer = getActiveLayer()
    empty = bpy.data.objects.new(layer.info, None)
    bpy.context.scene.objects.link(empty)
    bpy.context.scene.update()
    try:
        empty.location = getSelectedPoint().co
    except:
        empty.location = (0,0,0)
    bpy.context.scene.update()
    origLoc = empty.matrix_world.translation
    layer.parent = empty
    empty.location = origLoc
    return empty

def keyTransform(_obj, _frame):
    _obj.keyframe_insert(data_path="location", frame=_frame) 
    _obj.keyframe_insert(data_path="rotation_euler", frame=_frame) 
    _obj.keyframe_insert(data_path="scale", frame=_frame)

def k():
    target = ss()
    for obj in target:
        keyTransform(obj, currentFrame())

def keyMatrix(_obj, _frame):
    _obj.keyframe_insert(data_path="matrix_world", frame=_frame) 

def select(target=None):
    if not target:
        target=bpy.context.selected_objects;
    print("selected " + str(target))
    return target

s = select

def ss():
    returns = select()
    if (len(returns) > 0):
        return returns[0]
    else:
        return None

def delete(_obj=None):
    if not _obj:
        _obj = ss()
    bpy.ops.object.select_all(action='DESELECT')
    # https://blender.stackexchange.com/questions/140481/blender-2-8-object-object-has-no-attribute-hide
    _obj.hide_viewport = False
    _obj.hide_set(False)
    _obj.select_set(True)
    bpy.ops.object.delete()
    gc.collect()

d = delete

def refresh():
    bpy.context.view_layer.update()

def remapAlt(value, min1, max1, min2, max2):
    range1 = max1 - min1
    range2 = max2 - min2
    valueScaled = float(value - min1) / float(range1)
    return min2 + (valueScaled * range2)

def remap(value, min1, max1, min2, max2):
    return np.interp(value,[min1, max1],[min2, max2])

def remapInt(value, min1, max1, min2, max2):
    return int(remap(value, min1, max1, min2, max2))

def matchName(_name):
    returns = []
    for i in range(0, len(bpy.context.scene.objects)):
        obj = bpy.context.scene.objects[i]
        if re.match(r'^' + str(_name) + '', obj.name): # curve object
            returns.append(obj)
    return returns

def selectName(_name="latk"):
    target = matchName(_name)
    deselect()
    for obj in target:
        obj.select = True

def deleteName(_name="latk"):
    target = matchName(_name)
    for obj in target:
        try:
            delete(obj)
        except:
            print("error deleting " + obj.name)

def dn():
    deleteName(_name="latk_ob")
    deleteName(_name="caps_ob")

def getKeyByIndex(data, index=0):
    for i, key in enumerate(data.keys()):
        if (i == index):
            return key

def roundVal(a, b):
    formatter = "{0:." + str(b) + "f}"
    return formatter.format(a)

def roundValInt(a):
    formatter = "{0:." + str(0) + "f}"
    return int(formatter.format(a))

def frame_to_time(frame_number):
    scene = bpy.context.scene
    fps = scene.render.fps
    fps_base = scene.render.fps_base
    raw_time = (frame_number - 1) / fps
    return round(raw_time, 3)

def bakeFrames():
    start = bpy.context.scene.frame_start
    end = bpy.context.scene.frame_end + 1
    scene = bpy.context.scene
    gp = getActiveGp()
    for layer in gp.data.layers:   
        for i in range(start, end):
            try:
                layer.frames.new(i)
            except:
                print ("Frame " + str(i) + " already exists.")

def getStartEnd(pad=True):
    start = bpy.context.scene.frame_start
    end = None
    if (pad==True):
        end = bpy.context.scene.frame_end + 1
    else:
        end = bpy.context.scene.frame_end
    return start, end

def setStartEnd(start, end, pad=True):
    if (pad==True):
        end += 1
    bpy.context.scene.frame_start = start
    bpy.context.scene.frame_end = end
    return start, end

def copyFrame(source, dest, limit=None):
    scene = bpy.context.scene
    layer = getActiveLayer()  
    #.
    frameSource = layer.frames[source]
    frameDest = layer.frames[dest]
    if not limit:
        limit = len(frameSource.strokes)
    for j in range(0, limit):
        scene.frame_set(source)
        strokeSource = frameSource.strokes[j]
        scene.frame_set(dest)
        strokeDest = frameDest.strokes.new(strokeSource.color.name)
        # either of ('SCREEN', '3DSPACE', '2DSPACE', '2DIMAGE')
        strokeDest.draw_mode = '3DSPACE'
        strokeDest.points.add(len(strokeSource.points))
        for l in range(0, len(strokeSource.points)):
            strokeDest.points[l].co = strokeSource.points[l].co

def copyFramePoints(source, dest, limit=None, pointsPercentage=1):
    scene = bpy.context.scene
    layer = getActiveLayer()  
    #.
    frameSource = layer.frames[source]
    frameDest = layer.frames[dest]
    if not limit:
        limit = len(frameSource.strokes)
    for j in range(0, limit):
        scene.frame_set(source)
        strokeSource = frameSource.strokes[j]
        scene.frame_set(dest)
        strokeDest = frameDest.strokes.new(strokeSource.color.name)
        # either of ('SCREEN', '3DSPACE', '2DSPACE', '2DIMAGE')
        strokeDest.draw_mode = '3DSPACE'
        if (j>=limit-1):
            newVal = roundValInt(len(strokeSource.points) * pointsPercentage)
            strokeDest.points.add(newVal)
            for l in range(0, newVal):
                strokeDest.points[l].co = strokeSource.points[l].co
        else:
            strokeDest.points.add(len(strokeSource.points))
            for l in range(0, len(strokeSource.points)):
                strokeDest.points[l].co = strokeSource.points[l].co

def addLocator(target=None):
    if not target:
        target = ss()
    empty = bpy.data.objects.new("Empty", None)
    bpy.context.scene.objects.link(empty)
    bpy.context.scene.update()
    if (target != None):
        empty.location = target.location
    return empty

def createCamera():
    # https://blenderartists.org/forum/showthread.php?312512-how-to-add-an-empty-and-a-camera-using-python-script
   cam = bpy.data.cameras.new("Camera")
   cam_ob = bpy.data.objects.new("Camera", cam)
   bpy.context.collection.objects.link(cam_ob)
   return cam_ob

def getActiveCamera():
    # https://blender.stackexchange.com/questions/8245/find-active-camera-from-python
    cam_ob = bpy.context.scene.camera
    #~
    if cam_ob is None:
        print("no scene camera")
        return None
    elif cam_ob.type == 'CAMERA':
        print("regular scene cam")
        return cam_ob
    else:
        print("%s object as camera" % cam_ob.type)
        ob = bpy.context.object
        if ob is not None and ob.type == 'CAMERA':
            #print("Active camera object")
            return ob
        else:
            return None

def goToFrame(_index):
    origFrame = bpy.context.scene.frame_current
    bpy.context.scene.frame_current = _index
    bpy.context.scene.frame_set(_index)
    refresh()
    print("Moved from timeline frame " + str(origFrame) + " to " + str(_index))
    return bpy.context.scene.frame_current

gotoFrame = goToFrame

def hideFrame(_obj, _frame, _hide):
    _obj.hide_viewport = _hide
    _obj.hide_render = _hide
    _obj.keyframe_insert(data_path="hide_viewport", frame=_frame) 
    _obj.keyframe_insert(data_path="hide_render", frame=_frame) 

def hideFrameByScale(_obj, _frame, _hide, showScaleVal=1, hideScaleVal=0.0001):
    #showScaleVal = 1
    #hideScaleVal = 0.001
    if (_hide == True):
        _obj.scale = [hideScaleVal, hideScaleVal, hideScaleVal]
    else:
        _obj.scale = [showScaleVal, showScaleVal, showScaleVal]
    #_obj.keyframe_insert(data_path="location", frame=_frame)
    #_obj.keyframe_insert(data_path="rotation_quaternion", frame=_frame)
    _obj.keyframe_insert(data_path="scale", frame=_frame)
    fcurves = _obj.animation_data.action.fcurves
    for fcurve in fcurves:
        for kf in fcurve.keyframe_points:
            kf.interpolation = 'CONSTANT'
    '''
    if (_obj.hide == True):
        _obj.hide = False
        _obj.keyframe_insert(data_path="hide", frame=_frame)
    if (_obj.hide_render == True):
        _obj.hide_render = False
        _obj.keyframe_insert(data_path="hide_render", frame=_frame)
    '''

def hideFramesByNumber(target=None):
    if not target:
        target = matchName("latk_")
    start, end = getStartEnd()
    for i in range(start, end):
        goToFrame(i)
        for j in range(0, len(target)):
            hideFrame(target[j], i, True)    
    #~
    for i in range(start, end):
        goToFrame(i)
        for j in range(0, len(target)):
            index = getFrameNumFromName(target[j].name)
            print(index)
            if (currentFrame() == index):
                hideFrame(target[j], i, False)

def getFrameNumFromName(target=None, separator="."):
    try:
        temp1 = target.split(separator)
        temp2 = "";
        last = len(temp1)-1
        for i in range(0, last):
            temp2 += temp1[i]
        index = int(temp1[last])
        return index
    except:
        return None

def hideFramesByScale(target=None):
    if not target:
        target = matchName("latk_")
    start, end = getStartEnd()
    for i in range(start, end):
        goToFrame(i)
        for j in range(0, len(target)):
            if (target[j].hide_viewport == False):
                hideFrameByScale(target[j], i, False)
    #turn off all hide keyframes
    for i in range(start, end):
        goToFrame(i)
        for j in range(0, len(target)):
            if (target[j].hide_viewport == True):
                hideFrameByScale(target[j], i, True)
                hideFrame(target[j], i, False) 
    
def deleteAnimationPath(target=None, paths=["hide", "hide_render"]):
    if not target:
        target = ss()
    fcurves = target.animation_data.action.fcurves
    curves_to_remove = []
    for path in paths:
        for i, curve in enumerate(fcurves):
            if (curve.data_path == path):
                curves_to_remove.append(i)
    for i in range(0, len(curves_to_remove)):
        fcurves.remove(fcurves[i])


def showHide(obj, hide, keyframe=False, frame=None):
    obj.hide_set(hide)
    obj.hide_render = hide

def showHideChildren(hide):
    target = getChildren()
    for obj in target:
        showHide(obj, hide)

def rgbToHex(color, normalized=False):
    if (normalized==True):
        return "#%02x%02x%02x" % (int(color[0] * 255.0), int(color[1] * 255.0), int(color[2] * 255.0))
    else:
        return "#%02x%02x%02x" % (int(color[0]), int(color[1]), int(color[2]))

def rgbIntToTuple(rgbint, normalized=False):
    rgbVals = [ rgbint // 256 // 256 % 256, rgbint // 256 % 256, rgbint % 256 ]
    if (normalized == True):
        for i in range(0, len(rgbVals)):
            c = float(rgbVals[i]) / 255.0
            rgbVals[i] = c;
    return (rgbVals[2], rgbVals[1], rgbVals[0])

def normRgbToHex(color):
    return rgbToHex(color, normalized=True)

def hexToRgb(color, normalized=False):
    hex = color.lstrip('#')
    hlen = len(hex)
    rgb = tuple(int(hex[i:i+hlen // 3], 16) for i in range(0, hlen, hlen // 3))
    if (normalized==True):
        return (rgb[0]/255.0, rgb[1]/255.0, rgb[2]/255.0)
    else:
        return rgb

def normHexToRgb(color):
    return hexToRgb(color, normalized=True)

def moveShot(start, end, x, y, z):
    gp = bpy.context.scene.grease_pencil
    target = (start, end)
    for g in range(target[0], target[1]+1):
        for f in range(0, len(gp.data.layers)):
            layer = gp.data.layers[f]
            currentFrame = g
            for i in range(0, len(layer.frames[currentFrame].strokes)):
                for j in range(0, len(layer.frames[currentFrame].strokes[i].points)):
                    layer.frames[currentFrame].strokes[i].points[j].co.x += x
                    layer.frames[currentFrame].strokes[i].points[j].co.y += y
                    layer.frames[currentFrame].strokes[i].points[j].co.z += z

def fixContext(ctx="VIEW_3D"):
    original_type = bpy.context.area.type
    bpy.context.area.type = ctx
    return original_type

def returnContext(original_type):
    bpy.context.area.type = original_type

def alignCamera():
    original_type = bpy.context.area.type
    print("Current context: " + original_type)
    bpy.context.area.type = "VIEW_3D"
    #~
    # strokes, points, frame
    bpy.ops.view3d.camera_to_view()
    #~
    bpy.context.area.type = original_type

a = alignCamera

def getChildren(myObject, name=None): 
    children = [] 
    for ob in bpy.data.objects: 
        if ob.parent == myObject: 
            if name == None or ob.name.startswith(name):
                children.append(ob) 
    return children 

# ~ ~ ~ ~ ~ ~ grease pencil ~ ~ ~ ~ ~ ~
def getActiveGp(_name=None):
    if not _name:
        try:
            gp = ss()
            if (gp.type == "GPENCIL"):
                return gp
        except:
            pass
    else:
        for obj in bpy.data.objects:
            if (obj.name == _name and obj.type == "GPENCIL"):
                return obj
    for obj in bpy.data.objects:
        if (obj.type == "GPENCIL"):
            return obj
    return createGp()

def createGp(_name=None, _newMaterial=True, _newLayer=False):
    bpy.ops.object.gpencil_add(type="EMPTY")
    bpy.data.grease_pencils[len(bpy.data.grease_pencils)-1].stroke_depth_order = "3D"  
    
    if (_newMaterial == True):
        createGpMaterial()
    
    if (_newLayer == True):
        newLayer()
    
    gp = ss()
    return gp

def forceDrawMode():
    #https://blenderartists.org/forum/showthread.php?255425-How-to-use-quot-bpy-ops-gpencil-draw()-quot
    ctx = fixContext()
    returns = bpy.ops.gpencil.draw(mode="DRAW")
    returnContext(ctx)
    return returns

def initGp():
    # https://blender.stackexchange.com/questions/48992/how-to-add-points-to-a-grease-pencil-stroke-or-make-new-one-with-python-script
    scene = bpy.context.scene
    if not scene.grease_pencil:
        a = [ a for a in bpy.context.screen.areas if a.type == 'VIEW_3D' ][0]
        override = {
            'scene'         : scene,
            'screen'        : bpy.context.screen,
            'object'        : bpy.context.object,
            'area'          : a,
            'region'        : a.regions[0],
            'window'        : bpy.context.window,
            'active_object' : bpy.context.object
        }
        bpy.ops.gpencil.data_add(override)
    return scene.grease_pencil

def getActivePalette():
    gp = getActiveGp()
    return gp.data.materials

def getActiveGpMtl():
    gp = getActiveGp()
    palette = getActivePalette()
    return palette[gp.active_material_index].grease_pencil

def getActiveColor():
    mtl = getActiveGpMtl()
    return mtl.color

def getActiveFillColor():
    mtl = getActiveGpMtl()
    return mtl.fill_color

def getActiveLayer():
    gp = getActiveGp()
    if (len(gp.data.layers) < 1):
        bpy.ops.gpencil.layer_add()
    layer = gp.data.layers.active
    return layer

def setActiveLayer(name="Layer"):
    gp = getActiveGp()
    gp.data.layers.active = gp.data.layers[name]
    return gp.data.layers.active

def deleteLayer(name=None):
    gp = getActiveGp()
    if not name:
        name = gp.data.layers.active.info
    gp.data.layers.remove(gp.data.layers[name])

def duplicateLayer():
    ctx = fixContext()
    bpy.ops.gpencil.layer_duplicate()
    returnContext(ctx)
    return getActiveLayer()

def splitLayer(splitNum=None):
    if not splitNum:
        splitNum = getActiveFrameTimelineNum()
    layer1 = getActiveLayer()
    layer2 = duplicateLayer()
    #~
    for frame in layer1.frames:
        if (frame.frame_number>=splitNum):
            layer1.frames.remove(frame)
    for frame in layer2.frames:
        if (frame.frame_number<splitNum):
            layer2.frames.remove(frame)
    #~
    if (len(layer2.frames) > 0):
        lastNum = layer2.frames[0].frame_number
        # cap the new layers with blank frames
        blankFrame(layer1, lastNum)
        blankFrame(layer2, lastNum-1)
        return layer2
    else:
        cleanEmptyLayers()
        return None

spl = splitLayer

def blankFrame(layer=None, frame=None):
    if not layer:
        layer = getActiveLayer()
    if not frame:
        frame = bpy.context.scene.frame_current
    try:
        layer.frames.new(frame)
    except:
        pass

'''
def getActiveFrameNum():
    returns = -1
    layer = getActiveLayer()
    for i, frame in enumerate(layer.frames):
        if (frame == layer.active_frame):
            returns = i
    return returns
'''

def checkForZero(v, hitRange=0.005):
    if (abs(v[0]) < hitRange and abs(v[1]) < hitRange and abs(v[2]) < hitRange):
        return True
    else:
        return False

def getActiveFrameTimelineNum():
    return getActiveLayer().frames[getActiveFrameNum()].frame_number

def checkLayersAboveFrameLimit(limit=20):
    gp = getActiveGp()
    returns = []
    print("~ ~ ~ ~")
    for layer in gp.data.layers:
        if (len(layer.frames) > limit + 1): # accounting for extra end cap frame
            returns.append(layer)
            print("layer " + layer.info + " is over limit " + str(limit) + " with " + str(len(layer.frames)) + " frames.")
    print(" - - - " + str(len(returns)) + " total layers over limit.")
    print("~ ~ ~ ~")
    return returns

cplf = checkLayersAboveFrameLimit

def splitLayersAboveFrameLimit(limit=20):
    layers = checkLayersAboveFrameLimit(limit)
    #~
    if (len(layers) <= 0):
        return
    for layer in layers:
        setActiveLayer(layer.info)
        for i in range(0, int(getLayerLength()/limit)):
            currentLayer = getActiveLayer()
            print("* " + currentLayer.info + ": pass " + str(i))
            if (getLayerLength() < limit or currentLayer.lock==True):
                break
            goToFrame(currentLayer.frames[limit].frame_number)
            setActiveFrame(currentLayer.frames[limit].frame_number)
            splitLayer(currentLayer.frames[limit].frame_number)
            print("Split layer " + currentLayer.info + " with " + str(len(currentLayer.frames)) + " frames.")

splf = splitLayersAboveFrameLimit

def getLayerLength(name=None):
    layer = None
    if not name:
        layer = getActiveLayer()
    else:
        layer = getActiveGp().layers[name]
    return len(layer.frames)

def cleanEmptyLayers():
    gp = getActiveGp()
    for layer in gp.data.layers:
        if (len(layer.frames) == 0):
            gp.data.layers.remove(layer)

def clearLayers():
    gp = getActiveGp()
    for layer in gp.data.layers:
        gp.data.layers.remove(layer)

def clearPalette():
    palette = getActivePalette()
    for color in palette.colors:
        palette.colors.remove(color)

def clearAll():
    clearLayers()
    clearPalette()

def createColor(_color=(0,0,0)):
    if (len(_color) == 3):
        _color = (_color[0], _color[1], _color[2], 1)
    gp = getActiveGp()
    palette = getActivePalette()
    places = 7
    #~
    for i in range(0, len(palette)):
        color = palette[i].grease_pencil.color
        if (roundVal(_color[0], places) == roundVal(color[0], places) and roundVal(_color[1], places) == roundVal(color[1], places) and roundVal(_color[2], places) == roundVal(color[2], places)):
            gp.active_material_index = i
            return color
    mat = createGpMaterial(_color)
    return mat.grease_pencil.color

def createGpMaterial(_color=(0,0,0)):
    gp = getActiveGp()
    palette = getActivePalette()
    if (len(_color) == 3):
        _color = (_color[0], _color[1], _color[2], 1)
    mat = bpy.data.materials.new(name="Material")
    bpy.data.materials.create_gpencil_data(mat)
    mat.grease_pencil.color = _color
    mat.grease_pencil.fill_color = (_color[0], _color[1], _color[2], 0)
    palette.append(mat)
    gp.active_material_index = len(palette)-1
    return mat

# ~ ~ ~ 
def createColorWithPalette(_color, numPlaces=7, maxColors=0):
    if (len(_color) == 3):
        _color = (_color[0], _color[1], _color[2], 1)
    palette = getActivePalette()
    gp = getActiveGp()
    matchingColorIndex = -1
    places = numPlaces
    for i in range(0, len(palette)):
        color = palette[i].grease_pencil.color
        if (roundVal(_color[0], places) == roundVal(color[0], places) and roundVal(_color[1], places) == roundVal(color[1], places) and roundVal(_color[2], places) == roundVal(color[2], places)):
            matchingColorIndex = i
    #~
    if (matchingColorIndex == -1):
        if (maxColors<1 or len(palette)<maxColors):
            color = createColor(_color)
        else:
            distances = []
            sortedColors = []
            for mat in palette:
                sortedColors.append(mat.grease_pencil.color)
            for color in sortedColors:
                distances.append(getDistance(_color, (color[0], color[1], color[2], color[3])))
            sortedColors.sort(key=dict(zip(sortedColors, distances)).get)
            createColor(sortedColors[0])
    else:
        gp.active_material_index = matchingColorIndex
        color = palette[matchingColorIndex].grease_pencil.color
    #~        
    return color
# ~ ~ ~

def matchColorToPalette(_color):
    if (len(_color) == 3):
        _color = (_color[0], _color[1], _color[2], 1)
    palette = getActivePalette()
    gp = getActiveGp()
    distances = []
    sortedColors = []
    for mat in palette:
        sortedColors.append(mat.grease_pencil.color)
    for color in sortedColors:
        distances.append(getDistance(_color, (color[0], color[1], color[2], color[3])))
    sortedColors.sort(key=dict(zip(sortedColors, distances)).get)
    return createColor(sortedColors[0])

def createAndMatchColorPalette(color, numMaxColors=16, numColPlaces=5):
    if (len(color) == 3):
        color = (color[0], color[1], color[2], 1)
    palette = getActivePalette()
    if (len(palette) < numMaxColors):
        createColorWithPalette(color, numColPlaces, numMaxColors)
    else:
        matchColorToPalette(color)
    return getActiveColor()

def changeColor():
    frame = getActiveFrame()
    palette = getActivePalette()
    strokes = getSelectedStrokes()
    #~
    lineWidthBackup = []
    pointsBackup = []
    for stroke in strokes:
        lineWidthBackup.append(stroke.line_width)
        pointsBackup.append(stroke.points)
    #~
    deleteSelected()
    #~
    for i, points in enumerate(pointsBackup):
        newStroke = frame.strokes.new(getActiveColor().name)
        newStroke.draw_mode = "3DSPACE" # either of ("SCREEN", "3DSPACE", "2DSPACE", "2DIMAGE")
        newStroke.line_width = lineWidthBackup[i]
        newStroke.points.add(len(points))
        for j in range(0, len(points)):
            createPoint(newStroke, j, points[j].co)
    #print(str(len(strokes)) + " changed to " + palette.colors.active.name)

c = changeColor

def newLayer(name="NewLayer", setActive=True):
    gp = getActiveGp()
    gp.data.layers.new(name)
    if (setActive==True):
        gp.data.layers.active = gp.data.layers[len(gp.data.layers)-1]
    return gp.data.layers[len(gp.data.layers)-1]

def getStrokeCoords(target=None):
    returns = []
    if not target:
        target = getSelectedStroke()
    for point in target.points:
        returns.append(point.co)
    return returns

def getStrokePressures(target=None):
    returns = []
    if not target:
        target = getSelectedStroke()
    for point in target.points:
        returns.append(point.pressure)
    return returns

def getStrokeStrengths(target=None):
    returns = []
    if not target:
        target = getSelectedStroke()
    for point in target.points:
        returns.append(point.strength)
    return returns

def lookUpStrokeColor(target=None):
    palette = getActivePalette()
    if (len(palette) < 1):
        palette = createMtlPalette()
        return palette[0]
    if not target:
        target = getSelectedStroke()
    return palette[target.material_index]

def getStrokeColor(target=None):
    return lookUpStrokeColor(target).grease_pencil.color

def getStrokeAlpha(target=None):
    mtl = lookUpStrokeColor(target).grease_pencil
    if (mtl.show_stroke == False):
        return 0
    else:
        return mtl.color[3]

def getStrokeFillColor(target=None):
    return lookUpStrokeColor(target).grease_pencil.fill_color

def getStrokeFillAlpha(target=None):
    mtl = lookUpStrokeColor(target).grease_pencil
    if (mtl.show_fill == False):
        return 0
    else:
        return mtl.fill_color[3]

def getStrokeCoordsPlus(target=None):
    returns = []
    if not target:
        target = getSelectedStroke()
    for point in target.points:
        returns.append((point.co[0], point.co[1], point.co[2], point.pressure, point.strength))
    return returns

def reprojectAllStrokes():
    strokes = getAllStrokes()
    newLayer()
    for stroke in strokes:
        coords = getStrokeCoords(stroke)
        try:
            drawCoords(coords)
        except:
            pass

def compareTuple(t1, t2, numPlaces=5):
    if (roundVal(t1[0], numPlaces) == roundVal(t2[0], numPlaces) and roundVal(t1[1], numPlaces) == roundVal(t2[1], numPlaces) and roundVal(t1[2], numPlaces) == roundVal(t2[2], numPlaces)):
        return True
    else:
        return False

def setActiveObject(target=None):
    if not target:
        target = ss()
    #bpy.context.scene.objects.active = target
    # https://blender.stackexchange.com/questions/126577/blender-2-8-api-python-set-active-object
    bpy.context.view_layer.objects.active = target
    return target

def getActiveObject():
    return bpy.context.view_layer.objects.active

def deleteFromAllFrames():
    origStrokes = []
    frame = getActiveFrame()
    for stroke in frame.strokes:
        addToOrig = False
        for point in stroke.points:
            if (point.select):
               addToOrig = True
               break
        if (addToOrig == True):
           origStrokes.append(stroke) 
    print("Checking for " + str(len(origStrokes)) + " selected strokes.")
    #~    
    allStrokes = getAllStrokes()
    deleteList = []
    numPlaces = 5
    for allStroke in allStrokes:
        doDelete = False
        for origStroke in origStrokes:
            if (len(allStroke.points) == len(origStroke.points)):
                for i in range(0, len(allStroke.points)):
                    if (roundVal(allStroke.points[i].co.x, numPlaces) == roundVal(origStroke.points[i].co.x, numPlaces) and roundVal(allStroke.points[i].co.y, numPlaces) == roundVal(origStroke.points[i].co.y, numPlaces) and roundVal(allStroke.points[i].co.z, numPlaces) == roundVal(origStroke.points[i].co.z, numPlaces)):
                        doDelete = True
                    else:
                        doDelete = False
                        break
        if (doDelete):
            deleteList.append(allStroke)
    #~
    print(str(len(deleteList)) + " strokes listed for deletion.")
    for stroke in deleteList:
        stroke.select = True
    layer = getActiveLayer()
    start, end = getStartEnd()
    for i in range(start, end):
        goToFrame(i)    
        for j in range(0, len(layer.frames)):
            setActiveFrame(j)
            deleteSelected()

df = deleteFromAllFrames

def getAllLayers():
    gp = getActiveGp()
    print("Got " + str(len(gp.data.layers)) + " layers.")
    return gp.data.layers

def getAllFrames(active=False):
    returns = []
    layers = getAllLayers()
    for layer in layers:
        if (active==False):
            for frame in layer.frames:
                returns.append(frame)
        else:
            returns.append(layer.active_frame)
    print("Got " + str(len(returns)) + " frames.")
    return returns

def getActiveFrame():
    gp = getActiveGp()
    layer = gp.data.layers.active
    frame = layer.active_frame
    return frame

# gp not timeline
def setActiveFrame(index):
    layer = getActiveLayer()
    if index < len(layer.frames):
        layer.active_frame = layer.frames[index]
        refresh()
        print("Moved to layer frame " + str(index))
    else:
        print("Outside of layer range")
    return layer.active_frame

def getAllStrokes(active=False):
    returns = []
    frames = getAllFrames(active)
    for frame in frames:
        for stroke in frame.strokes:
            returns.append(stroke)
    print("Got " + str(len(returns)) + " strokes.")
    return returns

def getLayerStrokes(name=None):
    gp = getActiveGp()
    if not name:
        name = gp.data.layers.active.info
    layer = gp.data.layers[name]
    strokes = []
    for frame in layer.frames:
        for stroke in frame.strokes:
            strokes.append(stroke)
    return strokes

def getFrameStrokes(num=None, name=None):
    gp = getActiveGp()
    if not name:
        name = gp.data.layers.active.info
    layer = gp.data.layers[name]
    if not num:
        num = layer.active_frame.frame_number
    strokes = []
    for frame in layer.frames:
        if (frame.frame_number == num):
            for stroke in frame.strokes:
                strokes.append(stroke)
    return strokes

def getLayerStrokesAvg(name=None):
    gp = getActiveGp()
    if not name:
        name = gp.data.layers.active.info
    layer = gp.data.layers[name]
    return float(roundVal(len(getLayerStrokes(name)) / len(layer.frames), 2))

def getAllStrokesAvg(locked=True):
    gp = getActiveGp()
    avg = 0
    for layer in gp.data.layers:
        if (layer.lock == False or locked == True):
            avg += getLayerStrokesAvg(layer.info)
    return float(roundVal(avg / len(gp.data.layers), 2))

def getSelectedStrokes(active=False):
    returns = []
    strokes = getAllStrokes(active)
    for stroke in strokes:
        if (stroke.select):
            returns.append(stroke)
        else:
            for point in stroke.points:
                if (point.select):
                    returns.append(stroke)
                    break
    if (len(returns) > 0):
        print(str(len(returns)) + " selected strokes.")
    else:
        print("No selected strokes.")
    return returns

def getSelectedStroke():
    strokes = getSelectedStrokes()
    if (len(strokes) > 0):
        print("Only returning first selected stroke.")
        return strokes[0]
    else:
        print("No selected strokes.")

def getAllPoints(useCoords=False):
    returns = []
    strokes = getAllStrokes()
    for stroke in strokes:
        for point in stroke.points:
            if (useCoords==True):
                returns.append(point.co)
            else:
                returns.append(point)
    return returns

def getSelectedPoints(useCoords=False):
    returns = []
    strokes = getSelectedStrokes()
    for stroke in strokes:
        for point in stroke.points:
            if (point.select):
                if (useCoords==True):
                    returns.append(point.co)
                else:
                    returns.append(point)
    return returns

def getSelectedPoint(useCoords=False):
    stroke = getSelectedStroke()
    for point in stroke.points:
        if (point.select):
            if (useCoords==True):
                return point.co
            else:
                return point
    return None

def getAllCoords():
    return getAllPoints(True)

def getSelectedCoords():
    return getSelectedPoints(True)

def getSelectedCoord():
    return getSelectedPoint(True)

def deleteSelected(target="strokes"):
    original_type = bpy.context.area.type
    print("Current context: " + original_type)
    bpy.context.area.type = "VIEW_3D"
    #~
    # strokes, points, frame
    bpy.ops.gpencil.delete(type=target.upper())
    #~
    bpy.context.area.type = original_type

# https://www.blender.org/forum/viewtopic.php?t=27834
def AssembleOverrideContextForView3dOps():
    #=== Iterates through the blender GUI's windows, screens, areas, regions to find the View3D space and its associated window.  Populate an 'oContextOverride context' that can be used with bpy.ops that require to be used from within a View3D (like most addon code that runs of View3D panels)
    # Tip: If your operator fails the log will show an "PyContext: 'xyz' not found".  To fix stuff 'xyz' into the override context and try again!
    for oWindow in bpy.context.window_manager.windows:          ###IMPROVE: Find way to avoid doing four levels of traversals at every request!!
        oScreen = oWindow.screen
        for oArea in oScreen.areas:
            if oArea.type == 'VIEW_3D':                         ###LEARN: Frequently, bpy.ops operators are called from View3d's toolbox or property panel.  By finding that window/screen/area we can fool operators in thinking they were called from the View3D!
                for oRegion in oArea.regions:
                    if oRegion.type == 'WINDOW':                ###LEARN: View3D has several 'windows' like 'HEADER' and 'WINDOW'.  Most bpy.ops require 'WINDOW'
                        #=== Now that we've (finally!) found the damn View3D stuff all that into a dictionary bpy.ops operators can accept to specify their context.  I stuffed extra info in there like selected objects, active objects, etc as most operators require them.  (If anything is missing operator will fail and log a 'PyContext: error on the log with what is missing in context override) ===
                        oContextOverride = {'window': oWindow, 'screen': oScreen, 'area': oArea, 'region': oRegion, 'scene': bpy.context.scene, 'edit_object': bpy.context.edit_object, 'active_object': bpy.context.active_object, 'selected_objects': bpy.context.selected_objects}   # Stuff the override context with very common requests by operators.  MORE COULD BE NEEDED!
                        print("-AssembleOverrideContextForView3dOps() created override context: ", oContextOverride)
                        return oContextOverride
    raise Exception("ERROR: AssembleOverrideContextForView3dOps() could not find a VIEW_3D with WINDOW region to create override context to enable View3D operators.  Operator cannot function.")

def TestView3dOperatorFromPythonScript():       # Run this from a python script and operators that would normally fail because they were not called from a View3D context will work!
    oContextOverride = AssembleOverrideContextForView3dOps()    # Get an override context suitable for bpy.ops operators that require View3D
    bpy.ops.mesh.knife_project(oContextOverride)                # An operator like this normally requires to run off the View3D context.  By overriding it with what it needs it will run from any context (like Python script, Python shell, etc)
    print("TestView3dOperatorFromPythonScript() completed succesfully.")

def addVec3(p1, p2):
    return(p1[0]+p2[0], p1[1]+p2[1], p1[2]+p2[2])

def multVec3(p1, p2):
    return(p1[0]*p2[0], p1[1]*p2[1], p1[2]*p2[2])

def setThickness(thickness):
    gp = getActiveGp()
    bpy.ops.object.gpencil_modifier_add(type="GP_THICK")
    gp.grease_pencil_modifiers["Thickness"].thickness_factor = thickness 
    bpy.ops.object.gpencil_modifier_apply(apply_as="DATA", modifier="Thickness")

def separatePointsByDistance(points, colors, threshold):
    if (len(points) != len(colors)):
        return None

    separatedPoints = []
    separatedColors = []
    currentPoints = []
    currentColors = []

    for i in range(0, len(points) - 1):
        currentPoints.append(points[i])
        currentColors.append(colors[i])

        distance = getDistance(points[i], points[i + 1])

        if (distance > threshold):
            separatedPoints.append(currentPoints)
            separatedColors.append(currentColors)
            currentPoints = []
            currentColors = []

    currentPoints.append(points[len(points) - 1])
    currentColors.append(colors[len(colors) - 1])
    separatedPoints.append(currentPoints)
    separatedColors.append(currentColors)

    return separatedPoints, separatedColors










