import os
import addon_utils
import bpy
import gpu
#import bgl
from mathutils import Vector, Matrix
import bmesh

import sys
import argparse
import cv2
import numpy as np
import platform
#import latk

from . import latk
from . latk import *
from . latk_tools import *
from . latk_mtl import *
from . latk_mesh import *
from . latk_draw import *
from . latk_rw import *
from . latk_svg import *
#from . latk_binvox import *

from skimage.morphology import skeletonize
from mathutils import Vector, Quaternion
from collections import namedtuple
import random
import itertools

import h5py
import skeletor as sk
import trimesh
from scipy.spatial.distance import cdist
from scipy.spatial import Delaunay
from scipy.spatial import cKDTree
import scipy.ndimage as nd
from pyntcloud import PyntCloud 
import pandas as pd
import pdb
import networkx as nx
import jellyfish
from random import uniform as rnd

from . growing_neural_gas.neuralgas import *

if (sys.version_info.major == 3):
    if (sys.version_info.minor == 10):
        if (platform.system() == "Windows" and platform.processor().startswith("Intel64")):
            from . skeleton_tracing.swig.bin.python310.win.x64.trace_skeleton import *
    elif (sys.version_info.minor == 11):
        if (platform.system() == "Windows" and platform.processor().startswith("Intel64")):
            from . skeleton_tracing.swig.bin.python311.win.x64.trace_skeleton import *
else:
    from . skeleton_tracing.py.trace_skeleton import *

'''
try:
    from . skeleton_tracing.swig.trace_skeleton import *
except Exception as error:
    print(error)
    from . skeleton_tracing.py.trace_skeleton import *
'''

#from . import binvox_rw
from . vox2vox import binvox_rw
from . latk_onnx import *
from . latk_pytorch import *

def findAddonPath(name=None):
    #if not name:
        #name = __name__
    for mod in addon_utils.modules():
        if mod.bl_info["name"] == name:
            url = mod.__file__
            return os.path.dirname(url)
    return None

def getModelPath(name, url):
    return os.path.join(findAddonPath(name), url)

def group_points_into_strokes(points, radius, minPointsCount):
    strokeGroups = []
    unassigned_points = set(range(len(points)))

    while len(unassigned_points) > 0:
        strokeGroup = [next(iter(unassigned_points))]
        unassigned_points.remove(strokeGroup[0])

        for i in range(len(points)):
            if i in unassigned_points and cdist([points[i]], [points[strokeGroup[-1]]])[0][0] < radius:
                strokeGroup.append(i)
                unassigned_points.remove(i)

        if (len(strokeGroup) >= minPointsCount):
            strokeGroup = list(dict.fromkeys(strokeGroup)) # remove duplicates
            strokeGroups.append(strokeGroup)

        print("Found " + str(len(strokeGroups)) + " strokeGroups, " + str(len(unassigned_points)) + " points remaining.")
    return strokeGroups

def checkForMesh(verts, faces):
    mesh = None
    
    try: 
        mesh = trimesh.Trimesh(verts, faces)
    except:
        tri = Delaunay(verts)
        mesh = trimesh.Trimesh(tri.points, tri.simplices) 
    
    return mesh   

def neuralGasGen(verts, colors=None, matrix_world=None, max_neurons=100000, max_iter=100, max_age=10, eb=0.1, en=0.006, alpha=0.5, beta=0.995, l=20):
    latk_settings = bpy.context.scene.latk_settings
    origCursorLocation = bpy.context.scene.cursor.location
    bpy.context.scene.cursor.location = (0.0, 0.0, 0.0)

    gp = getActiveGp()
    layer = getActiveLayer()
    if not layer:
        layer = gp.data.layers.new(name="meshToGp")
    frame = getActiveFrame()
    if not frame or frame.frame_number != currentFrame():
        frame = layer.frames.new(currentFrame())

    # 1. Generate GNG
    gas = GrowingNeuralGas(verts, max_neurons=max_neurons, max_iter=max_iter, max_age=max_age, eb=eb, en=en, alpha=alpha, beta=beta, l=l)
    gas.learn()

    # 2. get edge indices
    edgeIndices = []
    for edge in gas.gng.es:
        edgeIndices.append((edge.source, edge.target))

    # 3. merge edges with matching indices
    reps = 10

    for i in range(0, reps):
        newEdgeIndices = []

        while edgeIndices:
            edge = edgeIndices.pop(0)
            for j, matchEdge in enumerate(edgeIndices):
                if (edge[1] == matchEdge[0]):
                    newEdge = edgeIndices.pop(j)
                    edge = edge + newEdge
                    break
                elif (edge[0] == matchEdge[1]):
                    newEdge = edgeIndices.pop(j)
                    edge = newEdge + edge
                    break        

            edge = list(dict.fromkeys(edge)) # this removes repeated indices
            #edge.sort()

            newEdgeIndices.append(edge)

        edgeIndices = newEdgeIndices

    # 4. Get points from indices
    edgeList = []

    for edge in edgeIndices:
        points = []
        
        for index in edge:
            points.append(gas.gng.vs[index]["weight"])
        
            #points = sorted(points, key=lambda point: distance(point, points[0]))
            edgeList.append(points)

    allPoints = []

    for edge in edgeList:
        for point in edge:
            if matrix_world:
                point = matrix_world @ Vector(point)
            allPoints.append(point)

    strokeColors = transferVertexColors(verts, colors, allPoints)
    strokeColorCounter = 0

    for edge in edgeList: 
        stroke = frame.strokes.new()
        stroke.display_mode = '3DSPACE'
        stroke.line_width = int(latk_settings.thickness2) #10 # adjusted from 100 for 2.93
        stroke.material_index = gp.active_material_index

        stroke.points.add(len(edge))

        for i, point in enumerate(edge):
            #point = matrixWorldInverted @ Vector((point[0], point[2], point[1]))
            #point = (point[0], point[1], point[2])
            if matrix_world:
                point = matrix_world @ Vector(point)
            pressure = 1.0
            strength = 1.0
            createPoint(stroke, i, point, pressure, strength, strokeColors[strokeColorCounter])
            strokeColorCounter += 1

    bpy.context.scene.cursor.location = origCursorLocation

    bpy.data.grease_pencils[gp.name].stroke_depth_order = "3D"
    
    return gp

