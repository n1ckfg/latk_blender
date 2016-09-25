# https://blenderartists.org/forum/archive/index.php/t-253200.html

import bpy
import bmesh

def createFill(inputVerts):
    verts = []
    #~
    # Create mesh 
    me = bpy.data.meshes.new("myMesh") 
    #~
    # Create object
    ob = bpy.data.objects.new("myObject", me) 
    #~
    #ob.location = origin
    ob.show_name = True
    #~
    # Link object to scene
    bpy.context.scene.objects.link(ob)
    #~
    # Get a BMesh representation
    bm = bmesh.new() # create an empty BMesh
    bm.from_mesh(me) # fill it in from a Mesh
    #~
    # Hot to create vertices
    for i in range(0, len(inputVerts)):
        vert = bm.verts.new((inputVerts[i].co[0], inputVerts[i].co[1], inputVerts[i].co[2]))
        verts.append(vert)
    '''
    vertex1 = bm.verts.new( (0.0, 0.0, 3.0) )
    vertex2 = bm.verts.new( (2.0, 0.0, 3.0) )
    vertex3 = bm.verts.new( (2.0, 2.0, 3.0) )
    vertex4 = bm.verts.new( (0.0, 2.0, 3.0) )
    '''
    #~
    # Initialize the index values of this sequence.
    bm.verts.index_update()
    #~
    # How to create edges 
    '''
    bm.edges.new( (vertex1, vertex2) )
    bm.edges.new( (vertex2, vertex3) )
    bm.edges.new( (vertex3, vertex4) )
    bm.edges.new( (vertex4, vertex1) )
    '''
    #~
    # How to create a face
    # it's not necessary to create the edges before, I made it only to show how create 
    # edges too
    '''
    bm.faces.new( (vertex1, vertex2, vertex3, vertex4) )
    '''
    bm.faces.new(verts)
    #~
    # Finish up, write the bmesh back to the mesh
    bm.to_mesh(me)