# 2 of 9. TOOLS

def cameraArray(target=None): 
    if not target:
        target = ss()
    coords = [(target.matrix_world * v.co) for v in target.data.vertices]
    cams = []
    for coord in coords:
        cam = createCamera()
        cam.location = coord
        cams.append(cam)
    for cam in cams:
        lookAt(cam, target)

def lookAt(looker, lookee):
    deselect()
    select([looker, lookee])
    lookerPos = looker.matrix_world.to_translation()
    lookeePos = lookee.matrix_world.to_translation()
    #~
    direction = lookeePos - lookerPos
    #~
    # point the cameras '-Z' and use its 'Y' as up
    rot_quat = direction.to_track_quat('-Z', 'Y')
    #~
    # assume we're using euler rotation
    looker.rotation_euler = rot_quat.to_euler()
    
def getLayerInfo(layer):
    return layer.info.split(".")[0]

def getActiveFrameNum(layer=None):
    # assumes layer can have only one active frame
    if not layer:
        layer = getActiveLayer()
    returns = -1
    for i in range(0, len(layer.frames)):
        if (layer.frames[i] == layer.active_frame):
            returns = i
    return returns

def matchWithParent(_child, _parent, _index):
    if (_parent):
        #bpy.context.scene.frame_set(_index)
        #if (_index == bpy.context.scene.frame_start):
        '''
        for v in _child.data.splines.active.bezier_points:
            loc = v.co * _parent.matrix_world.inverted()
            v.co = loc
        '''
        loc, rot, scale = _parent.matrix_world.inverted().decompose()
        _child.location = loc
        #_child.rotation_quaternion = rot
        _child.scale = scale
        #bpy.context.scene.update()
        _child.parent = _parent
        keyTransform(_child, _index)   

def clearState():
    for ob in bpy.data.objects.values():
        try:
            ob.selected=False
        except:
            pass
    bpy.context.scene.objects.active = None

def onionSkin(layers=None, onion=False):
    if not layers:
        layers = getActiveGp().layers
    for layer in layers:
        layer.use_onion_skinning = onion

def bakeParentToChild(start=None, end=None):
    if (start==None and end==None):
        start, end = getStartEnd()
    # https://www.blender.org/api/blender_python_api_2_72_1/bpy.ops.nla.html
    #bpy.ops.nla.bake(frame_start=start, frame_end=end, step=1, only_selected=True, visual_keying=True, clear_constraints=True, clear_parents=True, bake_types={'OBJECT'})    
    bpy.ops.nla.bake(frame_start=start, frame_end=end, step=1, only_selected=True, visual_keying=True, clear_constraints=True, clear_parents=True, use_current_action=True, bake_types={'OBJECT'})    

def bakeParentToChildByName(name="crv"):
    start, end = getStartEnd()
    target = matchName(name)
    for obj in target:
        bpy.context.scene.objects.active = obj
        #print(bpy.context.scene.objects.active.name)
        bakeParentToChild(start, end)

def getWorldCoords(co=None, camera=None, usePixelCoords=True, useRenderScale=True, flipV=True):
    # https://blender.stackexchange.com/questions/882/how-to-find-image-coordinates-of-the-rendered-vertex
    # Test the function using the active object (which must be a camera)
    # and the 3D cursor as the location to find.
    scene = bpy.context.scene
    if not camera:
        camera = bpy.context.object
    if not co:
        co = bpy.context.scene.cursor_location
    #~
    co_2d = bpy_extras.object_utils.world_to_camera_view(scene, camera, co)
    pixel_2d = None
    #~
    if (usePixelCoords==False):
        print("2D Coords: ", co_2d)
        return co_2d
    else:
        render_size = getSceneResolution(useRenderScale)
        if (flipV==True):
            pixel_2d = (round(co_2d.x * render_size[0]), round(render_size[1] - (co_2d.y * render_size[1])))
        else:
            pixel_2d = (round(co_2d.x * render_size[0]), round(co_2d.y * render_size[1]))
        print("Pixel Coords: ", pixel_2d)
        return pixel_2d

def getSceneResolution(useRenderScale=True):
    # https://blender.stackexchange.com/questions/882/how-to-find-image-coordinates-of-the-rendered-vertex
    scene = bpy.context.scene
    render_scale = scene.render.resolution_percentage / 100
    if (useRenderScale==True):
        return (int(scene.render.resolution_x * render_scale), int(scene.render.resolution_y * render_scale))
    else:
        return (int(scene.render.resolution_x), int(scene.render.resolution_y))

def setSceneResolution(width=1920, height=1080, scale=50):
    # https://blender.stackexchange.com/questions/9164/modify-render-settings-for-all-scenes-using-python
    for scene in bpy.data.scenes:
        scene.render.resolution_x = width
        scene.render.resolution_y = height
        scene.render.resolution_percentage = scale
        scene.render.use_border = False

def getSceneFps():
    return bpy.context.scene.render.fps

def setSceneFps(fps=12):
    for scene in bpy.data.scenes:
        scene.render.fps = fps

def deselect():
    bpy.ops.object.select_all(action='DESELECT')

def selectAll():
    bpy.ops.object.select_all(action='SELECT')

# TODO fix so you can find selected group regardless of active object
def getActiveGroup():
    obj = bpy.context.scene.objects.active
    for group in bpy.data.groups:
        for groupObj in group.objects:
            if(obj.name == groupObj.name):
                return group
    return None

def getChildren(target=None):
    if not target:
        target=s()[0]
    # https://www.blender.org/forum/viewtopic.php?t=8661
    return [ob for ob in bpy.context.scene.objects if ob.parent == target]

def groupName(name="crv", gName="myGroup"):
    deselect()
    selectName(name)
    makeGroup(gName)

def makeGroup(name="myGroup", newGroup=True):
    if (newGroup==True):
        bpy.ops.group.create(name=name)
    else:
        bpy.ops.group_link(group=name)

def deleteGroup(name="myGroup"):
    group = bpy.data.groups[name]
    for obj in group.objects:
        delete(obj)
    removeGroup(name)

def deleteGroups(name=["myGroup"]):
    for n in name:
        deleteGroup(n)