def neuralGasGen2(verts, colors=None, matrix_world=None, max_neurons=100000, max_iter=100, max_age=10, eb=0.1, en=0.006, alpha=0.5, beta=0.995, l=20, radius=2, minPointsCount=5):
    latk_settings = bpy.context.scene.latk_settings
    origCursorLocation = bpy.context.scene.cursor.location
    bpy.context.scene.cursor.location = (0.0, 0.0, 0.0)

    gp = getActiveGp()
    layer = getActiveLayer()
    if not layer:
        layer = gp.data.layers.new(name="meshToGp")
    frame = getActiveFrame()
    if not frame or frame.frame_number != currentFrame():
        frame = layer.frames.new(currentFrame())

    gas = GrowingNeuralGas(verts, max_neurons=max_neurons, max_iter=max_iter, max_age=max_age, eb=eb, en=en, alpha=alpha, beta=beta, l=l)
    gas.learn()
           
    verts = []
    for vert in gas.gng.vs:
        verts.append(vert["weight"])

    strokeGroups = group_points_into_strokes(verts, radius, minPointsCount)

    lastColor = (1,1,1,1)
    for strokeGroup in strokeGroups:
        strokeColors = []
        for i in range(0, len(strokeGroup)):
            try:
                newColor = colors[strokeGroup[i]]
                strokeColors.append(newColor)
                lastColor = newColor
            except:
                strokeColors.append((0,1,0,1)) #lastColor)

        stroke = frame.strokes.new()
        stroke.display_mode = '3DSPACE'
        stroke.line_width = int(latk_settings.thickness2) #10 # adjusted from 100 for 2.93
        stroke.material_index = gp.active_material_index

        stroke.points.add(len(strokeGroup))

        for i, strokeIndex in enumerate(strokeGroup):    
            if not matrix_world:
                point = verts[strokeIndex]
            else:
                point = matrix_world @ Vector(verts[strokeIndex])

            #point = matrixWorldInverted @ Vector((point[0], point[2], point[1]))
            #point = (point[0], point[1], point[2])
            pressure = 1.0
            strength = 1.0
            createPoint(stroke, i, point, pressure, strength, strokeColors[i])

    bpy.context.scene.cursor.location = origCursorLocation

    bpy.data.grease_pencils[gp.name].stroke_depth_order = "3D"

    return gp

def similar2(a, b):
    return jellyfish.jaro_distance(a, b)

def neuralGasGen3(verts, colors=None, matrix_world=None, max_neurons=100000, max_iter=100, max_age=10, eb=0.1, en=0.006, alpha=0.5, beta=0.995, l=20, radius=2, minPointsCount=5):
    latk_settings = bpy.context.scene.latk_settings
    origCursorLocation = bpy.context.scene.cursor.location
    bpy.context.scene.cursor.location = (0.0, 0.0, 0.0)

    gp = getActiveGp()
    layer = getActiveLayer()
    if not layer:
        layer = gp.data.layers.new(name="meshToGp")
    frame = getActiveFrame()
    if not frame or frame.frame_number != currentFrame():
        frame = layer.frames.new(currentFrame())

    gas = GrowingNeuralGas(verts, max_neurons=max_neurons, max_iter=max_iter, max_age=max_age, eb=eb, en=en, alpha=alpha, beta=beta, l=l)
    gas.learn()

    verts = []
    for vert in gas.gng.vs:
        verts.append(vert["weight"])

    edges = []
    for edge in gas.gng.es:
        edges.append((edge.source, edge.target))    

    lengths = []
    for edge in edges:
        lengths.append(getDistance(verts[edge[0]], verts[edge[1]]))

    print(str(len(verts)) + ", " + str(len(edges)) + ", " + str(len(lengths)))

    g = nx.Graph()
    for edge, L in zip(edges, lengths):
        g.add_edge(*edge, length=L)

    strokeCounter = 0
    similarityScores = []

    numStrokes = 100
    minStrokePoints = 10
    maxStrokePoints = 9999
    maxSimilarity = 0.8    

    while strokeCounter < numStrokes:
        points = []
        similarity = []

        start = int(rnd(0, len(verts) - 2))
        end = start + 1

        try:
            # run the shortest path query using length for edge weight
            path = nx.shortest_path(g, source=start, target=end, weight='length')

            for index in path:
                vert = verts[index]
                similarity.append(str(index))

                #col = mesh.visual.vertex_colors[index]
                #col = (float(col[0])/255.0, float(col[1])/255.0, float(col[2])/255.0, float(col[3])/255.0)
                # TODO find out why colors are too light
                #col = (col[0] * col[0], col[1] * col[1], col[2] * col[2], col[3])
                col = (1,1,1,1)

                newVert = (-vert[0], vert[2], vert[1])

                if matrix_world:
                    newVert = matrix_world @ Vector(newVert)

                pressure = 1.0
                strength = 1.0
                lp = latk.LatkPoint(co=newVert, pressure=pressure, strength=strength, col=col)

                points.append(lp)
                
                if (len(points) >= maxStrokePoints):
                    break
        except:
            print("Skipped stroke: No path from start to end.")
            pass

        if (len(points) >= minStrokePoints):  
            readyToAdd = True

            similarityString = ' '.join(map(str, similarity))

            if (checkSimilarity == True):
                for score in similarityScores:
                    similarityTest = similar2(score, similarityString)
                    if (similarityTest > maxSimilarity):
                        readyToAdd = False
                        print("Skipped stroke: Failed similarity test (" + str(similarityTest) + ").")
                        break

            if (readyToAdd):
                similarityScores.append(similarityString)
                
                stroke = frame.strokes.new()
                stroke.display_mode = '3DSPACE'
                stroke.line_width = int(latk_settings.thickness2) #10 # adjusted from 100 for 2.93
                stroke.material_index = gp.active_material_index

                stroke.points = points
                        
                strokeCounter += 1
                print("Added stroke " + str(strokeCounter) + " / " + str(numStrokes) + ".")
                    
    bpy.context.scene.cursor.location = origCursorLocation

    bpy.data.grease_pencils[gp.name].stroke_depth_order = "3D"

    return gp

