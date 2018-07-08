'''
LIGHTNING ARTIST TOOLKIT v1.0.0

The Lightning Artist Toolkit was developed with support from:
   Canada Council on the Arts
   Eyebeam Art + Technology Center
   Ontario Arts Council
   Toronto Arts Council
   
Copyright (c) 2018 Nick Fox-Gieg
http://fox-gieg.com

~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

The Lightning Artist Toolkit (Blender) is free software: you can redistribute it 
and/or modify it under the terms of the GNU General Public License 
as published by the Free Software Foundation, either version 3 of 
the License, or (at your option) any later version.

The Lightning Artist Toolkit (Blender) is distributed in the hope that it will 
be useful, but WITHOUT ANY WARRANTY; without even the implied warranty 
of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with the Lightning Artist Toolkit (Blender).  If not, see 
<http://www.gnu.org/licenses/>.
'''

# 1 of 9. MAIN

bl_info = {
    "name": "Lightning Artist Toolkit (Latk)", 
    "author": "Nick Fox-Gieg",
    "category": "Animation"
}

import bpy
import bpy_extras
from mathutils import *
from math import sqrt
import math
import json
import re
from bpy_extras.io_utils import unpack_list
#from curve_simplify import *
import random
import bmesh
import sys
import gc
import xml.etree.ElementTree as etree
from operator import itemgetter
#~
import zipfile
from io import BytesIO
import os
#~
from bpy.props import (BoolProperty, FloatProperty, StringProperty, EnumProperty)
from bpy_extras.io_utils import (ImportHelper, ExportHelper)

# * * * * * * * * * * * * * * * * * * * * * * * * * *
# * * * * * * * * * * * * * * * * * * * * * * * * * *
# * * * * * * * * * * * * * * * * * * * * * * * * * *

# 2 of 9. TOOLS

def gpWorldRoot(name="Empty"):
    bpy.ops.object.empty_add(type="PLAIN_AXES")
    target = ss()
    target.name = name
    layers = getAllLayers()
    for layer in layers:
        layer.parent = target
    return target
    
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
    coords = [(target.matrix_world * v.co) for v in target.data.vertices]
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
        scene.objects.active = cam
    parentMultiple(cams, target)
    #~
    if (hideTarget==True):
        target.hide = True
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
    bpy.context.scene.objects.active = None

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

def bakeParentToChildByName(name="crv"):
    start, end = getStartEnd()
    target = matchName(name)
    for obj in target:
        bpy.context.scene.objects.active = obj
        bakeParentToChild(start, end)

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
    obj = bpy.context.scene.objects.active
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

def groupName(name="crv", gName="myGroup"):
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

def renameCurves(name="mesh", nameMesh="crv_ob_mesh", nameCurve="crv"):
    target = matchName(nameMesh)
    for i in range(0, len(target)):
        target[i].name = name + "_" + str(i)

def deleteUnparentedCurves(name="crv"):
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

def getDistance(v1, v2):
    return sqrt( (v1[0] - v2[0])**2 + (v1[1] - v2[1])**2 + (v1[2] - v2[2])**2)
    
def parentMultiple(target, root, fixTransforms=True):
    bpy.context.scene.objects.active = root # last object will be the parent
    bpy.ops.object.select_all(action='DESELECT')
    for i in range(0, len(target)):
        target[i].select = True
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
                bpy.context.scene.objects.active=obj
                if (fixTransforms==True):
                    bpy.ops.object.parent_clear(type='CLEAR_KEEP_TRANSFORM')
                else:
                    bpy.ops.object.parent_clear()
    else:
        # http://blender.stackexchange.com/questions/9200/make-object-a-a-parent-of-object-b-via-python
        for i in range(0, len(target)-1):
            target[i].select=True
        bpy.context.scene.objects.active = target[len(target)-1] # last object will be the parent
        #~
        if (fixTransforms==True):
            bpy.ops.object.parent_set(type='OBJECT', xmirror=False, keep_transform=False) 
        else:   
            bpy.ops.object.parent_set(type='OBJECT', xmirror=False, keep_transform=True) 

def keyTransform(_obj, _frame):
    _obj.keyframe_insert(data_path="location", frame=_frame) 
    _obj.keyframe_insert(data_path="rotation_euler", frame=_frame) 
    _obj.keyframe_insert(data_path="scale", frame=_frame)

def keyMatrix(_obj, _frame):
    _obj.keyframe_insert(data_path="matrix_world", frame=_frame) 

def select(target=None):
    if not target:
        target=bpy.context.selected_objects;
    print("selected " + str(target))
    return target

def delete(_obj=None):
    if not _obj:
        _obj = ss()
    bpy.ops.object.select_all(action='DESELECT')
    bpy.data.objects[_obj.name].select = True
    bpy.ops.object.delete()
    gc.collect()

def refresh():
    bpy.context.scene.update()

def remap(value, min1, max1, min2, max2):
    range1 = max1 - min1
    range2 = max2 - min2
    valueScaled = float(value - min1) / float(range1)
    return min2 + (valueScaled * range2)
    
def matchName(_name):
    returns = []
    for i in range(0, len(bpy.context.scene.objects)):
        obj = bpy.context.scene.objects[i]
        if re.match(r'^' + str(_name) + '', obj.name): # curve object
            returns.append(obj)
    return returns

def selectName(_name="crv"):
    target = matchName(_name)
    deselect()
    for obj in target:
        obj.select = True

def deleteName(_name="crv"):
    target = matchName(_name)
    for obj in target:
        try:
            delete(obj)
        except:
            print("error deleting " + obj.name)

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
    for layer in gp.layers:   
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

def createCamera():
    # https://blenderartists.org/forum/showthread.php?312512-how-to-add-an-empty-and-a-camera-using-python-script
   cam = bpy.data.cameras.new("Camera")
   cam_ob = bpy.data.objects.new("Camera", cam)
   bpy.context.scene.objects.link(cam_ob)
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
            print("Active camera object")
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

def hideFrame(_obj, _frame, _hide):
    _obj.hide = _hide
    _obj.hide_render = _hide
    _obj.keyframe_insert(data_path="hide", frame=_frame) 
    _obj.keyframe_insert(data_path="hide_render", frame=_frame) 

def showHide(obj, hide, keyframe=False, frame=None):
    obj.hide = hide
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

def normRgbToHex(color):
    return rgbToHex(color, normalized=True)

def moveShot(start, end, x, y, z):
    gp = bpy.context.scene.grease_pencil
    target = (start, end)
    for g in range(target[0], target[1]+1):
        for f in range(0, len(gp.layers)):
            layer = gp.layers[f]
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

# ~ ~ ~ ~ ~ ~ grease pencil ~ ~ ~ ~ ~ ~
def getActiveGp(_name="GPencil"):
    try:
        pencil = bpy.context.scene.grease_pencil
    except:
        pencil = None
    try:
        gp = bpy.data.grease_pencil[pencil.name]
    except:
        gp = bpy.data.grease_pencil.new(_name)
        bpy.context.scene.grease_pencil = gp
    print("Active GP block is: " + gp.name)
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
    palette = gp.palettes.active
    if (palette == None):
        palette = gp.palettes.new(gp.name + "_Palette", set_active = True)
    if (len(palette.colors) < 1):
        color = palette.colors.new()
        color.color = (0,0,0)
    print("Active palette is: " + gp.palettes.active.name)
    return palette

def getActiveColor():
    palette = getActivePalette()
    print("Active color is: " + "\"" + palette.colors.active.name + "\" " + str(palette.colors.active.color))
    return palette.colors.active

def getActiveLayer():
    gp = getActiveGp()
    layer = gp.layers.active
    return layer

def setActiveLayer(name="Layer"):
    gp = getActiveGp()
    gp.layers.active = gp.layers[name]
    return gp.layers.active

def deleteLayer(name=None):
    gp = getActiveGp()
    if not name:
        name = gp.layers.active.info
    gp.layers.remove(gp.layers[name])

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

def blankFrame(layer=None, frame=None):
    if not layer:
        layer = getActiveLayer()
    if not frame:
        frame = bpy.context.scene.frame_current
    try:
        layer.frames.new(frame)
    except:
        pass

def getActiveFrameNum():
    returns = -1
    layer = getActiveLayer()
    for i, frame in enumerate(layer.frames):
        if (frame == layer.active_frame):
            returns = i
    return returns

def getActiveFrameTimelineNum():
    return getActiveLayer().frames[getActiveFrameNum()].frame_number

def checkLayersAboveFrameLimit(limit=20):
    gp = getActiveGp()
    returns = []
    print("~ ~ ~ ~")
    for layer in gp.layers:
        if (len(layer.frames) > limit + 1): # accounting for extra end cap frame
            returns.append(layer)
            print("layer " + layer.info + " is over limit " + str(limit) + " with " + str(len(layer.frames)) + " frames.")
    print(" - - - " + str(len(returns)) + " total layers over limit.")
    print("~ ~ ~ ~")
    return returns

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

def getLayerLength(name=None):
    layer = None
    if not name:
        layer = getActiveLayer()
    else:
        layer = getActiveGp().layers[name]
    return len(layer.frames)

def cleanEmptyLayers():
    gp = getActiveGp()
    for layer in gp.layers:
        if (len(layer.frames) == 0):
            gp.layers.remove(layer)

def clearPalette():
    palette = getActivePalette()
    for color in palette.colors:
        palette.colors.remove(color)

def createColor(_color):
    frame = getActiveFrame()
    palette = getActivePalette()
    matchingColorIndex = -1
    places = 7
    for i in range(0, len(palette.colors)):
        if (roundVal(_color[0], places) == roundVal(palette.colors[i].color.r, places) and roundVal(_color[1], places) == roundVal(palette.colors[i].color.g, places) and roundVal(_color[2], places) == roundVal(palette.colors[i].color.b, places)):
            matchingColorIndex = i
    #~
    if (matchingColorIndex == -1):
        color = palette.colors.new()
        color.color = _color
    else:
        palette.colors.active = palette.colors[matchingColorIndex]
        color = palette.colors[matchingColorIndex]
    #~        
    print("Active color is: " + "\"" + palette.colors.active.name + "\" " + str(palette.colors.active.color))
    return color

