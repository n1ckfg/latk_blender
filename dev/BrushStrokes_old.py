# http://blender.stackexchange.com/questions/24694/query-grease-pencil-strokes-from-python

from mathutils import *
import json

def writeBrushStrokes():
    gp = bpy.context.scene.grease_pencil
    globalScale = Vector((0.1, 0.1, 0.1))
    globalOffset = Vector((0, 0, 0))
    useScaleAndOffset = True
    numPlaces = 7
    roundValues = True
    #writeFilePath = "C:\\Users\\Public\\Temp\\"
    writeFilePath = "/Users/nick/Projects/LightningArtist/LightningArtistJS/animations/"
    writeFileName = "dino"
    writeFileType = "json"
    sb = ""
    #.
    for f in range(0, len(gp.layers)):
        layer = gp.layers[f]
        for h in range(0, len(layer.frames)):
            currentFrame = h
            goToFrame(h)
            sb += "        [" + "\n"
            for i in range(0, len(layer.frames[currentFrame].strokes)):
                sb += "            [" + "\n"
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
                        x = -(point.x * globalScale.x) + globalOffset.x
                        y = (point.z * globalScale.y) + globalOffset.y
                        z = (point.y * globalScale.z) + globalOffset.z
                    else:
                        x = -point.x
                        y = point.z
                        z = point.y
                    #.
                    if roundValues == True:
                        sb += "                {\"x\":" + roundVal(x, numPlaces) + ", \"y\":" + roundVal(y, numPlaces) + ", \"z\":" + roundVal(z, numPlaces)
                    else:
                        sb += "                {\"x\":" + str(x) + ", \"y\":" + str(y) + ", \"z\":" + str(z)                    
                    #.
                    if j == len(layer.frames[currentFrame].strokes[i].points) - 1:
                        sb += "}" + "\n"
                    else:
                        sb += "}," + "\n"
                if i == len(layer.frames[currentFrame].strokes) - 1:
                    sb += "            ]" + "\n"
                else:
                    sb += "            ]," + "\n"
            if h == len(layer.frames) - 1:
                sb += "        ]" + "\n"
            else:
                sb += "        ]," + "\n"
        #.
        s = "{" + "\n" 
        s += "    \"start_frame\":" + str(0) + "," + "\n"
        s += "    \"loop\":" + str(False).lower() + "," + "\n"
        s += "    \"brushstrokes\":[" + "\n" + sb + "    ]" + "\n" + "}" + "\n"
        #.
        if (len(gp.layers) == 1):
            url = writeFilePath + writeFileName + "." + writeFileType
        else:
            url = writeFilePath + writeFileName + str(f + 1) + "." + writeFileType
        #.
        with open(url, "w") as f:
            f.write(s)
            f.closed
        print("Wrote " + url)

def readBrushStrokes():
    gp = getActiveGp()
    '''
    gp = bpy.data.grease_pencil.new("My GPencil")
    scene = bpy.context.scene
    scene.grease_pencil = gp
    '''
    #scene.frame_set(5) # ensure we'll see the stroke (set to frame 5 below)
    layer = gp.layers.new("Name for new layer", set_active=True)
    layer.info # note: it's not layer.name!
    #layer.color = (1, 0.3, 0) #new API
    palette = getActivePalette()
    #.
    globalScale = Vector((10, 10, 10))
    globalOffset = Vector((0, 0, 0))
    useScaleAndOffset = True
    #.
    #readFilePath = "C:\\Users\\Public\\Temp\\"
    readFilePath = "/Users/nick/Projects/LightningArtist/LightningArtistJS/animations/"
    readFileName = "current.json"
    #.
    with open(readFilePath + readFileName) as data_file:    
        data = json.load(data_file)
        print("Read " + str(len(data["brushstrokes"])) + " frames.")
    #.
    for i in range(0, len(data["brushstrokes"])):
        frame = layer.frames.new(i) # frame number 5
        for j in range(0, len(data["brushstrokes"][i])):
            stroke = frame.strokes.new(getActiveColor().name)
            stroke.draw_mode = "3DSPACE" # either of ("SCREEN", "3DSPACE", "2DSPACE", "2DIMAGE")
            stroke.points.add(len(data["brushstrokes"][i][j])) # add 4 points
            #stroke.points[0].co = (..., ..., ...) # set 1st point's location
            #stroke.points.foreach_set("co", (0,0,0,0,0,4,0,6,4,8,6,4)) # set all at once efficiently
            for l in range(0, len(data["brushstrokes"][i][j])):
                #print(data["brushstrokes"][i][j][l])
                x = 0.0
                y = 0.0
                z = 0.0
                if useScaleAndOffset == True:
                    x = (data["brushstrokes"][i][j][l]["x"] * globalScale.x) + globalOffset.x
                    y = (data["brushstrokes"][i][j][l]["z"] * globalScale.y) + globalOffset.y
                    z = (data["brushstrokes"][i][j][l]["y"] * globalScale.z) + globalOffset.z
                else:
                    x = data["brushstrokes"][i][j][l]["x"]
                    y = data["brushstrokes"][i][j][l]["z"]
                    z = data["brushstrokes"][i][j][l]["y"]
                #stroke.points[l].co = (x, y, z)
                createPoint(stroke, l, (x, y, z))

rb = readBrushStrokes
wb = writeBrushStrokes

# ~ ~ ~ ~ ~ ~ ~ ~ 
def roundVal(a, b):
    formatter = "{0:." + str(b) + "f}"
    return formatter.format(a)

def frame_to_time(frame_number):
    scene = bpy.context.scene
    fps = scene.render.fps
    fps_base = scene.render.fps_base
    raw_time = (frame_number - 1) / fps
    return round(raw_time, 3)

def bakeFrames(end):
    start = 1
    end += 1
    scene = bpy.context.scene
    gp = scene.grease_pencil
    layer = gp.layers[0]    
    for i in range(start, end):
        try:
            layer.frames.new(i)
        except:
            print ("Frame " + str(i) + " already exists.")

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

def w():
    bakeFrames(144)
    wb()

def goToFrame(_index):
    bpy.context.scene.frame_current = _index
    bpy.context.scene.frame_set(_index)
    return bpy.context.scene.frame_current

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

def moveShot(shot, x, y, z):
    gp = bpy.context.scene.grease_pencil
    target = chooseShot(shot)
    for g in range(target[0], target[1]+1):
        for f in range(0, len(gp.layers)):
            layer = gp.layers[f]
            currentFrame = g
            for i in range(0, len(layer.frames[currentFrame].strokes)):
                for j in range(0, len(layer.frames[currentFrame].strokes[i].points)):
                    layer.frames[currentFrame].strokes[i].points[j].co.x += x
                    layer.frames[currentFrame].strokes[i].points[j].co.y += y
                    layer.frames[currentFrame].strokes[i].points[j].co.z += z

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

def createPoint(_stroke, _index, _point):
    _stroke.points[_index].co = _point
    _stroke.points[_index].select = True
    _stroke.points[_index].pressure = 1
    _stroke.points[_index].strength = 1

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
