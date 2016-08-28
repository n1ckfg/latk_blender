# https://wiki.blender.org/index.php/User:Antoniov/Grease_Pencil_Api_Changes

import bpy

c = bpy.context
try:
    pencil = c.scene.grease_pencil
except:
    pencil = None

try:
    gp = bpy.data.grease_pencil(pencil.name)
except:
    gp = bpy.data.grease_pencil.new("TEST")
    c.scene.grease_pencil = gp

palette = gp.palettes.new("TestPalette", set_active = True)
color = palette.colors.new()
color.color = (1.0, 10.0, 0.0)
layer = gp.layers.new("TestLayer")
frame = layer.frames.new(c.scene.frame_current)
stroke = frame.strokes.new(colorname=color.name)
stroke.draw_mode = "3DSPACE"
stroke.points.add(2)
stroke.points[0].co = (0,0,0)
stroke.points[0].select = True
stroke.points[0].pressure = 1
stroke.points[0].strength = 1
stroke.points[1].co = (100,100,0)
stroke.points[1].select = True
stroke.points[1].pressure = 1
stroke.points[1].strength = 1