# ~ ~ ~ 
def createColorWithPalette(_color, numPlaces=7, maxColors=0):
    palette = getActivePalette()
    matchingColorIndex = -1
    places = numPlaces
    for i in range(0, len(palette.colors)):
        if (roundVal(_color[0], places) == roundVal(palette.colors[i].color.r, places) and roundVal(_color[1], places) == roundVal(palette.colors[i].color.g, places) and roundVal(_color[2], places) == roundVal(palette.colors[i].color.b, places)):
            matchingColorIndex = i
    #~
    if (matchingColorIndex == -1):
        if (maxColors<1 or len(palette.colors)<maxColors):
            color = palette.colors.new()
            color.color = _color
        else:
            distances = []
            sortedColors = []
            for color in palette.colors:
                sortedColors.append(color)
            for color in sortedColors:
                distances.append(getDistance(_color, color.color))
            sortedColors.sort(key=dict(zip(sortedColors, distances)).get)
            palette.colors.active = palette.colors[sortedColors[0].name]
    else:
        palette.colors.active = palette.colors[matchingColorIndex]
        color = palette.colors[matchingColorIndex]
    #~        
    print("Active color is: " + "\"" + palette.colors.active.name + "\" " + str(palette.colors.active.color))
    return color
# ~ ~ ~

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
    print(str(len(strokes)) + " changed to " + palette.colors.active.name)

def newLayer(name="NewLayer", setActive=True):
    gp = getActiveGp()
    gp.layers.new(name)
    if (setActive==True):
        gp.layers.active = gp.layers[len(gp.layers)-1]
    return gp.layers[len(gp.layers)-1]

def getStrokePoints(target=None):
    returns = []
    if not target:
        target = getSelectedStroke()
    for point in target.points:
        returns.append(point.co)
    return returns

def reprojectAllStrokes():
    strokes = getAllStrokes()
    newLayer()
    for stroke in strokes:
        points = getStrokePoints(stroke)
        try:
        	drawPoints(points)
        except:
        	pass

def compareTuple(t1, t2, numPlaces=5):
    if (roundVal(t1[0], numPlaces) == roundVal(t2[0], numPlaces) and roundVal(t1[1], numPlaces) == roundVal(t2[1], numPlaces) and roundVal(t1[2], numPlaces) == roundVal(t2[2], numPlaces)):
        return True
    else:
        return False

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

def getAllLayers():
    gp = getActiveGp()
    print("Got " + str(len(gp.layers)) + " layers.")
    return gp.layers

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
    layer = gp.layers.active
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
        name = gp.layers.active.info
    layer = gp.layers[name]
    strokes = []
    for frame in layer.frames:
        for stroke in frame.strokes:
            strokes.append(stroke)
    return strokes

def getFrameStrokes(num=None, name=None):
    gp = getActiveGp()
    if not name:
        name = gp.layers.active.info
    layer = gp.layers[name]
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
        name = gp.layers.active.info
    layer = gp.layers[name]
    return float(roundVal(len(getLayerStrokes(name)) / len(layer.frames), 2))

def getAllStrokesAvg(locked=True):
    gp = getActiveGp()
    avg = 0
    for layer in gp.layers:
        if (layer.lock == False or locked == True):
            avg += getLayerStrokesAvg(layer.info)
    return float(roundVal(avg / len(gp.layers), 2))

def getSelectedStrokes(active=True):
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

# * * * * * * * * * * * * * * * * * * * * * * * * * *
# * * * * * * * * * * * * * * * * * * * * * * * * * *
# * * * * * * * * * * * * * * * * * * * * * * * * * *

# 3 of 9. READ / WRITE

def exportAlembic(url="test.abc"):
    bpy.ops.wm.alembic_export(filepath=url, vcolors=True, face_sets=True, renderable_only=False)

def exportForUnity(sketchFab=True):
    start, end = getStartEnd()
    target = matchName("crv")
    sketchFabList = []
    sketchFabListNum = []
    for tt in range(0, len(target)):
        deselect()
        for i in range(start, end):
            deselect()
            goToFrame(i)
            if (target[tt].hide==False):
                deselect()
                target[tt].select=True
                exportName = target[tt].name
                exportName = exportName.split("crv_")[1]
                exportName = exportName.split("_mesh")[0]
                exporter(manualSelect=True, fileType="fbx", name=exportName, legacyFbx=True)
                sketchFabList.append("0.083 " + exportName + ".fbx\r")
                sketchFabListNum.append(float(exportName.split("_")[len(exportName.split("_"))-1]))
                break
    if (sketchFab==True):
        print("before sort: ")
        print(sketchFabList)
        print(sketchFabListNum)
        # this sorts entries by number instead of order in Outliner pane
        sketchFabList.sort(key=lambda x: x[0])
        ind = [i[0] for i in sorted(enumerate(sketchFabListNum),key=lambda x: x[1])]
        sketchFabList = [i[0] for i in sorted(zip(sketchFabList, ind),key=lambda x: x[1])]
        #~
        print(getFilePath() + getFileName())
        tempName = exportName.split("_")
        tempString = ""
        for i in range(0, len(tempName)-1):
            tempString += str(tempName[i])
            if (i < len(tempName)-1):
                tempString += "_"
        print("after sort: ")
        print(sketchFabList)
        writeTextFile(getFilePath() + getFileName() + "_" + tempString + ".sketchfab.timeframe", sketchFabList)

def exporter(name="test", url=None, winDir=False, manualSelect=False, fileType="fbx", legacyFbx=False):
    if not url:
        url = getFilePath()
        if (winDir==True):
            url += "\\"
        else:
            url += "/"
    #~
    if (fileType.lower() == "alembic"):
        bpy.ops.wm.alembic_export(filepath=name + ".abc", vcolors=True, face_sets=True, renderable_only=False)
    else:
        if (manualSelect == True):
                if (fileType.lower()=="fbx"):
                    if (legacyFbx == True):
                        bpy.ops.export_scene.fbx(filepath=url + name + ".fbx", use_selection=True, version="ASCII6100") # legacy version
                    else:
                        bpy.ops.export_scene.fbx(filepath=url + name + ".fbx", use_selection=True, version="BIN7400")
                else:
                    bpy.ops.export_scene.obj(filepath=url + name + ".obj", use_selection=True)
        else:
            for j in range(bpy.context.scene.frame_start, bpy.context.scene.frame_end + 1):
                bpy.ops.object.select_all(action='DESELECT')
                goToFrame(j)
                for i in range(0, len(bpy.data.objects)):
                    if (bpy.data.objects[i].hide == False):
                        bpy.data.objects[i].select = True
                #bpy.context.scene.update()
                #~
                if (fileType=="fbx"):
                    if (legacyFbx == True):
                        bpy.ops.export_scene.fbx(filepath=url + name + "_" + str(j) + ".fbx", use_selection=True, version="ASCII6100") # legacy version
                    else:
                        bpy.ops.export_scene.fbx(filepath=url + name + "_" + str(j) + ".fbx", use_selection=True, version="BIN7400")
                else:
                    bpy.ops.export_scene.obj(filepath=url + name + "_" + str(j) + ".obj", use_selection=True)


def importAppend(blendfile, section, obj, winDir=False):
    # http://blender.stackexchange.com/questions/38060/how-to-link-append-with-a-python-script
    # blendfile = "D:/path/to/the/repository.blend"
    # section   = "\\Action\\"
    # obj    = "myaction"
    #~
    url  = blendfile + section + obj
    if (winDir==True):
        section = blendfile + "\\" + section + "\\"
    else:
        section = blendfile + "/" + section + "/"
    #~
    bpy.ops.wm.append(filepath=url, filename=obj, directory=section)

def writeTextFile(name="test.txt", lines=None):
    file = open(name,"w") 
    for line in lines:
        file.write(line) 
    file.close() 

def readTextFile(name="text.txt"):
    file = open(name, "r") 
    return file.read() 

def saveFile(name, format=True):
    if (format==True):
        name = getFilePath() + name + ".blend"
    bpy.ops.wm.save_as_mainfile(filepath=name)

def openFile(name, format=True):
    if (format==True):
        name = getFilePath() + name + ".blend"
    bpy.ops.wm.open_mainfile(filepath=name)

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