def preserveGroups(name=["myGroup"]):
    allNames = []
    for group in bpy.data.groups:
        allNames.append(group.name)
    for aN in allNames:
        doDelete = True
        for n in name:
            if (aN == n):
                doDelete = False
        if (doDelete == True):
            deleteGroup(aN)

def preserveGroupName(name="myGroup"):
    allNames = []
    for group in bpy.data.groups:
        allNames.append(group.name)
    for aN in allNames:
        doDelete = True
        for n in name:
            if re.match(r'^' + n + '', aN):
                doDelete = False
        if (doDelete == True):
            deleteGroup(aN)

def deleteGroupName(name="myGroup"):
    allNames = []
    for group in bpy.data.groups:
        allNames.append(group.name)
    for aN in allNames:
        doDelete = False
        for n in name:
            if re.match(r'^' + n + '', aN):
                doDelete = True
        if (doDelete == True):
            deleteGroup(aN)

def removeGroup(name="myGroup", allGroups=False):
    if (allGroups==False):
        group = bpy.data.groups[name]
        #for group in bpy.data.groups:
            #if group.users == 1 and len(group.users_dupli_group) == 0: # EDIT
        group.user_clear()
        bpy.data.groups.remove(group) 
        #~
        #bpy.ops.group_unlink(group=group.name)
    else:
        for group in bpy.data.groups:
            group.user_clear()
            bpy.data.groups.remove(group)   
            #~
            #bpy.ops.group_unlink(group=group.name)

def importGroup(path, name, winDir=False):
    importAppend(path, "Group", name, winDir)

def removeObj(name="myObj", allObjs=False):
    if (allObjs==False):
        obj = bpy.data.objects[name]
        obj.user_clear()
        bpy.data.objects.remove(obj) 
    else:
        for obj in bpy.data.objects:
            obj.user_clear()
            bpy.data.objects.remove(obj)  
    refresh()

def deleteDuplicateStrokes(fromAllFrames = False):
    strokes = getSelectedStrokes()
    checkPoints = []
    for i in range(0, len(strokes)):
        checkPoints.append(sumPoints(strokes[i]))
    for i in range(0, len(strokes)):
        for j in range(0, len(strokes)):
            try:
                if ( j != i and checkPoints[i] == checkPoints[j]):
                    bpy.ops.object.select_all(action='DESELECT')
                    strokes[i].select = True
                    deleteSelected()
            except:
                pass

def deleteStroke(_stroke):
    bpy.ops.object.select_all(action='DESELECT')
    _stroke.select = True
    deleteSelected()

def deleteStrokes(_strokes):
    bpy.ops.object.select_all(action='DESELECT')
    for stroke in _strokes:
        stroke.select = True
    deleteSelected()

def selectStrokePoint(_stroke, _index):
    for i, point in enumerate(_stroke.points):
        if (i==_index):
            point.select=True
        else:
            point.select=False
    return _stroke.points[_index]

def selectLastStrokePoint(_stroke):
    return selectStrokePoint(_stroke, len(_stroke.points)-1)

def getEmptyStrokes(_strokes, _minPoints=0):
    returns = []
    for stroke in _strokes:
        if (len(stroke.points) <= _minPoints):
            returns.append(stroke)
    print("Found " + str(len(returns)) + " empty strokes.")
    return returns

def cleanEmptyStrokes(_strokes, _minPoints=0):
    target = getEmptyStrokes(_strokes, _minPoints)
    deleteStrokes(target)

def consolidateGroups():
    wholeNames = []
    mergeNames = []
    for group in bpy.data.groups:
        if("." in group.name):
            mergeNames.append(group.name)
        else:
            wholeNames.append(group.name)
    for sourceName in mergeNames:
        sourceGroup = bpy.data.groups[sourceName]
        destGroup = None
        for destName in wholeNames:
            if (sourceName.split(".")[0] == destName):
                destGroup = bpy.data.groups[destName]
                break
        if (destGroup==None):
            break
        else:
            for obj in sourceGroup.objects:
                try:
                    destGroup.objects.link(obj)
                except:
                    pass
            removeGroup(sourceName)
    print(mergeNames)
    print(wholeNames)


def sumPoints(stroke):
    x = 0
    y = 0
    z = 0
    for point in stroke.points:
        co = point.co
        x += co[0]
        y += co[1]
        z += co[2]
    return roundVal(x + y + z, 5)

def renameCurves(name="mesh", nameMesh="crv_ob_mesh", nameCurve="crv"):
    target = matchName(nameMesh)
    for i in range(0, len(target)):
        target[i].name = name + "_" + str(i)
    #dn(nameCurve)

def deleteUnparentedCurves(name="crv"):
    target = matchName(name)
    toDelete = []
    for i in range(0, len(target)):
        if (target[i].parent==None):
            toDelete.append(target[i])
    print(str(len(toDelete)) + " objects selected for deletion.")
    for i in range(0, len(toDelete)):
        delete(toDelete[i])

def currentFrame(target=None):
    if not target:
        return bpy.context.scene.frame_current
    else:
        goToFrame(target)

def distributeStrokesAlt(step=1):
    palette = getActivePalette()
    strokes = getAllStrokes()
    layer = getActiveLayer()
    strokesToBuild = []
    counter = 1
    for i in range(0, len(strokes)):
        goToFrame(i+1)
        try:
            layer.frames.new(bpy.context.scene.frame_current)
        except:
            pass
        layer.active_frame = layer.frames[i+1]
        '''
        strokesToBuild.append(strokes[i])
        for l in range(0, len(strokesToBuild)):    
            strokeDest = getActiveFrame().strokes.new(palette.colors[0].name)
            strokeDest.draw_mode = '3DSPACE'
            strokeDest.points.add(len(strokesToBuild[l].points))
            for m in range(0, len(strokesToBuild[l].points)):
                strokeDest.points[m].co = strokesToBuild[l].points[m].co 
                strokeDest.points[m].pressure = 1
                strokeDest.points[m].strength = 1
        '''
        copyFrame(0, i+1, counter)
        counter += step
        if (counter > len(strokes)-1):
            counter = len(strokes)-1