def strokeGen(verts, colors, matrix_world=None, radius=2, minPointsCount=5): #, origin=None): #limitPalette=32):
    latk_settings = bpy.context.scene.latk_settings
    origCursorLocation = bpy.context.scene.cursor.location
    bpy.context.scene.cursor.location = (0.0, 0.0, 0.0)

    gp = getActiveGp()
    layer = getActiveLayer()
    if not layer:
        layer = gp.data.layers.new(name="meshToGp")
    frame = getActiveFrame()
    if not frame or frame.frame_number != currentFrame():
        frame = layer.frames.new(currentFrame())

    strokeGroups = group_points_into_strokes(verts, radius, minPointsCount)

    lastColor = (1,1,1,1)
    for strokeGroup in strokeGroups:
        strokeColors = []
        for i in range(0, len(strokeGroup)):
            try:
                newColor = colors[strokeGroup[i]]
                strokeColors.append(newColor)
                lastColor = newColor
            except:
                strokeColors.append((0,1,0,1)) #lastColor)
        '''
        if (limitPalette == 0):
            createColor(color)
        else:
            createAndMatchColorPalette(color, limitPalette, 5) # num places
        '''

        stroke = frame.strokes.new()
        stroke.display_mode = '3DSPACE'
        stroke.line_width = int(latk_settings.thickness2) #10 # adjusted from 100 for 2.93
        stroke.material_index = gp.active_material_index

        stroke.points.add(len(strokeGroup))

        for i, strokeIndex in enumerate(strokeGroup):    
            if not matrix_world:
                point = verts[strokeIndex]
            else:
                point = matrix_world @ Vector(verts[strokeIndex])

            #point = matrixWorldInverted @ Vector((point[0], point[2], point[1]))
            #point = (point[0], point[1], point[2])
            pressure = 1.0
            strength = 1.0
            createPoint(stroke, i, point, pressure, strength, strokeColors[i])

    bpy.context.scene.cursor.location = origCursorLocation

    bpy.data.grease_pencils[gp.name].stroke_depth_order = "3D"
    
    return gp

def contourGen(verts, faces, matrix_world):
    latk_settings = bpy.context.scene.latk_settings
    origCursorLocation = bpy.context.scene.cursor.location
    bpy.context.scene.cursor.location = (0.0, 0.0, 0.0)

    la = latk.Latk(init=True)

    gp = getActiveGp()
    layer = getActiveLayer()
    if not layer:
        layer = gp.data.layers.new(name="meshToGp")
    frame = getActiveFrame()
    if not frame or frame.frame_number != currentFrame():
        frame = layer.frames.new(currentFrame())

    mesh = checkForMesh(verts, faces)

    bounds = getDistance(mesh.bounds[0], mesh.bounds[1])

    # generate a set of contour lines at regular intervals
    interval = bounds * 0.01 #0.03  #0.1 # the spacing between contours
    print("Interval: " + str(interval))

    # x, z
    slice_range = np.arange(mesh.bounds[0][2], mesh.bounds[1][2], interval)
    # y
    #slice_range = np.arange(mesh.bounds[0][1], mesh.bounds[0][2], interval)

    # loop over the z values and generate a contour at each level
    for slice_pos in slice_range:
        # x
        #slice_mesh = mesh.section(plane_origin=[slice_pos, 0, 0], plane_normal=[1, 0, 0])
        # y
        #slice_mesh = mesh.section(plane_origin=[0, slice_pos, 0], plane_normal=[0, 1, 0])
        # z
        slice_mesh = mesh.section(plane_origin=[0, 0, slice_pos], plane_normal=[0, 0, 1])
        
        if slice_mesh != None:
            for entity in slice_mesh.entities:
                stroke = frame.strokes.new()
                stroke.display_mode = '3DSPACE'
                stroke.line_width = int(latk_settings.thickness2) #10 # adjusted from 100 for 2.93
                stroke.material_index = gp.active_material_index
                stroke.points.add(len(entity.points))

                for i, index in enumerate(entity.points):
                    vert = None
                    if not matrix_world:
                        vert = slice_mesh.vertices[index] 
                    else:
                        vert = matrix_world @ Vector(slice_mesh.vertices[index])
                    #vert = [vert[0], vert[1], vert[2]]
                    createPoint(stroke, i, vert, 1.0, 1.0)

    #fromLatkToGp(la, resizeTimeline=False)
    #setThickness(latk_settings.thickness)

    bpy.context.scene.cursor.location = origCursorLocation

    bpy.data.grease_pencils[gp.name].stroke_depth_order = "3D"

    return gp

def skelGen(verts, faces, matrix_world):
    latk_settings = bpy.context.scene.latk_settings
    origCursorLocation = bpy.context.scene.cursor.location
    bpy.context.scene.cursor.location = (0.0, 0.0, 0.0)

    la = latk.Latk(init=True)

    gp = getActiveGp()
    layer = getActiveLayer()
    if not layer:
        layer = gp.data.layers.new(name="meshToGp")
    frame = getActiveFrame()
    if not frame or frame.frame_number != currentFrame():
        frame = layer.frames.new(currentFrame())

    mesh = checkForMesh(verts, faces)

    fixed = sk.pre.fix_mesh(mesh, remove_disconnected=5, inplace=False)
    skel = sk.skeletonize.by_wavefront(fixed, waves=1, step_size=1)

    for entity in skel.skeleton.entities:
        stroke = frame.strokes.new()
        stroke.display_mode = '3DSPACE'
        stroke.line_width = int(latk_settings.thickness2) #10 # adjusted from 100 for 2.93
        stroke.material_index = gp.active_material_index
        stroke.points.add(len(entity.points))

        for i, index in enumerate(entity.points):
            vert = None
            if not matrix_world:
                vert = skel.vertices[index]
            else:
                vert = matrix_world @ Vector(skel.vertices[index])
            createPoint(stroke, i, vert, 1.0, 1.0)

    #fromLatkToGp(la, resizeTimeline=False)
    #setThickness(latk_settings.thickness)

    bpy.context.scene.cursor.location = origCursorLocation

    bpy.data.grease_pencils[gp.name].stroke_depth_order = "3D"

    return gp

