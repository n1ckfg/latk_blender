# * * * * * * * * * * * * *
# LightningArtist Toolkit *
# by Nick Fox-Gieg        *
# fox-gieg.com            *
# * * * * * * * * * * * * * 

bl_info = {
    "name": "LightningArtist Toolkit", 
    "category": "Animation"
}

def register():
	pass

def unregister():
	pass

import bpy
from mathutils import *
from math import sqrt
import json
import re
from bpy_extras.io_utils import unpack_list
#from curve_simplify import *
import random

# * * * * * * * * * * * * * * * * * * * * * * * * * *
# * * * * * * * * * * * * * * * * * * * * * * * * * *
# * * * * * * * * * * * * * * * * * * * * * * * * * *

def getDistance(v1, v2):
    return sqrt( (v1[0] - v2[0])**2 + (v1[1] - v2[1])**2 + (v1[2] - v2[2])**2)
    
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
        original_type = bpy.context.area.type
        print("Current context: " + original_type)
        bpy.context.area.type = "VIEW_3D"
        #~
        if (fixTransforms==True):
            bpy.ops.object.parent_set(type='OBJECT', xmirror=False, keep_transform=False) 
        else:   
            bpy.ops.object.parent_set(type='OBJECT', xmirror=False, keep_transform=True) 
        #~
        bpy.context.area.type = original_type 
        print("Parent is " + target[len(target)-1].name)   

def keyTransform(_obj, _frame):
    #_obj.location = _pos
    #_obj.rotation_quaternion = _rot
    #_obj.scale = _scale
    _obj.keyframe_insert(data_path="location", frame=_frame) 
    _obj.keyframe_insert(data_path="rotation_euler", frame=_frame) 
    _obj.keyframe_insert(data_path="scale", frame=_frame)
    #bpy.context.scene.update()

def keyMatrix(_obj, _frame):
    _obj.keyframe_insert(data_path="matrix_world", frame=_frame) 

def select(target=None):
    if not target:
        target=bpy.context.selected_objects;
    print("selected " + str(target))
    return target

'''
def move(x, y, z, target=None):
    if not target:
        target = select()
    bpy.ops.object.select_all(action='DESELECT')
    for i in range(0, len(target)):
        bpy.data.objects[target[i].name].select = True
        bpy.ops.transform.translate(value=(x, y, z))

def moveTo(x, y, z, target=None):
    if not target:
        target = select()
    bpy.ops.object.select_all(action='DESELECT')
    for i in range(0, len(target)):
        bpy.data.objects[target[i].name].select = True
        bpy.ops.transform.location = str((x, y, z))
'''

'''
def delete(_obj, clearMemory=False):
    bpy.ops.object.mode_set(mode = 'OBJECT')
    #if not target:
        #target = s()
    #for _obj in target:
    if (clearMemory==True):
        mesh = bpy.data.meshes[_obj.name]
        mesh.user_clear()
        bpy.data.meshes.remove(mesh)
    bpy.ops.object.select_all(action='DESELECT')
    bpy.data.objects[_obj.name].select = True
    bpy.ops.object.delete()   
    #print("Deleted " + _obj.name)  
'''

def delete(_obj):
    #oldMode = bpy.context.mode
    #bpy.ops.object.mode_set(mode='OBJECT')
    bpy.ops.object.select_all(action='DESELECT')
    bpy.data.objects[_obj.name].select = True
    bpy.ops.object.delete()
    #bpy.ops.object.mode_set(mode=oldMode)   

def refresh():
    bpy.context.scene.update()

def matchName(_name):
    returns = []
    for i in range(0, len(bpy.context.scene.objects)):
        obj = bpy.context.scene.objects[i]
        if re.match(r'^' + str(_name) + '', obj.name): # curve object
            returns.append(obj)
    return returns

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
    gp = scene.grease_pencil
    layer = gp.layers[0]    
    for i in range(start, end):
        try:
            layer.frames.new(i)
        except:
            print ("Frame " + str(i) + " already exists.")

def getStartEnd():
    start = bpy.context.scene.frame_start
    end = bpy.context.scene.frame_end + 1
    return start, end

