# 3 of 10. READ / WRITE

def exportAlembic(url="test.abc"):
    bpy.ops.wm.alembic_export(filepath=url, vcolors=True, face_sets=True, renderable_only=False)

def exportForUnity(filepath=None, sketchFab=True):
    #origFilepath = ""
    #if not filepath:
        #filepath = getFilePath()
    #else:
    filepath = filepath.split(".fbx")[0] + "_"
    rootFilepath = filepath.split(getFileName())[0]
    #~
    start, end = getStartEnd()
    target = matchName("latk")
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
                exportName = exportName.split("latk_")[1]
                exportName = exportName.split("_mesh")[0]
                exporter(url=filepath, manualSelect=True, fileType="fbx", name=exportName, legacyFbx=True)
                sketchFabList.append(str(1.0/getSceneFps()) + " " + getFileName() + "_" + exportName + ".fbx\r") #"0.083 " + exportName + ".fbx\r")
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
        #writeTextFile(filepath + getFileName() + "_" + tempString + ".sketchfab.timeframe", sketchFabList)
        writeTextFile(rootFilepath + "sketchfab.timeframe", sketchFabList)

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

def newFile():
    bpy.ops.wm.read_homefile()

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
def writeBrushStrokes(filepath=None, bake=True, roundValues=True, numPlaces=7, zipped=False):
    url = filepath # compatibility with gui keywords
    #~
    if(bake == True):
        bakeFrames()
    gp = bpy.context.scene.grease_pencil
    globalScale = Vector((0.1, 0.1, 0.1))
    globalOffset = Vector((0, 0, 0))
    useScaleAndOffset = True
    #numPlaces = 7
    #roundValues = True
    palette = getActivePalette()
    #~
    sg = []
    sg.append("{")
    sg.append("\t\"creator\": \"blender\",")
    sg.append("\t\"grease_pencil\": [")
    sg.append("\t\t{")
    sg.append("\t\t\t\"frame_rate\": " + str(getSceneFps()) + ",")
    sg.append("\t\t\t\"layers\": [")
    #~
    sl = []
    for f, layer in enumerate(gp.layers):
        sb = []
        for h, frame in enumerate(layer.frames):
            currentFrame = h
            goToFrame(h)
            sb.append("\t\t\t\t\t\t{") # one frame
            sb.append("\t\t\t\t\t\t\t\"frame_number\": " + str(frame.frame_number) + ",")
            if (layer.parent):
                sb.append("\t\t\t\t\t\t\t\"parent_location\": " + "[" + str(layer.parent.location[0]) + ", " + str(layer.parent.location[1]) + ", " + str(layer.parent.location[2]) + "],")
            sb.append("\t\t\t\t\t\t\t\"strokes\": [")
            if (len(frame.strokes) > 0):
                sb.append("\t\t\t\t\t\t\t\t{") # one stroke
                for i, stroke in enumerate(frame.strokes):
                    color = (0,0,0)
                    alpha = 0.9
                    fill_color = (1,1,1)
                    fill_alpha = 0.0
                    try:
                        col = palette.colors[stroke.colorname]
                        color = col.color
                        alpha = col.alpha 
                        fill_color = col.fill_color
                        fill_alpha = col.fill_alpha
                    except:
                        pass
                    sb.append("\t\t\t\t\t\t\t\t\t\"color\": [" + str(color[0]) + ", " + str(color[1]) + ", " + str(color[2])+ "],")
                    sb.append("\t\t\t\t\t\t\t\t\t\"alpha\": " + str(alpha) + ",")
                    sb.append("\t\t\t\t\t\t\t\t\t\"fill_color\": [" + str(fill_color[0]) + ", " + str(fill_color[1]) + ", " + str(fill_color[2])+ "],")
                    sb.append("\t\t\t\t\t\t\t\t\t\"fill_alpha\": " + str(fill_alpha) + ",")
                    sb.append("\t\t\t\t\t\t\t\t\t\"points\": [")
                    for j, point in enumerate(stroke.points):
                        x = point.co.x
                        y = point.co.z
                        z = point.co.y
                        pressure = 1.0
                        pressure = point.pressure
                        strength = 1.0
                        strength = point.strength
                        #~
                        if useScaleAndOffset == True:
                            x = (x * globalScale.x) + globalOffset.x
                            y = (y * globalScale.y) + globalOffset.y
                            z = (z * globalScale.z) + globalOffset.z
                        #~
                        if roundValues == True:
                            sb.append("\t\t\t\t\t\t\t\t\t\t{\"co\": [" + roundVal(x, numPlaces) + ", " + roundVal(y, numPlaces) + ", " + roundVal(z, numPlaces) + "], \"pressure\": " + roundVal(pressure, numPlaces) + ", \"strength\": " + roundVal(strength, numPlaces))
                        else:
                            sb.append("\t\t\t\t\t\t\t\t\t\t{\"co\": [" + str(x) + ", " + str(y) + ", " + str(z) + "], \"pressure\": " + str(pressure) + ", \"strength\": " + str(strength))                  
                        #~
                        if j == len(stroke.points) - 1:
                            sb[len(sb)-1] +="}"
                            sb.append("\t\t\t\t\t\t\t\t\t]")
                            if (i == len(frame.strokes) - 1):
                                sb.append("\t\t\t\t\t\t\t\t}") # last stroke for this frame
                            else:
                                sb.append("\t\t\t\t\t\t\t\t},") # end stroke
                                sb.append("\t\t\t\t\t\t\t\t{") # begin stroke
                        else:
                            sb[len(sb)-1] += "},"
                    if i == len(frame.strokes) - 1:
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
    