# http://blender.stackexchange.com/questions/24694/query-grease-pencil-strokes-from-python
def writeBrushStrokes(filepath=None, bake=True, zipped=False):
    url = filepath # compatibility with gui keywords
    #~
    if(bake == True):
        bakeFrames()
    gp = bpy.context.scene.grease_pencil
    globalScale = Vector((0.1, 0.1, 0.1))
    globalOffset = Vector((0, 0, 0))
    useScaleAndOffset = True
    numPlaces = 7
    roundValues = True
    palette = getActivePalette()
    #~
    sg = []
    sg.append("{")
    sg.append("\t\"creator\": \"blender\",")
    sg.append("\t\"grease_pencil\": [")
    sg.append("\t\t{")
    sg.append("\t\t\t\"layers\": [")
    #~
    sl = []
    for f in range(0, len(gp.layers)):
        sb = []
        layer = gp.layers[f]
        for h in range(0, len(layer.frames)):
            currentFrame = h
            goToFrame(h)
            sb.append("\t\t\t\t\t\t{") # one frame
            sb.append("\t\t\t\t\t\t\t\"frame_number\": " + str(layer.frames[currentFrame].frame_number) + ",")
            if (layer.parent):
                sb.append("\t\t\t\t\t\t\t\"parent_location\": " + "[" + str(layer.parent.location[0]) + ", " + str(layer.parent.location[1]) + ", " + str(layer.parent.location[2]) + "],")
            sb.append("\t\t\t\t\t\t\t\"strokes\": [")
            if (len(layer.frames[currentFrame].strokes) > 0):
                sb.append("\t\t\t\t\t\t\t\t{") # one stroke
                for i in range(0, len(layer.frames[currentFrame].strokes)):
                    color = (0,0,0)
                    try:
                        color = palette.colors[layer.frames[currentFrame].strokes[i].colorname].color
                    except:
                        pass
                    sb.append("\t\t\t\t\t\t\t\t\t\"color\": [" + str(color[0]) + ", " + str(color[1]) + ", " + str(color[2])+ "],")
                    sb.append("\t\t\t\t\t\t\t\t\t\"points\": [")
                    for j in range(0, len(layer.frames[currentFrame].strokes[i].points)):
                        x = 0.0
                        y = 0.0
                        z = 0.0
                        pressure = 1.0
                        strength = 1.0
                        #~
                        point = layer.frames[currentFrame].strokes[i].points[j].co
                        pressure = layer.frames[currentFrame].strokes[i].points[j].pressure
                        strength = layer.frames[currentFrame].strokes[i].points[j].strength
                        #~
                        if useScaleAndOffset == True:
                            x = (point.x * globalScale.x) + globalOffset.x
                            y = (point.z * globalScale.y) + globalOffset.y
                            z = (point.y * globalScale.z) + globalOffset.z
                        else:
                            x = point.x
                            y = point.z
                            z = point.y
                        #~
                        if roundValues == True:
                            sb.append("\t\t\t\t\t\t\t\t\t\t{\"co\": [" + roundVal(x, numPlaces) + ", " + roundVal(y, numPlaces) + ", " + roundVal(z, numPlaces) + "], \"pressure\": " + roundVal(pressure, numPlaces) + ", \"strength\": " + roundVal(strength, numPlaces))
                        else:
                            sb.append("\t\t\t\t\t\t\t\t\t\t{\"co\": [" + str(x) + ", " + str(y) + ", " + str(z) + "], \"pressure\": " + pressure + ", \"strength\": " + strength)                  
                        #~
                        if j == len(layer.frames[currentFrame].strokes[i].points) - 1:
                            sb[len(sb)-1] +="}"
                            sb.append("\t\t\t\t\t\t\t\t\t]")
                            if (i == len(layer.frames[currentFrame].strokes) - 1):
                                sb.append("\t\t\t\t\t\t\t\t}") # last stroke for this frame
                            else:
                                sb.append("\t\t\t\t\t\t\t\t},") # end stroke
                                sb.append("\t\t\t\t\t\t\t\t{") # begin stroke
                        else:
                            sb[len(sb)-1] += "},"
                    if i == len(layer.frames[currentFrame].strokes) - 1:
                        sb.append("\t\t\t\t\t\t\t]")
            else:
                sb.append("\t\t\t\t\t\t\t]")
            if h == len(layer.frames) - 1:
                sb.append("\t\t\t\t\t\t}")
            else:
                sb.append("\t\t\t\t\t\t},")
        #~
        sf = []
        sf.append("\t\t\t\t{") 
        sf.append("\t\t\t\t\t\"name\": \"" + layer.info + "\",")
        if (layer.parent):
            sf.append("\t\t\t\t\t\"parent\": \"" + layer.parent.name + "\",")
        sf.append("\t\t\t\t\t\"frames\": [")
        sf.append("\n".join(sb))
        sf.append("\t\t\t\t\t]")
        if (f == len(gp.layers)-1):
            sf.append("\t\t\t\t}")
        else:
            sf.append("\t\t\t\t},")
        sl.append("\n".join(sf))
        #~
    sg.append("\n".join(sl))
    sg.append("\t\t\t]")
    sg.append("\t\t}")
    sg.append("\t]")
    sg.append("}")
    #~
    if (zipped == True):
        filenameRaw = os.path.split(url)[1].split(".")
        filename = ""
        for i in range(0, len(filenameRaw)-1):
            filename += filenameRaw[i]
        imz = InMemoryZip()
        imz.append(filename + ".json", "\n".join(sg))
        imz.writetofile(url)
    else:
        with open(url, "w") as f:
            f.write("\n".join(sg))
            f.closed
    print("Wrote " + url)
    #~                
    return {'FINISHED'}
    
def readBrushStrokes(filepath=None):
    url = filepath # compatibility with gui keywords
    #~
    gp = getActiveGp()
    #~
    globalScale = Vector((10, 10, 10))
    globalOffset = Vector((0, 0, 0))
    useScaleAndOffset = True
    #~
    data = None

    filename = os.path.split(url)[1].split(".")
    filetype = filename[len(filename)-1].lower()
    if (filetype == "latk" or filetype == "zip"):
        imz = InMemoryZip()
        imz.readFromDisk(url)
        # https://stackoverflow.com/questions/6541767/python-urllib-error-attributeerror-bytes-object-has-no-attribute-read/6542236
        data = json.loads(imz.files[0].decode("utf-8"))        
    else:
        with open(url) as data_file:    
            data = json.load(data_file)
            print("Read " + str(len(data["grease_pencil"][0]["layers"][0]["frames"])) + " frames on first layer.")
    #~
    for h in range(0, len(data["grease_pencil"][0]["layers"])):
        layer = gp.layers.new(data["grease_pencil"][0]["layers"][h]["name"], set_active=True)
        palette = getActivePalette()    
        #~
        for i in range(0, len(data["grease_pencil"][0]["layers"][h]["frames"])):
            frame = layer.frames.new(i) # frame number 5
            for j in range(0, len(data["grease_pencil"][0]["layers"][h]["frames"][i]["strokes"])):
                strokeColor = (0,0,0)
                try:
                    strokeColor = (data["grease_pencil"][0]["layers"][h]["frames"][i]["strokes"][j]["color"][0], data["grease_pencil"][0]["layers"][h]["frames"][i]["strokes"][j]["color"][1], data["grease_pencil"][0]["layers"][h]["frames"][i]["strokes"][j]["color"][2])
                except:
                    pass
                createColor(strokeColor)
                stroke = frame.strokes.new(getActiveColor().name)
                stroke.draw_mode = "3DSPACE" # either of ("SCREEN", "3DSPACE", "2DSPACE", "2DIMAGE")
                stroke.points.add(len(data["grease_pencil"][0]["layers"][h]["frames"][i]["strokes"][j]["points"])) # add 4 points
                for l in range(0, len(data["grease_pencil"][0]["layers"][h]["frames"][i]["strokes"][j]["points"])):
                    x = 0.0
                    y = 0.0
                    z = 0.0
                    pressure = 1.0
                    strength = 1.0
                    if useScaleAndOffset == True:
                        x = (data["grease_pencil"][0]["layers"][h]["frames"][i]["strokes"][j]["points"][l]["co"][0] * globalScale.x) + globalOffset.x
                        y = (data["grease_pencil"][0]["layers"][h]["frames"][i]["strokes"][j]["points"][l]["co"][2] * globalScale.y) + globalOffset.y
                        z = (data["grease_pencil"][0]["layers"][h]["frames"][i]["strokes"][j]["points"][l]["co"][1] * globalScale.z) + globalOffset.z
                    else:
                        x = data["grease_pencil"][0]["layers"][h]["frames"][i]["strokes"][j]["points"][l]["co"][0]
                        y = data["grease_pencil"][0]["layers"][h]["frames"][i]["strokes"][j]["points"][l]["co"][2]
                        z = data["grease_pencil"][0]["layers"][h]["frames"][i]["strokes"][j]["points"][l]["co"][1]
                    #~
                    if ("pressure" in data["grease_pencil"][0]["layers"][h]["frames"][i]["strokes"][j]["points"][l]):
                        pressure = data["grease_pencil"][0]["layers"][h]["frames"][i]["strokes"][j]["points"][l]["pressure"]
                    if ("strength" in data["grease_pencil"][0]["layers"][h]["frames"][i]["strokes"][j]["points"][l]):
                        strength = data["grease_pencil"][0]["layers"][h]["frames"][i]["strokes"][j]["points"][l]["strength"]
                    #stroke.points[l].co = (x, y, z)
                    createPoint(stroke, l, (x, y, z), pressure, strength)
    #~                
    return {'FINISHED'}
# ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~
# ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~

def writeSvg(filepath=None):
    minLineWidth=3
    camera=None
    fps=None
    start=None
    end=None
    #~
    if not camera:
        camera = getActiveCamera()
    if not fps:
        fps = getSceneFps()
    if (start==None or end==None):
        start, end = getStartEnd()
    fps = float(fps)
    duration = float(end - start) / fps
    gp = getActiveGp()
    #url = getFilePath() + name
    url = filepath
    print(url)
    sW = getSceneResolution()[0]
    sH = getSceneResolution()[1]
    svg = []
    #~
    # HEADER
    svg.append("<?xml version=\"1.0\" encoding=\"utf-8\"?>\r");
    svg.append("<!DOCTYPE svg PUBLIC \"-//W3C//DTD SVG 1.1//EN\" \"http://www.w3.org/Graphics/SVG/1.1/DTD/svg11.dtd\">\r")
    svg.append("<svg version=\"1.1\" id=\"Layer_1\" xmlns=\"http://www.w3.org/2000/svg\" xmlns:xlink=\"http://www.w3.org/1999/xlink\" x=\"0px\" y=\"0px\"\r")
    svg.append("\t" + "width=\"" + str(sW) + "px\" height=\"" + str(sH) + "px\" viewBox=\"0 0 " + str(sW) + " " + str(sH) + "\" enable-background=\"new 0 0 " + str(sW) + " " + str(sH) +"\" xml:space=\"preserve\">\r")
    #~
    # BODY
    for layer in gp.layers:
        layerInfo = layer.info.replace(" ", "_").replace(".", "_")
        svg.append("\t" + "<g id=\"" + layerInfo + "\">\r")
        for i, frame in enumerate(layer.frames):
            svg.append("\t\t" + "<g id=\"" + layerInfo + "_frame" + str(i) + "\">\r")
            palette = getActivePalette()
            for stroke in frame.strokes:
                width = stroke.line_width
                if (width == None or width < minLineWidth):
                    width = minLineWidth
                color = palette.colors[stroke.colorname]
                print("found color: " + color.name)
                cStroke = (color.color[0], color.color[1], color.color[2], color.alpha)
                cFill = (color.fill_color[0], color.fill_color[1], color.fill_color[2], color.fill_alpha)
                svg.append("\t\t\t" + svgStroke(points=stroke.points, stroke=(cStroke[0], cStroke[1], cStroke[2]), fill=(cFill[0], cFill[1], cFill[2]), strokeWidth=minLineWidth, strokeOpacity=cStroke[3], fillOpacity=cFill[3], camera=camera) + "\r")
            #~
            svg.append("\t\t\t" + svgAnimate(frame=frame.frame_number, fps=fps, duration=duration) + "\r")
            svg.append("\t\t" + "</g>\r")
        svg.append("\t" + "</g>\r")
    #~
    # FOOTER
    svg.append("</svg>\r")
    #~
    writeTextFile(url, svg)

