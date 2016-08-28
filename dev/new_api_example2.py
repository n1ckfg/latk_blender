# https://wiki.blender.org/index.php/User:Antoniov/Grease_Pencil_Api_Changes

def getActiveGp(_name="GPencil"):
    try:
        pencil = bpy.context.scene.grease_pencil
    except:
        pencil = None
    try:
        gp = bpy.data.grease_pencil(pencil.name)
    except:
        gp = bpy.data.grease_pencil.new(_name)
        bpy.context.scene.grease_pencil = gp
    return gp

def testStroke():
    gp = getActiveGp()
    palette = gp.palettes.new("TestPalette", set_active = True)
    color = palette.colors.new()
    color.color = (1.0, 10.0, 0.0)
    layer = gp.layers.new("TestLayer")
    frame = layer.frames.new(bpy.context.scene.frame_current)
    stroke = frame.strokes.new(colorname=color.name)
    stroke.draw_mode = "3DSPACE"
    stroke.points.add(2)
    createPoint(stroke, 0, (0,0,0))
    createPoint(stroke, 1, (100,100,0))

def createPoint(_stroke, _index, _point):
    _stroke.points[_index].co = _point
    _stroke.points[_index].select = True
    _stroke.points[_index].pressure = 1
    _stroke.points[_index].strength = 1

testStroke()
