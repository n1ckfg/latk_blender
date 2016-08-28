gp = bpy.context.scene.grease_pencil
layer = gp.layers[0]
color = layer.color

for i in bpy.context.selected_objects:
    if re.match(r'^crv', i.name): # curve object
        print(i.name)
        print("  ", i.data, i.data.name, i.data.extrude )
        i.data.extrude = 0.001
        scn = bpy.scene.GetCurrent()
        ob = scn.objects.active
        m = ob.getData(mesh=True)
        if(len(m.materials) < 1):
            mat = Material.New('newMat')
            m.materials += [mat]
        m.materials[0].rgbCol = color