def svgAnimate(frame=0, fps=12, duration=10, startFrame=False, endFrame=False):
    keyIn = (float(frame) / float(fps)) / float(duration)
    keyOut = keyIn + (1.0/float(fps))
    returns = "<animate attributeName=\"display\" repeatCount=\"indefinite\" dur=\"" + str(duration) + "s\" keyTimes=\"0;" + str(keyIn) + ";" + str(keyOut) + ";1\" values=\"none;inline;none;none\"/>"
    return returns

def svgStroke(points=None, stroke=(0,0,1), fill=(1,0,0), strokeWidth=2.0, strokeOpacity=1.0, fillOpacity=1.0, camera=None, closed=False):
    # https://developer.mozilla.org/en-US/docs/Web/SVG/Element/path
    returns = "<path stroke=\""+ normRgbToHex(stroke) + "\" fill=\""+ normRgbToHex(fill) + "\" stroke-width=\"" + str(strokeWidth) + "\" stroke-opacity=\"" + str(strokeOpacity) + "\" fill-opacity=\"" + str(fillOpacity) + "\" d=\""
    for i, point in enumerate(points):
        co = getWorldCoords(co=point.co, camera=camera)
        if (i == 0):
            returns += "M" + str(co[0]) + " " + str(co[1]) + " "
        elif (i > 0 and i < len(points)-1):
            returns += "L" + str(co[0]) + " " + str(co[1]) + " "
        elif (i == len(points)-1):
            if (closed==True):
                returns += "L" + str(co[0]) + " " + str(co[1]) + " z"
            else:
                returns += "L" + str(co[0]) + " " + str(co[1])
    returns += "\"/>"
    return returns

# ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~

def writePainter(filepath=None):
    camera=getActiveCamera()
    outputFile = []
    dim = (float(getSceneResolution()[0]), float(getSceneResolution()[1]), 0.0)
    outputFile.append(painterHeader(dim))
    #~
    strokes = []
    gp = getActiveGp()
    palette = getActivePalette()
    for layer in gp.layers:
        if (layer.lock == False):
            for stroke in layer.active_frame.strokes:
                strokes.append(stroke)
    counter = 0
    for stroke in strokes:
        color = palette.colors[stroke.color.name].color
        points = []
        for point in stroke.points: 
            co = getWorldCoords(co=point.co, camera=camera)
            x = co[0] 
            y = co[1]
            prs = point.pressure
            point = (x, y, prs, counter)
            counter += 1
            points.append(point)
        outputFile.append(painterStroke(points, color))
    #~
    outputFile.append(painterFooter())
    writeTextFile(filepath, outputFile)

def painterHeader(dim=(1024,1024,1024), bgColor=(1,1,1)):
    s = "script_version_number version 10\r"
    s += "artist_name \"\"\r"
    s += "start_time date Wed, May 24, 2017 time 3:23 PM\r"
    s += "start_random 1366653360 1884255589\r"
    #s += "variant \"Painter Brushes\" \"F-X\" \"Big Wet Luscious\"\r"
    #s += "max_size_slider   14.00000\r"
    #s += "min_radius_fraction_slider    0.20599\r"
    s += "build\r"
    s += "penetration_slider 100 percent\r"
    #s += "texture \"Paper Textures\" \"<str t=17500 i=001>\"\r"
    s += "grain_inverted unchecked\r"
    s += "directional_grain unchecked\r"
    s += "scale_slider 1.00000\r"
    s += "paper_brightness_slider 0.50000\r"
    s += "paper_contrast_slider 1.00000\r"
    s += "portfolio_change \"\"\r"
    #s += "gradation \"Painter Gradients.gradients\" \"<str t=17503 i=001>\"\r"
    #s += "weaving \"Painter Weaves.weaves\" \"<str t=17504 i=001>\"\r"
    #s += "pattern_change \"Painter Patterns\" \"<str t=17001 i=001>\"\r"
    #s += "path_library_change \"Painter Selections\"\r"
    #s += "nozzle_change \"Painter Nozzles\" \"<str t=17000 i=001>\"\r"
    s += "use_brush_grid unchecked\r"
    s += "new_tool 1\r"
    s += "gradation_options type 0 order 0 angle 0.00 spirality  1.000\r"
    s += "pattern_options pattern_type 1 offset 0.594\r"
    s += "preserve_transparency unchecked\r"
    s += "wind_direction 4.712389\r"
    #s += "color red 1 green 109 blue 255\r"
    #s += "background_color red 255 green 4 blue 4\r"
    #s += "change_file \"ntitled-1\"\r"
    s += "new_3 \"Untitled-1\" width " + str(int(dim[0])) + " height " + str(int(dim[1])) + " resolution 72.00000 width_unit 1 height_unit 1 resolution_unit 1 paper_color red " + str(int(bgColor[0] * 255.0)) + " green " + str(int(bgColor[1] * 255.0)) + " blue " + str(int(bgColor[2] * 255.0)) + " movie 0 frames 1\r"
    return s

def painterFooter():
    s = "end_time date Wed, May 24, 2017 time 3:25 PM\r"
    return s

def painterStroke(points, color=(0,0,0)):
    s = "color red " + str(int(color[0]*255.0)) + " green " + str(int(color[1]*255.0)) + " blue " + str(int(color[2]*255.0)) + "\r"
    s += "stroke_start\r"
    for point in points:
        s += painterPoint(point)
    s += "stroke_end\r"
    return s

def painterPoint(point):
    x = point[0]
    y = point[1]
    time = point[3]
    s = "pnt x " + str(x) + " y " + str(y) + " time " + str(time) + " prs " + str(roundVal(point[2], 2)) + " tlt 0.00 brg 0.00 whl 1.00 rot 0.00\r"
    return s

# ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~

def importNorman(filepath=None):
    globalScale = Vector((1, 1, 1))
    globalOffset = Vector((0, 0, 0))
    useScaleAndOffset = True
    numPlaces = 7
    roundValues = True
    #~
    with open(filepath) as data_file: 
        data = json.load(data_file)
    #~
    frames = []    
    for i in range(0, len(data["data"])):
        strokes = []
        for j in range(0, len(data["data"][i])):
            points = []
            for k in range(0, len(data["data"][i][j])):
                points.append((data["data"][i][j][k]["x"], data["data"][i][j][k]["y"], data["data"][i][j][k]["z"]))
            strokes.append(points)
        frames.append(strokes)
    #~
    gp = getActiveGp()
    layer = gp.layers.new("Norman_layer", set_active=True)
    for i in range(0, len(frames)):
        frame = layer.frames.new(i)
        for j in range(0, len(frames[i])):
            strokeColor = (0.5,0.5,0.5)
            createColor(strokeColor)
            stroke = frame.strokes.new(getActiveColor().name)
            stroke.draw_mode = "3DSPACE" # either of ("SCREEN", "3DSPACE", "2DSPACE", "2DIMAGE")
            stroke.points.add(len(frames[i][j])) # add 4 points
            for l in range(0, len(frames[i][j])):
                x = 0.0
                y = 0.0
                z = 0.0
                pressure = 1.0
                strength = 1.0
                if useScaleAndOffset == True:
                    x = (frames[i][j][l][0] * globalScale.x) + globalOffset.x
                    y = (frames[i][j][l][2] * globalScale.y) + globalOffset.y
                    z = (frames[i][j][l][1] * globalScale.z) + globalOffset.z
                else:
                    x = frames[i][j][l][0]
                    y = frames[i][j][l][2]
                    z = frames[i][j][l][1]
                #~
                createPoint(stroke, l, (x, y, z), pressure, strength)