def distributeStrokes(pointStep=10, step=1, minPointStep=2):
    start, end = getStartEnd()
    palette = getActivePalette()
    strokes = getAllStrokes()
    layer = getActiveLayer()
    strokeCounter = 0
    extraFrameCounter = 0
    #~
    for i in range(0, len(strokes)):
        goToFrame(i+1+extraFrameCounter)
        try:
            layer.frames.new(bpy.context.scene.frame_current)
        except:
            pass
        layer.active_frame = layer.frames[bpy.context.scene.frame_current]
        #~
        if (pointStep < minPointStep):
            copyFrame(0, i+1+extraFrameCounter, strokeCounter+1)
        else:
            copyFrame(0, i+1+extraFrameCounter, strokeCounter)
        #lastGoodLoc = bpy.context.scene.frame_current
        #print("* * * main frame at: " + str(lastGoodLoc) + " * * *")
        #~
        if (pointStep >= minPointStep):
        #else:
            pointsCounter = 0
            stroke = strokes[strokeCounter]
            points = stroke.points
            subFrames = roundValInt(len(points)/pointStep)
            #print("points: " + str(len(points)) + "   subframes: " + str(subFrames))
            for j in range(0, subFrames):
                extraFrameCounter += 1
                #inLoc = lastGoodLoc #strokeCounter+1+extraFrameCounterLast
                outLoc = i+1+extraFrameCounter
                goToFrame(outLoc)
                try:
                    layer.frames.new(bpy.context.scene.frame_current)
                except:
                    pass
                layer.active_frame = layer.frames[bpy.context.scene.frame_current]
                #~
                #print("-> copying " + str(inLoc) + " to " + str(outLoc))
                #~ * * * * * * *
                #copyFrame(0, outLoc, strokeCounter+1)#, j * pointStep)
                #copyFrame(0, outLoc, strokeCounter)
                for l in range(0, strokeCounter):
                    createStroke(layer.frames[0].strokes[l].points, layer.frames[0].strokes[l].color.color, layer.frames[outLoc])#newStroke.color.color)
                #~ * * * * * * *
                #refresh()
                newStroke = layer.frames[0].strokes[strokeCounter]
                newPoints = []
                for l in range(0, len(newStroke.points)):
                    if (l < j * pointStep):
                        newPoints.append(newStroke.points[l])  
                #~                                         
                #createStroke(newPoints, (1,0,0), layer.frames[outLoc])
                createStroke(newPoints, newStroke.color.color, layer.frames[outLoc])
        #~
        strokeCounter += step
        if (strokeCounter > len(strokes)-1):
            strokeCounter = len(strokes)-1
    #~
    lastLoc = len(strokes)+1+extraFrameCounter
    goToFrame(lastLoc)
    try:
        layer.frames.new(bpy.context.scene.frame_current)
    except:
        pass
    layer.active_frame = layer.frames[bpy.context.scene.frame_current]
    copyFrame(0, lastLoc)

ds = distributeStrokes

# note that unlike createStroke, this creates a stroke from raw coordinates
def drawPoints(points=None, color=None, frame=None, layer=None):
    if (len(points) > 0):
        if not color:
            color = getActiveColor()
        if not layer:
            layer = getActiveLayer()
            if not layer:
                gp = getActiveGp()
                layer = gp.layers.new("GP_Layer")
                gp.layers.active = layer
        if not frame:
            frame = getActiveFrame()
            if not frame:
                try:
                    frame = layer.frames.new(currentFrame())
                except:
                    pass
        stroke = frame.strokes.new(color.name)
        stroke.draw_mode = "3DSPACE"
        stroke.points.add(len(points))
        for i, point in enumerate(points):
            pressure = 1.0
            strength = 1.0
            if (len(point) > 3):
                pressure = point[3]
            if (len(point) > 4):
                strength = point[4]
            createPoint(stroke, i, (point[0], point[2], point[1]), pressure, strength)
        return stroke
    else:
        return None

def writeOnStrokes(step=1):
    gp = getActiveGp()
    for i in range(0, len(gp.layers)):
        gp.layers.active_index = i
        distributeStrokes(step)

def getDistance(v1, v2):
    return sqrt( (v1[0] - v2[0])**2 + (v1[1] - v2[1])**2 + (v1[2] - v2[2])**2)
    
'''
def joinObjects(target=None):
    if not target:
        target = s()
    for i in range(1, len(target)):
        try:
            bpy.ops.object.select_all(action='DESELECT')
            bpy.context.scene.objects.active = target[i]
            #print("****** " + str(bpy.context.scene.objects.active))
            #bpy.context.scene.objects.active.select = True
            target[i].select =True
            target[i-1].select =True
            bpy.ops.object.join()
            #bpy.context.scene.objects.unlink(strokesToJoin[sj-1])
        except:
            pass
    return target[len(target)-1]
'''

def parentMultiple(target, root, fixTransforms=True):
    bpy.context.scene.objects.active = root # last object will be the parent
    bpy.ops.object.select_all(action='DESELECT')
    for i in range(0, len(target)):
        target[i].select = True
    if (fixTransforms==True):
        bpy.ops.object.parent_set(type='OBJECT', xmirror=False, keep_transform=False) 
    else:
        bpy.ops.object.parent_set(type='OBJECT', xmirror=False, keep_transform=True)

def makeParent(target=None, unParent=False, fixTransforms=True):
    if not target:
        target = s()
    if (unParent==True):
        for obj in target:
            if (obj.parent != None):
                bpy.context.scene.objects.active=obj
                if (fixTransforms==True):
                    bpy.ops.object.parent_clear(type='CLEAR_KEEP_TRANSFORM')
                else:
                    bpy.ops.object.parent_clear()
    else:
        # http://blender.stackexchange.com/questions/9200/make-object-a-a-parent-of-object-b-via-python
        for i in range(0, len(target)-1):
            target[i].select=True
        bpy.context.scene.objects.active = target[len(target)-1] # last object will be the parent
        #original_type = bpy.context.area.type
        #print("Current context: " + original_type)
        #bpy.context.area.type = "VIEW_3D"
        #~
        if (fixTransforms==True):
            bpy.ops.object.parent_set(type='OBJECT', xmirror=False, keep_transform=False) 
        else:   
            bpy.ops.object.parent_set(type='OBJECT', xmirror=False, keep_transform=True) 
        #~
        #bpy.context.area.type = original_type 
        #print("Parent is " + target[len(target)-1].name)   

