def getDistance(v1, v2):
    return sqrt( (v1[0] - v2[0])**2 + (v1[1] - v2[1])**2 + (v1[2] - v2[2])**2)
    
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