def gmlParser(filepath=None, splitStrokes=True):
    globalScale = (1, 1, 1)
    screenBounds = (1, 1, 1)
    up = (0, 1, 0)
    useTime = True
    minStrokeLength=3
    #~
    masterLayerList = []
    tree = etree.parse(filepath)
    root = tree.getroot()
    #~
    strokeCounter = 0
    pointCounter = 0
    gp = getActiveGp()
    fps = getSceneFps()
    start, end = getStartEnd()
    #~
    tag = root.find("tag")
    origLayerName = "GML_Tag"
    layer = newLayer(origLayerName)
    masterLayerList.append(layer)
    #~
    header = tag.find("header")
    #~
    environment = header.find("environment")
    if not environment:
        environment = tag.find("environment")
    if environment:
        upEl = environment.find("up")
        if (upEl):
            up = (float(upEl.find("x").text), float(upEl.find("y").text), float(upEl.find("z").text))
        screenBoundsEl = environment.find("screenBounds")
        if (screenBoundsEl):
            sbX = float(screenBoundsEl.find("x").text)
            sbY = float(screenBoundsEl.find("y").text)
            sbZ = 1.0
            try:
                sbZ = float(screenBoundsEl.find("z").text)
            except:
                pass
            screenBounds = (sbX, sbY, sbZ)
    globalScale = (globalScale[0] * screenBounds[0], globalScale[1] * screenBounds[1], globalScale[2] * screenBounds[2])
    #~
    drawing = tag.find("drawing")
    strokesEl = drawing.findall("stroke")
    strokeCounter += len(strokesEl)
    strokes = []
    for stroke in strokesEl:
        #~
        pts = stroke.findall("pt")
        pointCounter += len(pts)
        gmlPoints = []
        for pt in pts:
            x = float(pt.find("x").text) * globalScale[0]
            y = float(pt.find("y").text) * globalScale[1]
            z = 0.0
            try:
                z = float(pt.find("z").text) * globalScale[2]
            except:
                pass
            time = 0.0
            try:
                time = float(pt.find("time").text)
            except:
                pass
            gmlPoints.append((x,y,z,time))
        gmlPoints = sorted(gmlPoints, key=itemgetter(3)) # sort by time
        strokes.append(gmlPoints)
        #~
        for gmlPoint in gmlPoints:
            frameNum = int(gmlPoint[3] * float(fps))
            print(str(gmlPoint[3]))
            goToFrame(frameNum)
            try:
                layer.frames.new(frameNum)
            except:
                pass
        for frame in layer.frames:
            goToFrame(frame.frame_number)
            layer.active_frame = frame
            #~
            if (splitStrokes==False):
                for stroke in strokes:
                    lastPoint = stroke[len(stroke)-1]
                    if (int(lastPoint[3] * float(fps)) <= frame.frame_number):
                        if (len(stroke) >= minStrokeLength):
                            drawPoints(stroke, frame=frame, layer=layer)
            #~
            gpPoints = []
            for gmlPoint in gmlPoints:
                if (int(gmlPoint[3] * float(fps)) <= frame.frame_number):
                    gpPoints.append(gmlPoint)
            print("...Drawing into frame " + str(frame.frame_number) + " with " + str(len(gpPoints)) + " points.")
            if (len(gpPoints) >= minStrokeLength):
                if (splitStrokes==True):
                    layer = newLayer(layer.info)
                    masterLayerList.append(layer)
                drawPoints(points=gpPoints, frame=frame, layer=layer)
    # cleanup
    if (splitStrokes==True):
        for layer in masterLayerList:
            if (len(layer.frames)<1):
                deleteLayer(layer.info)
        cleanCounter = 1
        for layer in masterLayerList:
            for gpLayer in gp.layers:
                if (layer.info==gpLayer.info):
                    gpLayer.info = origLayerName + "_" + str(cleanCounter)
                    cleanCounter += 1
                    break
    #~
    print("* * * * * * * * * * * * * * *")
    print("strokes: " + str(strokeCounter) + "   points: " + str(pointCounter))

def writeGml(filepath=None, make2d=False):
    timeCounter = 0
    timeIncrement = 0.01
    #~
    globalScale = (10, 10, 10)
    globalOffset = (0, 0, 0)
    useScaleAndOffset = True
    numPlaces = 7
    roundValues = True
    #~
    # ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~
    sg = gmlHeader((512,512,512))
    for i in range(0,len(strokes)):
        sg += gmlStroke(strokes[i])
    sg += gmlFooter()
    # ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~
    #~
    url = filename + ".gml"
    with open(url, "w") as f:
        f.write(sg)
        f.closed
        print("Wrote " + url)    

def gmlHeader(dim=(1024,1024,1024)):
    s = "<gml spec=\"0.1b\">\r"
    s += "\t<tag>\r"
    s += "\t\t<header>\r"
    s += "\t\t\t<client>\r"
    s += "\t\t\t\t<name>KinectToPin</name>\r"
    s += "\t\t\t</client>\r"
    s += "\t\t\t<environment>\r"
    s += "\t\t\t\t<up>\r"
    s += "\t\t\t\t\t<x>0</x>\r"
    s += "\t\t\t\t\t<y>1</y>\r"
    s += "\t\t\t\t\t<z>0</z>\r"
    s += "\t\t\t\t</up>\r"
    s += "\t\t\t\t<screenBounds>\r"
    s += "\t\t\t\t\t<x>" + str(dim[0]) + "</x>\r"
    s += "\t\t\t\t\t<y>" + str(dim[1]) + "</y>\r"
    s += "\t\t\t\t\t<z>" + str(dim[2]) + "</z>\r"
    s += "\t\t\t\t</screenBounds>\r"
    s += "\t\t\t</environment>\r"
    s += "\t\t</header>\r"
    s += "\t\t<drawing>\r"
    return s

def gmlFooter():
    s = "\t\t</drawing>\r"
    s += "\t</tag>\r"
    s += "</gml>\r"
    return s

def gmlStroke(points):
    s = "\t\t\t<stroke>\r"
    for point in points:
        s += gmlPoint(point)
    s += "\t\t\t</stroke>\r"
    return s

def gmlPoint(point):
    global timeCounter
    global timeIncrement
    s = "\t\t\t\t<pt>\r"
    s += "\t\t\t\t\t<x>" + str(point[0]) + "</x>\r"
    s += "\t\t\t\t\t<y>" + str(point[1]) + "</y>\r"
    s += "\t\t\t\t\t<z>" + str(point[2]) + "</z>\r"
    s += "\t\t\t\t\t<time>" + str(timeCounter) + "</time>\r"
    s += "\t\t\t\t</pt>\r"
    timeCounter += timeIncrement
    return s

# ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~

def smilParser(filepath=None):
    if not filepath:
        filepath = "C:\\Users\\nick\\Desktop\\error.svg"
    globalScale = (0.01, 0.01, 0.01)
    screenBounds = (1, 1, 1)
    up = (0, 1, 0)
    useTime = True
    minStrokeLength=3
    #~
    masterLayerList = []
    tree = etree.parse(filepath)
    root = tree.getroot()
    #~
    strokeCounter = 0
    pointCounter = 0
    gp = getActiveGp()
    fps = getSceneFps()
    start, end = getStartEnd()
    #~
    paths = getAllTags("path", tree)
    for path in paths:
        strokes = path.attrib["d"].split('M')
        for stroke in strokes:
            pointsList = []
            pointsRaw = stroke.split(" ")
            for pointRaw in pointsRaw:
                pointRaw = pointRaw.split("Q")[0]
                pointRaw = pointRaw.replace("Z", "")
                pointRaw = pointRaw.replace("L", "")
                try:
                    pointsList.append(float(pointRaw))
                except:
                    pass
            if (len(pointsList) % 2 != 0):
                pointsList.pop()
            points = []
            for i in range(0, len(pointsList), 2):
                point = (pointsList[i] * globalScale[0], pointsList[i+1] * globalScale[1], 0)
                points.append(point)
            if (len(points) > 1):
                drawPoints(points)

def getAllTags(name=None, xml=None):
    returns = []
    for node in xml.iter():
        if (node.tag.split('}')[1] == name):
            returns.append(node)
    return returns

def writePointCloud(name=None, strokes=None):
    if not strokes:
        strokes = getSelectedStrokes()
    lines = []
    for stroke in strokes:
        for point in stroke.points:
            x = str(point.co[0])
            y = str(point.co[1])
            z = str(point.co[2])
            lines.append(x + ", " + y + ", " + z + "\n")
    writeTextFile(name=name, lines=lines)


class InMemoryZip(object):

    def __init__(self):
        # Create the in-memory file-like object for working w/imz
        self.in_memory_zip = BytesIO()
        self.files = []

    def append(self, filename_in_zip, file_contents):
        # Appends a file with name filename_in_zip and contents of
        # file_contents to the in-memory zip.
        # Get a handle to the in-memory zip in append mode
        zf = zipfile.ZipFile(self.in_memory_zip, "a", zipfile.ZIP_DEFLATED, False)

        # Write the file to the in-memory zip
        zf.writestr(filename_in_zip, file_contents)

        # Mark the files as having been created on Windows so that
        # Unix permissions are not inferred as 0000
        for zfile in zf.filelist:
             zfile.create_system = 0         

        return self

    def readFromMemory(self):
        # Returns a string with the contents of the in-memory zip.
        self.in_memory_zip.seek(0)
        return self.in_memory_zip.read()

    def readFromDisk(self, url):
        zf = zipfile.ZipFile(url, 'r')
        for file in zf.infolist():
            self.files.append(zf.read(file.filename))

    def writetofile(self, filename):
        # Writes the in-memory zip to a file.
        f = open(filename, "wb")
        f.write(self.readFromMemory())
        f.close()

# * * * * * * * * * * * * * * * * * * * * * * * * * *
# * * * * * * * * * * * * * * * * * * * * * * * * * *
# * * * * * * * * * * * * * * * * * * * * * * * * * *

# 4 of 9. MATERIALS / RENDERING

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
def searchMtl(color=None, name="crv"):
    returns = []
    if not color:
        color = getActiveColor().color
    curves = matchName(name)
    for curve in curves:
        if (compareTuple(curve.data.materials[0].diffuse_color, color)):
            returns.append(curve)
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
def consolidateMtlAlt(name="crv"):
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

# * * * * * * * * * * * * * * * * * * * * * * * * * *
# * * * * * * * * * * * * * * * * * * * * * * * * * *
# * * * * * * * * * * * * * * * * * * * * * * * * * *

# 5 of 9. MESHES / GEOMETRY

def joinObjects(target=None, center=False):
    if not target:
        target = s()
    #~
    bpy.ops.object.select_all(action='DESELECT') 
    target[0].select = True
    bpy.context.scene.objects.active = target[0]
    for i in range(1, len(target)):
        target[i].select = True
    #~
    bpy.ops.object.join()
    #~
    for i in range(1, len(target)):
        try:
            scn.objects.unlink(target[i])
        except:
            pass
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
    pencil = getActiveGp()
    palette = getActivePalette()
    #~
    for b in range(0, len(pencil.layers)):
        layer = pencil.layers[b]
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

def gpMeshQ(val = 0.1):
    gpMesh(_decimate=val, _saveLayers=True)