def copyFrame(source, dest):
    scene = bpy.context.scene
    gp = scene.grease_pencil
    layer = gp.layers[0]    
    #.
    frameSource = layer.frames[source]
    frameDest = layer.frames[dest]
    for j in range(0, len(frameSource.strokes)):
        scene.frame_set(source)
        strokeSource = frameSource.strokes[j]
        scene.frame_set(dest)
        strokeDest = frameDest.strokes.new()
        # either of ('SCREEN', '3DSPACE', '2DSPACE', '2DIMAGE')
        strokeDest.draw_mode = '3DSPACE'
        strokeDest.points.add(len(strokeSource.points))
        for l in range(0, len(strokeSource.points)):
            strokeDest.points[l].co = strokeSource.points[l].co

def goToFrame(_index):
    origFrame = bpy.context.scene.frame_current
    bpy.context.scene.frame_current = _index
    bpy.context.scene.frame_set(_index)
    refresh()
    print("Moved from frame " + str(origFrame) + " to " + str(_index))
    return bpy.context.scene.frame_current

def hideFrame(_obj, _frame, _hide):
    _obj.hide = _hide
    _obj.hide_render = _hide
    _obj.keyframe_insert(data_path="hide", frame=_frame) 
    _obj.keyframe_insert(data_path="hide_render", frame=_frame) 

'''
def chooseShot(shot):
    start = 0
    end = 0
    if shot == 1:
        start = 1
        end = 44
    elif shot == 2:
        start = 45
        end = 63
    return [start, end]
'''

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

def fixContext():
    bpy.context.area.type = "VIEW_3D"

def alignCamera():
    original_type = bpy.context.area.type
    print("Current context: " + original_type)
    bpy.context.area.type = "VIEW_3D"
    #~
    # strokes, points, frame
    bpy.ops.view3d.camera_to_view()
    #~
    #bpy.context.area.type = "CONSOLE"
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

def createPoint(_stroke, _index, _point, pressure=1, strength=1):
    _stroke.points[_index].co = _point
    _stroke.points[_index].select = True
    _stroke.points[_index].pressure = pressure
    _stroke.points[_index].strength = strength

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

'''
def pasteToNewLayer():
    frame = getActiveFrame()
    oldStrokes = getSelectedStrokes()
    #~
    for oldStroke in oldStrokes:
        newStroke = frame.strokes.new(oldStroke.color_name)
        newStroke.draw_mode = "3DSPACE" # either of ("SCREEN", "3DSPACE", "2DSPACE", "2DIMAGE")
        newStroke.line_width = oldStroke.line_width
        newStroke.points = oldStroke.points
        #newStroke.points.add(len(oldStroke.points))
        #for j in range(0, len(oldStroke.points)):
            #createPoint(newStroke, j, points[j].co)
'''

def searchMtl(color=None, name="crv"):
    returns = []
    if not color:
        color = getActiveColor().color
    curves = matchName(name)
    for curve in curves:
        if (compareTuple(curve.data.materials[0].diffuse_color, color)):
            returns.append(curve)
    print ("found: " + str(returns))
    return returns

def compareTuple(t1, t2, numPlaces=5):
    if (roundVal(t1[0], numPlaces) == roundVal(t2[0], numPlaces) and roundVal(t1[1], numPlaces) == roundVal(t2[1], numPlaces) and roundVal(t1[2], numPlaces) == roundVal(t2[2], numPlaces)):
        return True
    else:
        return False

def changeMtl(color=(1,1,0), searchColor=None, name="crv"):
    if not searchColor:
        searchColor = getActiveColor().color       
    curves = searchMtl(color=searchColor, name=name)
    print("changed: " + str(curves))
    for curve in curves:
        curve.data.materials[0].diffuse_color = color

def consolidateMtl(name="crv"):
    palette = getActivePalette()
    for color in palette.colors:
        curves = searchMtl(color=color.color, name=name)
        for i in range(1, len(curves)):
            curves[i].data.materials[0] = curves[0].data.materials[0]

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
    #bpy.context.area.type = "CONSOLE"
    bpy.context.area.type = original_type

# ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~
# ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~
# shortcuts

def up():
    makeParent(unParent=True)

def ss():
    return select()[0]

c = changeColor
a = alignCamera
s = select
d = delete
df = deleteFromAllFrames
dn = deleteName

# * * * * * * * * * * * * * * * * * * * * * * * * * *
# * * * * * * * * * * * * * * * * * * * * * * * * * *
# * * * * * * * * * * * * * * * * * * * * * * * * * *

