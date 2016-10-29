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
    palette = getActivePalette()
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
            if (len(layer.frames[currentFrame].strokes) > 0):
                sb += "                                {" + "\n" # one stroke
                for i in range(0, len(layer.frames[currentFrame].strokes)):
                    color = (0,0,0)
                    try:
                        #color = layer.frames[currentFrame].strokes[i].color.color
                        color = palette.colors[layer.frames[currentFrame].strokes[i].colorname].color
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
            else:
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

