def testStroke():
    gp = getActiveGp()
    palette = getActivePalette()
    color = getActiveColor()
    color.color = (1.0, 10.0, 0.0)
    layer = gp.layers.new("TestLayer")
    frame = layer.frames.new(bpy.context.scene.frame_current)
    stroke = frame.strokes.new(color.name)
    stroke.draw_mode = "3DSPACE"
    stroke.points.add(2)
    createPoint(stroke, 0, (0,0,0))
    createPoint(stroke, 1, (100,100,0))

def testJson():
    readFilePath = "/Users/nick/Projects/animations/"
    readFileName = "new_test.json"
    with open(readFilePath + readFileName) as data_file:    
        data = json.load(data_file)
        print("Read " + str(len(data["grease_pencil"][0]["layers"][0]["frames"])) + " frames on first layer.")
        print("First color: " + str(data["grease_pencil"][0]["layers"][0]["frames"][0]["strokes"][0]["color"]))
        print("First point: " + str(data["grease_pencil"][0]["layers"][0]["frames"][0]["strokes"][0]["points"][0]))

# ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~
# ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~
# shortcuts

# * * * * * * * * * * * * * * * * * * * * * * * * * *
# * * * * * * * * * * * * * * * * * * * * * * * * * *
# * * * * * * * * * * * * * * * * * * * * * * * * * *