def keyTransform(_obj, _frame):
    #_obj.location = _pos
    #_obj.rotation_quaternion = _rot
    #_obj.scale = _scale
    _obj.keyframe_insert(data_path="location", frame=_frame) 
    _obj.keyframe_insert(data_path="rotation_euler", frame=_frame) 
    _obj.keyframe_insert(data_path="scale", frame=_frame)
    #bpy.context.scene.update()

def keyMatrix(_obj, _frame):
    _obj.keyframe_insert(data_path="matrix_world", frame=_frame) 

def select(target=None):
    if not target:
        target=bpy.context.selected_objects;
    print("selected " + str(target))
    return target

'''
def move(x, y, z, target=None):
    if not target:
        target = select()
    bpy.ops.object.select_all(action='DESELECT')
    for i in range(0, len(target)):
        bpy.data.objects[target[i].name].select = True
        bpy.ops.transform.translate(value=(x, y, z))

def moveTo(x, y, z, target=None):
    if not target:
        target = select()
    bpy.ops.object.select_all(action='DESELECT')
    for i in range(0, len(target)):
        bpy.data.objects[target[i].name].select = True
        bpy.ops.transform.location = str((x, y, z))
'''

'''
def delete(_obj, clearMemory=False):
    bpy.ops.object.mode_set(mode = 'OBJECT')
    #if not target:
        #target = s()
    #for _obj in target:
    if (clearMemory==True):
        mesh = bpy.data.meshes[_obj.name]
        mesh.user_clear()
        bpy.data.meshes.remove(mesh)
    bpy.ops.object.select_all(action='DESELECT')
    bpy.data.objects[_obj.name].select = True
    bpy.ops.object.delete()   
    #print("Deleted " + _obj.name)  
'''

def delete(_obj=None):
    if not _obj:
        _obj = ss()
    #oldMode = bpy.context.mode
    #bpy.ops.object.mode_set(mode='OBJECT')
    bpy.ops.object.select_all(action='DESELECT')
    bpy.data.objects[_obj.name].select = True
    bpy.ops.object.delete()
    gc.collect()
    #bpy.ops.object.mode_set(mode=oldMode)   

def refresh():
    bpy.context.scene.update()

def remap(value, min1, max1, min2, max2):
    range1 = max1 - min1
    range2 = max2 - min2
    valueScaled = float(value - min1) / float(range1)
    return min2 + (valueScaled * range2)
    
def matchName(_name):
    returns = []
    for i in range(0, len(bpy.context.scene.objects)):
        obj = bpy.context.scene.objects[i]
        if re.match(r'^' + str(_name) + '', obj.name): # curve object
            returns.append(obj)
    return returns

def selectName(_name="crv"):
    target = matchName(_name)
    deselect()
    for obj in target:
        obj.select = True

def deleteName(_name="crv"):
    target = matchName(_name)
    for obj in target:
        try:
            delete(obj)
        except:
            print("error deleting " + obj.name)

def roundVal(a, b):
    formatter = "{0:." + str(b) + "f}"
    return formatter.format(a)

def roundValInt(a):
    formatter = "{0:." + str(0) + "f}"
    return int(formatter.format(a))

def frame_to_time(frame_number):
    scene = bpy.context.scene
    fps = scene.render.fps
    fps_base = scene.render.fps_base
    raw_time = (frame_number - 1) / fps
    return round(raw_time, 3)

def bakeFrames():
    start = bpy.context.scene.frame_start
    end = bpy.context.scene.frame_end + 1
    scene = bpy.context.scene
    gp = getActiveGp()
    #layer = gp.layers[0] 
    for layer in gp.layers:   
        for i in range(start, end):
            try:
                layer.frames.new(i)
            except:
                print ("Frame " + str(i) + " already exists.")

def getStartEnd(pad=True):
    start = bpy.context.scene.frame_start
    end = None
    if (pad==True):
        end = bpy.context.scene.frame_end + 1
    else:
        end = bpy.context.scene.frame_end
    return start, end

def setStartEnd(start, end, pad=True):
    if (pad==True):
        end += 1
    bpy.context.scene.frame_start = start
    bpy.context.scene.frame_end = end
    return start, end

def copyFrame(source, dest, limit=None):
    scene = bpy.context.scene
    layer = getActiveLayer()  
    #.
    frameSource = layer.frames[source]
    frameDest = layer.frames[dest]
    if not limit:
        limit = len(frameSource.strokes)
    for j in range(0, limit):
        scene.frame_set(source)
        strokeSource = frameSource.strokes[j]
        scene.frame_set(dest)
        strokeDest = frameDest.strokes.new(strokeSource.color.name)
        # either of ('SCREEN', '3DSPACE', '2DSPACE', '2DIMAGE')
        strokeDest.draw_mode = '3DSPACE'
        strokeDest.points.add(len(strokeSource.points))
        for l in range(0, len(strokeSource.points)):
            strokeDest.points[l].co = strokeSource.points[l].co

def copyFramePoints(source, dest, limit=None, pointsPercentage=1):
    scene = bpy.context.scene
    layer = getActiveLayer()  
    #.
    frameSource = layer.frames[source]
    frameDest = layer.frames[dest]
    if not limit:
        limit = len(frameSource.strokes)
    for j in range(0, limit):
        scene.frame_set(source)
        strokeSource = frameSource.strokes[j]
        scene.frame_set(dest)
        strokeDest = frameDest.strokes.new(strokeSource.color.name)
        # either of ('SCREEN', '3DSPACE', '2DSPACE', '2DIMAGE')
        strokeDest.draw_mode = '3DSPACE'
        if (j>=limit-1):
            newVal = roundValInt(len(strokeSource.points) * pointsPercentage)
            strokeDest.points.add(newVal)
            for l in range(0, newVal):
                strokeDest.points[l].co = strokeSource.points[l].co
        else:
            strokeDest.points.add(len(strokeSource.points))
            for l in range(0, len(strokeSource.points)):
                strokeDest.points[l].co = strokeSource.points[l].co