def readBrushStrokes(filepath=None, resizeTimeline=True):
    url = filepath # compatibility with gui keywords
    #~
    gp = getActiveGp()
    #~
    useScaleAndOffset = True
    globalScale = Vector((10, 10, 10))
    globalOffset = Vector((0, 0, 0))
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
    #~
    longestFrameNum = 1
    for layerJson in data["grease_pencil"][0]["layers"]:
        layer = gp.layers.new(layerJson["name"], set_active=True)
        palette = getActivePalette()    
        #~
        for i, frameJson in enumerate(layerJson["frames"]):
            try:
            	frame = layer.frames.new(layerJson["frames"][i]["frame_number"]) 
            except:
            	frame = layer.frames.new(i) 
            if (frame.frame_number > longestFrameNum):
                longestFrameNum = frame.frame_number
            for strokeJson in frameJson["strokes"]:
                strokeColor = (0,0,0)
                try:
                    colorJson = strokeJson["color"]
                    strokeColor = (colorJson[0], colorJson[1], colorJson[2])
                except:
                    pass
                createColor(strokeColor)
                stroke = frame.strokes.new(getActiveColor().name)
                stroke.draw_mode = "3DSPACE" # either of ("SCREEN", "3DSPACE", "2DSPACE", "2DIMAGE")
                pointsJson = strokeJson["points"]
                stroke.points.add(len(pointsJson)) # add 4 points
                for l, pointJson in enumerate(pointsJson):
                    coJson = pointJson["co"] 
                    x = coJson[0]
                    y = coJson[2]
                    z = coJson[1]
                    pressure = 1.0
                    strength = 1.0
                    if (useScaleAndOffset == True):
                        x = (x * globalScale.x) + globalOffset.x
                        y = (y * globalScale.y) + globalOffset.y
                        z = (z * globalScale.z) + globalOffset.z
                    #~
                    if ("pressure" in pointJson):
                        pressure = pointJson["pressure"]
                    if ("strength" in pointJson):
                        strength = pointJson["strength"]
                    #stroke.points[l].co = (x, y, z)
                    createPoint(stroke, l, (x, y, z), pressure, strength)
    #~  
    if (resizeTimeline == True):
        setStartEnd(0, longestFrameNum, pad=False)              
    return {'FINISHED'}

# ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~
# ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~

def writeSvg(filepath=None):
	# Note: keep fps at 24 and above to prevent timing artifacts. 
	# Last frame in timeline must be empty.
    minLineWidth=3
    camera = getActiveCamera()
    fps = float(getSceneFps())
    start, end = getStartEnd()
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
            goToFrame(frame.frame_number)
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

