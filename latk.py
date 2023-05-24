'''
The Lightning Artist Toolkit was developed with support from:
   Canada Council on the Arts
   Eyebeam Art + Technology Center
   Ontario Arts Council
   Toronto Arts Council
   
Copyright (c) 2020 Nick Fox-Gieg
http://fox-gieg.com

~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
# 
#     http://www.apache.org/licenses/LICENSE-2.0
# 
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
'''

import json
from math import sqrt
from numpy import float32
from numpy import isnan

class Latk(object):     
    def __init__(self, filepath=None, layers=None, init=False, coords=None, color=None, frame_rate=12): # args string, Latk array, float tuple array, float tuple           
        if not layers:
        	self.layers = [] # LatkLayer
        else:
        	self.layers = layers
        self.frame_rate = frame_rate

        if (filepath != None):
            self.read(filepath, True)
        elif (init == True):
            self.layers.append(LatkLayer())
            self.layers[0].frames.append(LatkFrame())
            if (coords != None): # 
                stroke = LatkStroke()
                stroke.setCoords(coords)
                if (color != None):
                    stroke.color = color
                self.layers[0].frames[0].strokes.append(stroke)            

    def getFileNameNoExt(self, s): # args string, return string
        returns = ""
        temp = s.split(".")
        if (len(temp) > 1): 
            for i in range(0, len(temp)-1):
                if (i > 0):
                    returns += "."
                returns += temp[i]
        else:
            return s
        return returns
        
    def getExtFromFileName(self, s): # args string, returns string 
        returns = ""
        temp = s.split(".")
        returns = temp[len(temp)-1]
        return returns

    def read(self, filepath, clearExisting=True, yUp=False, useScaleAndOffset=False, globalScale=(1.0, 1.0, 1.0), globalOffset=(0.0, 0.0, 0.0)): # defaults to Blender Z up
        data = None

        if (clearExisting == True):
            self.layers = []
        
        fileType = self.getExtFromFileName(filepath)
        if (fileType == "latk" or fileType == "zip"):
            imz = InMemoryZip()
            imz.readFromDisk(filepath)
            data = json.loads(imz.files[0].decode("utf-8"))        
        else:
            with open(filepath) as data_file:    
                data = json.load(data_file)
        
        if ("version" not in data): # latk format v2.7 or older
            if ("grease_pencil" not in data): # latk format v2.0 or older
                layer = LatkLayer()
                if ("x" in data["brushstrokes"][0][0]): # latk format v1.0, single frame 
                    frame = LatkFrame()
                    for jsonStroke in data["brushstrokes"]:                       
                        color = (1,1,1)                 
                        points = []
                        for jsonPoint in jsonStroke:
                            x = float(jsonPoint["x"])
                            y = None
                            z = None
                            if (yUp == False):
                                y = float(jsonPoint["z"])
                                z = float(jsonPoint["y"])  
                            else:
                                y = float(jsonPoint["y"])
                                z = float(jsonPoint["z"]) 
                            #~
                            if (useScaleAndOffset == True):
                                x = (x * globalScale[0]) + globalOffset[0]
                                y = (y * globalScale[1]) + globalOffset[1]
                                z = (z * globalScale[2]) + globalOffset[2]
                            #~                                                           
                            pressure = 1.0
                            strength = 1.0
                            points.append(LatkPoint((x,y,z), pressure, strength))                                         
                        stroke = LatkStroke(points, color)
                        frame.strokes.append(stroke)
                        layer.frames.append(frame)
                    self.layers.append(layer)
                else: # latk format v2.0, animation
                    for jsonFrame in data["brushstrokes"]:                          
                        frame = LatkFrame()
                        for jsonStroke in jsonFrame:                       
                            color = (1,1,1)
                            
                            points = []
                            for jsonPoint in jsonStroke:
                                x = float(jsonPoint["x"])
                                y = None
                                z = None
                                if (yUp == False):
                                    y = float(jsonPoint["z"])
                                    z = float(jsonPoint["y"])  
                                else:
                                    y = float(jsonPoint["y"])
                                    z = float(jsonPoint["z"]) 
                                #~
                                if (useScaleAndOffset == True):
                                    x = (x * globalScale[0]) + globalOffset[0]
                                    y = (y * globalScale[1]) + globalOffset[1]
                                    z = (z * globalScale[2]) + globalOffset[2]
                                #~                                                           
                                pressure = 1.0
                                strength = 1.0
                                points.append(LatkPoint((x,y,z), pressure, strength))
                                                    
                            stroke = LatkStroke(points, color)
                            frame.strokes.append(stroke)
                        layer.frames.append(frame)
                    self.layers.append(layer)
            else: # latk format v2.7, Blender 2.7 Grease Pencil
                for jsonGp in data["grease_pencil"]:          
                    for jsonLayer in jsonGp["layers"]:
                        layer = LatkLayer(name=jsonLayer["name"])
                        
                        for jsonFrame in jsonLayer["frames"]:
                            frame = LatkFrame()
                            for jsonStroke in jsonFrame["strokes"]:                       
                                color = (1,1,1)
                                try:
                                    r = jsonStroke["color"][0]
                                    g = jsonStroke["color"][1]
                                    b = jsonStroke["color"][2]
                                    color = (r,g,b)
                                except:
                                    pass
                                
                                points = []
                                for jsonPoint in jsonStroke["points"]:
                                    x = float(jsonPoint["co"][0])
                                    y = None
                                    z = None
                                    if (yUp == False):
                                        y = float(jsonPoint["co"][2])
                                        z = float(jsonPoint["co"][1])  
                                    else:
                                        y = float(jsonPoint["co"][1])
                                        z = float(jsonPoint["co"][2]) 
                                    #~
                                    if (useScaleAndOffset == True):
                                        x = (x * globalScale[0]) + globalOffset[0]
                                        y = (y * globalScale[1]) + globalOffset[1]
                                        z = (z * globalScale[2]) + globalOffset[2]
                                    #~                                                           
                                    pressure = 1.0
                                    strength = 1.0
                                    try:
                                        pressure = jsonPoint["pressure"]
                                        if (isnan(pressure) == True):
                                            pressure = 1.0
                                    except:
                                        pass
                                    try:
                                        strength = jsonPoint["strength"]
                                        if (isnan(strength) == True):
                                            strength = 1.0
                                    except:
                                        pass
                                    points.append(LatkPoint((x,y,z), pressure, strength))
                                                        
                                stroke = LatkStroke(points, color)
                                frame.strokes.append(stroke)
                            layer.frames.append(frame)
                        self.layers.append(layer)
        else: # v2.8 and newer use version keys
            if (float(data["version"]) >= 2.8): # latk format v2.8, Blender 2.8 Grease Pencil
                for jsonGp in data["grease_pencil"]:          
                    for jsonLayer in jsonGp["layers"]:
                        layer = LatkLayer(name=jsonLayer["name"])
                        
                        for jsonFrame in jsonLayer["frames"]:
                            frame = LatkFrame()
                            for jsonStroke in jsonFrame["strokes"]: 
                                color = (0.0,0.0,0.0,1.0)
                                try:
                                    r = jsonStroke["color"][0]
                                    g = jsonStroke["color"][1]
                                    b = jsonStroke["color"][2]
                                    a = 1.0
                                    try:
                                        a = jsonStroke["color"][3]
                                    except:
                                        pass
                                    color = (r,g,b,a)
                                except:
                                    pass

                                fill_color = (0.0,0.0,0.0,0.0)
                                try:
                                    r = jsonStroke["fill_color"][0]
                                    g = jsonStroke["fill_color"][1]
                                    b = jsonStroke["fill_color"][2]
                                    a = 0.0
                                    try:
                                        a = jsonStroke["fill_color"][3]
                                    except:
                                        pass
                                    fill_color = (r,g,b,a)
                                except:
                                    pass

                                points = []
                                for jsonPoint in jsonStroke["points"]:
                                    x = float(jsonPoint["co"][0])
                                    y = None
                                    z = None
                                    if (yUp == False):
                                        y = float(jsonPoint["co"][2])
                                        z = float(jsonPoint["co"][1])  
                                    else:
                                        y = float(jsonPoint["co"][1])
                                        z = float(jsonPoint["co"][2]) 
                                    #~
                                    if (useScaleAndOffset == True):
                                        x = (x * globalScale[0]) + globalOffset[0]
                                        y = (y * globalScale[1]) + globalOffset[1]
                                        z = (z * globalScale[2]) + globalOffset[2]
                                    #~                                                                                             
                                    pressure = 1.0
                                    strength = 1.0
                                    vertex_color = (0.0,0.0,0.0,0.0)

                                    try:
                                        pressure = jsonPoint["pressure"]
                                        if (isnan(pressure) == True):
                                            pressure = 1.0
                                    except:
                                        pass
                                    try:
                                        strength = jsonPoint["strength"]
                                        if (isnan(strength) == True):
                                            strength = 1.0
                                    except:
                                        pass
                                    try:
                                        vertex_color = jsonPoint["vertex_color"]
                                        if (isnan(vertex_color) == True):
                                            vertex_color = (0.0,0.0,0.0,1.0)
                                    except:
                                        pass  

                                    points.append(LatkPoint((x,y,z), pressure, strength, vertex_color))
                                                        
                                stroke = LatkStroke(points, color, fill_color)
                                frame.strokes.append(stroke)
                            layer.frames.append(frame)
                        self.layers.append(layer)

    def write(self, filepath, yUp=True, useScaleAndOffset=False, zipped=True, globalScale=(1.0, 1.0, 1.0), globalOffset=(0.0, 0.0, 0.0)): # defaults to Unity, Maya Y up
        FINAL_LAYER_LIST = [] # string array

        for layer in self.layers:
            sb = [] # string array
            sbHeader = [] # string array
            sbHeader.append("\t\t\t\t\t\"frames\": [")
            sb.append("\n".join(sbHeader))

            for h, frame in enumerate(layer.frames):
                sbbHeader = [] # string array
                sbbHeader.append("\t\t\t\t\t\t{")
                sbbHeader.append("\t\t\t\t\t\t\t\"strokes\": [")
                sb.append("\n".join(sbbHeader))
                
                for i, stroke in enumerate(frame.strokes):
                    sbb = [] # string array
                    sbb.append("\t\t\t\t\t\t\t\t{")
                    color = (0.0, 0.0, 0.0, 1.0)
                    fill_color = (0.0, 0.0, 0.0, 0.0)
                    
                    try:
                        color = stroke.color
                        if (len(color) < 4):
                            color = (color[0], color[1], color[2], 1.0)
                    except:
                        pass
                    try:
                        fill_color = stroke.fill_color
                        if (len(fill_color) < 4):
                            fill_color = (fill_color[0], fill_color[1], fill_color[2], 0.0)
                    except:
                        pass
                    sbb.append("\t\t\t\t\t\t\t\t\t\"color\": [" + str(float32(color[0])) + ", " + str(float32(color[1])) + ", " + str(float32(color[2])) + ", " + str(float32(color[3])) + "],")
                    sbb.append("\t\t\t\t\t\t\t\t\t\"fill_color\": [" + str(float32(fill_color[0])) + ", " + str(float32(fill_color[1])) + ", " + str(float32(fill_color[2])) + ", " + str(float32(fill_color[3])) + "],")

                    if (len(stroke.points) > 0): 
                        sbb.append("\t\t\t\t\t\t\t\t\t\"points\": [")
                        for j, point in enumerate(stroke.points):
                            x = point.co[0]
                            y = None
                            z = None
                            r = point.vertex_color[0]
                            g = point.vertex_color[1]
                            b = point.vertex_color[2]
                            a = point.vertex_color[3]
                            if (yUp == True):
                                y = point.co[2]
                                z = point.co[1]
                            else:
                                y = point.co[1]
                                z = point.co[2]  
                            #~
                            if (useScaleAndOffset == True):
                                x = (x * globalScale[0]) + globalOffset[0]
                                y = (y * globalScale[1]) + globalOffset[1]
                                z = (z * globalScale[2]) + globalOffset[2]
                            #~ 
                            pointStr = "\t\t\t\t\t\t\t\t\t\t{\"co\": [" + str(float32(x)) + ", " + str(float32(y)) + ", " + str(float32(z)) + "], \"pressure\": " + str(float32(point.pressure)) + ", \"strength\": " + str(float32(point.strength)) + ", \"vertex_color\": [" + str(float32(r)) + ", " + str(float32(g)) + ", " + str(float32(b)) + ", " + str(float32(a)) + "]}"
                                          
                            if (j == len(stroke.points) - 1):
                                sbb.append(pointStr)
                                sbb.append("\t\t\t\t\t\t\t\t\t]")
                            else:
                                pointStr += ","
                                sbb.append(pointStr)
                    else:
                        sbb.append("\t\t\t\t\t\t\t\t\t\"points\": []")
                    
                    if (i == len(frame.strokes) - 1):
                        sbb.append("\t\t\t\t\t\t\t\t}")
                    else:
                        sbb.append("\t\t\t\t\t\t\t\t},")
                    
                    sb.append("\n".join(sbb))
                
                sbFooter = []
                if (h == len(layer.frames) - 1): 
                    sbFooter.append("\t\t\t\t\t\t\t]")
                    sbFooter.append("\t\t\t\t\t\t}")
                else:
                    sbFooter.append("\t\t\t\t\t\t\t]")
                    sbFooter.append("\t\t\t\t\t\t},")
                sb.append("\n".join(sbFooter))
            
            FINAL_LAYER_LIST.append("\n".join(sb))
        
        s = [] # string
        s.append("{")
        s.append("\t\"creator\": \"latk.py\",")
        s.append("\t\"version\": 2.8,")
        s.append("\t\"grease_pencil\": [")
        s.append("\t\t{")
        s.append("\t\t\t\"layers\": [")

        for i, layer in enumerate(self.layers):
            s.append("\t\t\t\t{")
            if (layer.name != None and layer.name != ""): 
                s.append("\t\t\t\t\t\"name\": \"" + layer.name + "\",")
            else:
                s.append("\t\t\t\t\t\"name\": \"layer" + str(i + 1) + "\",")
                
            s.append(FINAL_LAYER_LIST[i])

            s.append("\t\t\t\t\t]")
            if (i < len(self.layers) - 1): 
                s.append("\t\t\t\t},")
            else:
                s.append("\t\t\t\t}")
                s.append("\t\t\t]") # end layers
        s.append("\t\t}")
        s.append("\t]")
        s.append("}")
        
        fileType = self.getExtFromFileName(filepath)
        if (zipped == True or fileType == "latk" or fileType == "zip"):
            filepathNoExt = self.getFileNameNoExt(filepath)
            imz = InMemoryZip()
            imz.append(filepathNoExt + ".json", "\n".join(s))
            imz.writetofile(filepath)            
        else:
            with open(filepath, "w") as f:
                f.write("\n".join(s))
                f.closed
                
    def clean(self, epsilon=0.01):
        for layer in self.layers:
            for frame in layer.frames:
                for stroke in frame.strokes:
                    coords = []
                    pressures = []
                    strengths = []
                    for point in stroke.points:
                        coords.append(point.co)
                        pressures.append(point.pressure)
                        strengths.append(point.strength)
                    stroke.setCoords(rdp(coords, epsilon=epsilon))
                    for i in range(0, len(stroke.points)):
                        index = self.remapInt(i, 0, len(stroke.points), 0, len(pressures))
                        stroke.points[i].pressure = pressures[index]
                        stroke.points[i].strength = strengths[index]

    def filter(self, cleanMinPoints = 2, cleanMinLength = 0.1):
        if (cleanMinPoints < 2):
            cleanMinPoints = 2 
        for layer in self.layers:
            for frame in layer.frames: 
                for stroke in frame.strokes:
                    # 1. Remove the stroke if it has too few points.
                    if (len(stroke.points) < cleanMinPoints): 
                        try:
                            frame.strokes.remove(stroke)
                        except:
                            pass
                    else:
                        totalLength = 0.0
                        for i in range(1, len(stroke.points)): 
                            p1 = stroke.points[i] # float tuple
                            p2 = stroke.points[i-1] # float tuple
                            # 2. Remove the point if it's a duplicate.
                            if (self.hitDetect3D(p1.co, p2.co, 0.1)): 
                                try:
                                    stroke.points.remove(stroke)
                                except:
                                    pass
                            else:
                                totalLength += self.getDistance(p1.co, p2.co)
                        # 3. Remove the stroke if its length is too small.
                        if (totalLength < cleanMinLength): 
                            try:
                                frame.strokes.remove(stroke)
                            except:
                                pass
                        else:
                            # 4. Finally, check the number of points again.
                            if (len(stroke.points) < cleanMinPoints): 
                                try:
                                    frame.strokes.remove(stroke)
                                except:
                                    pass

    def normalize(self, minVal=0.0, maxVal=1.0):
        allX = []
        allY = []
        allZ = []
        for layer in self.layers:
            for frame in layer.frames:
                for stroke in frame.strokes:
                    for point in stroke.points:
                        coord = point.co
                        allX.append(coord[0])
                        allY.append(coord[1])
                        allZ.append(coord[2])
        allX.sort()
        allY.sort()
        allZ.sort()
        #~
        leastValArray = [ allX[0], allY[0], allZ[0] ]
        mostValArray = [ allX[len(allX)-1], allY[len(allY)-1], allZ[len(allZ)-1] ]
        leastValArray.sort()
        mostValArray.sort()
        leastVal = leastValArray[0]
        mostVal = mostValArray[2]
        valRange = mostVal - leastVal
        #~
        xRange = (allX[len(allX)-1] - allX[0]) / valRange
        yRange = (allY[len(allY)-1] - allY[0]) / valRange
        zRange = (allZ[len(allZ)-1] - allZ[0]) / valRange
        #~
        minValX = minVal * xRange
        minValY = minVal * yRange
        minValZ = minVal * zRange
        maxValX = maxVal * xRange
        maxValY = maxVal * yRange
        maxValZ = maxVal * zRange
        #~
        for layer in self.layers:
            for frame in layer.frames:
                for stroke in frame.strokes:
                    for point in stroke.points:  
                        coord = point.co
                        x = self.remap(coord[0], allX[0], allX[len(allX)-1], minValX, maxValX)
                        y = self.remap(coord[1], allY[0], allY[len(allY)-1], minValY, maxValY)
                        z = self.remap(coord[2], allZ[0], allZ[len(allZ)-1], minValZ, maxValZ)
                        point.co = (x,y,z)

    def smoothStroke(self, stroke):
        points = stroke.points
        #~
        weight = 18
        scale = 1.0 / (weight + 2)
        lower = 0
        upper = 0
        center = 0
        #~
        for i in range(1, len(points) - 2):
            lower = points[i-1].co
            center = points[i].co
            upper = points[i+1].co
            #~
            x = (lower[0] + weight * center[0] + upper[0]) * scale
            y = (lower[1] + weight * center[1] + upper[1]) * scale
            z = (lower[2] + weight * center[2] + upper[2]) * scale
            stroke.points[i].co = (x, y, z) #center = (x, y, z)
        
    def splitStroke(self, stroke): 
        points = stroke.points
        #~
        for i in range(1, len(points), 2):
            center = (points[i].co[0], points[i].co[1], points[i].co[2])
            lower = (points[i-1].co[0], points[i-1].co[1], points[i-1].co[2])
            x = (center[0] + lower[0]) / 2
            y = (center[1] + lower[1]) / 2
            z = (center[2] + lower[2]) / 2
            p = (x, y, z)
            #~
            pressure = (points[i-1].pressure + points[i].pressure) / 2
            strength = (points[i-1].strength + points[i].strength) / 2
            #~
            pt = LatkPoint(p, pressure, strength)
            stroke.points.insert(i, pt)

    def reduceStroke(self, stroke):
        for i in range(0, len(stroke.points), 2):
            stroke.points.remove(stroke.points[i])

    def refine(self, splitReps=2, smoothReps=10, reduceReps=0, doClean=True):
        if (doClean==True):
            self.clean()
        if (smoothReps < splitReps):
            smoothReps = splitReps
        for layer in self.layers:
            for frame in layer.frames: 
                for stroke in frame.strokes:   
                    points = stroke.points
                    #~
                    for i in range(0, splitReps):
                        self.splitStroke(stroke)  
                        self.smoothStroke(stroke)  
                    #~
                    for i in range(0, smoothReps - splitReps):
                        self.smoothStroke(stroke)
                    #~
                    for i in range(0, reduceReps):
                        self.reduceStroke(stroke)    

    def setStroke(self, stroke):
        lastLayer = self.layers[len(self.layers)-1]
        lastFrame = lastLayer.frames[len(lastLayer.frames)-1]
        lastFrame.strokes.append(stroke)

    def setPoints(self, points, color=(0.0,0.0,0.0,1.0)):
        lastLayer = self.layers[len(self.layers)-1]
        lastFrame = lastLayer.frames[len(lastLayer.frames)-1]
        stroke = LatkStroke()
        stroke.points = points
        stroke.color = color
        lastFrame.strokes.append(stroke)
    
    def setCoords(self, coords, color=(0.0,0.0,0.0,1.0)):
        lastLayer = self.layers[len(self.layers)-1]
        lastFrame = lastLayer.frames[len(lastLayer.frames)-1]
        stroke = LatkStroke()
        stroke.setCoords(coords)
        stroke.color = color
        lastFrame.strokes.append(stroke)

    def getDistance(self, v1, v2):
        return sqrt((v1[0] - v2[0])**2 + (v1[1] - v2[1])**2 + (v1[2] - v2[2])**2)

    def hitDetect3D(self, p1, p2, hitbox=0.01):
        if (self.getDistance(p1, p2) <= hitbox):
            return True
        else:
            return False
             
    def roundVal(self, a, b):
        formatter = "{0:." + str(b) + "f}"
        return formatter.format(a)

    def roundValInt(self, a):
        formatter = "{0:." + str(0) + "f}"
        return int(formatter.format(a))

    def remap(self, value, min1, max1, min2, max2):
        range1 = max1 - min1
        range2 = max2 - min2
        valueScaled = float(value - min1) / float(range1)
        return min2 + (valueScaled * range2)

    def remapInt(self, value, min1, max1, min2, max2):
        return int(self.remap(value, min1, max1, min2, max2))

    def writeTextFile(self, name="test.txt", lines=None):
        file = open(name,"w") 
        for line in lines:
            file.write(line) 
        file.close() 

    def readTextFile(self, name="text.txt"):
        file = open(name, "r") 
        return file.read() 

# ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~
# ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~

    def readTiltBrush(self, filepath=None, vertSkip=1):
        globalScale = (0.1, 0.1, 0.1)
        globalOffset = (0, 0, 0)
        useScaleAndOffset = True

        filetype = self.getExtFromFileName(filepath)

        if (filetype == "tilt" or filetype == "zip"): # Tilt Brush binary file with original stroke data
            t = Tilt(filepath)
            #~
            layer = LatkLayer(name="TiltBrush")
            frame = LatkFrame()
            #~
            for tstroke in t.sketch.strokes:
                strokeColor = (0,0,0)
                pointGroup = []
                try:
                    strokeColor = (tstroke.brush_color[0], tstroke.brush_color[1], tstroke.brush_color[2])
                except:
                    pass
                for i in range(0, len(tstroke.controlpoints), vertSkip):
                    controlpoint = tstroke.controlpoints[i]
                    last_controlpoint = tstroke.controlpoints[i-1]
                    x = 0.0
                    y = 0.0
                    z = 0.0
                    #~
                    point = controlpoint.position
                    last_point = last_controlpoint.position
                    if (i==0 or point != last_point): # try to prevent duplicate points
                        pressure = 1.0
                        strength = 1.0
                        try:
                            pressure = controlpoint.extension[0]
                            # TODO strength?
                        except:
                            pass
                        #~
                        x = point[0]
                        y = point[2]
                        z = point[1]
                        if useScaleAndOffset == True:
                            x = (x * globalScale[0]) + globalOffset[0]
                            y = (y * globalScale[1]) + globalOffset[1]
                            z = (z * globalScale[2]) + globalOffset[2]
                        pointGroup.append((x, y, z, pressure, strength))
                        #~
                points = []
                for l, point in enumerate(pointGroup):
                    point = LatkPoint(co=(point[0], point[1], point[2]), pressure=point[3], strength=point[4])
                    points.append(point)
                
                stroke = LatkStroke(points, strokeColor)
                frame.strokes.append(stroke)
            
            layer.frames.append(frame)
            self.layers.append(layer)
        else: # Tilt Brush JSON export file, not original stroke data
            pressure = 1.0
            strength = 1.0
            #~
            with open(filepath) as data_file: 
                data = json.load(data_file)
            #~
            layer = LatkLayer(name="TiltBrush")
            frame = LatkFrame()
            #~
            for strokeJson in data["strokes"]:
                strokeColor = (0,0,0)
                try:
                    colorGroup = tiltBrushJson_DecodeData(strokeJson["c"], "c")
                    strokeColor = (colorGroup[0][0], colorGroup[0][1], colorGroup[0][2])
                except:
                    pass
                #~
                vertsFailed = False
                vertGroup = []
                pointGroup = []
                try:
                    vertGroup = tiltBrushJson_DecodeData(strokeJson["v"], "v")
                except:
                    vertsFailed = True

                if (vertsFailed==False and len(vertGroup) > 0):
                    for j in range(0, len(vertGroup), vertSkip):
                        if (j==0 or vertGroup[j] != vertGroup[j-1]): # try to prevent duplicate points
                            vert = vertGroup[j]
                            if (vert[0] == 0 and vert[1] == 0 and vert[2] == 0):
                                pass
                            else:
                                try:
                                    x = -vert[0]
                                    y = vert[2]
                                    z = vert[1]
                                    if (useScaleAndOffset == True):
                                        x = (x * globalScale[0]) + globalOffset[0]
                                        y = (y * globalScale[1]) + globalOffset[1]
                                        z = (z * globalScale[2]) + globalOffset[2]
                                    pointGroup.append((x, y, z, pressure, strength))
                                except:
                                    pass

                if (vertsFailed==False):
                    stroke = LatkStroke(color=strokeColor)
                    for l, point in enumerate(pointGroup):
                        point = LatkPoint(co=(point[0], point[1], point[2]), pressure=point[3], strength=point[4])
                        stroke.points.append(point)
                
                frame.strokes.append(stroke)
            
            layer.frames.append(frame)
            self.layers.append(layer)

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    def readAsc(self, filepath=None, strokeLength=1, vertexColor=True):
        globalScale = (1, 1, 1)
        globalOffset = (0, 0, 0)
        useScaleAndOffset = True
        #numPlaces = 7
        #roundValues = True

        with open(filepath) as data_file: 
            data = data_file.readlines()

        allPoints = []
        allPressures = []
        colors = []
        colorIs255 = False
        for line in data:
            pointRaw = line.split(",")
            if (len(pointRaw) < 3):
                pointRaw = line.split(" ")
            point = (float(pointRaw[0]), float(pointRaw[1]), float(pointRaw[2]))
            allPoints.append(point)
            
            color = None
            pressure = 1.0
            
            if (len(pointRaw) == 4):
                pressure = float(pointRaw[3])
            elif (len(pointRaw) == 6):
                color = (float(pointRaw[3]), float(pointRaw[4]), float(pointRaw[5]))
            elif(len(pointRaw) > 6):
                pressure = float(pointRaw[3])
                color = (float(pointRaw[4]), float(pointRaw[5]), float(pointRaw[6]))

            if (colorIs255 == False and color != None and color[0] + color[1] + color[2] > 3.1):
                    colorIs255 = True
            elif (colorIs255 == True):
                color = (color[0] / 255.0, color[1] / 255.0, color[2] / 255.0)

            allPressures.append(pressure)
            colors.append(color)

        layer = LatkLayer(name="ASC_layer")
        frame = LatkFrame()
        stroke = None
        pointsCounter = 0
        pointsTotal = 0

        for i in range(0, len(allPoints)-1):
            color = colors[i]
            
            if (pointsCounter == 0):
                stroke = LatkStroke()
                if (vertexColor == False and color != None):
                    stroke.color = color
            
            x = allPoints[i][0]
            y = allPoints[i][2]
            z = allPoints[i][1]
            pressure = allPressures[i]
            strength = 1.0
            if useScaleAndOffset == True:
                x = (x * globalScale[0]) + globalOffset[0]
                y = (y * globalScale[1]) + globalOffset[1]
                z = (z * globalScale[2]) + globalOffset[2]
            point = LatkPoint((x, y, z), pressure, strength)
            color = colors[i]
            if (vertexColor == True and color != None):
                if (len(color) < 4):
                    color = (color[0], color[1], color[2], 1)
                point.vertex_color = color
            stroke.points.append(point)

            pointsCounter += 1
            pointsTotal += 1
            if (pointsCounter > strokeLength-1):
                frame.strokes.append(stroke)
                pointsCounter = 0
            if (pointsTotal > len(allPoints)-1):
                break

        layer.frames.append(frame)
        self.layers.append(layer)

    def writeAsc(self, filepath=None, vertexColor=True):
        ascData = []

        for layer in self.layers:
            for frame in layer.frames:
                for stroke in frame.strokes:
                    color = None
                    if (vertexColor == False):
                        color = stroke.color
                    for point in stroke.points:
                        coord = point.co
                        x = coord[0]
                        y = coord[2]
                        z = coord[1]
                        pressure = point.pressure
                        if (vertexColor == True):
                            color = point.vertex_color
                        r = color[0]
                        g = color[1]
                        b = color[2]
                        ascData.append(str(x) + "," + str(y) + "," + str(z) + "," + str(pressure) + "," + str(r) + "," + str(g) + "," + str(b)) 

        self.writeTextFile(filepath, "\n".join(ascData))

# ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~
# ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~

class LatkLayer(object):    
    def __init__(self, frames=None, name="layer"): 
        if not frames:
        	self.frames = [] # LatkFrame
        else:
        	self.frames = frames
        self.name = name
        self.parent = None

    def getInfo(self):
        return self.name.split(".")[0]
    
# ~ ~ ~ ~ ~ ~ ~ ~ ~ ~

class LatkFrame(object):   
    def __init__(self, strokes=None, frame_number=0): 
        if not strokes:
        	self.strokes = [] # LatkStroke
        else:
        	self.strokes = strokes
        self.frame_number = frame_number
        self.parent_location = (0.0,0.0,0.0)
        
# ~ ~ ~ ~ ~ ~ ~ ~ ~ ~

class LatkStroke(object):       
    def __init__(self, points=None, color=(0.0, 0.0, 0.0, 1.0), fill_color=(0.0, 0.0, 0.0, 0.0)): 
        if not points:
        	self.points = []
        else:
            self.points = points
        self.color = color
        #self.alpha = 1.0
        self.fill_color = fill_color
        #self.fill_alpha = 0.0

    def setCoords(self, coords):
        self.points = []
        for coord in coords:
            self.points.append(LatkPoint(coord))

    def getCoords(self):
        returns = []
        for point in self.points:
            returns.append(point.co)
        return returns

    def getPressures(self):
        returns = []
        for point in self.points:
            returns.append(point.pressure)
        return returns

    def getStrengths(self):
        returns = []
        for point in self.points:
            returns.append(point.strength)
        return returns

