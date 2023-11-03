'''
The Lightning Artist Toolkit was developed with support from:
   Canada Council on the Arts
   Eyebeam Art + Technology Center
   Ontario Arts Council
   Toronto Arts Council
   
Copyright (c) 2023 Nick Fox-Gieg
https://fox-gieg.com

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
import numpy as np
from . latk_zip import *
from . latk_tilt import *
from . latk_rdp import *
from . latk_kmeans import *

class Latk(object):     
    def __init__(self, filepath=None, layers=None, init=False, coords=None, color=None, frame_rate=12): # args string, Latk array, float tuple array, float tuple           
        if not layers:
        	self.layers = [] # LatkLayer
        else:
        	self.layers = layers
        
        self.frame_rate = frame_rate
        self.version = 2.9

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
                            
                            if (useScaleAndOffset == True):
                                x = (x * globalScale[0]) + globalOffset[0]
                                y = (y * globalScale[1]) + globalOffset[1]
                                z = (z * globalScale[2]) + globalOffset[2]
                                                                                       
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
                                
                                if (useScaleAndOffset == True):
                                    x = (x * globalScale[0]) + globalOffset[0]
                                    y = (y * globalScale[1]) + globalOffset[1]
                                    z = (z * globalScale[2]) + globalOffset[2]
                                                                                           
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
                                    
                                    if (useScaleAndOffset == True):
                                        x = (x * globalScale[0]) + globalOffset[0]
                                        y = (y * globalScale[1]) + globalOffset[1]
                                        z = (z * globalScale[2]) + globalOffset[2]
                                                                                               
                                    pressure = 1.0
                                    strength = 1.0
                                    try:
                                        pressure = jsonPoint["pressure"]
                                        if (np.isnan(pressure) == True):
                                            pressure = 1.0
                                    except:
                                        pass
                                    try:
                                        strength = jsonPoint["strength"]
                                        if (np.isnan(strength) == True):
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
                                    
                                    if (useScaleAndOffset == True):
                                        x = (x * globalScale[0]) + globalOffset[0]
                                        y = (y * globalScale[1]) + globalOffset[1]
                                        z = (z * globalScale[2]) + globalOffset[2]
                                                                                                                                 
                                    pressure = 1.0
                                    strength = 1.0
                                    vertex_color = (0.0,0.0,0.0,0.0)

                                    try:
                                        pressure = jsonPoint["pressure"]
                                        if (np.isnan(pressure) == True):
                                            pressure = 1.0
                                    except:
                                        pass
                                    try:
                                        strength = jsonPoint["strength"]
                                        if (np.isnan(strength) == True):
                                            strength = 1.0
                                    except:
                                        pass
                                    try:
                                        vertex_color = jsonPoint["vertex_color"]
                                        if (np.isnan(vertex_color) == True):
                                            vertex_color = (0.0,0.0,0.0,1.0)
                                    except:
                                        pass  

                                    points.append(LatkPoint((x,y,z), pressure, strength, vertex_color))
                                                        
                                stroke = LatkStroke(points, color, fill_color)
                                frame.strokes.append(stroke)
                            layer.frames.append(frame)
                        self.layers.append(layer)

    def write(self, filepath, yUp=True, useScaleAndOffset=False, zipped=True, globalScale=(1.0, 1.0, 1.0), globalOffset=(0.0, 0.0, 0.0), precision=32): # defaults to Unity, Maya Y up
        FINAL_LAYER_LIST = []

        for layer in self.layers:
            sb = []
            sbHeader = []
            sbHeader.append("\t\t\t\t\t\"frames\": [")
            sb.append("\n".join(sbHeader))

            for h, frame in enumerate(layer.frames):
                sbbHeader = []
                sbbHeader.append("\t\t\t\t\t\t{")
                sbbHeader.append("\t\t\t\t\t\t\t\"strokes\": [")
                sb.append("\n".join(sbbHeader))
                
                for i, stroke in enumerate(frame.strokes):
                    sbb = []
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

                    if (precision == 64):
                        sbb.append("\t\t\t\t\t\t\t\t\t\"color\": [" + str(np.float64(color[0])) + ", " + str(np.float64(color[1])) + ", " + str(np.float64(color[2])) + ", " + str(np.float64(color[3])) + "],")
                        sbb.append("\t\t\t\t\t\t\t\t\t\"fill_color\": [" + str(np.float64(fill_color[0])) + ", " + str(np.float64(fill_color[1])) + ", " + str(np.float64(fill_color[2])) + ", " + str(np.float64(fill_color[3])) + "],")
                    elif (precision == 16):
                        sbb.append("\t\t\t\t\t\t\t\t\t\"color\": [" + str(np.float16(color[0])) + ", " + str(np.float16(color[1])) + ", " + str(np.float16(color[2])) + ", " + str(np.float16(color[3])) + "],")
                        sbb.append("\t\t\t\t\t\t\t\t\t\"fill_color\": [" + str(np.float16(fill_color[0])) + ", " + str(np.float16(fill_color[1])) + ", " + str(np.float16(fill_color[2])) + ", " + str(np.float16(fill_color[3])) + "],")
                    else:
                        sbb.append("\t\t\t\t\t\t\t\t\t\"color\": [" + str(np.float32(color[0])) + ", " + str(np.float32(color[1])) + ", " + str(np.float32(color[2])) + ", " + str(np.float32(color[3])) + "],")
                        sbb.append("\t\t\t\t\t\t\t\t\t\"fill_color\": [" + str(np.float32(fill_color[0])) + ", " + str(np.float32(fill_color[1])) + ", " + str(np.float32(fill_color[2])) + ", " + str(np.float32(fill_color[3])) + "],")

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
                            
                            if (useScaleAndOffset == True):
                                x = (x * globalScale[0]) + globalOffset[0]
                                y = (y * globalScale[1]) + globalOffset[1]
                                z = (z * globalScale[2]) + globalOffset[2]
                             
                            if (precision == 64):
                                pointStr = "\t\t\t\t\t\t\t\t\t\t{\"co\": [" + str(np.float64(x)) + ", " + str(np.float64(y)) + ", " + str(np.float64(z)) + "], \"pressure\": " + str(np.float64(point.pressure)) + ", \"strength\": " + str(np.float64(point.strength)) + ", \"vertex_color\": [" + str(np.float64(r)) + ", " + str(np.float64(g)) + ", " + str(np.float64(b)) + ", " + str(np.float64(a)) + "]}"
                            elif (precision == 16):
                                pointStr = "\t\t\t\t\t\t\t\t\t\t{\"co\": [" + str(np.float16(x)) + ", " + str(np.float16(y)) + ", " + str(np.float16(z)) + "], \"pressure\": " + str(np.float16(point.pressure)) + ", \"strength\": " + str(np.float16(point.strength)) + ", \"vertex_color\": [" + str(np.float16(r)) + ", " + str(np.float16(g)) + ", " + str(np.float16(b)) + ", " + str(np.float16(a)) + "]}"
                            else:
                                pointStr = "\t\t\t\t\t\t\t\t\t\t{\"co\": [" + str(np.float32(x)) + ", " + str(np.float32(y)) + ", " + str(np.float32(z)) + "], \"pressure\": " + str(np.float32(point.pressure)) + ", \"strength\": " + str(np.float32(point.strength)) + ", \"vertex_color\": [" + str(np.float32(r)) + ", " + str(np.float32(g)) + ", " + str(np.float32(b)) + ", " + str(np.float32(a)) + "]}"
                                          
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
        s.append("\t\"version\": " + str(self.version) + ",")
        s.append("\t\"precision\": " + str(precision) + ",")
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
        
        leastValArray = [ allX[0], allY[0], allZ[0] ]
        mostValArray = [ allX[len(allX)-1], allY[len(allY)-1], allZ[len(allZ)-1] ]
        leastValArray.sort()
        mostValArray.sort()
        leastVal = leastValArray[0]
        mostVal = mostValArray[2]
        valRange = mostVal - leastVal
        
        xRange = (allX[len(allX)-1] - allX[0]) / valRange
        yRange = (allY[len(allY)-1] - allY[0]) / valRange
        zRange = (allZ[len(allZ)-1] - allZ[0]) / valRange
        
        minValX = minVal * xRange
        minValY = minVal * yRange
        minValZ = minVal * zRange
        maxValX = maxVal * xRange
        maxValY = maxVal * yRange
        maxValZ = maxVal * zRange
        
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
        
        weight = 18
        scale = 1.0 / (weight + 2)
        lower = 0
        upper = 0
        center = 0
        
        for i in range(1, len(points) - 2):
            lower = points[i-1].co
            center = points[i].co
            upper = points[i+1].co
            
            x = (lower[0] + weight * center[0] + upper[0]) * scale
            y = (lower[1] + weight * center[1] + upper[1]) * scale
            z = (lower[2] + weight * center[2] + upper[2]) * scale
            stroke.points[i].co = (x, y, z) #center = (x, y, z)
        
    def splitStroke(self, stroke): 
        points = stroke.points
        
        for i in range(1, len(points), 2):
            center = (points[i].co[0], points[i].co[1], points[i].co[2])
            lower = (points[i-1].co[0], points[i-1].co[1], points[i-1].co[2])
            x = (center[0] + lower[0]) / 2
            y = (center[1] + lower[1]) / 2
            z = (center[2] + lower[2]) / 2
            p = (x, y, z)
            
            pressure = (points[i-1].pressure + points[i].pressure) / 2
            strength = (points[i-1].strength + points[i].strength) / 2
            
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
                    
                    for i in range(0, splitReps):
                        self.splitStroke(stroke)  
                        self.smoothStroke(stroke)  
                    
                    for i in range(0, smoothReps - splitReps):
                        self.smoothStroke(stroke)
                    
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
        '''
        range1 = max1 - min1
        range2 = max2 - min2
        valueScaled = float(value - min1) / float(range1)
        return min2 + (valueScaled * range2)
        '''
        return np.interp(value,[min1, max1],[min2, max2])

    def remapInt(self, value, min1, max1, min2, max2):
        return int(self.remap(value, min1, max1, min2, max2))

    def scale_numpy_array(arr, min_v, max_v):
        new_range = (min_v, max_v)
        max_range = max(new_range)
        min_range = min(new_range)

        scaled_unit = (max_range - min_range) / (np.max(arr) - np.min(arr))
        return arr * scaled_unit - np.min(arr) * scaled_unit + min_range

    def countAllFrames(self):
        returns = 0
        for layer in self.layers:
            returns += len(layer.frames)
        return returns

    def countAllStrokes(self):
        returns = 0
        for layer in self.layers:
            for frame in layer.frames:
                returns += len(frame.strokes)
        return returns

    def countAllPoints(self):
        returns = 0
        for layer in self.layers:
            for frame in layer.frames:
                for stroke in frame.strokes:
                    returns += len(stroke.points)
        return returns

    def getAllPoints(self, vertsOnly=True):
        returns = []
        for layer in self.layers:
            for frame in layer.frames:
                for stroke in frame.strokes:
                    for point in stroke.points:
                        if (vertsOnly == True):
                            returns.append(point.co)
                        else:
                            returns.append(point)
        return np.array(returns)

    def getBounds(self):
        points = self.getAllPoints()
        
        minX = np.min(points[:, 0])
        maxX = np.max(points[:, 0])

        minY = np.min(points[:, 1])
        maxY = np.max(points[:, 1])

        minZ = np.min(points[:, 2])
        maxZ = np.max(points[:, 2])

        return minX, maxY, minY, maxY, minZ, maxZ

    def changeExtension(_url, _newExt):
        returns = ""
        returnsPathArray = _url.split(".")
        for i in range(0, len(returnsPathArray)-1):
            returns += returnsPathArray[i]
        returns += _newExt
        return returns
    
    def writeTextFile(self, name="test.txt", lines=None):
        file = open(name,"w") 
        for line in lines:
            file.write(line) 
        file.close() 

    def readTextFile(self, name="text.txt"):
        file = open(name, "r") 
        return file.read() 

    def readTiltBrush(self, filepath=None, vertSkip=1):
        globalScale = (0.1, 0.1, 0.1)
        globalOffset = (0, 0, 0)
        useScaleAndOffset = True

        filetype = self.getExtFromFileName(filepath)

        if (filetype == "tilt" or filetype == "zip"): # Tilt Brush binary file with original stroke data
            t = Tilt(filepath)
            
            layer = LatkLayer(name="TiltBrush")
            frame = LatkFrame()
            
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
                        
                        x = point[0]
                        y = point[2]
                        z = point[1]
                        if useScaleAndOffset == True:
                            x = (x * globalScale[0]) + globalOffset[0]
                            y = (y * globalScale[1]) + globalOffset[1]
                            z = (z * globalScale[2]) + globalOffset[2]
                        pointGroup.append((x, y, z, pressure, strength))
                        
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
            
            with open(filepath) as data_file: 
                data = json.load(data_file)
            
            layer = LatkLayer(name="TiltBrush")
            frame = LatkFrame()
            
            for strokeJson in data["strokes"]:
                strokeColor = (0,0,0)
                try:
                    colorGroup = tiltBrushJson_DecodeData(strokeJson["c"], "c")
                    strokeColor = (colorGroup[0][0], colorGroup[0][1], colorGroup[0][2])
                except:
                    pass
                
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
    

class LatkFrame(object):   
    def __init__(self, strokes=None, frame_number=0): 
        if not strokes:
        	self.strokes = [] # LatkStroke
        else:
        	self.strokes = strokes
        self.frame_number = frame_number
        self.parent_location = (0.0,0.0,0.0)
        

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


class LatkPoint(object):
    def __init__(self, co, pressure=1.0, strength=1.0, vertex_color=(0.0, 0.0, 0.0, 0.0)): # args float tuple, float, float
        self.co = co
        self.pressure = pressure
        self.strength = strength
        self.vertex_color = vertex_color
        self.distance = -1
        self.index = -1
    