def importVRDoodler(filepath=None):
    globalScale = Vector((1, 1, 1))
    globalOffset = Vector((0, 0, 0))
    useScaleAndOffset = True
    #numPlaces = 7
    #roundValues = True

    with open(filepath) as data_file: 
        data = data_file.readlines()

    vrd_strokes = []
    vrd_points = []
    for line in data:
        if str(line).startswith("l") == True:
            if (len(vrd_points) > 0):
                vrd_strokes.append(vrd_points)
                vrd_points = []
        elif str(line).startswith("v") == True:
            vrd_pointRaw = line.split()
            vrd_point = (-1 * float(vrd_pointRaw[1]), float(vrd_pointRaw[2]), float(vrd_pointRaw[3]))
            vrd_points.append(vrd_point)

    gp = getActiveGp()
    layer = gp.layers.new("VRDoodler_layer", set_active=True)
    start, end = getStartEnd()
    frame = layer.frames.new(start)
    for vrd_stroke in vrd_strokes:
        strokeColor = (0.5,0.5,0.5)
        createColor(strokeColor)
        stroke = frame.strokes.new(getActiveColor().name)
        stroke.draw_mode = "3DSPACE" # either of ("SCREEN", "3DSPACE", "2DSPACE", "2DIMAGE")
        stroke.points.add(len(vrd_stroke)) # add 4 points
        for l, vrd_point in enumerate(vrd_stroke):
            x = vrd_point[0]
            y = vrd_point[2]
            z = vrd_point[1]
            pressure = 1.0
            strength = 1.0
            if useScaleAndOffset == True:
                x = (x * globalScale.x) + globalOffset.x
                y = (y * globalScale.y) + globalOffset.y
                z = (z * globalScale.z) + globalOffset.z
            #~
            createPoint(stroke, l, (x, y, z), pressure, strength)

def importPainter(filepath=None):
    globalScale = Vector((1, 1, -1))
    globalOffset = Vector((0, 0, 0))
    useScaleAndOffset = True
    #numPlaces = 7
    #roundValues = True

    gp = getActiveGp()
    layer = gp.layers.new("Painter_layer", set_active=True)
    start, end = getStartEnd()
    frame = getActiveFrame()
    if not frame:
        frame = layer.frames.new(start)

    width = 0
    height = 0
    points = []
    pressures = []

    with open(filepath) as data_file: 
        data = data_file.readlines()

    for line in data:
        if (line.startswith("new")):
            vals = line.split(" ")
            for i, val in enumerate(vals):
                if (val == "width"):
                    width = float(vals[i+1])
                elif (val == "height"):
                    height = float(vals[i+1])
        elif (line.startswith("color")):
            r = 0
            g = 0
            b = 0
            vals = line.split(" ")
            for i, val in enumerate(vals):
                if (val == "red"):
                    r = float(vals[i+1]) / 255.0
                if (val == "green"):
                    g = float(vals[i+1]) / 255.0
                if (val == "blue"):
                    b = float(vals[i+1]) / 255.0
            createColor((r, g, b))
        elif (line.startswith("stroke_start")):
            points = []
            pressures = []
        elif (line.startswith("pnt")):
            vals = line.split(" ")
            x = 0
            y = 0
            z = 0
            pressure = 0
            for i, val in enumerate(vals):
                if (val == "x"):
                    x = float(vals[i+1]) / width
                elif (val == "y"):
                    y = float(vals[i+1]) / height
                elif (val == "prs"):
                    pressure = float(vals[i+1])
            points.append((x, y, z))
            pressures.append(pressure)
        elif (line.startswith("stroke_end")):
            stroke = frame.strokes.new(getActiveColor().name)
            stroke.draw_mode = "3DSPACE"
            stroke.points.add(len(points))

            for i in range(0, len(points)):
                point = points[i]
                x = point[0]
                y = point[2]
                z = point[1]
                pressure = pressures[i]
                strength = 1.0
                if useScaleAndOffset == True:
                    x = (x * globalScale.x) + globalOffset.x
                    y = (y * globalScale.y) + globalOffset.y
                    z = (z * globalScale.z) + globalOffset.z
                createPoint(stroke, i, (x, y, z), pressure, strength)

def importNorman(filepath=None):
    globalScale = Vector((1, 1, 1))
    globalOffset = Vector((0, 0, 0))
    useScaleAndOffset = True
    #numPlaces = 7
    #roundValues = True
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