def gpMesh(_thickness=0.1, _resolution=1, _bevelResolution=0, _bakeMesh=True, _decimate = 0.1, _curveType="nurbs", _useColors=True, _saveLayers=False, _singleFrame=False, _vertexColors=True, _vertexColorName="rgba", _animateFrames=True, _solidify=False, _subd=0, _remesh="none", _consolidateMtl=True, _caps=True, _joinMesh=True, _uvStroke=True, _uvFill=True, _usePressure=True):
    if (_joinMesh==True or _remesh != "none"):
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
                    #~
                    crv_ob = makeCurve(name="crv_" + getLayerInfo(layer) + "_" + str(layer.frames[c].frame_number), coords=coords, pressures=pressures, curveType=_curveType, resolution=_resolution, thickness=_thickness, bevelResolution=_bevelResolution, parent=layer.parent, capsObj=capsObj, useUvs=_uvStroke, usePressure=_usePressure)
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
                        if (_remesh != "none"):
                            meshObj = remesher(meshObj, mode=_remesh)
                        #~
                        # + + + + + + +
                        if (palette.colors[stroke.colorname].fill_alpha > 0.001):
                            fill_ob = createFill(stroke.points, useUvs=_uvFill)
                            joinObjects([meshObj, fill_ob])
                        # + + + + + + +
                        #~
                        if (_vertexColors==True):
                            colorVertices(meshObj, strokeColor, colorName = _vertexColorName) 
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
                if (_joinMesh==True): 
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
            if (_saveLayers==True):
                deselect()
                target = matchName("crv_" + getLayerInfo(layer))
                for tt in range(0, len(target)):
                    target[tt].select = True
                print("* baking")
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
            drawPoints(points)
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

def colorVertices(obj, color=(1,0,0), makeMaterial=False, colorName="rgba"):
    # start in object mode
    mesh = obj.data
    #~
    if not mesh.vertex_colors:
        mesh.vertex_colors.new(colorName) 
    #~
    color_layer = mesh.vertex_colors.active  
    #~
    i = 0
    for poly in mesh.polygons:
        for idx in poly.loop_indices:
            try:
                color_layer.data[i].color = (color[0], color[1], color[2], 1) # future-proofing 2.79a
            except:
                color_layer.data[i].color = color # 2.79 and earlier
            i += 1
    #~
    if (makeMaterial==True):
        colorVertexCyclesMat(obj)

def meshToGp(obj=None):
    if not obj:
        obj = ss()
    mesh = obj.data
    mat = obj.matrix_world
    #~
    points = []
    for face in mesh.polygons:
        for idx in face.vertices:
            pointsFace = []
            pointsFace.append(mesh.vertices[idx].co)
        finalPoint = Vector((0,0,0))
        for vert in pointsFace:
            finalPoint += vert
        finalPoint /= len(pointsFace)
        finalPoint = mat * finalPoint
        points.append((finalPoint.x, finalPoint.z, finalPoint.y))
    drawPoints(points)

def makeCurve(coords, pressures, resolution=2, thickness=0.1, bevelResolution=1, curveType="bezier", parent=None, capsObj=None, name="crv_ob", useUvs=True, usePressure=True):
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
    crv_ob = bpy.data.objects.new(name, curveData)
    #~
    # attach to scene and validate context
    scn = bpy.context.scene
    scn.objects.link(crv_ob)
    scn.objects.active = crv_ob
    crv_ob.select = True
    if (useUvs==True):
        crv_ob.data.use_uv_as_generated = True
    return crv_ob

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

# 6 of 9. DRAWING

# note that unlike createStroke, this creates a stroke from raw coordinates
def drawPoints(points=None, color=None, frame=None, layer=None):
    if (len(points) > 0):
        if not color:
            color = getActiveColor()
        if not layer:
            layer = getActiveLayer()
            if not layer:
                gp = getActiveGp()
                layer = gp.layers.new("GP_Layer")
                gp.layers.active = layer
        if not frame:
            frame = getActiveFrame()
            if not frame:
                try:
                    frame = layer.frames.new(currentFrame())
                except:
                    pass
        stroke = frame.strokes.new(color.name)
        stroke.draw_mode = "3DSPACE"
        stroke.points.add(len(points))
        for i, point in enumerate(points):
            pressure = 1.0
            strength = 1.0
            if (len(point) > 3):
                pressure = point[3]
            if (len(point) > 4):
                strength = point[4]
            createPoint(stroke, i, (point[0], point[2], point[1]), pressure, strength)
        return stroke
    else:
        return None

def createPoint(_stroke, _index, _point, pressure=1, strength=1):
    _stroke.points[_index].co = _point
    _stroke.points[_index].select = True
    _stroke.points[_index].pressure = pressure
    _stroke.points[_index].strength = strength

def addPoint(_stroke, _point, pressure=1, strength=1):
    _stroke.points.add(1)
    createPoint(_stroke, len(_stroke.points)-1, _point, pressure, strength)

def closeStroke(_stroke):
    addPoint(_stroke, _stroke.points[0].co)

def createStrokes(strokes, palette=None):
    if (palette == None):
        palette = getActivePalette()
    frame = getActiveFrame()
    if (frame == None):
        frame = getActiveLayer().frames.new(bpy.context.scene.frame_current)
    #~
    for strokeSource in strokes:
        strokeColor = (0,0,0)
        try:
            strokeColor = createColor(strokeSource.color.color)
        except:
            pass
        strokeDest = frame.strokes.new(getActiveColor().name)        
        strokeDest.draw_mode = '3DSPACE'
        strokeDest.points.add(len(strokeSource.points))
        for l in range(0, len(strokeSource.points)):
            strokeDest.points[l].co = strokeSource.points[l].co 
            strokeDest.points[l].pressure = 1
            strokeDest.points[l].strength = 1

def createStroke(points, color=(0,0,0), frame=None, palette=None):
    if (palette == None):
        palette = getActivePalette()
    if (frame == None):
        frame = getActiveFrame()
    #~
    strokeColor = createColor(color)
    stroke = frame.strokes.new(getActiveColor().name)        
    stroke.draw_mode = '3DSPACE'
    stroke.points.add(len(points))
    for l in range(0, len(points)):
        stroke.points[l].co = points[l].co 
        stroke.points[l].pressure = 1
        stroke.points[l].strength = 1

def deleteStroke(_stroke):
    bpy.ops.object.select_all(action='DESELECT')
    _stroke.select = True
    deleteSelected()

def deleteStrokes(_strokes):
    bpy.ops.object.select_all(action='DESELECT')
    for stroke in _strokes:
        stroke.select = True
    deleteSelected()

def selectStrokePoint(_stroke, _index):
    for i, point in enumerate(_stroke.points):
        if (i==_index):
            point.select=True
        else:
            point.select=False
    return _stroke.points[_index]

def selectLastStrokePoint(_stroke):
    return selectStrokePoint(_stroke, len(_stroke.points)-1)

def distributeStrokesAlt(step=1):
    palette = getActivePalette()
    strokes = getAllStrokes()
    layer = getActiveLayer()
    strokesToBuild = []
    counter = 1
    for i in range(0, len(strokes)):
        goToFrame(i+1)
        try:
            layer.frames.new(bpy.context.scene.frame_current)
        except:
            pass
        layer.active_frame = layer.frames[i+1]
        copyFrame(0, i+1, counter)
        counter += step
        if (counter > len(strokes)-1):
            counter = len(strokes)-1

def distributeStrokes(pointStep=10, step=1, minPointStep=2):
    start, end = getStartEnd()
    palette = getActivePalette()
    strokes = getAllStrokes()
    layer = getActiveLayer()
    strokeCounter = 0
    extraFrameCounter = 0
    #~
    for i in range(0, len(strokes)):
        goToFrame(i+1+extraFrameCounter)
        try:
            layer.frames.new(bpy.context.scene.frame_current)
        except:
            pass
        layer.active_frame = layer.frames[bpy.context.scene.frame_current]
        #~
        if (pointStep < minPointStep):
            copyFrame(0, i+1+extraFrameCounter, strokeCounter+1)
        else:
            copyFrame(0, i+1+extraFrameCounter, strokeCounter)
        #~
        if (pointStep >= minPointStep):
            pointsCounter = 0
            stroke = strokes[strokeCounter]
            points = stroke.points
            subFrames = roundValInt(len(points)/pointStep)
            for j in range(0, subFrames):
                extraFrameCounter += 1
                outLoc = i+1+extraFrameCounter
                goToFrame(outLoc)
                try:
                    layer.frames.new(bpy.context.scene.frame_current)
                except:
                    pass
                layer.active_frame = layer.frames[bpy.context.scene.frame_current]
                #~
                for l in range(0, strokeCounter):
                    createStroke(layer.frames[0].strokes[l].points, layer.frames[0].strokes[l].color.color, layer.frames[outLoc])#newStroke.color.color)
                newStroke = layer.frames[0].strokes[strokeCounter]
                newPoints = []
                for l in range(0, len(newStroke.points)):
                    if (l < j * pointStep):
                        newPoints.append(newStroke.points[l])  
                #~                                         
                createStroke(newPoints, newStroke.color.color, layer.frames[outLoc])
        #~
        strokeCounter += step
        if (strokeCounter > len(strokes)-1):
            strokeCounter = len(strokes)-1
    #~
    lastLoc = len(strokes)+1+extraFrameCounter
    goToFrame(lastLoc)
    try:
        layer.frames.new(bpy.context.scene.frame_current)
    except:
        pass
    layer.active_frame = layer.frames[bpy.context.scene.frame_current]
    copyFrame(0, lastLoc)

#ds = distributeStrokes

def writeOnStrokes(step=1):
    gp = getActiveGp()
    for i in range(0, len(gp.layers)):
        gp.layers.active_index = i
        distributeStrokes(step)

def makeLine(p1, p2):
    return drawPoints([p1, p2])

def makeGrid(gridRows=10, gridColumns=10, cell=0.1, zPos=0):
    strokes = []
    #~
    xMax = gridRows * cell;
    yMax = gridColumns * cell;
    xHalf = xMax / 2;
    yHalf = yMax / 2;
    #~
    for x in range(0, gridRows+1):
        xPos = x * cell;
        strokes.append(makeLine((-xHalf, xPos - xHalf, zPos), (xHalf, xPos - xHalf, zPos)))
    #~
    for y in range(0, gridColumns+1):
        yPos = y * cell;
        strokes.append(makeLine((yPos - yHalf, -yHalf, zPos), (yPos - yHalf, yHalf, zPos)))
    #~
    return strokes