# ~ ~ ~ ~ ~ ~ ~ ~ ~ ~

class LatkPoint(object):
    def __init__(self, co, pressure=1.0, strength=1.0, vertex_color=(0.0, 0.0, 0.0, 0.0)): # args float tuple, float, float
        self.co = co
        self.pressure = pressure
        self.strength = strength
        self.vertex_color = vertex_color
        self.distance = -1
        self.index = -1
    
# * * * * * * * * * * * * * * * * * * * * * * * * * *
# * * * * * * * * * * * * * * * * * * * * * * * * * *
# * * * * * * * * * * * * * * * * * * * * * * * * * *

import zipfile
from io import BytesIO

class InMemoryZip(object):

    def __init__(self):
        # Create the in-memory file-like object for working w/imz
        self.in_memory_zip = BytesIO()
        self.files = []

    def append(self, filename_in_zip, file_contents):
        # Appends a file with name filename_in_zip and contents of
        # file_contents to the in-memory zip.
        # Get a handle to the in-memory zip in append mode
        zf = zipfile.ZipFile(self.in_memory_zip, "a", zipfile.ZIP_DEFLATED, False)

        # Write the file to the in-memory zip
        zf.writestr(filename_in_zip, file_contents)

        # Mark the files as having been created on Windows so that
        # Unix permissions are not inferred as 0000
        for zfile in zf.filelist:
             zfile.create_system = 0         

        return self

    def readFromMemory(self):
        # Returns a string with the contents of the in-memory zip.
        self.in_memory_zip.seek(0)
        return self.in_memory_zip.read()

    def readFromDisk(self, url):
        zf = zipfile.ZipFile(url, 'r')
        for file in zf.infolist():
            self.files.append(zf.read(file.filename))

    def writetofile(self, filename):
        # Writes the in-memory zip to a file.
        f = open(filename, "wb")
        f.write(self.readFromMemory())
        f.close()