def gmlParser(filepath=None, splitStrokes=False, sequenceAnim=False):
    globalScale = (0.01, -0.01, 0.01)
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
        if (sequenceAnim == True):
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
    #~
    if (sequenceAnim == False):
        start, end = getStartEnd()
        layer = getActiveLayer()
        frame = None
        try:
            frame = layer.frames.new(start)
        except:
            frame = getActiveFrame()
        for i, stroke in enumerate(strokes):
            if (splitStrokes == True and i > 0):
                layer = newLayer(layer.info)
                masterLayerList.append(layer)
                try:
                    frame = layer.frames.new(start)
                except:
                    frame = getActiveFrame()
            drawPoints(stroke, frame=frame, layer=layer)
    #~
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
    print("* * * * * * * * * * * * * * *")
    print("strokes: " + str(strokeCounter) + "   points: " + str(pointCounter))

def writeGml(filepath=None, make2d=False):
    timeCounter = 0
    timeIncrement = 0.01
    #~
    globalScale = (1, 1, 1)
    globalOffset = (0, 0, 0)
    useScaleAndOffset = True
    #numPlaces = 7
    #roundValues = True
    #~
    frame = getActiveFrame()
    strokes = frame.strokes
    allX = []
    allY = []
    allZ = []
    for stroke in strokes:
        for point in stroke.points:
            coord = point.co
            allX.append(coord[0])
            allY.append(coord[1])
            allZ.append(coord[2])
    allX.sort()
    allY.sort()
    allZ.sort()
    maxPoint = (allX[len(allX)-1], allY[len(allY)-1], allZ[len(allZ)-1])
    minPoint = (allX[0], allY[0], allZ[0])
    # ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~
    sg = gmlHeader((480, 320, 18)) # Fat Tag default
    for stroke in strokes:
        coords = []
        for point in stroke.points:
            coord = point.co
            x = remap(coord[0], minPoint[0], maxPoint[0], 0, 1)
            y = remap(coord[1], minPoint[1], maxPoint[1], 0, 1)
            z = remap(coord[2], minPoint[2], maxPoint[2], 0, 1)
            coords.append((x, 1.0 - z, y))
        returnString, timeCounter = gmlStroke(coords, timeCounter, timeIncrement)
        sg += returnString
    sg += gmlFooter()
    # ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~
    writeTextFile(filepath, sg)
    return {'FINISHED'}

def gmlHeader(dim=(1024,1024,1024)):
    s = "<gml spec=\"0.1b\">\r"
    s += "\t<tag>\r"
    s += "\t\t<header>\r"
    s += "\t\t\t<client>\r"
    s += "\t\t\t\t<name>Latk</name>\r"
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

def gmlStroke(points, timeCounter, timeIncrement):
    s = "\t\t\t<stroke>\r"
    for point in points:
        returnString, timeCounter = gmlPoint(point, timeCounter, timeIncrement)
        s += returnString
    s += "\t\t\t</stroke>\r"
    return s, timeCounter

def gmlPoint(point, timeCounter, timeIncrement):
    s = "\t\t\t\t<pt>\r"
    s += "\t\t\t\t\t<x>" + str(point[0]) + "</x>\r"
    s += "\t\t\t\t\t<y>" + str(point[1]) + "</y>\r"
    s += "\t\t\t\t\t<z>" + str(point[2]) + "</z>\r"
    s += "\t\t\t\t\t<time>" + str(timeCounter) + "</time>\r"
    s += "\t\t\t\t</pt>\r"
    timeCounter += timeIncrement
    return s, timeCounter

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

'''
def writePointCloud(filepath=None, strokes=None):
    if not filepath:
        filepath = getFilePath()
    if not strokes:
        strokes = getSelectedStrokes()
        if not strokes:
            frame = getActiveFrame()
            strokes = frame.strokes
    lines = []
    for stroke in strokes:
        for point in stroke.points:
            x = str(point.co[0])
            y = str(point.co[1])
            z = str(point.co[2])
            lines.append(x + ", " + y + ", " + z + "\n")
    writeTextFile(name=name, lines=lines)
'''

