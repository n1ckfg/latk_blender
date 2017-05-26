# 3 of 8. READ / WRITE

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
                exporter(manualSelect=True, fileType="fbx", name=exportName)
                sketchFabList.append("0.083 " + exportName + ".fbx" + "\r")
                sketchFabListNum.append(float(exportName.split("_")[len(exportName.split("_"))-1]))
                break
    if (sketchFab==True):
        #sketchFabList.reverse()
        #~
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

def exporter(name="test", url=None, winDir=False, manualSelect=False, fileType="fbx"):
    if not url:
        url = getFilePath()
        if (winDir==True):
            url += "\\"
        else:
            url += "/"
    #~
    if (manualSelect == True):
            if (fileType=="fbx"):
                bpy.ops.export_scene.fbx(filepath=url + name + ".fbx", use_selection=True)
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
                bpy.ops.export_scene.fbx(filepath=url + name + "_" + str(j) + ".fbx", use_selection=True)
            else:
                bpy.ops.export_scene.obj(filepath=url + name + "_" + str(j) + ".obj", use_selection=True)


def importAppend(blendfile, section, obj, winDir=False):
    # http://blender.stackexchange.com/questions/38060/how-to-link-append-with-a-python-script
    #blendfile = "D:/path/to/the/repository.blend"
    #section   = "\\Action\\"
    #obj    = "myaction"
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

def writeBrushStrokes(filepath=None, bake=True):
    url = filepath # compatibility with gui keywords
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
                        pressure = 1.0
                        strength = 1.0
                        #.
                        point = layer.frames[currentFrame].strokes[i].points[j].co
                        pressure = layer.frames[currentFrame].strokes[i].points[j].pressure
                        strength = layer.frames[currentFrame].strokes[i].points[j].strength
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
                            sb += "                                        {\"co\": [" + roundVal(x, numPlaces) + ", " + roundVal(y, numPlaces) + ", " + roundVal(z, numPlaces) + "], \"pressure\": " + roundVal(pressure, numPlaces) + ", \"strength\": " + roundVal(strength, numPlaces)
                        else:
                            #sb += "                                       {\"x\":" + str(x) + ", \"y\":" + str(y) + ", \"z\":" + str(z)                    
                            sb += "                                        {\"co\": [" + str(x) + ", " + str(y) + ", " + str(z) + "], \"pressure\": " + pressure + ", \"strength\": " + strength                  
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
    #~                
    return {'FINISHED'}
    
def readBrushStrokes(filepath=None):
    url = filepath # compatibility with gui keywords
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

#def writeSvg(strokes=None, name="test.svg", minLineWidth=3, camera=None):
#def writeSvg(filepath=None, minLineWidth=3, camera=None, fps=12, start=0, end=73):
def writeSvg(filepath=None):
    minLineWidth=3
    camera=None
    fps=None
    start=None
    end=None
    #~
    #if not strokes:
        #strokes = getActiveFrame().strokes
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
    svg.append("<?xml version=\"1.0\" encoding=\"utf-8\"?>" + "\r");
    svg.append("<!DOCTYPE svg PUBLIC \"-//W3C//DTD SVG 1.1//EN\" \"http://www.w3.org/Graphics/SVG/1.1/DTD/svg11.dtd\">" + "\r")
    svg.append("<svg version=\"1.1\" id=\"Layer_1\" xmlns=\"http://www.w3.org/2000/svg\" xmlns:xlink=\"http://www.w3.org/1999/xlink\" x=\"0px\" y=\"0px\"" + "\r")
    svg.append("\t" + "width=\"" + str(sW) + "px\" height=\"" + str(sH) + "px\" viewBox=\"0 0 " + str(sW) + " " + str(sH) + "\" enable-background=\"new 0 0 " + str(sW) + " " + str(sH) +"\" xml:space=\"preserve\">" + "\r")
    #~
    # BODY
    for layer in gp.layers:
        layerInfo = layer.info.replace(" ", "_").replace(".", "_")
        svg.append("\t" + "<g id=\"" + layerInfo + "\">" + "\r")
        for i, frame in enumerate(layer.frames):
            svg.append("\t\t" + "<g id=\"" + layerInfo + "_frame" + str(i) + "\">" + "\r")
            palette = getActivePalette()
            for stroke in frame.strokes:
                width = stroke.line_width
                if (width == None or width < minLineWidth):
                    width = minLineWidth
                #cStroke = (0,0,0,1)
                #cFill = (1,1,1,0)
                #try:
                color = palette.colors[stroke.colorname]
                print("found color: " + color.name)
                cStroke = (color.color[0], color.color[1], color.color[2], color.alpha)
                cFill = (color.fill_color[0], color.fill_color[1], color.fill_color[2], color.fill_alpha)
                #except:
                    #print("color error")
                    #pass
                svg.append("\t\t\t" + svgStroke(points=stroke.points, stroke=(cStroke[0], cStroke[1], cStroke[2]), fill=(cFill[0], cFill[1], cFill[2]), strokeWidth=minLineWidth, strokeOpacity=cStroke[3], fillOpacity=cFill[3], camera=camera) + "\r")
            #~
            idTagBase = "anim_" + layerInfo + "_frame"
            idTag = idTagBase + str(i)
            prevIdTag = "0s"
            if (i>0):
                prevIdTag = idTagBase + str(i-1) + ".end"
            svg.append("\t\t\t" + svgAnimate(frame=frame.frame_number, fps=fps, duration=duration, idTag=idTag, prevIdTag=prevIdTag) + "\r")
            svg.append("\t\t" + "</g>" + "\r")
        svg.append("\t" + "</g>" + "\r")
    #~
    # FOOTER
    svg.append("</svg>" + "\r")
    #~
    writeTextFile(url, svg)

def svgAnimate(frame=0, fps=12, duration=10, idTag=None, prevIdTag=None):
    keyIn = (float(frame) / float(fps)) / float(duration)
    keyOut = keyIn + (1.0/float(fps))
    returns = "<animate id=\"" + str(idTag) + "\" attributeName=\"display\" values=\"none;inline;none;none\" keyTimes=\"0;" + str(keyIn) + ";" + str(keyOut) + ";1\" dur=\"" + str(duration) + "s\" begin=\"0s\" repeatCount=\"indefinite\"/>"
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

#def gmlParser(filepath=None, globalScale=(0.1,0.1,0.1), useTime=True):
def gmlParser(filepath=None, splitStrokes=True):
    globalScale = (1, 1, 1)
    screenBounds = (1, 1, 1)
    up = (0, 1, 0)
    useTime = True
    minStrokeLength=3
    #splitStrokes = True
    #~
    masterLayerList = []
    tree = etree.parse(filepath)
    root = tree.getroot()
    '''
    if (root.tag.lower() != "gml"):
        print("Not a GML file.")
        return
    '''
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
    #if header:
        #pass
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
        #layer = gp.layers.new("GML_Tag" + str(i+1) + "_stroke" + str(j+1))
        #gp.layers.active = layer
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
            #if (yUp==False):
            gmlPoints.append((x,y,z,time))
            #else:
                #gmlPoints.append((-x,z,y,time))
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

# * * * * * * * * * * * * * * * * * * * * * * * * * *
# * * * * * * * * * * * * * * * * * * * * * * * * * *
# * * * * * * * * * * * * * * * * * * * * * * * * * *

