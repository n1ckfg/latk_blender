def findCenterOfStrokes(strokes=None, selectAll=False):
    if not strokes:
        if (selectAll==False):
            strokes = getSelectedStrokes()
        else:
            strokes = getAllStrokes()
    #~
    allX = 0
    allY = 0
    allZ = 0
    pointCounter = 0
    #~
    for stroke in strokes:
        for point in stroke.points:
            pointCounter += 1
    #~
    for stroke in strokes:
        for point in stroke.points:
            allX += point.co[0]
            allY += point.co[1]
            allZ += point.co[2]
    #~
    avgPos = (allX/pointCounter, allY/pointCounter, allZ/pointCounter)
    return avgPos

def parentLayersToEmpty(layers=None, target=None):
    if not layers:
        layers = getActiveGp().layers
    if not target:
        bpy.ops.object.empty_add(type='PLAIN_AXES')
        target = ss()
    target.location = findCenterOfStrokes(selectAll=True)
    for layer in layers:
        layer.parent = target