def importAsc(filepath=None, strokeLength=1):
    globalScale = Vector((1, 1, 1))
    globalOffset = Vector((0, 0, 0))
    useScaleAndOffset = True
    #numPlaces = 7
    #roundValues = True

    with open(filepath) as data_file: 
        data = data_file.readlines()

    allPoints = []
    allPressures = []
    colors = []
    colorIs255 = False
    for line in data:
        pointRaw = line.split(",")
        point = (float(pointRaw[0]), float(pointRaw[1]), float(pointRaw[2]))
        allPoints.append(point)
        
        color = None
        pressure = 1.0
        
        if (len(pointRaw) == 4):
            pressure = float(pointRaw[3])
        elif (len(pointRaw) == 6):
            color = (float(pointRaw[3]), float(pointRaw[4]), float(pointRaw[5]))
        elif(len(pointRaw) > 6):
            pressure = float(pointRaw[3])
            color = (float(pointRaw[4]), float(pointRaw[5]), float(pointRaw[6]))

        if (colorIs255 == False and color != None and color[0] + color[1] + color[2] > 3.1):
                colorIs255 = True
        elif (colorIs255 == True):
            color = (color[0] / 255.0, color[1] / 255.0, color[2] / 255.0)

        allPressures.append(pressure)
        colors.append(color)

    gp = getActiveGp()
    layer = gp.layers.new("ASC_layer", set_active=True)
    start, end = getStartEnd()
    frame = getActiveFrame()
    if not frame:
        frame = layer.frames.new(start)

    for i in range(0, len(allPoints), strokeLength):
        color = colors[i]
        if (color != None):
            createColor(color)
        stroke = frame.strokes.new(getActiveColor().name)
        stroke.draw_mode = "3DSPACE"
        stroke.points.add(strokeLength)

        for j in range(0, strokeLength):
            x = allPoints[i+j][0]
            y = allPoints[i+j][2]
            z = allPoints[i+j][1]
            pressure = allPressures[i+j]
            strength = 1.0
            if useScaleAndOffset == True:
                x = (x * globalScale.x) + globalOffset.x
                y = (y * globalScale.y) + globalOffset.y
                z = (z * globalScale.z) + globalOffset.z
            createPoint(stroke, j, (x, y, z), pressure, strength)

def exportAsc(filepath=None):
    ascData = []
    gp = getActiveGp()
    palette = getActivePalette()
    for layer in gp.layers:
        for frame in layer.frames:
            for stroke in frame.strokes:
                color = palette.colors[stroke.colorname].color
                for point in stroke.points:
                    coord = point.co
                    x = coord[0]
                    y = coord[2]
                    z = coord[1]
                    pressure = point.pressure
                    r = color[0]
                    g = color[1]
                    b = color[2]
                    ascData.append(str(x) + "," + str(y) + "," + str(z) + "," + str(pressure) + "," + str(r) + "," + str(g) + "," + str(b)) 

    writeTextFile(filepath, "\n".join(ascData))

def importSculptrVr(filepath=None, strokeLength=1, scale=0.01, startLine=1):
    globalScale = Vector((scale, scale, scale))
    globalOffset = Vector((0, 0, 0))
    useScaleAndOffset = True
    #numPlaces = 7
    #roundValues = True

    with open(filepath) as data_file: 
        data = data_file.readlines()

    allPoints = []
    allPressures = []
    colors = []
    colorIs255 = False
    for i in range(startLine, len(data)):
        pointRaw = data[i].split(",")
        point = (float(pointRaw[0]), float(pointRaw[1]), float(pointRaw[2]))
        allPoints.append(point)
        
        color = None
        pressure = 1.0
        
        '''
        if (len(pointRaw) == 4):
            pressure = float(pointRaw[3])
        elif (len(pointRaw) == 6):
            color = (float(pointRaw[3]), float(pointRaw[4]), float(pointRaw[5]))
        elif(len(pointRaw) > 6):
            pressure = float(pointRaw[3])
        '''
        color = (float(pointRaw[4]), float(pointRaw[5]), float(pointRaw[6]))

        if (colorIs255 == False and color != None and color[0] + color[1] + color[2] > 3.1):
                colorIs255 = True
        elif (colorIs255 == True):
            color = (color[0] / 255.0, color[1] / 255.0, color[2] / 255.0)

        allPressures.append(pressure)
        colors.append(color)

    gp = getActiveGp()
    layer = gp.layers.new("ASC_layer", set_active=True)
    start, end = getStartEnd()
    frame = getActiveFrame()
    if not frame:
        frame = layer.frames.new(start)

    for i in range(0, len(allPoints), strokeLength):
        color = colors[i]
        if (color != None):
            createColor(color)
        stroke = frame.strokes.new(getActiveColor().name)
        stroke.draw_mode = "3DSPACE"
        stroke.points.add(strokeLength)

        for j in range(0, strokeLength):
            x = allPoints[i+j][0]
            y = allPoints[i+j][1]
            z = allPoints[i+j][2]
            pressure = allPressures[i+j]
            strength = 1.0
            if useScaleAndOffset == True:
                x = (x * globalScale.x) + globalOffset.x
                y = (y * globalScale.y) + globalOffset.y
                z = (z * globalScale.z) + globalOffset.z
            createPoint(stroke, j, (x, y, z), pressure, strength)