def createCamera():
    # https://blenderartists.org/forum/showthread.php?312512-how-to-add-an-empty-and-a-camera-using-python-script
   cam = bpy.data.cameras.new("Camera")
   cam_ob = bpy.data.objects.new("Camera", cam)
   bpy.context.scene.objects.link(cam_ob)
   return cam_ob

def getActiveCamera():
    # https://blender.stackexchange.com/questions/8245/find-active-camera-from-python
    cam_ob = bpy.context.scene.camera
    #~
    if cam_ob is None:
        print("no scene camera")
        return None
    elif cam_ob.type == 'CAMERA':
        print("regular scene cam")
        return cam_ob
    else:
        print("%s object as camera" % cam_ob.type)
        ob = bpy.context.object
        if ob is not None and ob.type == 'CAMERA':
            print("Active camera object")
            return ob
        else:
            return None

def createStrokes(strokes, palette=None):
    if (palette == None):
        palette = getActivePalette()
    frame = getActiveFrame()
    if (frame == None):
        frame = getActiveLayer().frames.new(bpy.context.scene.frame_current)
    #~
    for strokeSource in strokes:
        strokeColor = (0,0,0)
        try:
            strokeColor = createColor(strokeSource.color.color)
        except:
            pass
        strokeDest = frame.strokes.new(getActiveColor().name)        
        strokeDest.draw_mode = '3DSPACE'
        strokeDest.points.add(len(strokeSource.points))
        for l in range(0, len(strokeSource.points)):
            strokeDest.points[l].co = strokeSource.points[l].co 
            strokeDest.points[l].pressure = 1
            strokeDest.points[l].strength = 1

def createStroke(points, color=(0,0,0), frame=None, palette=None):
    if (palette == None):
        palette = getActivePalette()
    if (frame == None):
        #frame = getActiveLayer().frames.new(bpy.context.scene.frame_current)
        frame = getActiveFrame()
    #~
    strokeColor = createColor(color)
    stroke = frame.strokes.new(getActiveColor().name)        
    stroke.draw_mode = '3DSPACE'
    stroke.points.add(len(points))
    for l in range(0, len(points)):
        stroke.points[l].co = points[l].co 
        stroke.points[l].pressure = 1
        stroke.points[l].strength = 1

def goToFrame(_index):
    origFrame = bpy.context.scene.frame_current
    bpy.context.scene.frame_current = _index
    bpy.context.scene.frame_set(_index)
    refresh()
    print("Moved from timeline frame " + str(origFrame) + " to " + str(_index))
    return bpy.context.scene.frame_current

def hideFrame(_obj, _frame, _hide):
    _obj.hide = _hide
    _obj.hide_render = _hide
    _obj.keyframe_insert(data_path="hide", frame=_frame) 
    _obj.keyframe_insert(data_path="hide_render", frame=_frame) 

'''
def chooseShot(shot):
    start = 0
    end = 0
    if shot == 1:
        start = 1
        end = 44
    elif shot == 2:
        start = 45
        end = 63
    return [start, end]
'''

def showHide(obj, hide, keyframe=False, frame=None):
    obj.hide = hide
    obj.hide_render = hide
    #_obj.keyframe_insert(data_path="hide", frame=_frame) 
    #_obj.keyframe_insert(data_path="hide_render", frame=_frame) 

def showHideChildren(hide):
    target = getChildren()
    for obj in target:
        showHide(obj, hide)

def rgbToHex(color, normalized=False):
    if (normalized==True):
        return "#%02x%02x%02x" % (int(color[0] * 255.0), int(color[1] * 255.0), int(color[2] * 255.0))
    else:
        return "#%02x%02x%02x" % (int(color[0]), int(color[1]), int(color[2]))

def normRgbToHex(color):
    return rgbToHex(color, normalized=True)

def moveShot(start, end, x, y, z):
    gp = bpy.context.scene.grease_pencil
    target = (start, end)
    for g in range(target[0], target[1]+1):
        for f in range(0, len(gp.layers)):
            layer = gp.layers[f]
            currentFrame = g
            for i in range(0, len(layer.frames[currentFrame].strokes)):
                for j in range(0, len(layer.frames[currentFrame].strokes[i].points)):
                    layer.frames[currentFrame].strokes[i].points[j].co.x += x
                    layer.frames[currentFrame].strokes[i].points[j].co.y += y
                    layer.frames[currentFrame].strokes[i].points[j].co.z += z

def fixContext(ctx="VIEW_3D"):
    original_type = bpy.context.area.type
    bpy.context.area.type = ctx
    return original_type

def returnContext(original_type):
    bpy.context.area.type = original_type

def alignCamera():
    original_type = bpy.context.area.type
    print("Current context: " + original_type)
    bpy.context.area.type = "VIEW_3D"
    #~
    # strokes, points, frame
    bpy.ops.view3d.camera_to_view()
    #~
    #bpy.context.area.type = "CONSOLE"
    bpy.context.area.type = original_type

# ~ ~ ~ ~ ~ ~ grease pencil ~ ~ ~ ~ ~ ~
def getActiveGp(_name="GPencil"):
    try:
        pencil = bpy.context.scene.grease_pencil
    except:
        pencil = None
    try:
        gp = bpy.data.grease_pencil[pencil.name]
    except:
        gp = bpy.data.grease_pencil.new(_name)
        bpy.context.scene.grease_pencil = gp
    print("Active GP block is: " + gp.name)
    return gp

def forceDrawMode():
    #https://blenderartists.org/forum/showthread.php?255425-How-to-use-quot-bpy-ops-gpencil-draw()-quot
    ctx = fixContext()
    #bpy.ops.gpencil.draw('INVOKE_REGION_WIN', mode='DRAW_POLY', stroke=[{"name":"", "pen_flip":False, "is_start":True, "location":(0, 0, 0),"mouse":(0,0), "pressure":1, "time":0}, {"name":"", "pen_flip":False, "is_start":True, "location":(0, 0, 0), "mouse":(0,0), "pressure":1, "time":0}])
    returns = bpy.ops.gpencil.draw(mode="DRAW")
    returnContext(ctx)
    return returns

