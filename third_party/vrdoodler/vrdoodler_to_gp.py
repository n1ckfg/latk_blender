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

'''
VRDoodler license info:
CREATIVE COMMONS
Attribution-NonCommercial-ShareAlike 4.0 International (CC BY-NC-SA 4.0)
https://creativecommons.org/licenses/by-nc-sa/4.0/
'''

import os
import pprint
import sys

'''
try:
    sys.path.append(os.path.join(os.path.dirname(os.path.dirname(
        os.path.abspath(__file__))), 'Python'))
    from tiltbrush.tilt import Tilt
except ImportError:
    print >>sys.stderr, "Please put the 'Python' directory in your PYTHONPATH"
    sys.exit(1)
'''

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

    globalScale = (-0.01, 0.01, 0.01)
    globalOffset = (0, 0, 0)
    useScaleAndOffset = True
    numPlaces = 7
    roundValues = True
    # ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~
    sg = "{" + "\n"
    sg += "    \"creator\": \"vrdoodler\"," + "\n"
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
                        sb += "                                        {\"co\": [" + roundVal(x, numPlaces) + ", " + roundVal(y, numPlaces) + ", " + roundVal(z, numPlaces) + "]"
                    else:
                        sb += "                                        {\"co\": [" + str(x) + ", " + str(y) + ", " + str(z) + "]"                  
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
        sf += "                    \"name\": \"" + "VRDoodler_Layer" + "\"," + "\n"
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
    
    url = filename + ".json"
    with open(url, "w") as f:
        f.write(sg)
        f.closed
        print("Wrote " + url)    

if __name__ == '__main__':
    main()