def makeCube(pos=(0,0,0), size=1):
    strokes = []
    s = size / 2
    #~
    p1 = addVec3((-s, -s, s), pos)
    p2 = addVec3((-s, s, s), pos)
    p3 = addVec3((s, -s, s), pos)
    p4 = addVec3((s, s, s), pos)
    p5 = addVec3((-s, -s, -s), pos)
    p6 = addVec3((-s, s, -s), pos)
    p7 = addVec3((s, -s, -s), pos)
    p8 = addVec3((s, s, -s), pos)
    #~
    strokes.append(makeLine(p1, p2))
    strokes.append(makeLine(p2, p4))
    strokes.append(makeLine(p3, p1))
    strokes.append(makeLine(p4, p3))
    #~
    strokes.append(makeLine(p5, p6))
    strokes.append(makeLine(p6, p8))
    strokes.append(makeLine(p7, p5))
    strokes.append(makeLine(p8, p7))
    #~
    strokes.append(makeLine(p1, p5))
    strokes.append(makeLine(p2, p6))
    strokes.append(makeLine(p3, p7))
    strokes.append(makeLine(p4, p8))
    #~
    return strokes

def makeSquare(pos=(0,0,0), size=1):
    strokes = []
    s = size / 2
    p1 = addVec3((-s, -s, 0), pos)
    p2 = addVec3((-s, s, 0), pos)
    p3 = addVec3((s, -s, 0), pos)
    p4 = addVec3((s, s, 0), pos)
    strokes.append(makeLine(p1, p2))
    strokes.append(makeLine(p1, p3))
    strokes.append(makeLine(p4, p2))
    strokes.append(makeLine(p4, p3))
    #~
    return strokes

def makeCircle(pos=(0,0,0), size=1, resolution=10, vertical=True):
    points = []
    x = 0
    y = 0
    angle = 0.0
    step = 1.0/resolution
    #~
    while (angle < 2 * math.pi):
        x = (size/2.0) * math.cos(angle)
        y = (size/2.0) * math.sin(angle)
        if (vertical==True):
            points.append(addVec3((x, y, 0), pos))
        else:
            points.append(addVec3((x, 0, y), pos))
        angle += step
    #~
    return drawPoints(points)

def makeSphere(pos=(0,0,0), size=1, resolution=10, lat=10, lon=10):
    points = []
    for i in range(0, lat):
        for j in range(0, lon):
            points.append(multVec3(addVec3(getLatLon(i, j), pos), (size,size,size)))
    drawPoints(points)

def getLatLon(lat, lon):
    eulat = (math.pi / 2.0) - lat
    slat = math.sin(eulat)
    x = math.cos(lon) * slat
    y = math.sin(lon) * slat
    z = math.cos(eulat)
    return (x, y, z)

def makeStarBurst(pos=(0,0,0), size=1, reps=20):
    s = size/2.0
    strokes = []
    for i in range(0, reps):
        lat = random.uniform(0, 90)
        lon = random.uniform(0, 180)
        p2 = multVec3(getLatLon(lat, lon), (s, s, s))
        strokes.append(drawPoints([pos, p2]))
    return strokes

def makeTriangle(pos=(0,0,0), size=1):
    s = size/2.0
    p1 = (pos[0], pos[1] + s, pos[2])
    p2 = (pos[0] - s, pos[1] - s, pos[2])
    p3 = (pos[0] + s, pos[1] - s, pos[2])
    return drawPoints([p1, p2, p3, p1])

def makePyramid(pos=(0,0,0), size=1):
    strokes = []
    s = size/2.0
    p1 = (pos[0], pos[1] + s, pos[2])
    p2 = (pos[0] - s, pos[1] - s, pos[2] + s)
    p3 = (pos[0] + s, pos[1] - s, pos[2] + s)
    #~
    strokes.append(drawPoints([p1, p2, p3, p1]))
    #~
    p4 = (pos[0], pos[1] + s, pos[2])
    p5 = (pos[0] - s, pos[1] - s, pos[2] - s)
    p6 = (pos[0] + s, pos[1] - s, pos[2] - s)
    #~
    strokes.append(drawPoints([p4, p5, p6, p4]))
    #~
    strokes.append(drawPoints([p2, p5]))
    strokes.append(drawPoints([p3, p6]))
    #~
    return strokes

def smoothStroke(stroke=None):
    if not stroke:
        stroke = getSelectedStroke()
    points = stroke.points
    #~
    weight = 18
    scale = 1.0 / (weight + 2)
    nPointsMinusTwo = len(points) - 2
    lower = 0
    upper = 0
    center = 0
    #~
    for i in range(1, nPointsMinusTwo):
        lower = points[i-1].co
        center = points[i].co
        upper = points[i+1].co
        #~
        center.x = (lower.x + weight * center.x + upper.x) * scale
        center.y = (lower.y + weight * center.y + upper.y) * scale
    
def splitStroke(stroke=None):
    if not stroke:
        stroke = getSelectedStroke()    
    points = stroke.points
    co = []
    pressure = []
    strength = []
    #~
    for i in range(1, len(points), 2):
        center = (points[i].co.x, points[i].co.y, points[i].co.z)
        lower = (points[i-1].co.x, points[i-1].co.y, points[i-1].co.z)
        x = (center[0] + lower[0]) / 2
        y = (center[1] + lower[1]) / 2
        z = (center[2] + lower[2]) / 2
        p = (x, y, z)
        #~
        co.append(lower)
        co.append(p)
        co.append(center)
        #~
        pressure.append(points[i-1].pressure)
        pressure.append((points[i-1].pressure + points[i].pressure) / 2)
        pressure.append(points[i].pressure)
        #~
        strength.append(points[i-1].strength)
        strength.append((points[i-1].strength + points[i].strength) / 2)
        strength.append(points[i].strength)
    #~
    points.add(len(co) - len(points))
    for i in range(0, len(points)):
        createPoint(stroke, i, co[i], pressure[i], strength[i])

def refine(stroke=None, splitReps=2, smoothReps=10):
    if not stroke:
        stroke = getSelectedStroke()    
    points = stroke.points
    #~
    for i in range(0, splitReps):
        splitStroke(stroke)  
        smoothStroke(stroke)  
    #~
    for i in range(0, smoothReps - splitReps):
        smoothStroke(stroke)    


# * * * * * * * * * * * * * * * * * * * * * * * * * *
# * * * * * * * * * * * * * * * * * * * * * * * * * *
# * * * * * * * * * * * * * * * * * * * * * * * * * *

# 7 of 9. SHORTCUTS

def mf():
    dn()
    gpMesh(_resolution=1, _bevelResolution=0, _singleFrame=True)

def gp():
    dn()
    gpMeshPreview()

def gs():
    gpMesh(_singleFrame=True)
	
def gb():
    dn()
    gpMesh(_bakeMesh=True)

def gj():
    dn()
    gpMesh(_joinMesh=True)

def gpMeshPreview():
    # mesh curves faster but messier
    gpMesh(_resolution=1, _bevelResolution=0)

def gpMeshFinal():
    # mesh curves slower but nicer
    gpMesh(_resolution=1, _bevelResolution=1, _bakeMesh=True)

def gpMeshCubes():
    gpMesh(_resolution=1, _bevelResolution=0, _bakeMesh=True, _remesh=True)

def gpMeshColor():
    gpMesh(_resolution=1, _bevelResolution=0, _bakeMesh=True, _vertexColors=True)

def gpMeshBackground():
    gpMesh(_animateFrames=False, _bakeMesh=True, _thickness=0.008)

def gpJoinTest():
    dn()
    gpMesh(_bakeMesh=True, _joinMesh=True)

def rbUnity(fileName):
    readBrushStrokes("C:\\Users\\nick\\Documents\\GitHub\\LightningArtist\\latkUnity\\latkVive\\Assets\\" + fileName)

rb = readBrushStrokes
wb = writeBrushStrokes

def up():
    makeParent(unParent=True)

def ss():
    return select()[0]

def dn():
    deleteName(_name="crv_ob")
    deleteName(_name="caps_ob")

c = changeColor
a = alignCamera
s = select
d = delete
j = joinObjects
df = deleteFromAllFrames
spl = splitLayer
cplf = checkLayersAboveFrameLimit

splf = splitLayersAboveFrameLimit

# * * * * * * * * * * * * * * * * * * * * * * * * * *
# * * * * * * * * * * * * * * * * * * * * * * * * * *
# * * * * * * * * * * * * * * * * * * * * * * * * * *

# 8 of 9. TESTS

def testStroke():
    gp = getActiveGp()
    palette = getActivePalette()
    color = getActiveColor()
    color.color = (1.0, 10.0, 0.0)
    layer = gp.layers.new("TestLayer")
    frame = layer.frames.new(bpy.context.scene.frame_current)
    stroke = frame.strokes.new(color.name)
    stroke.draw_mode = "3DSPACE"
    stroke.points.add(2)
    createPoint(stroke, 0, (0,0,0))
    createPoint(stroke, 1, (100,100,0))

def testJson():
    readFilePath = "/Users/nick/Projects/animations/"
    readFileName = "new_test.json"
    with open(readFilePath + readFileName) as data_file:    
        data = json.load(data_file)
        print("Read " + str(len(data["grease_pencil"][0]["layers"][0]["frames"])) + " frames on first layer.")
        print("First color: " + str(data["grease_pencil"][0]["layers"][0]["frames"][0]["strokes"][0]["color"]))
        print("First point: " + str(data["grease_pencil"][0]["layers"][0]["frames"][0]["strokes"][0]["points"][0]))

def testDrawPoints():
    drawPoints([(0,0,0),(1,1,1),(0,1,0),(0,0,0)])
    
# * * * * * * * * * * * * * * * * * * * * * * * * * *
# * * * * * * * * * * * * * * * * * * * * * * * * * *
# * * * * * * * * * * * * * * * * * * * * * * * * * *

# 9 of 9. UI