def differenceEigenvalues(verts): #, k_n=50, thresh=0.03):
    latk_settings = bpy.context.scene.latk_settings
    # MIT License Copyright (c) 2015 Dena Bazazian Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the "Software"), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions: The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software. THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.

    pdVerts = pd.DataFrame(verts, columns=["x", "y", "z"])
    pcd1 = PyntCloud(pdVerts)
        
    # define hyperparameters
    k_n = latk_settings.edges_k_n # 50
    thresh = latk_settings.edges_thresh # 0.03

    pcd_np = np.zeros((len(pcd1.points), 6))

    # find neighbors
    kdtree_id = pcd1.add_structure("kdtree")
    k_neighbors = pcd1.get_neighbors(k=k_n, kdtree=kdtree_id) 

    # calculate eigenvalues
    ev = pcd1.add_scalar_field("eigen_values", k_neighbors=k_neighbors)

    x = pcd1.points['x'].values 
    y = pcd1.points['y'].values 
    z = pcd1.points['z'].values 

    e1 = pcd1.points['e3('+str(k_n+1)+')'].values
    e2 = pcd1.points['e2('+str(k_n+1)+')'].values
    e3 = pcd1.points['e1('+str(k_n+1)+')'].values

    sum_eg = np.add(np.add(e1,e2),e3)
    sigma = np.divide(e1,sum_eg)
    sigma_value = sigma

    # visualize the edges
    sigma = sigma>thresh

    # Save the edges and point cloud
    thresh_min = sigma_value < thresh
    sigma_value[thresh_min] = 0
    thresh_max = sigma_value > thresh
    sigma_value[thresh_max] = 255

    pcd_np[:,0] = x
    pcd_np[:,1] = y
    pcd_np[:,2] = z
    pcd_np[:,3] = sigma_value

    edge_np = np.delete(pcd_np, np.where(pcd_np[:,3] == 0), axis=0) 
    print(len(edge_np))

    clmns = ['x','y','z','red','green','blue']
    #pcd_pd = pd.DataFrame(data=pcd_np,columns=clmns)
    #pcd_pd['red'] = sigma_value.astype(np.uint8)

    #pcd_points = PyntCloud(pcd_pd)
    #edge_points = PyntCloud(pd.DataFrame(data=edge_np,columns=clmns))

    #PyntCloud.to_file(edge_points, outputPath) # Save just the edge points
    newVerts = []
    #for i in range(0, len(edge_points.points)):
    #    newVerts.append((edge_points.points["x"][i], edge_points.points["y"][i], edge_points.points["z"][i]))
    for edge in edge_np:
        newVerts.append((edge[0], edge[1], edge[2]))

    return newVerts

def strokeGen_orig(obj=None, strokeLength=1, strokeGaps=10.0, shuffleOdds=1.0, spreadPoints=0.1, limitPalette=32):
    if not obj:
        obj = ss()
    mesh = obj.data
    mat = obj.matrix_world
    #~
    gp = getActiveGp()
    layer = getActiveLayer()
    if not layer:
        layer = gp.data.layers.new(name="meshToGp")
    frame = getActiveFrame()
    if not frame or frame.frame_number != currentFrame():
        frame = layer.frames.new(currentFrame())
    #~
    images = None
    try:
        images = getUvImages()
    except:
        pass
    #~
    allPoints, allColors = getVertsAndColorsAlt(target=obj, useWorldSpace=True, useColors=True, useBmesh=False)
    #~
    pointSeqsToAdd = []
    colorsToAdd = []
    for i in range(0, len(allPoints), strokeLength):
        color = None
        if not images:
            try:
                color = allColors[i]
            except:
                color = getColorExplorer(obj, i)
        else:
            try:
                color = getColorExplorer(obj, i, images)
            except:
                color = getColorExplorer(obj, i)
        colorsToAdd.append(color)
        #~
        pointSeq = []
        for j in range(0, strokeLength):
            #point = allPoints[i]
            try:
                point = allPoints[i+j]
                if (len(pointSeq) == 0 or getDistance(pointSeq[len(pointSeq)-1], point) < strokeGaps):
                    pointSeq.append(point)
            except:
                break
        if (len(pointSeq) > 0): 
            pointSeqsToAdd.append(pointSeq)
    for i, pointSeq in enumerate(pointSeqsToAdd):
        color = colorsToAdd[i]
        #createColor(color)
        if (limitPalette == 0):
            createColor(color)
        else:
            createAndMatchColorPalette(color, limitPalette, 5) # num places
        #stroke = frame.strokes.new(getActiveColor().name)
        #stroke.draw_mode = "3DSPACE"
        stroke = frame.strokes.new()
        stroke.display_mode = '3DSPACE'
        stroke.line_width = 10 # adjusted from 100 for 2.93
        stroke.material_index = gp.active_material_index

        stroke.points.add(len(pointSeq))

        if (random.random() < shuffleOdds):
            random.shuffle(pointSeq)

        for j, point in enumerate(pointSeq):    
            x = point[0] + (random.random() * 2.0 * spreadPoints) - spreadPoints
            y = point[2] + (random.random() * 2.0 * spreadPoints) - spreadPoints
            z = point[1] + (random.random() * 2.0 * spreadPoints) - spreadPoints
            pressure = 1.0
            strength = 1.0
            createPoint(stroke, j, (x, y, z), pressure, strength)