# * * * * * * * * * * * * * * * * * * * * * * * * * *


"""
rdp
~~~

Python implementation of the Ramer-Douglas-Peucker algorithm.

:copyright: 2014-2016 Fabian Hirschmann <fabian@hirschmann.email>
:license: MIT, see LICENSE.txt for more details.

Copyright (c) 2014 Fabian Hirschmann <fabian@hirschmann.email>

Permission is hereby granted, free of charge, to any person obtaining a
copy of this software and associated documentation files (the
"Software"), to deal in the Software without restriction, including
without limitation the rights to use, copy, modify, merge, publish
distribute, sublicense, and/or sell copies of the Software, and to
permit persons to whom the Software is furnished to do so, subject to
the following conditions:

The above copyright notice and this permission notice shall be included
in all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND,
EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF
MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT.
IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY
CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT,
TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE
SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.

"""

from math import sqrt
from functools import partial
import numpy as np
import sys

def pldist(point, start, end):
    """
    Calculates the distance from ``point`` to the line given
    by the points ``start`` and ``end``.

    :param point: a point
    :type point: numpy array
    :param start: a point of the line
    :type start: numpy array
    :param end: another point of the line
    :type end: numpy array
    """
    if np.all(np.equal(start, end)):
        return np.linalg.norm(point - start)

    return np.divide(
            np.abs(np.linalg.norm(np.cross(end - start, start - point))),
            np.linalg.norm(end - start))


def rdp_rec(M, epsilon, dist=pldist):
    """
    Simplifies a given array of points.

    Recursive version.

    :param M: an array
    :type M: numpy array
    :param epsilon: epsilon in the rdp algorithm
    :type epsilon: float
    :param dist: distance function
    :type dist: function with signature ``f(point, start, end)`` -- see :func:`rdp.pldist`
    """
    dmax = 0.0
    index = -1

    for i in range(1, M.shape[0]):
        d = dist(M[i], M[0], M[-1])

        if d > dmax:
            index = i
            dmax = d

    if dmax > epsilon:
        r1 = rdp_rec(M[:index + 1], epsilon, dist)
        r2 = rdp_rec(M[index:], epsilon, dist)

        return np.vstack((r1[:-1], r2))
    else:
        return np.vstack((M[0], M[-1]))


def _rdp_iter(M, start_index, last_index, epsilon, dist=pldist):
    stk = []
    stk.append([start_index, last_index])
    global_start_index = start_index
    indices = np.ones(last_index - start_index + 1, dtype=bool)

    while stk:
        start_index, last_index = stk.pop()

        dmax = 0.0
        index = start_index

        for i in range(index + 1, last_index):
            if indices[i - global_start_index]:
                d = dist(M[i], M[start_index], M[last_index])
                if d > dmax:
                    index = i
                    dmax = d

        if dmax > epsilon:
            stk.append([start_index, index])
            stk.append([index, last_index])
        else:
            for i in range(start_index + 1, last_index):
                indices[i - global_start_index] = False

    return indices


def rdp_iter(M, epsilon, dist=pldist, return_mask=False):
    """
    Simplifies a given array of points.

    Iterative version.

    :param M: an array
    :type M: numpy array
    :param epsilon: epsilon in the rdp algorithm
    :type epsilon: float
    :param dist: distance function
    :type dist: function with signature ``f(point, start, end)`` -- see :func:`rdp.pldist`
    :param return_mask: return the mask of points to keep instead
    :type return_mask: bool
    """
    mask = _rdp_iter(M, 0, len(M) - 1, epsilon, dist)

    if return_mask:
        return mask

    return M[mask]


def rdp(M, epsilon=0, dist=pldist, algo="iter", return_mask=False):
    """
    Simplifies a given array of points using the Ramer-Douglas-Peucker
    algorithm.

    Example:

    >>> from rdp import rdp
    >>> rdp([[1, 1], [2, 2], [3, 3], [4, 4]])
    [[1, 1], [4, 4]]

    This is a convenience wrapper around both :func:`rdp.rdp_iter` 
    and :func:`rdp.rdp_rec` that detects if the input is a numpy array
    in order to adapt the output accordingly. This means that
    when it is called using a Python list as argument, a Python
    list is returned, and in case of an invocation using a numpy
    array, a NumPy array is returned.

    The parameter ``return_mask=True`` can be used in conjunction
    with ``algo="iter"`` to return only the mask of points to keep. Example:

    >>> from rdp import rdp
    >>> import numpy as np
    >>> arr = np.array([1, 1, 2, 2, 3, 3, 4, 4]).reshape(4, 2)
    >>> arr
    array([[1, 1],
           [2, 2],
           [3, 3],
           [4, 4]])
    >>> mask = rdp(arr, algo="iter", return_mask=True)
    >>> mask
    array([ True, False, False,  True], dtype=bool)
    >>> arr[mask]
    array([[1, 1],
           [4, 4]])

    :param M: a series of points
    :type M: numpy array with shape ``(n,d)`` where ``n`` is the number of points and ``d`` their dimension
    :param epsilon: epsilon in the rdp algorithm
    :type epsilon: float
    :param dist: distance function
    :type dist: function with signature ``f(point, start, end)`` -- see :func:`rdp.pldist`
    :param algo: either ``iter`` for an iterative algorithm or ``rec`` for a recursive algorithm
    :type algo: string
    :param return_mask: return mask instead of simplified array
    :type return_mask: bool
    """

    if algo == "iter":
        algo = partial(rdp_iter, return_mask=return_mask)
    elif algo == "rec":
        if return_mask:
            raise NotImplementedError("return_mask=True not supported with algo=\"rec\"")
        algo = rdp_rec
        
    if "numpy" in str(type(M)):
        return algo(M, epsilon, dist)

    return algo(np.array(M), epsilon, dist).tolist()

# * * * * * * * * * * * * * * * * * * * * * * * * * *

# based on https:#openprocessing.org/sketch/51404/

from random import uniform

def kdist(p1, p2):
    [x1,y1,z1] = p1
    [x2,y2,z2] = p2    
    return (((x2-x1)**2)+((y2-y1)**2)+((z2-z1)**2))**(1/2)     

class KMeans(object):
    def __init__(self, _points, _numCentroids): # ArrayList<PVector>, int
        self.particles = [] # ArrayList<KParticle>
        self.centroids = [] # ArrayList<KCentroid>
        self.centroidFinalPositions = [] # ArrayList<PVector>
        self.clusters = [] # ArrayList<KCluster>
        
        self.numberOfCentroids = _numCentroids # int
        self.minX = 0.0
        self.maxX = 0.0
        self.minY = 0.0
        self.maxY = 0.0
        self.minZ = 0.0
        self.maxZ = 0.0
        self.totalStability = 0.0
        self.stableThreshold = 0.0001
        self.ready = False
        
        for p in _points:
            if (p[0] < self.minX):
                self.minX = p[0]
            if (p[0] > self.maxX):
                self.maxX = p[0]
            if (p[1] < self.minY):
                self.minY = p[1]
            if (p[1] > self.maxY):
                self.maxY = p[1]
            if (p[2] < self.minZ):
                self.minZ = p[2]
            if (p[2] > self.maxZ):
                self.maxZ = p[2]
            self.particles.append(KParticle(p))
        
        self.init()
    
    def init(self):    
        self.ready = False
        self.centroids.clear()
        self.clusters.clear()
    
        for i in range(0, self.numberOfCentroids):
            c = KCentroid(i, 127+uniform(0,127), 127+uniform(0,127), 127+uniform(0,127), self.minX, self.maxX, self.minY, self.maxY, self.minZ, self.maxZ)
            self.centroids.append(c)
        
    def update(self):
        for particle in self.particles: 
            particle.FindClosestCentroid(self.centroids)
        
        self.totalStability = 0
        
        for centroid in self.centroids:
            centroid.update(self.particles)
            if (centroid.stability > 0):
                self.totalStability += centroid.stability
        
        if (self.totalStability < self.stableThreshold):
            for centroid in self.centroids:
                p = centroid.position # PVector
                self.clusters.append(KCluster(p))
                self.centroidFinalPositions.append(p)
            
            for particle in self.particles:
                self.clusters[particle.centroidIndex].points.append(particle.position)
            
            self.ready = True
        
        #println(totalStability + " " + ready)
    
    '''
    def draw(self):
        if (self.ready == False):
            for particle in self.particles:
                particle.draw()
        
            for centroid in self.centroids:
                centroid.draw()
    '''

    def run(self):
        if (self.ready == False):
            self.update()
        #self.draw()
 
# ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~

class KCentroid(object):
    def __init__(self, _internalIndex, _r, _g, _b, _minX, _maxX, _minY, _maxY, _minZ, _maxZ): # int, float, float, float, float, float, float, float, float, float
        self.position = (uniform(_minX, _maxX), uniform(_minY, _maxY), uniform(_minZ, _maxZ))
        self.colorR = _r
        self.colorG = _g
        self.colorB = _b
        self.internalIndex = _internalIndex
        self.stability = -1.0

    def update(self, _particles): # ArrayList<KParticle>
        #println("-----------------------")
        #println("K-Means KCentroid Tick")
        # move the centroid to its position

        newPosition = (0.0, 0.0, 0.0)

        numberOfAssociatedParticles = 0

        for curParticle in _particles:
            if (curParticle.centroidIndex == self.internalIndex):
                x = newPosition[0] + curParticle.position[0]
                y = newPosition[1] + curParticle.position[1]
                z = newPosition[2] + curParticle.position[2]
                newPosition = (x, y, z)
                numberOfAssociatedParticles += 1

        if (numberOfAssociatedParticles < 1):
            numberOfAssociatedParticles = 1

        newPosition = (newPosition[0] / numberOfAssociatedParticles, newPosition[1] / numberOfAssociatedParticles, newPosition[2] / numberOfAssociatedParticles)
        self.stability = kdist(self.position, newPosition)
        self.position = newPosition

    '''
    def draw(self):
        pushMatrix()
        translate(position.x, position.y, position.z)
        strokeWeight(10)
        stroke(colorR, colorG, colorB)
        point(0,0)
        popMatrix()
    '''

# ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~

class KParticle(object):
    def __init__(self, _position): # PVector
        self.position = _position # PVector
        self.velocity = (0.0,0.0,0.0) # PVector
        self.centroidIndex = 0 # int
        self.colorR = 0.0
        self.colorG = 0.0
        self.colorB = 0.0
        self.brightness = 0.8
    
    def FindClosestCentroid(self, _centroids): # ArrayList<KCentroid> 
        closestCentroidIndex = 0 # int
        closestDistance = 100000.0

        # find which centroid is the closest
        for i in range(0, len(_centroids)):             
            curCentroid = _centroids[i] # KCentroid

            distanceCheck = kdist(self.position, curCentroid.position) # float

            if (distanceCheck < closestDistance):
                closestCentroidIndex = i
                closestDistance = distanceCheck

        # now that we have the closest centroid chosen, assign the index,
        self.centroidIndex = closestCentroidIndex

        # and grab the color for the visualization        
        curCentroid = _centroids[self.centroidIndex] # KCentroid 
        self.colorR = curCentroid.colorR * self.brightness
        self.colorG = curCentroid.colorG * self.brightness
        self.colorB = curCentroid.colorB * self.brightness
    
    '''
    def draw(self):
        pushMatrix()
        translate(position.x, position.y, position.z)
        strokeWeight(2)
        stroke(colorR, colorG, colorB)
        point(0, 0)
        popMatrix()
    '''

# ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~

class KCluster(object):
    def __init__(self, _centroid): # PVector    
        self.centroid = _centroid
        self.points = []
# TILT BRUSH binary reader