class ImportLatk(bpy.types.Operator, ImportHelper):
    """Load a Latk File"""
    bl_idname = "import_scene.latk"
    bl_label = "Import Latk"
    bl_options = {'PRESET', 'UNDO'}

    filename_ext = ".json"
    filter_glob = StringProperty(
            default="*.latk;*.json;*.zip",
            options={'HIDDEN'},
            )

    def execute(self, context):
        import latk as la
        keywords = self.as_keywords(ignore=("axis_forward", "axis_up", "filter_glob", "split_mode"))
        if bpy.data.is_saved and context.user_preferences.filepaths.use_relative_paths:
            import os
            #keywords["relpath"] = os.path.dirname(bpy.data.filepath)
        #~
        la.readBrushStrokes(**keywords)
        return {'FINISHED'}

    '''
    def execute(self, context):
        # print("Selected: " + context.active_object.name)
        from . import import_obj

        if self.split_mode == 'OFF':
            self.use_split_objects = False
            self.use_split_groups = False
        else:
            self.use_groups_as_vgroups = False

        keywords = self.as_keywords(ignore=("axis_forward",
                                            "axis_up",
                                            "filter_glob",
                                            "split_mode",
                                            ))

        global_matrix = axis_conversion(from_forward=self.axis_forward,
                                        from_up=self.axis_up,
                                        ).to_4x4()
        keywords["global_matrix"] = global_matrix

        if bpy.data.is_saved and context.user_preferences.filepaths.use_relative_paths:
            import os
            keywords["relpath"] = os.path.dirname(bpy.data.filepath)

        return import_obj.load(context, **keywords)

    def draw(self, context):
        layout = self.layout
    '''

class ExportLatkJson(bpy.types.Operator, ExportHelper): # TODO combine into one class
    """Save a Latk Json File"""

    bake = BoolProperty(name="Bake Frames", description="Bake Keyframes to All Frames", default=True)

    bl_idname = "export_scene.latkjson"
    bl_label = 'Export Latk Json'
    bl_options = {'PRESET'}

    filename_ext = ".json"

    filter_glob = StringProperty(
            default="*.json",
            options={'HIDDEN'},
            )

    def execute(self, context):
        import latk as la
        keywords = self.as_keywords(ignore=("axis_forward", "axis_up", "filter_glob", "split_mode", "check_existing", "bake"))
        if bpy.data.is_saved and context.user_preferences.filepaths.use_relative_paths:
            import os
            #keywords["relpath"] = os.path.dirname(bpy.data.filepath)
        #~
        keywords["bake"] = self.bake
        #~
        la.writeBrushStrokes(**keywords, zipped=False)
        return {'FINISHED'}

class ExportLatk(bpy.types.Operator, ExportHelper):  # TODO combine into one class
    """Save a Latk File"""

    bake = BoolProperty(name="Bake Frames", description="Bake Keyframes to All Frames", default=True)

    bl_idname = "export_scene.latk"
    bl_label = 'Export Latk'
    bl_options = {'PRESET'}

    filename_ext = ".latk"

    filter_glob = StringProperty(
            default="*.latk",
            options={'HIDDEN'},
            )

    def execute(self, context):
        import latk as la
        keywords = self.as_keywords(ignore=("axis_forward", "axis_up", "filter_glob", "split_mode", "check_existing", "bake"))
        if bpy.data.is_saved and context.user_preferences.filepaths.use_relative_paths:
            import os
            #keywords["relpath"] = os.path.dirname(bpy.data.filepath)
        #~
        keywords["bake"] = self.bake
        #~
        la.writeBrushStrokes(**keywords, zipped=True)
        return {'FINISHED'}

    '''
    path_mode = path_reference_mode

    check_extension = True

    def execute(self, context):
        from . import export_obj

        from mathutils import Matrix
        keywords = self.as_keywords(ignore=("axis_forward",
                                            "axis_up",
                                            "global_scale",
                                            "check_existing",
                                            "filter_glob",
                                            ))

        global_matrix = (Matrix.Scale(self.global_scale, 4) *
                         axis_conversion(to_forward=self.axis_forward,
                                         to_up=self.axis_up,
                                         ).to_4x4())

        keywords["global_matrix"] = global_matrix
        return export_obj.save(context, **keywords)
    '''

# ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ 

class ImportNorman(bpy.types.Operator, ImportHelper):
    """Load a Norman File"""
    bl_idname = "import_scene.norman"
    bl_label = "Import Norman"
    bl_options = {'PRESET', 'UNDO'}

    filename_ext = ".json"
    filter_glob = StringProperty(
            default="*.json",
            options={'HIDDEN'},
            )

    def execute(self, context):
        import latk as la
        keywords = self.as_keywords(ignore=("axis_forward", "axis_up", "filter_glob", "split_mode"))
        if bpy.data.is_saved and context.user_preferences.filepaths.use_relative_paths:
            import os
            #keywords["relpath"] = os.path.dirname(bpy.data.filepath)
        #~
        la.importNorman(**keywords)
        return {'FINISHED'} 

class ImportGml(bpy.types.Operator, ImportHelper):
    """Load a Gml File"""
    bl_idname = "import_scene.gml"
    bl_label = "Import Gml"
    bl_options = {'PRESET', 'UNDO'}

    filename_ext = ".gml"
    filter_glob = StringProperty(
            default="*.gml",
            options={'HIDDEN'},
            )

    splitStrokes = BoolProperty(name="Split Strokes", description="Split Strokes on Layers", default=True)

    def execute(self, context):
        import latk as la
        keywords = self.as_keywords(ignore=("axis_forward", "axis_up", "filter_glob", "split_mode", "splitStrokes"))
        if bpy.data.is_saved and context.user_preferences.filepaths.use_relative_paths:
            import os
            #keywords["relpath"] = os.path.dirname(bpy.data.filepath)
        #~
        keywords["splitStrokes"] = self.splitStrokes
        #~
        la.gmlParser(**keywords)
        return {'FINISHED'} 

class ExportGml(bpy.types.Operator, ExportHelper):
    """Save an SVG SMIL File"""

    bl_idname = "export_scene.gml"
    bl_label = 'Export Gml'
    bl_options = {'PRESET'}

    filename_ext = ".gml"
    filter_glob = StringProperty(
            default="*.gml",
            options={'HIDDEN'},
            )

    make2d = BoolProperty(name="Make 2D", description="Project Coordinates to Camera View", default=True)

    def execute(self, context):
        import latk as la
        #keywords = self.as_keywords(ignore=("axis_forward", "axis_up", "filter_glob", "split_mode", "check_existing", "bake"))
        keywords = self.as_keywords(ignore=("axis_forward", "axis_up", "filter_glob", "split_mode", "check_existing"))
        if bpy.data.is_saved and context.user_preferences.filepaths.use_relative_paths:
            import os
            #keywords["relpath"] = os.path.dirname(bpy.data.filepath)
        #~
        keywords["make2d"] = self.make2d
        #~
        la.writeGml(**keywords)
        return {'FINISHED'} 

class ExportSvg(bpy.types.Operator, ExportHelper):
    """Save an SVG SMIL File"""

    bl_idname = "export_scene.svg"
    bl_label = 'Export Svg'
    bl_options = {'PRESET'}

    filename_ext = ".svg"
    filter_glob = StringProperty(
            default="*.svg",
            options={'HIDDEN'},
            )

    #bake = BoolProperty(name="Bake Frames", description="Bake Keyframes to All Frames", default=True)

    def execute(self, context):
        import latk as la
        #keywords = self.as_keywords(ignore=("axis_forward", "axis_up", "filter_glob", "split_mode", "check_existing", "bake"))
        keywords = self.as_keywords(ignore=("axis_forward", "axis_up", "filter_glob", "split_mode", "check_existing"))
        if bpy.data.is_saved and context.user_preferences.filepaths.use_relative_paths:
            import os
            #keywords["relpath"] = os.path.dirname(bpy.data.filepath)
        #~
        #keywords["bake"] = self.bake
        #~
        la.writeSvg(**keywords)
        return {'FINISHED'} 

class ExportPainter(bpy.types.Operator, ExportHelper):
    """Save an SVG SMIL File"""

    bl_idname = "export_scene.painter"
    bl_label = 'Export Painter'
    bl_options = {'PRESET'}

    filename_ext = ".txt"
    filter_glob = StringProperty(
            default="*.txt",
            options={'HIDDEN'},
            )

    #bake = BoolProperty(name="Bake Frames", description="Bake Keyframes to All Frames", default=True)

    def execute(self, context):
        import latk as la
        #keywords = self.as_keywords(ignore=("axis_forward", "axis_up", "filter_glob", "split_mode", "check_existing", "bake"))
        keywords = self.as_keywords(ignore=("axis_forward", "axis_up", "filter_glob", "split_mode", "check_existing"))
        if bpy.data.is_saved and context.user_preferences.filepaths.use_relative_paths:
            import os
            #keywords["relpath"] = os.path.dirname(bpy.data.filepath)
        #~
        #keywords["bake"] = self.bake
        #~
        la.writePainter(**keywords)
        return {'FINISHED'} 

def menu_func_import(self, context):
    self.layout.operator(ImportLatk.bl_idname, text="Latk Animation (.latk, .json)")
    self.layout.operator(ImportGml.bl_idname, text="Latk - GML (.gml)")
    self.layout.operator(ImportNorman.bl_idname, text="Latk - Norman (.json)")

def menu_func_export(self, context):
    self.layout.operator(ExportLatkJson.bl_idname, text="Latk Animation (.json)")
    self.layout.operator(ExportLatk.bl_idname, text="Latk Animation (.latk)")
    #self.layout.operator(ExportGml.bl_idname, text="Latk - GML (.gml)")
    self.layout.operator(ExportSvg.bl_idname, text="Latk - SVG SMIL (.svg)")
    self.layout.operator(ExportPainter.bl_idname, text="Latk - Corel Painter (.txt)")

def register():
    bpy.utils.register_module(__name__)

    bpy.types.INFO_MT_file_import.append(menu_func_import)
    bpy.types.INFO_MT_file_export.append(menu_func_export)

def unregister():
    bpy.utils.unregister_module(__name__)

    bpy.types.INFO_MT_file_import.remove(menu_func_import)
    bpy.types.INFO_MT_file_export.remove(menu_func_export)

if __name__ == "__main__":
    register()

# * * * * * * * * * * * * * * * * * * * * * * * * * *
# * * * * * * * * * * * * * * * * * * * * * * * * * *
# * * * * * * * * * * * * * * * * * * * * * * * * * *

# END
