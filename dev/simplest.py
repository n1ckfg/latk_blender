#2.77a
gp = bpy.data.grease_pencil.new("My GPencil")
bpy.context.scene.grease_pencil = gp
layer = gp.layers.new("Name for new layer", set_active=True)
frame = layer.frames.new(1)
stroke = frame.strokes.new()
stroke.draw_mode = "3DSPACE"
stroke.points.add(2)
stroke.points[0].co = (0.0, 0.0, 0.0)
stroke.points[1].co = (100, 100, 0.0)

#2.77 nightly
gp = bpy.data.grease_pencil.new("My GPencil")
bpy.context.scene.grease_pencil = gp
layer = gp.layers.new("Name for new layer", set_active=True)
frame = layer.frames.new(1)
stroke = frame.strokes.new("Color")
stroke.draw_mode = "3DSPACE"
stroke.points.add(2)
stroke.points[0].co = (0.0, 0.0, 0.0)
stroke.points[1].co = (100, 100, 0.0) 
bpy.context.scene.update()