def exportSculptrVrCsv(filepath=None, strokes=None, sphereRadius=10, octreeSize=7, vol_scale=0.33, mtl_val=255, file_format="sphere"):
    file_format = file_format.lower()
    #~
    if (sphereRadius < 0.01):
        sphereRadius = 0.01
    #~
    if (octreeSize < 0):
        octreeSize = 0
    if (octreeSize > 19):
        octreeSize = 19
    if (mtl_val != 127 and mtl_val != 254 and mtl_val != 255):
        mtl_val = 255
    #~
    if not filepath:
        filepath = getFilePath()
    if not strokes:
        strokes = getSelectedStrokes()
        if not strokes:
            frame = getActiveFrame()
            strokes = frame.strokes
    #~
    csvData = []

    allX = []
    allY = []
    allZ = []
    for stroke in strokes:
        for point in stroke.points:
            coord = point.co
            allX.append(coord[0])
            allY.append(coord[1])
            allZ.append(coord[2])
    allX.sort()
    allY.sort()
    allZ.sort()

    leastValArray = [ allX[0], allY[0], allZ[0] ]
    mostValArray = [ allX[len(allX)-1], allY[len(allY)-1], allZ[len(allZ)-1] ]
    leastValArray.sort()
    mostValArray.sort()
    leastVal = leastValArray[0]
    mostVal = mostValArray[2]
    valRange = mostVal - leastVal

    xRange = (allX[len(allX)-1] - allX[0]) / valRange
    yRange = (allY[len(allY)-1] - allY[0]) / valRange
    zRange = (allZ[len(allZ)-1] - allZ[0]) / valRange

    minVal = -1500.0
    maxVal = 1500.0
    if (file_format == "legacy"):
        minVal, maxVal = getSculptrVrVolRes(0)
    elif (file_format == "single"):
        minVal, maxVal = getSculptrVrVolRes(octreeSize)

    minValX = minVal * xRange * vol_scale
    minValY = minVal * yRange * vol_scale
    minValZ = minVal * zRange * vol_scale
    maxValX = maxVal * xRange * vol_scale
    maxValY = maxVal * yRange * vol_scale
    maxValZ = maxVal * zRange * vol_scale

    for stroke in strokes:
        for point in stroke.points:
            # might do this here if we want to use variable pressure later
            #minVal, maxVal = getSculptrVrVolRes(octreeSize)

            color = stroke.color.color
            r = int(color[0] * 255)
            g = int(color[1] * 255)
            b = int(color[2] * 255)
            coord = point.co
            if (file_format == "sphere"):
                x = remap(coord[0], allX[0], allX[len(allX)-1], minValX, maxValX)
                y = remap(coord[1], allY[0], allY[len(allY)-1], minValY, maxValY)
                z = remap(coord[2], allZ[0], allZ[len(allZ)-1], minValZ, maxValZ)
                pressure = remap(point.pressure, 0.0, 1.0, sphereRadius/100.0, sphereRadius)
                if (pressure < 0.01):
                	pressure = 0.01
                csvData.append([x, y, z, pressure, r, g, b])
            else:
                x = remapInt(coord[0], allX[0], allX[len(allX)-1], int(minValX), int(maxValX))
                y = remapInt(coord[1], allY[0], allY[len(allY)-1], int(minValY), int(maxValY))
                z = remapInt(coord[2], allZ[0], allZ[len(allZ)-1], int(minValZ), int(maxValZ))
                csvData.append([x, y, z, octreeSize, r, g, b, mtl_val])

    #csvData = sorted(csvDataInt, key=lambda x: x[1])
    #csvData = sorted(csvDataInt, key=lambda x: x[2])
    finalData = []
    finalData.append("# SculptrVR: " + file_format + " #")
    if (file_format == "legacy"): # xyz rgb
        for data in csvData:
            finalData.append(str(data[0]) + "," + str(data[1]) + "," + str(data[2]) + "," + str(data[4]) + "," + str(data[5]) + "," + str(data[6]))
    elif(file_format == "single"): # xyz octree_size rgb mtl_val
        for data in csvData:
            finalData.append(str(data[0]) + "," + str(data[1]) + "," + str(data[2]) + "," + str(data[3]) + "," + str(data[4]) + "," + str(data[5]) + "," + str(data[6]) + "," + str(data[7]))
    elif(file_format == "sphere"): # xyz radius rgb
        for data in csvData:
            finalData.append(str(data[0]) + "," + str(data[1]) + "," + str(data[2]) + "," + str(data[3]) + "," + str(data[4]) + "," + str(data[5]) + "," + str(data[6]))

    writeTextFile(filepath, "\n".join(finalData))

