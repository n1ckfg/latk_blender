# 8 of 10. SHORTCUTS

def mf():
    dn()
    gpMesh(_resolution=1, _bevelResolution=0, _singleFrame=True)

def gp():
    dn()
    gpMeshPreview()

def gs():
    gpMesh(_singleFrame=True)
    
def gb():
    dn()
    gpMesh(_bakeMesh=True)

def gj():
    dn()
    gpMesh(_joinMesh=True)

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

def gpMeshBackground():
    gpMesh(_animateFrames=False, _bakeMesh=True, _thickness=0.008)

def gpJoinTest():
    dn()
    gpMesh(_bakeMesh=True, _joinMesh=True)

def rbUnity(fileName):
    readBrushStrokes("C:\\Users\\nick\\Documents\\GitHub\\LightningArtist\\latkUnity\\latkVive\\Assets\\" + fileName)

rb = readBrushStrokes
wb = writeBrushStrokes

def up():
    makeParent(unParent=True)

def ss():
    return select()[0]

def dn():
    deleteName(_name="latk_ob")
    deleteName(_name="caps_ob")

c = changeColor
a = alignCamera
s = select
d = delete
j = joinObjects
df = deleteFromAllFrames
spl = splitLayer
cplf = checkLayersAboveFrameLimit

splf = splitLayersAboveFrameLimit

# * * * * * * * * * * * * * * * * * * * * * * * * * *
# * * * * * * * * * * * * * * * * * * * * * * * * * *
# * * * * * * * * * * * * * * * * * * * * * * * * * *