# Copyright 2016 Google Inc. All Rights Reserved.
# 
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
# 
#         http://www.apache.org/licenses/LICENSE-2.0
# 
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""Reads and writes .tilt files. The main export is 'class Tilt'."""

#__all__ = ('Tilt', 'Sketch', 'Stroke', 'ControlPoint', 'BadTilt', 'BadMetadata', 'MissingKey')

# Format characters are as for struct.pack/unpack, with the addition of
# '@' which is a 4-byte-length-prefixed data blob.
STROKE_EXTENSION_BITS = {
    0x1: ('flags', 'I'),
    0x2: ('scale', 'f'),
    'unknown': lambda bit: ('stroke_ext_%d' % math.log(bit, 2),
                                                    'I' if (bit & 0xffff) else '@')
}

STROKE_EXTENSION_BY_NAME = dict(
    (info[0], (bit, info[1]))
    for (bit, info) in STROKE_EXTENSION_BITS.items()
    if bit != 'unknown'
)

CONTROLPOINT_EXTENSION_BITS = {
    0x1: ('pressure', 'f'),
    0x2: ('timestamp', 'I'),
    'unknown': lambda bit: ('cp_ext_%d' % math.log(bit, 2), 'I')
}


#
# Internal utils
#


class memoized_property(object):
    """Modeled after @property, but runs the getter exactly once"""
    def __init__(self, fget):
        self.fget = fget
        self.name = fget.__name__

    def __get__(self, instance, owner):
        if instance is None:
            return None
        value = self.fget(instance)
        # Since this isn't a data descriptor (no __set__ method),
        # instance attributes take precedence over the descriptor.
        setattr(instance, self.name, value)
        return value


class binfile(object):
    # Helper for parsing
    def __init__(self, inf):
        self.inf = inf

    def read(self, n):
        return self.inf.read(n)

    def write(self, data):
        return self.inf.write(data)

    def read_length_prefixed(self):
        n, = self.unpack("<I")
        return self.inf.read(n)

    def write_length_prefixed(self, data):
        self.pack("<I", len(data))
        self.inf.write(data)

    def unpack(self, fmt):
        n = struct.calcsize(fmt)
        data = self.inf.read(n)
        return struct.unpack(fmt, data)

    def pack(self, fmt, *args):
        data = struct.pack(fmt, *args)
        return self.inf.write(data)

class BadTilt(Exception): pass
class BadMetadata(BadTilt): pass
class MissingKey(BadMetadata): pass

def validate_metadata(dct):
    def lookup(xxx_todo_changeme, key):
        (path, parent) = xxx_todo_changeme
        child_path = '%s.%s' % (path, key)
        if key not in parent:
            raise MissingKey('Missing %s' % child_path)
        return (child_path, parent[key])
    def check_string(xxx_todo_changeme1):
        (path, val) = xxx_todo_changeme1
        if not isinstance(val, str):
            raise BadMetadata('Not string: %s' % path)
    def check_float(xxx_todo_changeme2):
        (path, val) = xxx_todo_changeme2
        if not isinstance(val, (float, int)):
            raise BadMetadata('Not number: %s' % path)
    def check_array(xxx_todo_changeme3, desired_len=None, typecheck=None):
        (path, val) = xxx_todo_changeme3
        if not isinstance(val, (list, tuple)):
            raise BadMetadata('Not array: %s' % path)
        if desired_len and len(val) != desired_len:
            raise BadMetadata('Not length %d: %s' % (desired_len, path))
        if typecheck is not None:
            for i, child_val in enumerate(val):
                child_path = '%s[%s]' % (path, i)
                typecheck((child_path, child_val))
    def check_guid(xxx_todo_changeme4):
        (path, val) = xxx_todo_changeme4
        try:
            uuid.UUID(val)
        except Exception as e:
            raise BadMetadata('Not UUID: %s %s' % (path, e))
    def check_xform(pathval):
        check_array(lookup(pathval, 'position'), 3, check_float)
        check_array(lookup(pathval, 'orientation'), 4, check_float)

    root = ('metadata', dct)
    try: check_xform(lookup(root, 'ThumbnailCameraTransformInRoomSpace'))
    except MissingKey: pass
    try: check_xform(lookup(root, 'SceneTransformInRoomSpace'))
    except MissingKey: pass
    try: check_xform(lookup(root, 'CanvasTransformInSceneSpace'))
    except MissingKey: pass
    check_array(lookup(root, 'BrushIndex'), None, check_guid)
    check_guid(lookup(root, 'EnvironmentPreset'))
    if 'Authors' in dct:
        check_array(lookup(root, 'Authors'), None, check_string)


#
# External
#

import os
import math
import json
import uuid
import struct
import contextlib
from collections import defaultdict
import io

class Tilt(object):
    """Class representing a .tilt file. Attributes:
        .sketch         A tilt.Sketch instance. NOTE: this is read lazily.
        .metadata     A dictionary of data.

    To modify the sketch, see XXX.
    To modify the metadata, see mutable_metadata()."""
    @staticmethod
    @contextlib.contextmanager
    def as_directory(tilt_file):
        """Temporarily convert *tilt_file* to directory format."""
        if os.path.isdir(tilt_file):
            yield Tilt(tilt_file)
        else:
            import tiltbrush.unpack as unpack
            compressed = unpack.convert_zip_to_dir(tilt_file)
            try:
                yield Tilt(tilt_file)
            finally:
                unpack.convert_dir_to_zip(tilt_file, compressed)

    @staticmethod
    def iter(directory):
        for r,ds,fs in os.walk(directory):
            for f in ds+fs:
                if f.endswith('.tilt'):
                    try:
                        yield Tilt(os.path.join(r,f))
                    except BadTilt:
                        pass

    def __init__(self, filename):
        self.filename = filename
        self._sketch = None                    # lazily-loaded
        '''
        with self.subfile_reader('metadata.json') as inf:
            self.metadata = json.load(inf)
            try:
                validate_metadata(self.metadata)
            except BadMetadata as e:
                print('WARNING: %s' % e)
        '''

    def write_sketch(self):
        if False:
            # Recreate BrushIndex. Not tested and not strictly necessary, so not enabled
            old_index_to_brush = list(self.metadata['BrushIndex'])
            old_brushes = set( old_index_to_brush )
            new_brushes = set( old_index_to_brush[s.brush_idx] for s in self.sketch.strokes )
            if old_brushes != new_brushes:
                new_index_to_brush = sorted(new_brushes)
                brush_to_new_index = dict( (b, i) for (i, b) in enumerate(new_index_to_brush) )
                old_index_to_new_index = list(map(brush_to_new_index.get, old_index_to_brush))
                for stroke in self.sketch.strokes:
                    stroke.brush_idx = brush_to_new_index[old_index_to_brush[stroke.brush_idx]]
                with self.mutable_metadata() as dct:
                    dct['BrushIndex'] = new_index_to_brush

        self.sketch.write(self)

    @contextlib.contextmanager
    def subfile_reader(self, subfile):
        if os.path.isdir(self.filename):
            with file(os.path.join(self.filename, subfile), 'rb') as inf:
                yield inf
        else:
            from zipfile import ZipFile
            with ZipFile(self.filename, 'r') as inzip:
                with inzip.open(subfile) as inf:
                    yield inf

    @contextlib.contextmanager
    def subfile_writer(self, subfile):
        # Kind of a large hammer, but it works
        if os.path.isdir(self.filename):
            with file(os.path.join(self.filename, subfile), 'wb') as outf:
                yield outf
        else:
            with Tilt.as_directory(self.filename) as tilt2:
                with tilt2.subfile_writer(subfile) as outf:
                    yield outf

    @contextlib.contextmanager
    def mutable_metadata(self):
        """Return a mutable copy of the metadata.
        When the context manager exits, the updated metadata will
        validated and written to disk."""
        import copy
        mutable_dct = copy.deepcopy(self.metadata)
        yield mutable_dct
        validate_metadata(mutable_dct)
        if self.metadata != mutable_dct:
            # Copy into self.metadata, preserving topmost reference
            for k in list(self.metadata.keys()):
                del self.metadata[k]
            for k,v in mutable_dct.items():
                self.metadata[k] = copy.deepcopy(v)
                
            new_contents = json.dumps(
                mutable_dct, ensure_ascii=True, allow_nan=False,
                indent=2, sort_keys=True, separators=(',', ': '))
            with self.subfile_writer('metadata.json') as outf:
                outf.write(new_contents)

    @memoized_property
    def sketch(self):
        # Would be slightly more consistent semantics to do the data read
        # in __init__, and parse it here; but this is probably good enough.
        return Sketch(self)

def _make_ext_reader(ext_bits, ext_mask):
    """Helper for Stroke and ControlPoint parsing.
    Returns:
    - function reader(file) -> list<extension values>
    - function writer(file, values)
    - dict mapping extension_name -> extension_index
    """
    infos = []
    while ext_mask:
        bit = ext_mask & ~(ext_mask-1)
        ext_mask = ext_mask ^ bit
        try: info = ext_bits[bit]
        except KeyError: info = ext_bits['unknown'](bit)
        infos.append(info)

    if len(infos) == 0:
        return (lambda f: [], lambda f,vs: None, {})

    fmt = '<' + ''.join(info[1] for info in infos)
    names = [info[0] for info in infos]
    if '@' in fmt:
        # struct.unpack isn't general enough to do the job
        #print(fmt, names, infos)
        fmts = ['<'+info[1] for info in infos]
        def reader(f, fmts=fmts):
            values = [None] * len(fmts)
            for i,fmt in enumerate(fmts):
                if fmt == '<@':
                    nbytes, = struct.unpack('<I', f.read(4))
                    values[i] = f.read(nbytes)
                else:
                    values[i], = struct.unpack(fmt, f.read(4))
    else:
        def reader(f, fmt=fmt, nbytes=len(infos)*4):
            values = list(struct.unpack(fmt, f.read(nbytes)))
            return values

    def writer(f, values, fmt=fmt):
        return f.write(struct.pack(fmt, *values))

    lookup = dict( (name,i) for (i,name) in enumerate(names) )
    return reader, writer, lookup

def _make_stroke_ext_reader(ext_mask, memo={}):
    try:
        ret = memo[ext_mask]
    except KeyError:
        ret = memo[ext_mask] = _make_ext_reader(STROKE_EXTENSION_BITS, ext_mask)
    return ret

def _make_cp_ext_reader(ext_mask, memo={}):
    try:
        ret = memo[ext_mask]
    except KeyError:
        ret = memo[ext_mask] = _make_ext_reader(CONTROLPOINT_EXTENSION_BITS, ext_mask)
    return ret


class Sketch(object):
    """Stroke data from a .tilt file. Attributes:
        .strokes        List of tilt.Stroke instances
        .filename     Filename if loaded from file, but usually None
        .header         Opaque header data"""
    def __init__(self, source):
        """source is either a file name, a file-like instance, or a Tilt instance."""
        if isinstance(source, Tilt):
            with source.subfile_reader('data.sketch') as inf:
                self.filename = None
                self._parse(binfile(inf))
        elif hasattr(source, 'read'):
            self.filename = None
            self._parse(binfile(source))
        else:
            self.filename = source
            with file(source, 'rb') as inf:
                self._parse(binfile(inf))

    def write(self, destination):
        """destination is either a file name, a file-like instance, or a Tilt instance."""
        tmpf = io.StringIO()
        self._write(binfile(tmpf))
        data = tmpf.getvalue()

        if isinstance(destination, Tilt):
            with destination.subfile_writer('data.sketch') as outf:
                outf.write(data)
        elif hasattr(destination, 'write'):
            destination.write(data)
        else:
            with file(destination, 'wb') as outf:
                outf.write(data)

    def _parse(self, b):
        # b is a binfile instance
        # mutates self
        self.header = list(b.unpack("<3I"))
        self.additional_header = b.read_length_prefixed()
        (num_strokes, ) = b.unpack("<i")
        assert 0 <= num_strokes < 300000, num_strokes
        self.strokes = [Stroke.from_file(b) for i in range(num_strokes)]

    def _write(self, b):
        # b is a binfile instance.
        b.pack("<3I", *self.header)
        b.write_length_prefixed(self.additional_header)
        b.pack("<i", len(self.strokes))
        for stroke in self.strokes:
            stroke._write(b)


class Stroke(object):
    """Data for a single stroke from a .tilt file. Attributes:
        .brush_idx            Index into Tilt.metadata['BrushIndex']; tells you the brush GUID
        .brush_color        RGBA color, as 4 floats in the range [0, 1]
        .brush_size         Brush size, in decimeters, as a float. Multiply by
                                        get_stroke_extension('scale') to get a true size.
        .controlpoints    List of tilt.ControlPoint instances.

        .flags                    Wrapper around get/set_stroke_extension('flags')
        .scale                    Wrapper around get/set_stroke_extension('scale')

    Also see has_stroke_extension(), get_stroke_extension()."""
    @classmethod
    def from_file(cls, b):
        inst = cls()
        inst._parse(b)
        return inst

    def clone(self):
        """Returns a deep copy of the stroke."""
        inst = self.shallow_clone()
        inst.controlpoints = list(map(ControlPoint.clone, inst.controlpoints))
        return inst

    def __getattr__(self, name):
        if name in STROKE_EXTENSION_BY_NAME:
            try:
                return self.get_stroke_extension(name)
            except LookupError:
                raise AttributeError("%s (extension attribute)" % name)
        return super(Stroke, self).__getattr__(name)

    def __setattr__(self, name, value):
        if name in STROKE_EXTENSION_BY_NAME:
            return self.set_stroke_extension(name, value)
        return super(Stroke, self).__setattr__(name, value)

    def __delattr__(self, name):
        if name in STROKE_EXTENSION_BY_NAME:
            try:
                self.delete_stroke_extension(name)
                return
            except LookupError:
                raise AttributeError("%s (extension attribute)" % name)
        return super(Stroke, self).__delattr__(name)

    def shallow_clone(self):
        """Clone everything but the control points themselves."""
        inst = self.__class__()
        for attr in ('brush_idx', 'brush_color', 'brush_size', 'stroke_mask', 'cp_mask',
                                 'stroke_ext_writer', 'stroke_ext_lookup', 'cp_ext_writer', 'cp_ext_lookup'):
            setattr(inst, attr, getattr(self, attr))
        inst.extension = list(self.extension)
        inst.controlpoints = list(self.controlpoints)
        return inst

    def _parse(self, b):
        # b is a binfile instance
        (self.brush_idx, ) = b.unpack("<i")
        self.brush_color = b.unpack("<4f")
        (self.brush_size, self.stroke_mask, self.cp_mask) = b.unpack("<fII")
        stroke_ext_reader, self.stroke_ext_writer, self.stroke_ext_lookup = \
                _make_stroke_ext_reader(self.stroke_mask)
        self.extension = stroke_ext_reader(b)

        cp_ext_reader, self.cp_ext_writer, self.cp_ext_lookup = \
                _make_cp_ext_reader(self.cp_mask)
        
        (num_cp, ) = b.unpack("<i")
        assert num_cp < 10000, num_cp

        # Read the raw data up front, but parse it lazily
        bytes_per_cp = 4 * (3 + 4 + len(self.cp_ext_lookup))
        self._controlpoints = (cp_ext_reader, num_cp, b.inf.read(num_cp * bytes_per_cp))

    @memoized_property
    def controlpoints(self):
        (cp_ext_reader, num_cp, raw_data) = self.__dict__.pop('_controlpoints')
        b = binfile(io.BytesIO(raw_data))
        return [ControlPoint.from_file(b, cp_ext_reader) for i in range(num_cp)]

    def has_stroke_extension(self, name):
        """Returns true if this stroke has the requested extension data.
        
        The current stroke extensions are:
            scale         Non-negative float. The size of the player when making this stroke.
                                Multiply this by the brush size to get a true stroke size."""
        return name in self.stroke_ext_lookup

    def get_stroke_extension(self, name):
        """Returns the requested extension stroke data.
        Raises LookupError if it doesn't exist."""
        idx = self.stroke_ext_lookup[name]
        return self.extension[idx]

    def set_stroke_extension(self, name, value):
        """Sets stroke extension data.
        This method can be used to add extension data."""
        idx = self.stroke_ext_lookup.get(name, None)
        if idx is not None:
            self.extension[idx] = value
        else:
            # Convert from idx->value to name->value
            name_to_value = dict( (name, self.extension[idx])
                                                        for (name, idx) in self.stroke_ext_lookup.items() )
            name_to_value[name] = value

            bit, exttype = STROKE_EXTENSION_BY_NAME[name]
            self.stroke_mask |= bit
            _, self.stroke_ext_writer, self.stroke_ext_lookup = \
                    _make_stroke_ext_reader(self.stroke_mask)
            
            # Convert back to idx->value
            self.extension = [None] * len(self.stroke_ext_lookup)
            for (name, idx) in self.stroke_ext_lookup.items():
                self.extension[idx] = name_to_value[name]
                                                                                                                    
    def delete_stroke_extension(self, name):
        """Remove stroke extension data.
        Raises LookupError if it doesn't exist."""
        idx = self.stroke_ext_lookup[name]

        # Convert from idx->value to name->value
        name_to_value = dict( (name, self.extension[idx])
                                                    for (name, idx) in self.stroke_ext_lookup.items() )
        del name_to_value[name]

        bit, exttype = STROKE_EXTENSION_BY_NAME[name]
        self.stroke_mask &= ~bit
        _, self.stroke_ext_writer, self.stroke_ext_lookup = \
                _make_stroke_ext_reader(self.stroke_mask)

        # Convert back to idx->value
        self.extension = [None] * len(self.stroke_ext_lookup)
        for (name, idx) in self.stroke_ext_lookup.items():
            self.extension[idx] = name_to_value[name]

    def has_cp_extension(self, name):
        """Returns true if control points in this stroke have the requested extension data.
        All control points in a stroke are guaranteed to use the same set of extensions.

        The current control point extensions are:
            timestamp                 In seconds
            pressure                    From 0 to 1"""
        return name in self.cp_ext_lookup

    def get_cp_extension(self, cp, name):
        """Returns the requested extension data, or raises LookupError if it doesn't exist."""
        idx = self.cp_ext_lookup[name]
        return cp.extension[idx]

    def _write(self, b):
        b.pack("<i", self.brush_idx)
        b.pack("<4f", *self.brush_color)
        b.pack("<fII", self.brush_size, self.stroke_mask, self.cp_mask)
        self.stroke_ext_writer(b, self.extension)
        b.pack("<i", len(self.controlpoints))
        for cp in self.controlpoints:
            cp._write(b, self.cp_ext_writer)