def getSculptrVrVolRes(val):
    vol_res = 19 - val
    minVal = -pow(2, vol_res)
    maxVal = pow(2, vol_res)-1
    return minVal, maxVal

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

# ~ ~ ~

def tiltBrushJson_Grouper(n, iterable, fillvalue=None):
  """grouper(3, 'ABCDEFG', 'x') --> ABC DEF Gxx"""
  args = [iter(iterable)] * n
  return zip_longest(fillvalue=fillvalue, *args)

def tiltBrushJson_DecodeData(obj, dataType="v"):
    '''    
    VERTEX_ATTRIBUTES = [
        # Attribute name, type code
        ('v',  'f', None),
        ('n',  'f', 3),
        ('uv0','f', None),
        ('uv1','f', None),
        ('c',  'I', 1),
        ('t',  'f', 4),
    ]
    '''
    if (dataType=="v" or dataType=="n" or dataType=="t"):
        typeChar = "f"
    elif (dataType=="c"):
        typeChar = "I"

    num_verts = 1
    empty = None
    data_grouped = []
    
    data_bytes = base64.b64decode(obj)
    fmt = "<%d%c" % (len(data_bytes) / 4, typeChar)
    data_words = struct.unpack(fmt, data_bytes)
    
    if (dataType=="v" or dataType=="n"):
        num_verts = len(data_words) / 3
    elif (dataType=="t"):
        num_verts = len(data_words) / 4

    if (len(data_words) % num_verts != 0):
        return None
    else: 
        stride_words = int(len(data_words) / num_verts)
        if stride_words > 1:
            data_grouped = list(tiltBrushJson_Grouper(stride_words, data_words))
        else:
            data_grouped = list(data_words)

        if (dataType == "c"):
            for i in range(0, len(data_grouped)):
                data_grouped[i] = rgbIntToTuple(data_grouped[i][0], normalized=True)

        return(data_grouped)

