def colorVertices(obj, color=(1,0,0), makeMaterial=True, vertexPaintMode=False):
    # start in object mode
    mesh = obj.data
    #~
    if not mesh.vertex_colors:
        mesh.vertex_colors.new()
    #~
    """
    let us assume for sake of brevity that there is now 
    a vertex color map called  'Col'    
    """
    #~
    #color_layer = mesh.vertex_colors["Col"]
    #~
    # or you could avoid using the color_layer name
    color_layer = mesh.vertex_colors.active  
    #~
    i = 0
    for poly in mesh.polygons:
        for idx in poly.loop_indices:
            #rgb = [random.random() for i in range(3)]
            color_layer.data[i].color = color #rgb
            i += 1
    #~
    if (makeMaterial==True):
    	colorVertexCyclesMat(obj)
    #~
    # set to vertex paint mode to see the result
    if (vertexPaintMode==True):
    	bpy.ops.object.mode_set(mode='VERTEX_PAINT')

#def colorVertexCyclesMat(obj, color=(1,0,0), newMaterial=True):
def colorVertexCyclesMat(obj):
    # http://blender.stackexchange.com/questions/6084/use-python-to-add-multiple-colors-to-a-nurbs-curve
    # http://blender.stackexchange.com/questions/5668/add-nodes-to-material-with-python
    # this will fail if you don't have Cycles Render enabled
    mesh = obj.data 
    #~    
    #if len(mesh.vertex_colors) == 0:
        #bpy.ops.mesh.vertex_color_add()
    #~
    #if (newMaterial==True):
    obj.active_material = bpy.data.materials.new('material')
    obj.active_material.use_vertex_color_paint = True
    #~
    obj.active_material.use_nodes = True
    nodes = obj.active_material.node_tree.nodes
    material_output = nodes.get('Diffuse BSDF')
    nodeAttr = nodes.new("ShaderNodeAttribute")
    nodeAttr.attribute_name = "Col"
    obj.active_material.node_tree.links.new(material_output.inputs[0], nodeAttr.outputs[0])
    #~
    #loop through each vertex
    #num_verts = len(mesh.vertices)
    #for vert_i in range(num_verts):
        #colorVertex(obj, vert_i, color)
        #print("Finished vertex: " + str(vert_i) + "/" + str(num_verts))

def colorVertexAlt(obj, vert, color=[1,0,0]):
    mesh = obj.data 
    scn = bpy.context.scene
    #check if our mesh already has Vertex Colors, and if not add some... (first we need to make sure it's the active object)
    scn.objects.active = obj
    obj.select = True
    if len(mesh.vertex_colors) == 0:
        bpy.ops.mesh.vertex_color_add()
    i=0
    for poly in mesh.polygons:
        for vert_side in poly.loop_indices:
            global_vert_num = poly.vertices[vert_side-min(poly.loop_indices)] 
            if vert == global_vert_num:
                mesh.vertex_colors[0].data[i].color = color
            i += 1