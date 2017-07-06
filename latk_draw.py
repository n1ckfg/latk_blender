# 6 of 9. DRAWING

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

# * * * * * * * * * * * * * * * * * * * * * * * * * *
# * * * * * * * * * * * * * * * * * * * * * * * * * *
# * * * * * * * * * * * * * * * * * * * * * * * * * *