# http://blender.stackexchange.com/questions/24694/query-grease-pencil-strokes-from-python

def writeBrushStrokes(url=None, bake=True):
    #writeFilePath = "C:\\Users\\Public\\Temp\\"
    writeFilePath = "/Users/nick/Projects/LightningArtist/LightningArtistJS/animations/"
    writeFileName = "new_test.json"
    #~
    if(bake == True):
        bakeFrames()
    gp = bpy.context.scene.grease_pencil
    globalScale = Vector((0.1, 0.1, 0.1))
    globalOffset = Vector((0, 0, 0))
    useScaleAndOffset = True
    numPlaces = 7
    roundValues = True
    #~
    sg = "{" + "\n"
    sg += "    \"creator\": \"blender\"," + "\n"
    sg += "    \"grease_pencil\": [" + "\n"
    sg += "        {" + "\n"
    sg += "            \"layers\": [" + "\n"
    sl = ""
    for f in range(0, len(gp.layers)):
        sb = ""
        layer = gp.layers[f]
        for h in range(0, len(layer.frames)):
            currentFrame = h
            goToFrame(h)
            sb += "                        {" + "\n" # one frame
            #sb += "                           \"index\": " + str(h) + ",\n"
            sb += "                            \"strokes\": [" + "\n"
            sb += "                                {" + "\n" # one stroke
            for i in range(0, len(layer.frames[currentFrame].strokes)):
                color = (0,0,0)
                try:
                    color = layer.frames[currentFrame].strokes[i].color.color
                except:
                    pass
                sb += "                                    \"color\": [" + str(color[0]) + ", " + str(color[1]) + ", " + str(color[2])+ "]," + "\n"
                sb += "                                    \"points\": [" + "\n"
                for j in range(0, len(layer.frames[currentFrame].strokes[i].points)):
                    x = 0.0
                    y = 0.0
                    z = 0.0
                    #.
                    point = layer.frames[currentFrame].strokes[i].points[j].co
                    '''
                    if(layer.parent):
                        loc, rot, scale = layer.parent.matrix_world.decompose()
                        point = Vector([(point.x * loc.x * scale.x, point.y * loc.y * scale.y, point.z * loc.z * scale.z])
                    '''
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
                        #sb += "                                       {\"x\":" + roundVal(x, numPlaces) + ", \"y\":" + roundVal(y, numPlaces) + ", \"z\":" + roundVal(z, numPlaces)
                        sb += "                                        {\"co\": [" + roundVal(x, numPlaces) + ", " + roundVal(y, numPlaces) + ", " + roundVal(z, numPlaces) + "]"
                    else:
                        #sb += "                                       {\"x\":" + str(x) + ", \"y\":" + str(y) + ", \"z\":" + str(z)                    
                        sb += "                                        {\"co\": [" + str(x) + ", " + str(y) + ", " + str(z) + "]"                  
                    #~
                    if j == len(layer.frames[currentFrame].strokes[i].points) - 1:
                        sb += "}" + "\n"
                        sb += "                                    ]" + "\n"
                        if (i == len(layer.frames[currentFrame].strokes) - 1):
                            sb += "                                }" + "\n" # last stroke for this frame
                        else:
                            sb += "                                }," + "\n" # end stroke
                            sb += "                                {" + "\n" # begin stroke
                    else:
                        sb += "}," + "\n"
                if i == len(layer.frames[currentFrame].strokes) - 1:
                    sb += "                            ]" + "\n"
            if h == len(layer.frames) - 1:
                sb += "                        }" + "\n"
            else:
                sb += "                        }," + "\n"
        #~
        sf = "                {" + "\n" 
        sf += "                    \"name\": \"" + layer.info + "\"," + "\n"
        #s += "                    \"loop_in\":" + str(0) + "," + "\n"
        #s += "                    \"loop_out\":" + str(0) + "," + "\n"
        #s += "                    \"loop\":" + str(False).lower() + "," + "\n"
        sf += "                    \"frames\": [" + "\n" + sb + "                    ]" + "\n"
        if (f == len(gp.layers)-1):
            sf += "                }" + "\n"
        else:
            sf += "                }," + "\n"
        sl += sf
        #~
    sg += sl
    sg += "            ]" + "\n"
    sg += "        }"+ "\n"
    sg += "    ]"+ "\n"
    sg += "}"+ "\n"
    #if (len(gp.layers) == 1):
    if (url==None):
        url = writeFilePath + writeFileName
    #else:
        #url = writeFilePath + layer.info + str(f + 1) + "." + writeFileType
    #~
    with open(url, "w") as f:
        f.write(sg)
        f.closed
    print("Wrote " + url)