def initGp():
    # https://blender.stackexchange.com/questions/48992/how-to-add-points-to-a-grease-pencil-stroke-or-make-new-one-with-python-script
    scene = bpy.context.scene
    if not scene.grease_pencil:
        a = [ a for a in bpy.context.screen.areas if a.type == 'VIEW_3D' ][0]
        override = {
            'scene'         : scene,
            'screen'        : bpy.context.screen,
            'object'        : bpy.context.object,
            'area'          : a,
            'region'        : a.regions[0],
            'window'        : bpy.context.window,
            'active_object' : bpy.context.object
        }
        bpy.ops.gpencil.data_add(override)
    return scene.grease_pencil

def getActivePalette():
    gp = getActiveGp()
    palette = gp.palettes.active
    if (palette == None):
        palette = gp.palettes.new(gp.name + "_Palette", set_active = True)
    if (len(palette.colors) < 1):
        color = palette.colors.new()
        color.color = (0,0,0)
    print("Active palette is: " + gp.palettes.active.name)
    return palette

def getActiveColor():
    palette = getActivePalette()
    print("Active color is: " + "\"" + palette.colors.active.name + "\" " + str(palette.colors.active.color))
    return palette.colors.active

def getActiveLayer():
    gp = getActiveGp()
    layer = gp.layers.active
    return layer

def setActiveLayer(name="Layer"):
    gp = getActiveGp()
    gp.layers.active = gp.layers[name]
    return gp.layers.active

def deleteLayer(name=None):
    gp = getActiveGp()
    if not name:
        name = gp.layers.active.info
    gp.layers.remove(gp.layers[name])

def duplicateLayer():
    ctx = fixContext()
    bpy.ops.gpencil.layer_duplicate()
    returnContext(ctx)
    return getActiveLayer()

def splitLayer(splitNum=None):
    if not splitNum:
        splitNum = getActiveFrameTimelineNum()
    layer1 = getActiveLayer()
    layer2 = duplicateLayer()
    #~
    for frame in layer1.frames:
        if (frame.frame_number>=splitNum):
            layer1.frames.remove(frame)
    for frame in layer2.frames:
        if (frame.frame_number<splitNum):
            layer2.frames.remove(frame)
    #~
    if (len(layer2.frames) > 0):
        lastNum = layer2.frames[0].frame_number
        # cap the new layers with blank frames
        #blankFrame(layer1, bpy.context.scene.frame_current)
        #blankFrame(layer2, bpy.context.scene.frame_current-1)
        blankFrame(layer1, lastNum)
        blankFrame(layer2, lastNum-1)
        return layer2
    else:
        cleanEmptyLayers()
        return None

def blankFrame(layer=None, frame=None):
    if not layer:
        layer = getActiveLayer()
    if not frame:
        frame = bpy.context.scene.frame_current
    try:
        layer.frames.new(frame)
    except:
        pass

def getActiveFrameNum():
    returns = -1
    layer = getActiveLayer()
    for i, frame in enumerate(layer.frames):
        if (frame == layer.active_frame):
            returns = i
    return returns
    #return getActiveFrame().frame_number

def getActiveFrameTimelineNum():
    return getActiveLayer().frames[getActiveFrameNum()].frame_number

def checkLayersAboveFrameLimit(limit=20):
    gp = getActiveGp()
    returns = []
    print("~ ~ ~ ~")
    for layer in gp.layers:
        if (len(layer.frames) > limit + 1): # accounting for extra end cap frame
            returns.append(layer)
            print("layer " + layer.info + " is over limit " + str(limit) + " with " + str(len(layer.frames)) + " frames.")
    print(" - - - " + str(len(returns)) + " total layers over limit.")
    print("~ ~ ~ ~")
    return returns

def splitLayersAboveFrameLimit(limit=20):
    layers = checkLayersAboveFrameLimit(limit)
    #~
    if (len(layers) <= 0):
        return
    for layer in layers:
        setActiveLayer(layer.info)
        for i in range(0, int(getLayerLength()/limit)):
            currentLayer = getActiveLayer()
            print("* " + currentLayer.info + ": pass " + str(i))
            if (getLayerLength() < limit or currentLayer.lock==True):
                break
            goToFrame(currentLayer.frames[limit].frame_number)
            setActiveFrame(currentLayer.frames[limit].frame_number)
            #print("We are at layer " + currentLayer.info + " and frame " + str(getActiveFrameNum()) + " and timeline " + str(getActiveFrameTimelineNum()))
            #currentLayer = splitLayer(currentLayer.frames[limit].frame_number)
            splitLayer(currentLayer.frames[limit].frame_number)
            #setActiveLayer(currentLayer.info)
            print("Split layer " + currentLayer.info + " with " + str(len(currentLayer.frames)) + " frames.")
    #else:
        #print("No layers are above frame limit " + str(limit) + ".")

def getLayerLength(name=None):
    layer = None
    if not name:
        layer = getActiveLayer()
    else:
        layer = getActiveGp().layers[name]
    return len(layer.frames)

def cleanEmptyLayers():
    gp = getActiveGp()
    for layer in gp.layers:
        if (len(layer.frames) == 0):
            gp.layers.remove(layer)

def clearPalette():
    palette = getActivePalette()
    for color in palette.colors:
        palette.colors.remove(color)

def createPoint(_stroke, _index, _point, pressure=1, strength=1):
    _stroke.points[_index].co = _point
    _stroke.points[_index].select = True
    _stroke.points[_index].pressure = pressure
    _stroke.points[_index].strength = strength

def addPoint(_stroke, _point, pressure=1, strength=1):
    _stroke.points.add(1)
    createPoint(_stroke, len(_stroke.points)-1, _point, pressure, strength)

def closeStroke(_stroke):
    addPoint(_stroke, _stroke.points[0].co)

