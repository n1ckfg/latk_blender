# 6 of 10. DRAWING

# note that unlike createStroke, this creates a stroke from raw coordinates
def drawCoords(coords=None, color=None, frame=None, layer=None):
    if (len(coords) > 0):
        if not color:
            color = getActiveColor()
        else:
            color = createColor(color)
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
        stroke.points.add(len(coords))
        for i, coord in enumerate(coords):
            pressure = 1.0
            strength = 1.0
            if (len(coord) > 3):
                pressure = coord[3]
            if (len(coord) > 4):
                strength = coord[4]
            createPoint(stroke, i, (coord[0], coord[2], coord[1]), pressure, strength)
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
            try:
                copyFrame(0, i+1+extraFrameCounter, strokeCounter+1)
            except:
                pass
        else:
            try:
                copyFrame(0, i+1+extraFrameCounter, strokeCounter)
            except:
                pass
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
                    try:
                        createStroke(layer.frames[0].strokes[l].points, layer.frames[0].strokes[l].color.color, layer.frames[outLoc])#newStroke.color.color)
                    except:
                        pass
                newStroke = layer.frames[0].strokes[strokeCounter]
                newPoints = []
                for l in range(0, len(newStroke.points)):
                    if (l < j * pointStep):
                        newPoints.append(newStroke.points[l])  
                #~       
                try:                                  
                    createStroke(newPoints, newStroke.color.color, layer.frames[outLoc])
                except:
                    pass
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
    try:
        copyFrame(0, lastLoc)
    except:
        pass

#ds = distributeStrokes

def writeOnStrokes(pointStep=10, step=1):
    gp = getActiveGp()
    for i in range(0, len(gp.layers)):
        gp.layers.active_index = i
        distributeStrokes(pointStep=pointStep, step=step)

def makeLine(p1, p2):
    return drawCoords([p1, p2])

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
    return drawCoords(points)

def makeSphere(pos=(0,0,0), size=1, resolution=10, lat=10, lon=10):
    points = []
    for i in range(0, lat):
        for j in range(0, lon):
            points.append(multVec3(addVec3(getLatLon(i, j), pos), (size,size,size)))
    drawCoords(points)

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
        strokes.append(drawCoords([pos, p2]))
    return strokes

def makeTriangle(pos=(0,0,0), size=1):
    s = size/2.0
    p1 = (pos[0], pos[1] + s, pos[2])
    p2 = (pos[0] - s, pos[1] - s, pos[2])
    p3 = (pos[0] + s, pos[1] - s, pos[2])
    return drawCoords([p1, p2, p3, p1])

def makePyramid(pos=(0,0,0), size=1):
    strokes = []
    s = size/2.0
    p1 = (pos[0], pos[1] + s, pos[2])
    p2 = (pos[0] - s, pos[1] - s, pos[2] + s)
    p3 = (pos[0] + s, pos[1] - s, pos[2] + s)
    #~
    strokes.append(drawCoords([p1, p2, p3, p1]))
    #~
    p4 = (pos[0], pos[1] + s, pos[2])
    p5 = (pos[0] - s, pos[1] - s, pos[2] - s)
    p6 = (pos[0] + s, pos[1] - s, pos[2] - s)
    #~
    strokes.append(drawCoords([p4, p5, p6, p4]))
    #~
    strokes.append(drawCoords([p2, p5]))
    strokes.append(drawCoords([p3, p6]))
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