def scale_numpy_array(arr, min_v, max_v):
    new_range = (min_v, max_v)
    max_range = max(new_range)
    min_range = min(new_range)

    scaled_unit = (max_range - min_range) / (np.max(arr) - np.min(arr))
    return arr * scaled_unit - np.min(arr) * scaled_unit + min_range

def resizeVoxels(voxel, shape):
    ratio = shape[0] / voxel.shape[0]
    voxel = nd.zoom(voxel,
            ratio,
            order=1, 
            mode='nearest')
    voxel[np.nonzero(voxel)] = 1.0
    return voxel

def getAveragePositionObj(obj=None, applyTransforms=False):
    if not obj:
        obj = ss()
    if (applyTransforms == True):
        bpy.ops.object.transform_apply(location=True, rotation=True, scale=True)
    return getAveragePosition(obj.data.vertices, obj.matrix_world)

def getAveragePosition(verts, matrix_world=None):
    returns = Vector((0,0,0))
    for vert in verts:
        if not matrix_world:
            returns += Vector(vert)
        else:
            returns += matrix_world @ Vector(vert)
    returns /= float(len(verts))
    return returns

def transferVertexColors(sourceVerts, sourceColors, destVerts):
    sourceVerts = np.array(sourceVerts)
    sourceColors = np.array(sourceColors)
    destVerts = np.array(destVerts)

    tree = cKDTree(sourceVerts)

    _, indices = tree.query(destVerts) #, k=1)

    destColors = sourceColors[indices]

    return destColors

def vertsToBinvox(verts, dims=256, doFilter=False, axis='xyz'):
    shape = (dims, dims, dims)
    data = np.zeros(shape, dtype=bool)
    translate = (0, 0, 0)
    scale = 1
    axis_order = axis
    bv = binvox_rw.Voxels(data, shape, translate, scale, axis_order)

    verts = normalize(verts, minVal=0.0, maxVal=float(dims-1))
    
    for vert in verts:
        x = int(vert[0])
        y = int(vert[1])
        z = int(vert[2])
        data[x][y][z] = True

    if (doFilter == True):
        for i in range(0, 1): # 1
            nd.binary_dilation(bv.data.copy(), output=bv.data)

        for i in range(0, 3): # 3
            nd.sobel(bv.data.copy(), output=bv.data)

        nd.median_filter(bv.data.copy(), size=4, output=bv.data) # 4

        for i in range(0, 2): # 2
            nd.laplace(bv.data.copy(), output=bv.data)

        for i in range(0, 0): # 0
            nd.binary_erosion(bv.data.copy(), output=bv.data)

    return bv

'''
def binvoxToVerts(voxel, dims=256, axis='xyz'):
    verts = []
    for x in range(0, dims):
        for y in range(0, dims):
            for z in range(0, dims):
                if (voxel.data[x][y][z] == True):
                    verts.append([x, y, z])
    return verts
'''

def binvoxToH5(voxel, dims=256):
    shape=(dims, dims, dims)   
    voxel_data = voxel.data.astype(float) #voxel.data.astype(np.float)
    if shape is not None and voxel_data.shape != shape:
        voxel_data = resize(voxel.data.astype(np.float64), shape)
    return voxel_data

def h5ToBinvox(data, dims=256):
    data = np.rint(data).astype(np.uint8)
    shape = (dims, dims, dims) #data.shape
    translate = [0, 0, 0]
    scale = 1.0
    axis_order = 'xzy'
    return binvox_rw.Voxels(data, shape, translate, scale, axis_order)

def writeTempH5(data, url="output.im"):
    url = os.path.join(bpy.app.tempdir, url)
    f = h5py.File(url, 'w')
    # more compression options: https://docs.h5py.org/en/stable/high/dataset.html
    f.create_dataset('data', data=data, compression='gzip')
    f.flush()
    f.close()

def readTempH5(url="output.im"):
    url = os.path.join(bpy.app.tempdir, url)
    return h5py.File(url, 'r').get('data')[()]

def writeTempBinvox(data, dims=256, url="output.binvox"):
    url = os.path.join(bpy.app.tempdir, url)
    data = np.rint(data).astype(np.uint8)
    shape = (dims, dims, dims) #data.shape
    translate = [0, 0, 0]
    scale = 1.0
    axis_order = 'xzy'
    voxel = binvox_rw.Voxels(data, shape, translate, scale, axis_order)

    with open(url, 'bw') as f:
        voxel.write(f)

def readTempBinvox(dims=256, axis='xyz', url="output.binvox"):
    url = os.path.join(bpy.app.tempdir, url)
    voxel = None
    print("Reading from: " + url)
    with open(url, 'rb') as f:
        voxel = binvox_rw.read_as_3d_array(f, True) # fix coords
    verts = []
    for x in range(0, dims):
        for y in range(0, dims):
            for z in range(0, dims):
                if (voxel.data[x][y][z] == True):
                    verts.append([z, y, x])
    return verts

def npToCv(img):
    return cv2.cvtColor(img, cv2.COLOR_RGB2BGR)

def cvToNp(img):
    return np.asarray(img)

def cvToBlender(img):
    rgb_image = cv2.cvtColor(img, cv2.COLOR_BGRA2RGBA)
    blender_image = bpy.data.images.new("Image", width=rgb_image.shape[1], height=rgb_image.shape[0])
    pixels = np.flip(rgb_image.flatten())
    blender_image.pixels.foreach_set(pixels)
    blender_image.update()
    return blender_image

def createTempOutputSettings(newFilename="render.png", newFormat="PNG"):
    newFilepath = os.path.join(bpy.app.tempdir, newFilename)

    oldFilepath = bpy.context.scene.render.filepath
    oldFormat = bpy.context.scene.render.image_settings.file_format
    
    bpy.context.scene.render.filepath = newFilepath
    bpy.context.scene.render.image_settings.file_format = newFormat

    return oldFilepath, oldFormat, newFilepath, newFormat

def restoreOldOutputSettings(oldFilepath, oldFormat):
    bpy.context.scene.render.filepath = oldFilepath
    bpy.context.scene.render.image_settings.file_format = oldFormat

