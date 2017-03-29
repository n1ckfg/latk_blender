#!/usr/bin/env python

'''
The Lightning Artist Toolkit was developed with support from:
   Canada Council on the Arts
   Eyebeam Art + Technology Center
   Ontario Arts Council
   Toronto Arts Council
   
Copyright (c) 2016 Nick Fox-Gieg
http://fox-gieg.com
'''

# Tilt Brush license info:
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

"""This is sample Python 2.7 code that uses the tiltbrush.tilt module
to view raw Tilt Brush data."""

import os
import pprint
import sys

try:
    sys.path.append(os.path.join(os.path.dirname(os.path.dirname(
        os.path.abspath(__file__))), 'Python'))
    from tiltbrush.tilt import Tilt
except ImportError:
    print >>sys.stderr, "Please put the 'Python' directory in your PYTHONPATH"
    sys.exit(1)
    
def dump_sketch(sketch, filename):
    globalScale = (-0.01, 0.01, 0.01)
    globalOffset = (0, 0, 0)
    useScaleAndOffset = True
    numPlaces = 7
    roundValues = True
    # ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~
    sg = "{" + "\n"
    sg += "    \"creator\": \"tiltbrush\"," + "\n"
    sg += "    \"grease_pencil\": [" + "\n"
    sg += "        {" + "\n"
    sg += "            \"layers\": [" + "\n"
    sl = ""
    for f in range(0, 1): #layers
        sb = ""
        #layer = gp.layers[f]
        for h in range(0, 1): #frames
            currentFrame = h
            #goToFrame(h)
            sb += "                        {" + "\n" # one frame
            #sb += "                           \"index\": " + str(h) + ",\n"
            sb += "                            \"strokes\": [" + "\n"
            sb += "                                {" + "\n" # one stroke
            for i in range(0, len(sketch.strokes)):
            	stroke = sketch.strokes[i]
            	#vertGroupRaw = decodeData(data["strokes"][i]["v"], "v")
            	#colorGroup = decodeData(data["strokes"][i]["c"], "c")
            	#vertGroup = []
            	# hack that only approximates original position
            	'''
            	for j in range(0, len(vertGroupRaw), 3):
            		if (checkForZero(vertGroupRaw[j+1])==False):
            			vertGroup.append(vertGroupRaw[j+1])
            	'''
            	#for j in range(0, len(vertGroupRaw), 3):
            		#if (checkForZero(vertGroupRaw[j+2])==False):
            			#vertGroup.append(vertGroupRaw[j+2])

                color = (0,0,0)
                try:
                    color = (stroke.brush_color[0], stroke.brush_color[1], stroke.brush_color[2])
                except:
                    pass
                if roundValues == True:
                	sb += "                                    \"color\": [" + str(roundVal(color[0], numPlaces)) + ", " + str(roundVal(color[1], numPlaces)) + ", " + str(roundVal(color[2], numPlaces)) + "]," + "\n"
                else:
                	sb += "                                    \"color\": [" + str(color[0]) + ", " + str(color[1]) + ", " + str(color[2]) + "]," + "\n"
                sb += "                                    \"points\": [" + "\n"
                for j in range(0, len(stroke.controlpoints)):
                    x = 0.0
                    y = 0.0
                    z = 0.0
                    #~
                    point = stroke.controlpoints[j].position
                    pressure = 1.0
                    strength = 1.0
                    try:
                        pressure = stroke.controlpoints[j].extension[0]
                        strength = pressure
                    except:
                        pass
                    #~
                    if useScaleAndOffset == True:
                        x = (point[0] * globalScale[0]) + globalOffset[0]
                        y = (point[1] * globalScale[1]) + globalOffset[1]
                        z = (point[2] * globalScale[2]) + globalOffset[2]
                    else:
                        x = point[0]
                        y = point[1]
                        z = point[2]
                    #~
                    if roundValues == True:
                        sb += "                                        {\"co\": [" + roundVal(x, numPlaces) + ", " + roundVal(y, numPlaces) + ", " + roundVal(z, numPlaces) + "], \"pressure\": " + str(float(roundVal(pressure, numPlaces))) + ", \"strength\": " + str(float(roundVal(strength, numPlaces)))
                    else:
                        sb += "                                        {\"co\": [" + str(x) + ", " + str(y) + ", " + str(z) + "], \"pressure\": " + str(pressure) + ", \"strength\": " + str(strength)                  
                    #~
                    if j == len(stroke.controlpoints) - 1:
                        sb += "}" + "\n"
                        sb += "                                    ]" + "\n"
                        if (i == len(sketch.strokes) - 1):
                            sb += "                                }" + "\n" # last stroke for this frame
                        else:
                            sb += "                                }," + "\n" # end stroke
                            sb += "                                {" + "\n" # begin stroke
                    else:
                        sb += "}," + "\n"
                if i == len(sketch.strokes) - 1:
                    sb += "                            ]" + "\n"
            #if h == len(layer.frames) - 1:
            sb += "                        }" + "\n"
            #else:
                #sb += "                        }," + "\n"
        #~
        sf = "                {" + "\n" 
        sf += "                    \"name\": \"" + "TiltBrush_Layer" + "\"," + "\n"
        sf += "                    \"frames\": [" + "\n" + sb + "                    ]" + "\n"
        #if (f == len(gp.layers)-1):
        sf += "                }" + "\n"
        #else:
            #sf += "                }," + "\n"
        sl += sf
        #~
    sg += sl
    sg += "            ]" + "\n"
    sg += "        }"+ "\n"
    sg += "    ]"+ "\n"
    sg += "}"+ "\n"
	# ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~
    """Prints out some rough information about the strokes.
    Pass a tiltbrush.tilt.Sketch instance."""
    '''
    cooky, version, unused = sketch.header[0:3]
    '''
    #output += 'Cooky:0x%08x    Version:%s    Unused:%s    Extra:(%d bytes)' % (
        #cooky, version, unused, len(sketch.additional_header))
    '''
    if len(sketch.strokes):
        stroke = sketch.strokes[0]    # choose one representative one
        def extension_names(lookup):
            # lookup is a dict mapping name -> idx
            extensions = sorted(lookup.items(), key=lambda (n,i): i)
            return ', '.join(name for (name, idx) in extensions)
        #output += "Stroke Ext: %s" % extension_names(stroke.stroke_ext_lookup)
        #if len(stroke.controlpoints):
            #output += "CPoint Ext: %s" % extension_names(stroke.cp_ext_lookup)
    '''
    '''
    for (i, stroke) in enumerate(sketch.strokes):
        #output += "%3d: " % i,
        output += dump_stroke(stroke)
    '''
    
    url = filename + ".json"
    with open(url, "w") as f:
        f.write(sg)
        f.closed
        print("Wrote " + url)