class ControlPoint(object):
    """Data for a single control point from a stroke. Attributes:
        .position        Position as 3 floats. Units are decimeters.
        .orientation Orientation of controller as a quaternion (x, y, z, w)."""
    @classmethod
    def from_file(cls, b, cp_ext_reader):
        # b is a binfile instance
        # reader reads controlpoint extension data from the binfile
        inst = cls()
        inst.position = list(b.unpack("<3f"))
        inst.orientation = list(b.unpack("<4f"))
        inst.extension = cp_ext_reader(b)
        return inst

    def clone(self):
        inst = self.__class__()
        for attr in ('position', 'orientation', 'extension'):
            setattr(inst, attr, list(getattr(self, attr)))
        return inst

    def _write(self, b, cp_ext_writer):
        p = self.position; o = self.orientation
        b.pack("<7f", p[0], p[1], p[2], o[0], o[1], o[2], o[3])
        cp_ext_writer(b, self.extension)


def tiltBrushJson_Grouper(n, iterable, fillvalue=None):
  """grouper(3, 'ABCDEFG', 'x') --> ABC DEF Gxx"""
  args = [iter(iterable)] * n
  return zip_longest(fillvalue=fillvalue, *args)

def tiltBrushJson_DecodeData(obj, dataType="v"):
    '''    
    VERTEX_ATTRIBUTES = [
        # Attribute name, type code
        ('v',  'f', None),
        ('n',  'f', 3),
        ('uv0','f', None),
        ('uv1','f', None),
        ('c',  'I', 1),
        ('t',  'f', 4),
    ]
    '''
    if (dataType=="v" or dataType=="n" or dataType=="t"):
        typeChar = "f"
    elif (dataType=="c"):
        typeChar = "I"

    num_verts = 1
    empty = None
    data_grouped = []
    
    data_bytes = base64.b64decode(obj)
    fmt = "<%d%c" % (len(data_bytes) / 4, typeChar)
    data_words = struct.unpack(fmt, data_bytes)
    
    if (dataType=="v" or dataType=="n"):
        num_verts = len(data_words) / 3
    elif (dataType=="t"):
        num_verts = len(data_words) / 4

    if (len(data_words) % num_verts != 0):
        return None
    else: 
        stride_words = int(len(data_words) / num_verts)
        if stride_words > 1:
            data_grouped = list(tiltBrushJson_Grouper(stride_words, data_words))
        else:
            data_grouped = list(data_words)

        if (dataType == "c"):
            for i in range(0, len(data_grouped)):
                data_grouped[i] = rgbIntToTuple(data_grouped[i][0], normalized=True)

        return(data_grouped)

# * * * * * * * * * * * * * * * * * * * * * * * * * *
# * * * * * * * * * * * * * * * * * * * * * * * * * *
# * * * * * * * * * * * * * * * * * * * * * * * * * *