def renderFrame(depthPass=False):
    oldFilepath, oldFormat, newFilepath, newFormat = createTempOutputSettings()
    if (depthPass == True):
        setupDepthPass(newFilepath.split("." + newFormat)[0] + "_depth")
    bpy.ops.render.render(write_still=True)
    restoreOldOutputSettings(oldFilepath, oldFormat)
    if (depthPass == True):
        return os.path.join(newFilepath.split("." + newFormat)[0] + "_depth", "Image" + str(bpy.data.scenes['Scene'].frame_current).zfill(4) + "." + newFormat)
    else:
        return newFilepath

# https://www.saifkhichi.com/blog/blender-depth-map-surface-normals
def getDepthPassAlt():
    """Obtains depth map from Blender render.
    :return: The depth map of the rendered camera view as a numpy array of size (H,W).
    """
    z = bpy.data.images['Viewer Node']
    w, h = z.size
    dmap = np.array(z.pixels[:], dtype=np.float32) # convert to numpy array
    dmap = np.reshape(dmap, (h, w, 4))[:,:,0]
    dmap = np.rot90(dmap, k=2)
    dmap = np.fliplr(dmap)
    return dmap

# https://blender.stackexchange.com/questions/2170/how-to-access-render-result-pixels-from-python-script/23309#23309
# https://blender.stackexchange.com/questions/56967/how-to-get-depth-data-using-python-api
def setupDepthPass(url="/my_path/"):
    # Set up rendering of depth map:
    bpy.context.scene.use_nodes = True
    tree = bpy.context.scene.node_tree
    links = tree.links
    #~
    # clear default nodes
    for n in tree.nodes:
        tree.nodes.remove(n)
    #~
    # create input render layer node
    rl = tree.nodes.new('CompositorNodeRLayers')
    #~
    map = tree.nodes.new(type="CompositorNodeMapValue")
    # Size is chosen kind of arbitrarily, try out until you're satisfied with resulting depth map.
    map.size = [0.08]
    map.use_min = True
    map.min = [0]
    map.use_max = True
    map.max = [255]
    links.new(rl.outputs[2], map.inputs[0])
    #~
    invert = tree.nodes.new(type="CompositorNodeInvert")
    links.new(map.outputs[0], invert.inputs[1])
    #~
    # The viewer can come in handy for inspecting the results in the GUI
    depthViewer = tree.nodes.new(type="CompositorNodeViewer")
    links.new(invert.outputs[0], depthViewer.inputs[0])
    # Use alpha from input.
    links.new(rl.outputs[1], depthViewer.inputs[1])
    #~
    # create a file output node and set the path
    fileOutput = tree.nodes.new(type="CompositorNodeOutputFile")
    fileOutput.base_path = url
    links.new(invert.outputs[0], fileOutput.inputs[0])

def renderToCv(depthPass=False):
    image_path = renderFrame(depthPass)
    image = cv2.imread(image_path)
    return cv2.cvtColor(image, cv2.COLOR_RGB2BGR)

def renderToNp(depthPass=False):
    image_path = renderFrame(depthPass)
    width = bpy.context.scene.render.resolution_x
    height = bpy.context.scene.render.resolution_y

    image = bpy.data.images.load(image_path)
    image_array = np.array(image.pixels[:])
    image_array = image_array.reshape((height, width, 4))
    image_array = np.flipud(image_array)
    image_array = image_array[:, :, :3]
    return image_array.astype(np.float32)

# ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~
def loadModel003(name):
    latk_settings = bpy.context.scene.latk_settings
    returns = modelSelector003(name, latk_settings.Operation1)
    return returns

def loadModel004(name):
    latk_settings = bpy.context.scene.latk_settings
   
    returns1 = modelSelector004(name, latk_settings.ModelStyle1)
    returns2 = modelSelector004(name, latk_settings.ModelStyle2)

    return returns1, returns2

def modelSelector003(name, modelName):
    latk_settings = bpy.context.scene.latk_settings

    modelName = modelName.lower()
    latk_settings.dims = int(modelName.split("_")[0])
    return Vox2Vox_PyTorch(name, os.path.join("model", modelName + ".pth"))

def modelSelector004(name, modelName):
    modelName = modelName.lower()
    latk_settings = bpy.context.scene.latk_settings

    if (bpy.context.preferences.addons[name].preferences.Backend.lower() == "pytorch"):
        if (modelName == "anime"):
            return Informative_Drawings_PyTorch(name, os.path.join("checkpoints", "anime_style_netG_A_latest.pth"))
        elif (modelName == "contour"):
            return Informative_Drawings_PyTorch(name, os.path.join("checkpoints", "contour_style_netG_A_latest.pth"))
        elif (modelName == "opensketch"):
            return Informative_Drawings_PyTorch(name, os.path.join("checkpoints", "opensketch_style_netG_A_latest.pth"))
        elif (modelName == "pxp_001"):
            return Pix2Pix_PyTorch(name, os.path.join("checkpoints", "pix2pix002-001_60_net_G.pth"))
        elif (modelName == "pxp_002"):
            return Pix2Pix_PyTorch(name, os.path.join("checkpoints", "pix2pix002-002_60_net_G.pth"))
        elif (modelName == "pxp_003"):
            return Pix2Pix_PyTorch(name, os.path.join("checkpoints", "pix2pix002-003_60_net_G.pth"))
        elif (modelName == "pxp_004"):
            return Pix2Pix_PyTorch(name, os.path.join("checkpoints", "pix2pix002-004_60_net_G.pth"))
        else:
            return None
    elif (bpy.context.preferences.addons[name].preferences.Backend.lower() == "onnx"):
        if (modelName == "anime"):
            return Informative_Drawings_Onnx(name, os.path.join("onnx", "anime_style_512x512.onnx"))
        elif (modelName == "contour"):
            return Informative_Drawings_Onnx(name, os.path.join("onnx", "contour_style_512x512.onnx"))
        elif (modelName == "opensketch"):
            return Informative_Drawings_Onnx(name, os.path.join("onnx", "opensketch_style_512x512.onnx"))
        elif (modelName == "pxp_001"):
            return Pix2Pix_Onnx(name, os.path.join("onnx", "pix2pix004-002_140_net_G_simplified.onnx"))
        elif (modelName == "pxp_002"):
            return Pix2Pix_Onnx(name, os.path.join("onnx", "pix2pix003-002_140_net_G_simplified.onnx"))
        elif (modelName == "pxp_003"):
            return Pix2Pix_Onnx(name, os.path.join("onnx", "neuralcontours_140_net_G_simplified.onnx"))
        elif (modelName == "pxp_004"):
            return Pix2Pix_Onnx(name, os.path.join("onnx", "neuralcontours_140_net_G_simplified.onnx"))
        else:
            return None

