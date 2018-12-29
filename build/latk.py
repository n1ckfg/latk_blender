'''
The Lightning Artist Toolkit was developed with support from:
   Canada Council on the Arts
   Eyebeam Art + Technology Center
   Ontario Arts Council
   Toronto Arts Council
   
Copyright (c) 2018 Nick Fox-Gieg
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
import zipfile
from io import BytesIO
from math import sqrt

# * * * * * * * * * * * * * * * * * * * * * * * * * *

class Latk(object):     
    def __init__(self, fileName=None, latks=None, points=None, color=None): # args string, Latk array, float tuple array, float tuple           
        self.layers = [] # LatkLayer

        if (fileName==None and latks==None and points==None): # new empty Latk
            self.layers.append(LatkLayer())
            self.layers[0].frames.append(LatkFrame())
        elif (fileName==None and latks!=None and points==None): # merge Latk array
            pass # TODO read multiple times without clearing
        elif (fileName==None and latks==None and points!=None): # 
            self.layers.append(LatkLayer())
            self.layers[0].frames.append(LatkFrame())
            
            stroke = LatkStroke(_pts, _c)
            self.layers[0].frames[0].strokes.append(stroke)
        else: # load from url
            self.read(fileName, True)

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

    def read(self, fileName, clearExisting=True): # args string, bool
        data = None

        if (clearExisting == True):
            self.layers = []
        
        fileType = self.getExtFromFileName(fileName)
        if (fileType == "latk" or fileType == "zip"):
            imz = InMemoryZip()
            imz.readFromDisk(fileName)
            data = json.loads(imz.files[0].decode("utf-8"))        
        else:
            with open(fileName) as data_file:    
                data = json.load(data_file)
                            
        for jsonGp in data["grease_pencil"]:          
            for jsonLayer in jsonGp["layers"]:
                layer = LatkLayer(jsonLayer["name"])
                
                for jsonFrame in jsonLayer["frames"]:
                    frame = LatkFrame()
                    for jsonStroke in jsonFrame["strokes"]:                       
                        col = (1,1,1)
                        try:
                            r = float(jsonStroke["color"][0])
                            g = float(jsonStroke["color"][1])
                            b = float(jsonStroke["color"][2])
                            col = (r,g,b)
                        except:
                            pass
                        
                        points = []
                        for jsonPoint in jsonStroke["points"]:
                            x = float(jsonPoint["co"][0])
                            y = float(jsonPoint["co"][1])
                            z = float(jsonPoint["co"][2])
                            pressure = 1.0
                            strength = 1.0
                            try:
                                pressure = jsonPoint["pressure"]
                            except:
                                pass
                            try:
                                strength = jsonPoint["strength"]
                            except:
                                pass
                            points.append(LatkPoint((x,y,z), pressure, strength))
                                                
                        stroke = LatkStroke(points, col)
                        frame.strokes.append(stroke)
                    layer.frames.append(frame)
                self.layers.append(layer)

    def write(self, fileName): # args string
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
                    col = stroke.col
                    sbb.append("\t\t\t\t\t\t\t\t\t\"color\": [" + str(col[0]) + ", " + str(col[1]) + ", " + str(col[2]) + "],")

                    if (len(stroke.points) > 0): 
                        sbb.append("\t\t\t\t\t\t\t\t\t\"points\": [")
                        for j, point in enumerate(stroke.points):                                     
                            if (j == len(stroke.points) - 1):
                                sbb.append("\t\t\t\t\t\t\t\t\t\t{\"co\": [" + str(point.co[0]) + ", " + str(point.co[1]) + ", " + str(point.co[2]) + "], \"pressure\":" + str(point.pressure) + ", \"strength\":" + str(point.strength) + "}")
                                sbb.append("\t\t\t\t\t\t\t\t\t]")
                            else:
                                sbb.append("\t\t\t\t\t\t\t\t\t\t{\"co\": [" + str(point.co[0]) + ", " + str(point.co[1]) + ", " + str(point.co[2]) + "], \"pressure\":" + str(point.pressure) + ", \"strength\":" + str(point.strength) + "},")
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
        
        fileType = self.getExtFromFileName(fileName)
        if (fileType == "latk" or fileType == "zip"):
            fileNameNoExt = self.getFileNameNoExt(fileName)
            imz = InMemoryZip()
            imz.append(fileNameNoExt + ".json", "\n".join(s))
            imz.writetofile(fileName)            
        else:
            with open(fileName, "w") as f:
                f.write("\n".join(s))
                f.closed
                             
    def clean(self, cleanMinPoints = 2, cleanMinLength = 0.1):
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

    def smoothStroke(self, stroke):
        points = stroke.points
        #~
        weight = 18
        scale = 1.0 / (weight + 2)
        nPointsMinusTwo = len(points) - 2
        lower = 0
        upper = 0
        center = 0
        #~
        for i in range(1, nPointsMinusTwo):
            lower = points[i-1].co
            center = points[i].co
            upper = points[i+1].co
            #~
            x = (lower[0] + weight * center[0] + upper[0]) * scale
            y = (lower[1] + weight * center[1] + upper[1]) * scale
            z = (lower[2] + weight * center[2] + upper[2]) * scale
            center = (x, y, z)
        
    def splitStroke(self, stroke): 
        points = stroke.points
        co = []
        pressure = []
        strength = []
        #~
        for i in range(1, len(points), 2):
            center = (points[i].co[0], points[i].co[1], points[i].co[2])
            lower = (points[i-1].co[0], points[i-1].co[1], points[i-1].co[2])
            x = (center[0] + lower[0]) / 2
            y = (center[1] + lower[1]) / 2
            z = (center[2] + lower[2]) / 2
            p = (x, y, z)
            #~
            co.append(lower)
            co.append(p)
            co.append(center)
            #~
            pressure.append(points[i-1].pressure)
            pressure.append((points[i-1].pressure + points[i].pressure) / 2)
            pressure.append(points[i].pressure)
            #~
            strength.append(points[i-1].strength)
            strength.append((points[i-1].strength + points[i].strength) / 2)
            strength.append(points[i].strength)
        #~
        for i in range(len(co), len(points)):
            pt = LatkPoint(co[i], pressure[i], strength[i])
            stroke.points.insert(i, pt)

    def refine(self, splitReps=2, smoothReps=10, doClean=True):
        if (doClean==True):
            self.clean()
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

    def setStroke(self, stroke):
        lastLayer = self.layers[len(self.layers)-1]
        lastFrame = lastLayer.frames[len(lastLayer.frames)-1]
        lastFrame.strokes.append(stroke)

    def setPoints(self, points, col=None):
        lastLayer = self.layers[len(self.layers)-1]
        lastFrame = lastLayer.frames[len(lastLayer.frames)-1]
        stroke = LatkStroke()
        stroke.setPoints(points)
        if (col != None):
            stroke.col = col
        lastFrame.strokes.append(stroke)
    
    def getDistance(self, v1, v2):
        return sqrt( (v1[0] - v2[0])**2 + (v1[1] - v2[1])**2 + (v1[2] - v2[2])**2)

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

    def writeTextFile(self, name="test.txt", lines=None):
        file = open(name,"w") 
        for line in lines:
            file.write(line) 
        file.close() 

    def readTextFile(self, name="text.txt"):
        file = open(name, "r") 
        return file.read() 

# ~ ~ ~ ~ ~ ~ ~ ~ ~ ~

class LatkLayer(object):    
    def __init__(self, name=None): 
        if not name:
            name = "layer"   
        self.frames = [] # LatkFrame
        self.name = name
    
# ~ ~ ~ ~ ~ ~ ~ ~ ~ ~

class LatkFrame(object):   
    def __init__(self):    
        self.strokes = [] # LatkStroke
        
# ~ ~ ~ ~ ~ ~ ~ ~ ~ ~

class LatkStroke(object):       
    def __init__(self, points=None, col=(1.0,1.0,1.0)): # args float tuple array, float tuple 
        self.points = points
        self.col = col

    def setPoints(self, points, col=None):
        self.points = []
        for point in points:
            self.points.append(LatkPoint(point))
        if (col != None):
            self.col = col

    def getPoints(self):
        returns = []
        for point in self.points:
            returns.append(point.co)
        return returns

# ~ ~ ~ ~ ~ ~ ~ ~ ~ ~

class LatkPoint(object):
    def __init__(self, co, pressure=1.0, strength=1.0): # args float tuple, float, float
        self.co = co
        self.pressure = pressure
        self.strength = strength
    
# * * * * * * * * * * * * * * * * * * * * * * * * * *

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
# * * * * * * * * * * * * * * * * * * * * * * * * * *
# * * * * * * * * * * * * * * * * * * * * * * * * * *