def dump_stroke(stroke):
    strokeOutput = ""
    """Prints out some information about the stroke."""
    if len(stroke.controlpoints) and 'timestamp' in stroke.cp_ext_lookup:
        cp = stroke.controlpoints[0]
        for i in range(0, len(stroke.controlpoints)):
        	strokeOutput += str(i) + ". " + str(stroke.controlpoints[i].position) + "\n"
        timestamp = stroke.cp_ext_lookup['timestamp']
        start_ts = ' t:%6.1f' % (cp.extension[timestamp] * .001)
    else:
        start_ts = ''

    try:
        scale = stroke.extension[stroke.stroke_ext_lookup['scale']]
    except KeyError:
        scale = 1

    strokeOutput += "Brush: %2d    Size: %.3f    Color: #%02X%02X%02X %s    [%4d]" % (
        stroke.brush_idx, stroke.brush_size * scale,
        int(stroke.brush_color[0] * 255),
        int(stroke.brush_color[1] * 255),
        int(stroke.brush_color[2] * 255),
        #stroke.brush_color[3],
        start_ts,
        len(stroke.controlpoints))
    return strokeOutput + "\n"

def rgbIntToTuple(rgbint, normalized=False):
    rgbVals = [ rgbint // 256 // 256 % 256, rgbint // 256 % 256, rgbint % 256 ]
    if (normalized == True):
    	for i in range(0, len(rgbVals)):
    		c = float(rgbVals[i]) / 255.0
    		rgbVals[i] = c;
    return (rgbVals[2], rgbVals[1], rgbVals[0])

def roundVal(a, b):
    formatter = "{0:." + str(b) + "f}"
    return formatter.format(a)

def checkForZero(v):
	hitRange = 0.005
	if (abs(v[0]) < hitRange and abs(v[1]) < hitRange and abs(v[2]) < hitRange):
		return True
	else:
		return False

def main():
    import argparse
    parser = argparse.ArgumentParser(description="View information about a .tilt")
    parser.add_argument('--strokes', action='store_true', help="Dump the sketch strokes")
    parser.add_argument('--metadata', action='store_true', help="Dump the metadata")
    parser.add_argument('files', type=str, nargs='+', help="Files to examine")

    args = parser.parse_args()
    if not (args.strokes or args.metadata):
        print "You should pass at least one of --strokes or --metadata"

    for filename in args.files:
        t = Tilt(filename)
        if args.strokes:
            dump_sketch(t.sketch, filename)
        if args.metadata:
            pprint.pprint(t.metadata)

if __name__ == '__main__':
    main()