def readBrushStrokes(url=None):
    #readFilePath = "C:\\Users\\Public\\Temp\\"
    readFilePath = "/Users/nick/Projects/LightningArtist/LightningArtistJS/animations/"
    readFileName = "new_test.json"
    #~
    gp = getActiveGp()
    '''
    gp = bpy.data.grease_pencil.new("My GPencil")
    scene = bpy.context.scene
    scene.grease_pencil = gp
    '''
    #~
    globalScale = Vector((10, 10, 10))
    globalOffset = Vector((0, 0, 0))
    useScaleAndOffset = True
    #~
    if (url==None):
        url = readFilePath + readFileName
    with open(url) as data_file:    
        data = json.load(data_file)
        print("Read " + str(len(data["grease_pencil"][0]["layers"][0]["frames"])) + " frames on first layer.")
    #~
    #scene.frame_set(5) # ensure we'll see the stroke (set to frame 5 below)
    for h in range(0, len(data["grease_pencil"][0]["layers"])):
        layer = gp.layers.new(data["grease_pencil"][0]["layers"][h]["name"], set_active=True)
        palette = getActivePalette()    
        #layer.info # note: it's not layer.name!
        #layer.color = (1, 0.3, 0) #new API
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
                #stroke.points[0].co = (..., ..., ...) # set 1st point's location
                #stroke.points.foreach_set("co", (0,0,0,0,0,4,0,6,4,8,6,4)) # set all at once efficiently
                for l in range(0, len(data["grease_pencil"][0]["layers"][h]["frames"][i]["strokes"][j]["points"])):
                    #print(data["frames"][i][j][l])
                    x = 0.0
                    y = 0.0
                    z = 0.0
                    if useScaleAndOffset == True:
                        x = (data["grease_pencil"][0]["layers"][h]["frames"][i]["strokes"][j]["points"][l]["co"][0] * globalScale.x) + globalOffset.x
                        y = (data["grease_pencil"][0]["layers"][h]["frames"][i]["strokes"][j]["points"][l]["co"][2] * globalScale.y) + globalOffset.y
                        z = (data["grease_pencil"][0]["layers"][h]["frames"][i]["strokes"][j]["points"][l]["co"][1] * globalScale.z) + globalOffset.z
                    else:
                        x = data["grease_pencil"][0]["layers"][h]["frames"][i]["strokes"][j]["points"][l]["co"][0]
                        y = data["grease_pencil"][0]["layers"][h]["frames"][i]["strokes"][j]["points"][l]["co"][2]
                        z = data["grease_pencil"][0]["layers"][h]["frames"][i]["strokes"][j]["points"][l]["co"][1]
                    #stroke.points[l].co = (x, y, z)
                    createPoint(stroke, l, (x, y, z))

# ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~
# ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~
# shortcuts

def rbUnity(fileName):
    readBrushStrokes("C:\\Users\\nick\\Documents\\GitHub\\LightningArtist\\latkUnity\\latkVive\\Assets\\" + fileName)

rb = readBrushStrokes
wb = writeBrushStrokes

# * * * * * * * * * * * * * * * * * * * * * * * * * *
# * * * * * * * * * * * * * * * * * * * * * * * * * *
# * * * * * * * * * * * * * * * * * * * * * * * * * *

# https://gist.github.com/pcote/1307658
# http://blender.stackexchange.com/questions/7578/extruding-multiple-curves-at-once
# http://blender.stackexchange.com/questions/24694/query-grease-pencil-strokes-from-python
# https://wiki.blender.org/index.php/Dev:Py/Scripts/Cookbook/Code_snippets/Materials_and_textures
# http://blender.stackexchange.com/questions/58676/add-modifier-to-selected-and-another-to-active-object
# http://blenderscripting.blogspot.ca/2011/05/blender-25-python-bezier-from-list-of.html
# http://blender.stackexchange.com/questions/6750/poly-bezier-curve-from-a-list-of-coordinates
# http://blender.stackexchange.com/questions/7047/apply-transforms-to-linked-objects