def importTiltBrush(filepath=None, vertSkip=1):
    globalScale = Vector((1, 1, 1))
    globalOffset = Vector((0, 0, 0))
    useScaleAndOffset = True
    gp = getActiveGp()
    palette = getActivePalette()    

    filename = os.path.split(filepath)[1].split(".")
    filetype = filename[len(filename)-1].lower()
    if (filetype == "tilt" or filetype == "zip"): # Tilt Brush binary file with original stroke data
        t = Tilt(filepath)
        #~
        layer = gp.layers.new("TiltBrush", set_active=True)
        frame = layer.frames.new(1)
        #~
        for tstroke in t.sketch.strokes:
            strokeColor = (0,0,0)
            pointGroup = []
            try:
                strokeColor = (tstroke.brush_color[0], tstroke.brush_color[1], tstroke.brush_color[2])
            except:
                pass
            for i in range(0, len(tstroke.controlpoints), vertSkip):
                controlpoint = tstroke.controlpoints[i]
                last_controlpoint = tstroke.controlpoints[i-1]
                x = 0.0
                y = 0.0
                z = 0.0
                #~
                point = controlpoint.position
                last_point = last_controlpoint.position
                if (i==0 or point != last_point): # try to prevent duplicate points
                    pressure = 1.0
                    strength = 1.0
                    try:
                        pressure = controlpoint.extension[0]
                        # TODO strength?
                    except:
                        pass
                    #~
                    x = point[0]
                    y = point[2]
                    z = point[1]
                    if useScaleAndOffset == True:
                        x = (x * globalScale[0]) + globalOffset[0]
                        y = (y * globalScale[1]) + globalOffset[1]
                        z = (z * globalScale[2]) + globalOffset[2]
                    pointGroup.append((x, y, z, pressure, strength))
                    #~
            createColor(strokeColor)
            stroke = frame.strokes.new(getActiveColor().name)
            stroke.points.add(len(pointGroup)) # add 4 points
            stroke.draw_mode = "3DSPACE" # either of ("SCREEN", "3DSPACE", "2DSPACE", "2DIMAGE")  
            for l, point in enumerate(pointGroup):
                createPoint(stroke, l, (point[0], point[1], point[2]), point[3], point[4])
        # ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~
        """Prints out some rough information about the strokes.
        Pass a tiltbrush.tilt.Sketch instance."""
        '''
        cooky, version, unused = sketch.header[0:3]
        '''
        #output += 'Cooky:0x%08x    Version:%s    Unused:%s    Extra:(%d bytes)' % (
            #cooky, version, unused, len(sketch.additional_header))
        '''
        if len(sketch.strokes):
            stroke = sketch.strokes[0]    # choose one representative one
            def extension_names(lookup):
                # lookup is a dict mapping name -> idx
                extensions = sorted(lookup.items(), key=lambda (n,i): i)
                return ', '.join(name for (name, idx) in extensions)
            #output += "Stroke Ext: %s" % extension_names(stroke.stroke_ext_lookup)
            #if len(stroke.controlpoints):
                #output += "CPoint Ext: %s" % extension_names(stroke.cp_ext_lookup)
        '''
        '''
        for (i, stroke) in enumerate(sketch.strokes):
            #output += "%3d: " % i,
            output += dump_stroke(stroke)
        '''
    else: # Tilt Brush JSON export file, not original stroke data
        pressure = 1.0
        strength = 1.0
        #~
        with open(filepath) as data_file: 
            data = json.load(data_file)
        #~
        layer = gp.layers.new("TiltBrush", set_active=True)
        frame = layer.frames.new(1)
        #~
        for strokeJson in data["strokes"]:
            strokeColor = (0,0,0)
            try:
                colorGroup = tiltBrushJson_DecodeData(strokeJson["c"], "c")
                strokeColor = (colorGroup[0][0], colorGroup[0][1], colorGroup[0][2])
            except:
                pass
            #~
            vertsFailed = False
            vertGroup = []
            pointGroup = []
            try:
                vertGroup = tiltBrushJson_DecodeData(strokeJson["v"], "v")
            except:
                vertsFailed = True

            if (vertsFailed==False and len(vertGroup) > 0):
                for j in range(0, len(vertGroup), vertSkip):
                    if (j==0 or vertGroup[j] != vertGroup[j-1]): # try to prevent duplicate points
                        vert = vertGroup[j]
                        if (vert[0] == 0 and vert[1] == 0 and vert[2] == 0):
                            pass
                        else:
                            try:
                                x = -vert[0]
                                y = vert[2]
                                z = vert[1]
                                if (useScaleAndOffset == True):
                                    x = (x * globalScale.x) + globalOffset.x
                                    y = (y * globalScale.y) + globalOffset.y
                                    z = (z * globalScale.z) + globalOffset.z
                                pointGroup.append((x, y, z, pressure, strength))
                            except:
                                pass

            if (vertsFailed==False):
                createColor(strokeColor)
                stroke = frame.strokes.new(getActiveColor().name)
                stroke.points.add(len(pointGroup)) # add 4 points
                stroke.draw_mode = "3DSPACE" # either of ("SCREEN", "3DSPACE", "2DSPACE", "2DIMAGE")  
                for l, point in enumerate(pointGroup):
                    createPoint(stroke, l, (point[0], point[1], point[2]), point[3], point[4])
           
    return {'FINISHED'}

# * * * * * * * * * * * * * * * * * * * * * * * * * *
# * * * * * * * * * * * * * * * * * * * * * * * * * *
# * * * * * * * * * * * * * * * * * * * * * * * * * *