def doInference003(name, net, verts, dims=256, seqMin=0.0, seqMax=1.0):
    latk_settings = bpy.context.scene.latk_settings
    
    bv = vertsToBinvox(verts, dims, doFilter=latk_settings.do_filter)
    
    if (latk_settings.do_write_input == True):
        writeTempBinvox(bv.data, dims, url="input.binvox")
    
    h5 = binvoxToH5(bv, dims=dims)
    writeTempH5(h5)

    fake_B = net.detect()

    writeTempBinvox(fake_B, dims=dims)
    verts = readTempBinvox(dims=dims)
    dims_ = float(dims - 1)

    for i in range(0, len(verts)):
        x = remap(verts[i][0], 0.0, dims_, seqMin, seqMax)
        y = remap(verts[i][1], 0.0, dims_, seqMin, seqMax)
        z = remap(verts[i][2], 0.0, dims_, seqMin, seqMax)
        verts[i] = Vector((x, y, z))

    return verts

# https://blender.stackexchange.com/questions/262742/python-bpy-2-8-render-directly-to-matrix-array
# https://blender.stackexchange.com/questions/2170/how-to-access-render-result-pixels-from-python-script/3054#3054
def doInference004(name, net1, net2=None):
    latk_settings = bpy.context.scene.latk_settings

    img_np = None
    img_cv = None
    if (latk_settings.SourceImage.lower() == "depth"):
        img_np = renderToNp(depthPass=True) # inference expects np array
        img_temp = renderToNp()
        img_cv = npToCv(img_temp) # cv converted image used for color pixels later
    else:
        img_np = renderToNp() # inference expects np array
        img_cv = npToCv(img_np) # cv converted image used for color pixels later

    result = net1.detect(img_np)

    if (net2 != None):
        net1name = latk_settings.ModelStyle1.lower()
        if (bpy.context.preferences.addons[name].preferences.Backend.lower() == "pytorch" and (net1name == "anime" or net1name == "contour" or net1name == "opensketch")):
            outputUrl = os.path.join(bpy.app.tempdir, "intermediate.png")
            cv2.imwrite(outputUrl, result)
            result = cv2.imread(outputUrl)
        else:
            result = net2.detect(result)

    outputUrl = os.path.join(bpy.app.tempdir, "output.png")
    cv2.imwrite(outputUrl, result)

    im0 = cv2.imread(outputUrl)
    im0 = cv2.bitwise_not(im0) # invert
    imWidth = len(im0[0])
    imHeight = len(im0)
    im = (im0[:,:,0] > latk_settings.lineThreshold).astype(np.uint8)
    im = skeletonize(im).astype(np.uint8)
    polys = from_numpy(im, latk_settings.csize, latk_settings.maxIter)

    laFrame = latk.LatkFrame(frame_number=bpy.context.scene.frame_current)

    scene = bpy.context.scene
    camera = bpy.context.scene.camera

    frame = camera.data.view_frame(scene=bpy.context.scene)
    topRight = frame[0]
    bottomRight = frame[1]
    bottomLeft = frame[2]
    topLeft = frame[3]

    resolutionX = int(bpy.context.scene.render.resolution_x * (bpy.context.scene.render.resolution_percentage / 100))
    resolutionY = int(bpy.context.scene.render.resolution_y * (bpy.context.scene.render.resolution_percentage / 100))
    xRange = np.linspace(topLeft[0], topRight[0], resolutionX)
    yRange = np.linspace(topLeft[1], bottomLeft[1], resolutionY)

    originalStrokes = []
    originalStrokeColors = []
    separatedStrokes = []
    separatedStrokeColors = []

    # raycasting needs cursor at world origin
    origCursorLocation = bpy.context.scene.cursor.location
    bpy.context.scene.cursor.location = (0.0, 0.0, 0.0)
    
    for target in bpy.data.objects:
        if target.type == "MESH":
            matrixWorld = target.matrix_world
            matrixWorldInverted = matrixWorld.inverted()
            origin = matrixWorldInverted @ camera.matrix_world.translation

            for stroke in polys:
                newStroke = []
                newStrokeColor = []
                for point in stroke:
                    rgbPixel = img_cv[point[1]][point[0]]
                    rgbPixel2 = (rgbPixel[2], rgbPixel[1], rgbPixel[0], 1)

                    xPos = remap(point[0], 0, resolutionX, xRange.min(), xRange.max())
                    yPos = remap(point[1], 0, resolutionY, yRange.max(), yRange.min())
                   
                    pixelVector = Vector((xPos, yPos, topLeft[2]))
                    pixelVector.rotate(camera.matrix_world.to_quaternion())
                    destination = matrixWorldInverted @ (pixelVector + camera.matrix_world.translation) 
                    direction = (destination - origin).normalized()
                    hit, location, norm, face = target.ray_cast(origin, direction)

                    if hit:
                        location = target.matrix_world @ location
                        co = (location.x, location.y, location.z)
                        newStroke.append(co)
                        newStrokeColor.append(rgbPixel2)

                if (len(newStroke) > 1):
                    originalStrokes.append(newStroke)
                    originalStrokeColors.append(newStrokeColor)

        for i in range(0, len(originalStrokes)):
            separatedTempStrokes, separatedTempStrokeColors = separatePointsByDistance(originalStrokes[i], originalStrokeColors[i], latk_settings.distThreshold)

            for j in range(0, len(separatedTempStrokes)):
                separatedStrokes.append(separatedTempStrokes[j])
                separatedStrokeColors.append(separatedTempStrokeColors[j])

        for i in range(0, len(separatedStrokes)):
            laPoints = []
            for j in range(0, len(separatedStrokes[i])):
                laPoint = latk.LatkPoint(separatedStrokes[i][j])
                laPoint.vertex_color = separatedStrokeColors[i][j]
                laPoints.append(laPoint)

            if (len(laPoints) > 1):
                laFrame.strokes.append(latk.LatkStroke(laPoints))

    bpy.context.scene.cursor.location = origCursorLocation
    return laFrame

# ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~


def doVoxelOpCore(name, context, allFrames=False):
    latk_settings = context.scene.latk_settings

    dims = None
    
    op1 = latk_settings.Operation1.lower() 
    op2 = latk_settings.Operation2.lower() 
    op3 = latk_settings.Operation3.lower() 

    net1 = None
    obj = ss()
    la = latk.Latk(init=True)
    gp = fromLatkToGp(la, resizeTimeline = False)

    start = bpy.context.scene.frame_current
    end = start + 1
    if (allFrames == True):
        start, end = getStartEnd()
    #if (op1 != "none"):
        #start = start - 1

    for i in range(start, end):
        goToFrame(i)

        origCursorLocation = bpy.context.scene.cursor.location
        bpy.context.scene.cursor.location = (0.0, 0.0, 0.0)

        #s(obj)
        #bpy.context.view_layer.objects.active = obj
        #bpy.ops.object.transform_apply(location=True, rotation=True, scale=True)
        #bpy.ops.object.origin_set(type='ORIGIN_GEOMETRY')

        #verts, colors = getVertsAndColors(target=obj, useWorldSpace=False, useColors=True, useBmesh=False)
        verts, colors = getVertices(obj, getColors=True, worldSpace=False)
        #verts = getVertices(obj)
        faces = getFaces(obj)
        matrix_world = obj.matrix_world
        
        #bounds = obj.dimensions
        seqAbs = None #(bounds.x + bounds.y + bounds.z) / 3.0

        seqMin = 0.0
        seqMax = 1.0
    
        for vert in verts:
            x = vert[0]
            y = vert[1]
            z = vert[2]
            if (x < seqMin):
                seqMin = x
            if (x > seqMax):
                seqMax = x
            if (y < seqMin):
                seqMin = y
            if (y > seqMax):
                seqMax = y
            if (z < seqMin):
                seqMin = z
            if (z > seqMax):
                seqMax = z

        seqAbs = abs(seqMax - seqMin)

        if (op1 != "none"):
            if not net1:
                net1 = loadModel003(name)    
                dims = latk_settings.dims   

            avgPosOrig = None
            if (latk_settings.do_recenter == True):
                avgPosOrig = getAveragePosition(verts)

            vertsOrig = np.array(verts) #.copy()
            verts = doInference003(name, net1, verts, dims, seqMin, seqMax)

            if (latk_settings.do_recenter == True):
                avgPosNew = getAveragePosition(verts)
                diffPos = avgPosOrig - avgPosNew
                for i in range(0, len(verts)):
                    verts[i] = verts[i] + diffPos

            colors = transferVertexColors(vertsOrig, colors, verts)

        if (op2 == "get_edges" and op1 == "none"):
            vertsOrig = np.array(verts)
            verts = differenceEigenvalues(verts)
            colors = transferVertexColors(vertsOrig, colors, verts)           

        bpy.context.scene.cursor.location = origCursorLocation

        #gp = None

        if (op3 == "stroke_gen"):
            strokeGen(verts, colors, matrix_world=matrix_world, radius=seqAbs * latk_settings.strokegen_radius, minPointsCount=latk_settings.strokegen_minPointsCount) #, origin=obj.location) #limitPalette=context.scene.latk_settings.paletteLimit)
        elif (op3 == "neural_gas"):
            neuralGasGen(np.array(verts), colors, matrix_world=matrix_world, max_neurons=latk_settings.gas_max_neurons, max_iter=latk_settings.gas_max_iter, max_age=latk_settings.gas_max_age, l=latk_settings.gas_max_L)
        elif (op3 == "neural_gas2"):
            neuralGasGen2(np.array(verts), colors, matrix_world=matrix_world, max_neurons=latk_settings.gas_max_neurons, max_iter=latk_settings.gas_max_iter, max_age=latk_settings.gas_max_age, l=latk_settings.gas_max_L, radius=seqAbs * latk_settings.strokegen_radius, minPointsCount=latk_settings.strokegen_minPointsCount)
        elif (op3 == "neural_gas3"):
            neuralGasGen3(np.array(verts), colors, matrix_world=matrix_world, max_neurons=latk_settings.gas_max_neurons, max_iter=latk_settings.gas_max_iter, max_age=latk_settings.gas_max_age, l=latk_settings.gas_max_L, radius=seqAbs * latk_settings.strokegen_radius, minPointsCount=latk_settings.strokegen_minPointsCount)
        elif (op3 == "contour_gen"): #and op1 == "none"):
            contourGen(verts, faces, matrix_world=matrix_world)
        elif (op3 == "skel_gen"): #and op1 == "none"):
            skelGen(verts, faces, matrix_world=matrix_world)

    if (latk_settings.do_modifiers == True):
        gp = getActiveGp()
        
        bpy.ops.object.gpencil_modifier_add(type="GP_SIMPLIFY")
        gp.grease_pencil_modifiers["Simplify"].mode = "MERGE"
        gp.grease_pencil_modifiers["Simplify"].distance = latk_settings.strokegen_radius

        bpy.ops.object.gpencil_modifier_add(type="GP_SUBDIV")

        bpy.ops.object.gpencil_modifier_add(type="GP_SMOOTH")
        gp.grease_pencil_modifiers["Smooth"].use_keep_shape = True
