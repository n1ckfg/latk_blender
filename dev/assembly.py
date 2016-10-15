def assembleMesh():
    origFileName = getFileName()
    masterUrlList = []
    masterGroupList = []
    #~
    #start = bpy.context.scene.frame_start
    #end = bpy.context.scene.frame_end + 1
    #~
    pencil = getActiveGp()
    palette = getActivePalette()
    #~
    for b in range(0, len(pencil.layers)):
        layer = pencil.layers[b]
        url = origFileName + "_layer" + str(b+1) + "_" + layer.info
        masterGroupList.append(layer.info)
        masterUrlList.append(url)
    #~
    #openFile(origFileName)
    readyToSave = True
    for i in range(0, len(masterUrlList)):
        try:
            importGroup(getFilePath() + masterUrlList[i] + ".blend", masterGroupList[i], winDir=True)
            print("Imported group " + masterGroupList[i] + ", " + str(i+1) + " of " + str(len(masterGroupList)))
        except:
            readyToSave = False
            print("Error importing group " + masterGroupList[i] + ", " + str(i+1) + " of " + str(len(masterGroupList)))
    if (readyToSave==True):
        saveFile(origFileName + "_ASSEMBLY")
        print(origFileName + "_ASSEMBLY.blend" + " saved.")
    else:
        print(origFileName + "_ASSEMBLY.blend" + " was not saved because some groups were missing.")