def createColor(_color):
    frame = getActiveFrame()
    palette = getActivePalette()
    matchingColorIndex = -1
    places = 7
    for i in range(0, len(palette.colors)):
        if (roundVal(_color[0], places) == roundVal(palette.colors[i].color.r, places) and roundVal(_color[1], places) == roundVal(palette.colors[i].color.g, places) and roundVal(_color[2], places) == roundVal(palette.colors[i].color.b, places)):
            matchingColorIndex = i
    #~
    if (matchingColorIndex == -1):
        color = palette.colors.new()
        color.color = _color
    else:
        palette.colors.active = palette.colors[matchingColorIndex]
        color = palette.colors[matchingColorIndex]
    #~        
    print("Active color is: " + "\"" + palette.colors.active.name + "\" " + str(palette.colors.active.color))
    return color

# ~ ~ ~ 
def createColorWithPalette(_color, numPlaces=7, maxColors=0):
    #frame = getActiveFrame()
    palette = getActivePalette()
    matchingColorIndex = -1
    places = numPlaces
    for i in range(0, len(palette.colors)):
        if (roundVal(_color[0], places) == roundVal(palette.colors[i].color.r, places) and roundVal(_color[1], places) == roundVal(palette.colors[i].color.g, places) and roundVal(_color[2], places) == roundVal(palette.colors[i].color.b, places)):
            matchingColorIndex = i
    #~
    if (matchingColorIndex == -1):
        if (maxColors<1 or len(palette.colors)<maxColors):
            color = palette.colors.new()
            color.color = _color
        else:
            distances = []
            sortedColors = []
            for color in palette.colors:
                sortedColors.append(color)
            for color in sortedColors:
                distances.append(getDistance(_color, color.color))
            sortedColors.sort(key=dict(zip(sortedColors, distances)).get)
            palette.colors.active = palette.colors[sortedColors[0].name]
    else:
        palette.colors.active = palette.colors[matchingColorIndex]
        color = palette.colors[matchingColorIndex]
    #~        
    print("Active color is: " + "\"" + palette.colors.active.name + "\" " + str(palette.colors.active.color))
    return color
# ~ ~ ~

def changeColor():
    frame = getActiveFrame()
    palette = getActivePalette()
    strokes = getSelectedStrokes()
    #~
    lineWidthBackup = []
    pointsBackup = []
    for stroke in strokes:
        lineWidthBackup.append(stroke.line_width)
        pointsBackup.append(stroke.points)
    #~
    deleteSelected()
    #~
    for i, points in enumerate(pointsBackup):
        newStroke = frame.strokes.new(getActiveColor().name)
        newStroke.draw_mode = "3DSPACE" # either of ("SCREEN", "3DSPACE", "2DSPACE", "2DIMAGE")
        newStroke.line_width = lineWidthBackup[i]
        newStroke.points.add(len(points))
        for j in range(0, len(points)):
            createPoint(newStroke, j, points[j].co)
    print(str(len(strokes)) + " changed to " + palette.colors.active.name)

'''
def pasteToNewLayer():
    frame = getActiveFrame()
    oldStrokes = getSelectedStrokes()
    #~
    for oldStroke in oldStrokes:
        newStroke = frame.strokes.new(oldStroke.color_name)
        newStroke.draw_mode = "3DSPACE" # either of ("SCREEN", "3DSPACE", "2DSPACE", "2DIMAGE")
        newStroke.line_width = oldStroke.line_width
        newStroke.points = oldStroke.points
        #newStroke.points.add(len(oldStroke.points))
        #for j in range(0, len(oldStroke.points)):
            #createPoint(newStroke, j, points[j].co)
'''

def newLayer(name="NewLayer", setActive=True):
    gp = getActiveGp()
    gp.layers.new(name)
    if (setActive==True):
        gp.layers.active = gp.layers[len(gp.layers)-1]
    return gp.layers[len(gp.layers)-1]

def getStrokePoints(target=None):
    returns = []
    if not target:
        target = getSelectedStroke()
    for point in target.points:
        returns.append(point.co)
    return returns

def reprojectAllStrokes():
    strokes = getAllStrokes()
    newLayer()
    for stroke in strokes:
        points = getStrokePoints(stroke)
        try:
        	drawPoints(points)
        except:
        	pass

def compareTuple(t1, t2, numPlaces=5):
    if (roundVal(t1[0], numPlaces) == roundVal(t2[0], numPlaces) and roundVal(t1[1], numPlaces) == roundVal(t2[1], numPlaces) and roundVal(t1[2], numPlaces) == roundVal(t2[2], numPlaces)):
        return True
    else:
        return False

def deleteFromAllFrames():
    origStrokes = []
    frame = getActiveFrame()
    for stroke in frame.strokes:
        addToOrig = False
        for point in stroke.points:
            if (point.select):
               addToOrig = True
               break
        if (addToOrig == True):
           origStrokes.append(stroke) 
    print("Checking for " + str(len(origStrokes)) + " selected strokes.")
    #~    
    allStrokes = getAllStrokes()
    deleteList = []
    numPlaces = 5
    for allStroke in allStrokes:
        doDelete = False
        for origStroke in origStrokes:
            if (len(allStroke.points) == len(origStroke.points)):
                for i in range(0, len(allStroke.points)):
                    if (roundVal(allStroke.points[i].co.x, numPlaces) == roundVal(origStroke.points[i].co.x, numPlaces) and roundVal(allStroke.points[i].co.y, numPlaces) == roundVal(origStroke.points[i].co.y, numPlaces) and roundVal(allStroke.points[i].co.z, numPlaces) == roundVal(origStroke.points[i].co.z, numPlaces)):
                        doDelete = True
                    else:
                        doDelete = False
                        break
        if (doDelete):
            deleteList.append(allStroke)
    #~
    print(str(len(deleteList)) + " strokes listed for deletion.")
    for stroke in deleteList:
        stroke.select = True
    layer = getActiveLayer()
    start, end = getStartEnd()
    for i in range(start, end):
        goToFrame(i)    
        for j in range(0, len(layer.frames)):
            setActiveFrame(j)
            deleteSelected()

def getAllLayers():
    gp = getActiveGp()
    print("Got " + str(len(gp.layers)) + " layers.")
    return gp.layers