def gpMesh(_thickness=0.0125, _resolution=1, _bevelResolution=0, _bakeMesh=False, _decimate = 0.1, _curveType="nurbs", _useColors=True, _vertexColors=False, _animateFrames=True, _solidify=False, _subd=0, _remesh=False, _consolidateMtl=True):
    totalStrokes = str(len(getAllStrokes()))
    origParent = None
    start = bpy.context.scene.frame_start
    end = bpy.context.scene.frame_end + 1
    #~
    pencil = getActiveGp()
    palette = getActivePalette()
    #~
    for b in range(0, len(pencil.layers)):
        layer = pencil.layers[b]
        for c in range(0, len(layer.frames)):
            frameList = []
            for stroke in layer.frames[c].strokes:
                stroke_points = stroke.points
                coords = [ (point.co.x, point.co.y, point.co.z) for point in stroke_points ]
                '''
                coords = []
                if (_minDistance > 0.0):
                    for pp in range(0, len(coordsOrig)):
                        if (pp > 0 and getDistance(coordsOrig[pp], coordsOrig[pp-1]) >= _minDistance):
                            coords.append(coordsOrig[pp])
                else:
                    coords = coordsOrig
                '''
                # * * * * * * * * * * * * * *
                # TODO fix parenting. Here's where the initial transform corrections go.
                if (layer.parent):
                    origParent = layer.parent
                    layer.parent = None
                    #print(layer.parent.name)
                    #layer.parent = None
                    #for coord in coords:
                        #coord = layer.matrix_inverse * Vector(coord)
                # * * * * * * * * * * * * * *                         
                #~
                crv_ob = makeCurve(coords=coords, curveType=_curveType, resolution=_resolution, thickness=_thickness, bevelResolution=_bevelResolution, parent=layer.parent)
                strokeColor = (0.5,0.5,0.5)
                if (_useColors==True):
                    '''
                    try:
                        strokeColor = stroke.color.color
                    except:
                        strokeColor = (0.5,0.5,0.5)
                        print ("error reading color")
                    '''
                    strokeColor = palette.colors[stroke.colorname].color
                mat = bpy.data.materials.new("new_mtl")
                crv_ob.data.materials.append(mat)
                crv_ob.data.materials[0].diffuse_color = strokeColor
                # TODO can you store vertex colors in a curve?
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
                if (_bakeMesh==True or _remesh==True):
                    bpy.ops.object.modifier_add(type='DECIMATE')
                    bpy.context.object.modifiers["Decimate"].ratio = _decimate     
                    meshObj = applyModifiers(crv_ob)
                    #~
                    if (_remesh==True):
                        meshObj = remesher(meshObj)
                    #~
                    if (_vertexColors==True):
                    	colorVertices(meshObj, strokeColor)                        
                    frameList.append(meshObj)    
                else:
                    frameList.append(crv_ob)    
                # * * * * * * * * * * * * * *
                # TODO fix parenting. Here's where the output gets parented to the layer's parent.
                #if (origParent != None):
                    #index = len(frameList)-1
                    #layer.parent = origParent
                    #frameList[index].parent = layer.parent
                if (origParent != None):
                    makeParent([frameList[len(frameList)-1], origParent])
                    layer.parent = origParent
                # * * * * * * * * * * * * * *
                bpy.ops.object.select_all(action='DESELECT')
            #~
            for i in range(0, len(frameList)):
                print(frameList[i].name + " of " + totalStrokes + " total")
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
            #~
            if (_consolidateMtl==True):
                consolidateMtl()

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

def makeCurve(coords, resolution=2, thickness=0.1, bevelResolution=1, curveType="bezier", parent=None):
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

# ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~
# ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~
# shortcuts
def gp():
    dn()
    gpMeshPreview()

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

# * * * * * * * * * * * * * * * * * * * * * * * * * *
# * * * * * * * * * * * * * * * * * * * * * * * * * *
# * * * * * * * * * * * * * * * * * * * * * * * * * *

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

# ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~
# ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~
# shortcuts

# * * * * * * * * * * * * * * * * * * * * * * * * * *
# * * * * * * * * * * * * * * * * * * * * * * * * * *
# * * * * * * * * * * * * * * * * * * * * * * * * * *

# END
