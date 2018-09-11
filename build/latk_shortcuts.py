# 8 of 10. SHORTCUTS

def up():
    makeParent(unParent=True)

def ss():
	returns = select()
	if (len(returns) > 0):
	    return returns[0]
	else:
		return None

def dn():
    deleteName(_name="latk_ob")
    deleteName(_name="caps_ob")

def k():
	target = ss()
	for obj in target:
		keyTransform(obj, currentFrame())

rb = readBrushStrokes
wb = writeBrushStrokes
c = changeColor
a = alignCamera
s = select
d = delete
j = joinObjects
df = deleteFromAllFrames
spl = splitLayer
cplf = checkLayersAboveFrameLimit

splf = splitLayersAboveFrameLimit

getVertices = getVerts
gotoFrame = goToFrame

# * * * * * * * * * * * * * * * * * * * * * * * * * *
# * * * * * * * * * * * * * * * * * * * * * * * * * *
# * * * * * * * * * * * * * * * * * * * * * * * * * *