def getAllFrames(active=False):
    returns = []
    layers = getAllLayers()
    for layer in layers:
        if (active==False):
            for frame in layer.frames:
                returns.append(frame)
        else:
            returns.append(layer.active_frame)
    print("Got " + str(len(returns)) + " frames.")
    return returns

def getActiveFrame():
    gp = getActiveGp()
    layer = gp.layers.active
    frame = layer.active_frame
    return frame

# gp not timeline
def setActiveFrame(index):
    layer = getActiveLayer()
    if index < len(layer.frames):
        layer.active_frame = layer.frames[index]
        refresh()
        print("Moved to layer frame " + str(index))
    else:
        print("Outside of layer range")
    return layer.active_frame

def getAllStrokes(active=False):
    returns = []
    frames = getAllFrames(active)
    for frame in frames:
        for stroke in frame.strokes:
            returns.append(stroke)
    print("Got " + str(len(returns)) + " strokes.")
    return returns

def getLayerStrokes(name=None):
    gp = getActiveGp()
    if not name:
        name = gp.layers.active.info
    layer = gp.layers[name]
    strokes = []
    for frame in layer.frames:
        for stroke in frame.strokes:
            strokes.append(stroke)
    return strokes

def getFrameStrokes(num=None, name=None):
    gp = getActiveGp()
    if not name:
        name = gp.layers.active.info
    layer = gp.layers[name]
    if not num:
        num = layer.active_frame.frame_number
    strokes = []
    for frame in layer.frames:
        if (frame.frame_number == num):
            for stroke in frame.strokes:
                strokes.append(stroke)
    return strokes

def getLayerStrokesAvg(name=None):
    gp = getActiveGp()
    if not name:
        name = gp.layers.active.info
    layer = gp.layers[name]
    return float(roundVal(len(getLayerStrokes(name)) / len(layer.frames), 2))

def getAllStrokesAvg(locked=True):
    gp = getActiveGp()
    avg = 0
    for layer in gp.layers:
        if (layer.lock == False or locked == True):
            avg += getLayerStrokesAvg(layer.info)
    return float(roundVal(avg / len(gp.layers), 2))

def getSelectedStrokes(active=True):
    returns = []
    strokes = getAllStrokes(active)
    for stroke in strokes:
        if (stroke.select):
            returns.append(stroke)
        else:
            for point in stroke.points:
                if (point.select):
                    returns.append(stroke)
                    break
    if (len(returns) > 0):
        print(str(len(returns)) + " selected strokes.")
    else:
        print("No selected strokes.")
    return returns

def getSelectedStroke():
    strokes = getSelectedStrokes()
    if (len(strokes) > 0):
        print("Only returning first selected stroke.")
        return strokes[0]
    else:
        print("No selected strokes.")

def deleteSelected(target="strokes"):
    original_type = bpy.context.area.type
    print("Current context: " + original_type)
    bpy.context.area.type = "VIEW_3D"
    #~
    # strokes, points, frame
    bpy.ops.gpencil.delete(type=target.upper())
    #~
    #bpy.context.area.type = "CONSOLE"
    bpy.context.area.type = original_type

# https://www.blender.org/forum/viewtopic.php?t=27834
def AssembleOverrideContextForView3dOps():
    #=== Iterates through the blender GUI's windows, screens, areas, regions to find the View3D space and its associated window.  Populate an 'oContextOverride context' that can be used with bpy.ops that require to be used from within a View3D (like most addon code that runs of View3D panels)
    # Tip: If your operator fails the log will show an "PyContext: 'xyz' not found".  To fix stuff 'xyz' into the override context and try again!
    for oWindow in bpy.context.window_manager.windows:          ###IMPROVE: Find way to avoid doing four levels of traversals at every request!!
        oScreen = oWindow.screen
        for oArea in oScreen.areas:
            if oArea.type == 'VIEW_3D':                         ###LEARN: Frequently, bpy.ops operators are called from View3d's toolbox or property panel.  By finding that window/screen/area we can fool operators in thinking they were called from the View3D!
                for oRegion in oArea.regions:
                    if oRegion.type == 'WINDOW':                ###LEARN: View3D has several 'windows' like 'HEADER' and 'WINDOW'.  Most bpy.ops require 'WINDOW'
                        #=== Now that we've (finally!) found the damn View3D stuff all that into a dictionary bpy.ops operators can accept to specify their context.  I stuffed extra info in there like selected objects, active objects, etc as most operators require them.  (If anything is missing operator will fail and log a 'PyContext: error on the log with what is missing in context override) ===
                        oContextOverride = {'window': oWindow, 'screen': oScreen, 'area': oArea, 'region': oRegion, 'scene': bpy.context.scene, 'edit_object': bpy.context.edit_object, 'active_object': bpy.context.active_object, 'selected_objects': bpy.context.selected_objects}   # Stuff the override context with very common requests by operators.  MORE COULD BE NEEDED!
                        print("-AssembleOverrideContextForView3dOps() created override context: ", oContextOverride)
                        return oContextOverride
    raise Exception("ERROR: AssembleOverrideContextForView3dOps() could not find a VIEW_3D with WINDOW region to create override context to enable View3D operators.  Operator cannot function.")

def TestView3dOperatorFromPythonScript():       # Run this from a python script and operators that would normally fail because they were not called from a View3D context will work!
    oContextOverride = AssembleOverrideContextForView3dOps()    # Get an override context suitable for bpy.ops operators that require View3D
    bpy.ops.mesh.knife_project(oContextOverride)                # An operator like this normally requires to run off the View3D context.  By overriding it with what it needs it will run from any context (like Python script, Python shell, etc)
    #bpy.ops.screen.screen_full_area(oContextOverride)
    print("TestView3dOperatorFromPythonScript() completed succesfully.")

def addVec3(p1, p2):
    return(p1[0]+p2[0], p1[1]+p2[1], p1[2]+p2[2])

def multVec3(p1, p2):
    return(p1[0]*p2[0], p1[1]*p2[1], p1[2]*p2[2])

# * * * * * * * * * * * * * * * * * * * * * * * * * *
# * * * * * * * * * * * * * * * * * * * * * * * * * *
# * * * * * * * * * * * * * * * * * * * * * * * * * *

