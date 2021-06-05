# 10 of 12. UI

class LightningArtistToolkitPreferences(bpy.types.AddonPreferences):
    bl_idname = __name__
    
    '''
    extraFormats_TiltBrush = bpy.props.BoolProperty(
        name = 'Tilt Brush',
        description = "Tilt Brush import",
        default = True
    )
    '''

    extraFormats_GML = bpy.props.BoolProperty(
        name = 'GML',
        description = "Graffiti Markup Language import/export",
        default = False
    )

    '''
    extraFormats_ASC = bpy.props.BoolProperty(
        name = 'ASC Point Cloud',
        description = "ASC point cloud import/export",
        default = True
    )
    '''

    extraFormats_Painter = bpy.props.BoolProperty(
        name = 'Corel Painter',
        description = "Corel Painter script import/export",
        default = False
    )

    extraFormats_SVG = bpy.props.BoolProperty(
        name = 'SVG',
        description = "SVG import/export",
        default = True
    )

    extraFormats_Norman = bpy.props.BoolProperty(
        name = 'NormanVR',
        description = "NormanVR import",
        default = False
    )

    extraFormats_VRDoodler = bpy.props.BoolProperty(
        name = 'VRDoodler',
        description = "VRDoodler import",
        default = False
    )

    extraFormats_FBXSequence = bpy.props.BoolProperty(
        name = 'Sketchfab FBX Sequence',
        description = "FBX Sequence export",
        default = True
    )

    extraFormats_SculptrVR = bpy.props.BoolProperty(
        name = 'SculptrVR CSV',
        description = "SculptrVR CSV import/export",
        default = True
    )

    extraFormats_AfterEffects = bpy.props.BoolProperty(
        name = 'After Effects JSX',
        description = "After Effects JSX export",
        default = False
    )

    extraFormats_UnrealXYZ = bpy.props.BoolProperty(
        name = 'Unreal XYZ Point Cloud',
        description = "Color point cloud for Unreal",
        default = True
    )

    def draw(self, context):
        layout = self.layout
        layout.label("Add menu items to import:")
        #layout.prop(self, "extraFormats_TiltBrush")
        layout.prop(self, "extraFormats_SculptrVR")
        #layout.prop(self, "extraFormats_ASC")
        layout.prop(self, "extraFormats_GML")
        layout.prop(self, "extraFormats_Painter")
        layout.prop(self, "extraFormats_SVG")
        layout.prop(self, "extraFormats_Norman")
        layout.prop(self, "extraFormats_VRDoodler")
        #~
        layout.label("Add menu items to export:")
        layout.prop(self, "extraFormats_SculptrVR")
        #layout.prop(self, "extraFormats_ASC")
        layout.prop(self, "extraFormats_GML")
        layout.prop(self, "extraFormats_Painter")
        layout.prop(self, "extraFormats_SVG")
        layout.prop(self, "extraFormats_AfterEffects")
        layout.prop(self, "extraFormats_FBXSequence")
        layout.prop(self, "extraFormats_UnrealXYZ")

# ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~
# LATK IMPORT 

class ImportLatk(bpy.types.Operator, ImportHelper):
    """Load a Latk File"""
    resizeTimeline = BoolProperty(name="Resize Timeline", description="Set in and out points", default=True)
    useScaleAndOffset = BoolProperty(name="Use Scale and Offset", description="Compensate scale for Blender viewport", default=True)
    doPreclean = BoolProperty(name="Pre-Clean", description="Try to remove duplicate strokes and points", default=False)
    cleanFactor = FloatProperty(name="Clean Factor", description="Strength of clean method", default=0.01)
    clearExisting = BoolProperty(name="Clear Existing", description="Delete existing Grease Pencil strokes", default=False)
    limitPalette = IntProperty(name="Limit Palette", description="Restrict number of colors (0 = unlimited)", default=256)

    bl_idname = "import_scene.latk"
    bl_label = "Import Latk"
    bl_options = {'PRESET', 'UNDO'}

    filename_ext = ".json"
    filter_glob = StringProperty(
            default="*.latk;*.json",
            options={'HIDDEN'},
            )

    def execute(self, context):
        import latk_blender as la
        keywords = self.as_keywords(ignore=("axis_forward", "axis_up", "filter_glob", "split_mode", "resizeTimeline", "doPreclean", "limitPalette", "useScaleAndOffset", "clearExisting", "cleanFactor")) 
        if bpy.data.is_saved:
            import os
        #~
        keywords["resizeTimeline"] = self.resizeTimeline
        keywords["useScaleAndOffset"] = self.useScaleAndOffset
        keywords["doPreclean"] = self.doPreclean
        keywords["limitPalette"] = self.limitPalette
        keywords["clearExisting"] = self.clearExisting
        keywords["cleanFactor"] = self.cleanFactor
        la.readBrushStrokes(**keywords)
        return {'FINISHED'}

# ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~
# LATK EXPORT 

class ExportLatkJson(bpy.types.Operator, ExportHelper): # TODO combine into one class
    """Save a Latk Json File"""

    bake = BoolProperty(name="Bake Frames", description="Bake Keyframes to All Frames", default=False)
    #roundValues = BoolProperty(name="Limit Precision", description="Round Values to Reduce Filesize", default=False)    
    #numPlaces = IntProperty(name="Number Places", description="Number of Decimal Places", default=7)
    useScaleAndOffset = BoolProperty(name="Use Scale and Offset", description="Compensate scale for Blender viewport", default=True)

    bl_idname = "export_scene.latkjson"
    bl_label = 'Export Latk Json'
    bl_options = {'PRESET'}

    filename_ext = ".json"

    filter_glob = StringProperty(
            default="*.json",
            options={'HIDDEN'},
            )

    def execute(self, context):
        import latk_blender as la
        keywords = self.as_keywords(ignore=("axis_forward", "axis_up", "filter_glob", "split_mode", "check_existing", "bake", "useScaleAndOffset")) #, "roundValues", "numPlaces"))
        if bpy.data.is_saved:
            import os
        #~
        keywords["bake"] = self.bake
        #keywords["roundValues"] = self.roundValues
        #keywords["numPlaces"] = self.numPlaces
        keywords["useScaleAndOffset"] = self.useScaleAndOffset
        #~
        la.writeBrushStrokes(**keywords, zipped=False)
        return {'FINISHED'}

class ExportLatk(bpy.types.Operator, ExportHelper):  # TODO combine into one class
    """Save a Latk File"""

    bake = BoolProperty(name="Bake Frames", description="Bake Keyframes to All Frames", default=False)
    #roundValues = BoolProperty(name="Limit Precision", description="Round Values to Reduce Filesize", default=False)    
    #numPlaces = IntProperty(name="Number Places", description="Number of Decimal Places", default=7)
    useScaleAndOffset = BoolProperty(name="Use Scale and Offset", description="Compensate scale for Blender viewport", default=True)

    bl_idname = "export_scene.latk"
    bl_label = 'Export Latk'
    bl_options = {'PRESET'}

    filename_ext = ".latk"

    filter_glob = StringProperty(
            default="*.latk",
            options={'HIDDEN'},
            )

    def execute(self, context):
        import latk_blender as la
        keywords = self.as_keywords(ignore=("axis_forward", "axis_up", "filter_glob", "split_mode", "check_existing", "bake", "useScaleAndOffset")) #, "roundValues", "numPlaces"))
        if bpy.data.is_saved:
            import os
        #~
        keywords["bake"] = self.bake
        #keywords["roundValues"] = self.roundValues
        #keywords["numPlaces"] = self.numPlaces
        keywords["useScaleAndOffset"] = self.useScaleAndOffset
        #~
        la.writeBrushStrokes(**keywords, zipped=True)
        return {'FINISHED'}

# ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~
# ...MORE IMPORT 

class ImportTiltBrush(bpy.types.Operator, ImportHelper):
    """Load a Tilt Brush File"""
    bl_idname = "import_scene.tbjson"
    bl_label = "Import Tilt Brush"
    bl_options = {'PRESET', 'UNDO'}

    filename_ext = ".json"
    filter_glob = StringProperty(
            default="*.tilt;*.json",
            options={'HIDDEN'},
            )

    vertSkip = IntProperty(name="Read Vertices", description="Read every n vertices", default=1)

    def execute(self, context):
        import latk_blender as la
        keywords = self.as_keywords(ignore=("axis_forward", "axis_up", "filter_glob", "split_mode"))
        if bpy.data.is_saved:
            import os
        #~
        keywords["vertSkip"] = self.vertSkip
        la.importTiltBrush(**keywords)
        return {'FINISHED'} 


class ImportNorman(bpy.types.Operator, ImportHelper):
    """Load a Norman File"""
    bl_idname = "import_scene.norman"
    bl_label = "Import Norman"
    bl_options = {'PRESET', 'UNDO'}

    filename_ext = ".json"
    filter_glob = StringProperty(
            default="*.json",
            options={'HIDDEN'},
            )

    def execute(self, context):
        import latk_blender as la
        keywords = self.as_keywords(ignore=("axis_forward", "axis_up", "filter_glob", "split_mode"))
        if bpy.data.is_saved:
            import os
        #~
        la.importNorman(**keywords)
        return {'FINISHED'} 


class ImportVRDoodler(bpy.types.Operator, ImportHelper):
    """Load a VRDoodler File"""
    bl_idname = "import_scene.vrdoodler"
    bl_label = "Import VRDoodler"
    bl_options = {'PRESET', 'UNDO'}

    filename_ext = ".obj"
    filter_glob = StringProperty(
            default="*.obj",
            options={'HIDDEN'},
            )

    def execute(self, context):
        import latk_blender as la
        keywords = self.as_keywords(ignore=("axis_forward", "axis_up", "filter_glob", "split_mode"))
        if bpy.data.is_saved:
            import os
        #~
        la.importVRDoodler(**keywords)
        return {'FINISHED'} 

class ImportSvg(bpy.types.Operator, ImportHelper):
    """Load an SVG image to Grease Pencil"""
    useScaleAndOffset = BoolProperty(name="Use Scale and Offset", description="Compensate scale for Blender viewport", default=True)
    doPreclean = BoolProperty(name="Pre-Clean", description="Try to remove duplicate strokes and points", default=True)
    cleanFactor = FloatProperty(name="Clean Factor", description="Strength of clean method", default=0.001)

    bl_idname = "import_scene.svg"
    bl_label = "Import SVG"
    bl_options = {'PRESET', 'UNDO'}

    filename_ext = ".svg"
    filter_glob = StringProperty(
            default="*.svg",
            options={'HIDDEN'},
            )

    def execute(self, context):
        import latk_blender as la
        keywords = self.as_keywords(ignore=("axis_forward", "axis_up", "filter_glob", "split_mode", "useScaleAndOffset", "doPreclean", "cleanFactor"))
        if bpy.data.is_saved:
            import os
        keywords["useScaleAndOffset"] = self.useScaleAndOffset
        keywords["doPreclean"] = self.doPreclean
        keywords["cleanFactor"] = self.cleanFactor            
        #~
        la.load_svg(**keywords)
        return {'FINISHED'} 

class ImportASC(bpy.types.Operator, ImportHelper):
    """Load an ASC point cloud"""
    bl_idname = "import_scene.asc"
    bl_label = "Import ASC point cloud"
    bl_options = {'PRESET', 'UNDO'}

    filename_ext = ".asc"
    filter_glob = StringProperty(
            default="*.asc;*.xyz",
            options={'HIDDEN'},
            )

    importAsGP = BoolProperty(name="Import as GP", description="Create Grease Pencil strokes instead of vertices", default=True)
    vertexColor = BoolProperty(name="Vertex Colors", description="Use vertex colors per point, instead of stroke colors", default=True)
    strokeLength = IntProperty(name="Points per Stroke", description="Group every n points into strokes", default=10)

    def execute(self, context):
        import latk_blender as la
        keywords = self.as_keywords(ignore=("axis_forward", "axis_up", "filter_glob", "split_mode"))
        if bpy.data.is_saved:
            import os
        #~
        keywords["importAsGP"] = self.importAsGP
        keywords["strokeLength"] = self.strokeLength
        keywords["vertexColor"] = self.vertexColor
        la.importAsc(**keywords)
        return {'FINISHED'} 


class ImportSculptrVR(bpy.types.Operator, ImportHelper):
    """Load an ASC point cloud"""
    bl_idname = "import_scene.sculptrvr"
    bl_label = "Import SculptrVR CSV"
    bl_options = {'PRESET', 'UNDO'}

    filename_ext = ".csv"
    filter_glob = StringProperty(
            default="*.csv",
            options={'HIDDEN'},
            )

    strokeLength = IntProperty(name="Points per Stroke", description="Group every n points into strokes", default=1)

    def execute(self, context):
        import latk_blender as la
        keywords = self.as_keywords(ignore=("axis_forward", "axis_up", "filter_glob", "split_mode"))
        if bpy.data.is_saved:
            import os
        #~
        keywords["strokeLength"] = self.strokeLength
        la.importSculptrVr(**keywords)
        return {'FINISHED'} 


class ImportPainter(bpy.types.Operator, ImportHelper):
    """Load a Painter script"""
    bl_idname = "import_scene.painter"
    bl_label = "Import Painter"
    bl_options = {'PRESET', 'UNDO'}

    filename_ext = ".txt"
    filter_glob = StringProperty(
            default="*.txt",
            options={'HIDDEN'},
            )

    def execute(self, context):
        import latk_blender as la
        keywords = self.as_keywords(ignore=("axis_forward", "axis_up", "filter_glob", "split_mode"))
        if bpy.data.is_saved:
            import os
        #~
        la.importPainter(**keywords)
        return {'FINISHED'} 


class ImportGml(bpy.types.Operator, ImportHelper):
    """Load a GML File"""
    bl_idname = "import_scene.gml"
    bl_label = "Import Gml"
    bl_options = {'PRESET', 'UNDO'}

    filename_ext = ".gml"
    filter_glob = StringProperty(
            default="*.gml",
            options={'HIDDEN'},
            )

    sequenceAnim = BoolProperty(name="Sequence in Time", description="Create a new frame for each stroke", default=False)
    splitStrokes = BoolProperty(name="Split Strokes", description="Split animated strokes to layers", default=False)
                
    def execute(self, context):
        import latk_blender as la
        keywords = self.as_keywords(ignore=("axis_forward", "axis_up", "filter_glob", "split_mode", "splitStrokes", "sequenceAnim"))
        if bpy.data.is_saved:
            import os
        #~
        keywords["splitStrokes"] = self.splitStrokes
        keywords["sequenceAnim"] = self.sequenceAnim
        #~
        la.gmlParser(**keywords)
        return {'FINISHED'} 


# ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~
# ...MORE EXPORT 

class ExportGml(bpy.types.Operator, ExportHelper):
    """Save a GML File"""

    bl_idname = "export_scene.gml"
    bl_label = 'Export Gml'
    bl_options = {'PRESET'}

    filename_ext = ".gml"
    filter_glob = StringProperty(
            default="*.gml",
            options={'HIDDEN'},
            )

    make2d = BoolProperty(name="Make 2D", description="Project Coordinates to Camera View", default=False)

    def execute(self, context):
        import latk_blender as la
        keywords = self.as_keywords(ignore=("axis_forward", "axis_up", "filter_glob", "split_mode", "check_existing"))
        if bpy.data.is_saved:
            import os
        #~
        keywords["make2d"] = self.make2d
        #~
        la.writeGml(**keywords)
        return {'FINISHED'} 


class ExportFbxSequence(bpy.types.Operator, ExportHelper):
    """Save an FBX Sequence"""

    bl_idname = "export_scene.fbx_sequence"
    bl_label = 'Export FBX Sequence'
    bl_options = {'PRESET'}

    filename_ext = ".fbx"
    filter_glob = StringProperty(
            default="*.fbx",
            options={'HIDDEN'},
            )

    sketchFab = BoolProperty(name="Sketchfab List", description="Generate list for Sketchfab animation", default=True)

    def execute(self, context):
        import latk_blender as la
        keywords = self.as_keywords(ignore=("axis_forward", "axis_up", "filter_glob", "split_mode", "check_existing"))
        if bpy.data.is_saved:
            import os
        #~
        keywords["sketchFab"] = self.sketchFab
        #~
        la.exportForUnity(**keywords)
        return {'FINISHED'} 


class ExportSculptrVR(bpy.types.Operator, ExportHelper):
    """Save a SculptrVR CSV"""

    bl_idname = "export_scene.sculptrvr"
    bl_label = 'Export SculptrVR CSV'
    bl_options = {'PRESET'}

    filename_ext = ".csv"
    filter_glob = StringProperty(
            default="*.csv",
            options={'HIDDEN'},
            )

    sphereRadius = FloatProperty(name="Sphere Radius", description="Sphere Radius (min 0.01)", default=10)
    octreeSize = IntProperty(name="Octree Size", description="Octree Size (0-19)", default=7)
    vol_scale = FloatProperty(name="Volume Scale", description="Volume Scale (0-1)", default=0.33)
    mtl_val = IntProperty(name="Material", description="Material Value (127, 254, or 255)", default=255)
    file_format = EnumProperty(
        name="File Format",
        items=(
            ("SPHERE", "Sphere per Voxel", "Recommended", 0),
            ("SINGLE", "Single Voxel", "Single voxel at octree size", 1),
            ("LEGACY", "Legacy Format", "Probably too small to see", 2),
        ),
        default="SPHERE"
    )


    def execute(self, context):
        import latk_blender as la
        keywords = self.as_keywords(ignore=("axis_forward", "axis_up", "filter_glob", "split_mode", "check_existing"))
        if bpy.data.is_saved:
            import os
        #~
        keywords["sphereRadius"] = self.sphereRadius
        keywords["octreeSize"] = self.octreeSize
        keywords["vol_scale"] = self.vol_scale
        keywords["mtl_val"] = self.mtl_val
        keywords["file_format"] = self.file_format
        #~
        la.exportSculptrVrCsv(**keywords)
        return {'FINISHED'} 


class ExportASC(bpy.types.Operator, ExportHelper):
    """Save an ASC point cloud"""

    bl_idname = "export_scene.asc"
    bl_label = 'Export ASC'
    bl_options = {'PRESET'}

    filename_ext = ".asc"
    filter_glob = StringProperty(
            default="*.asc",
            options={'HIDDEN'},
            )

    vertexColor = BoolProperty(name="Vertex Colors", description="Use vertex colors per point, instead of stroke colors", default=True)

    def execute(self, context):
        import latk_blender as la
        keywords = self.as_keywords(ignore=("axis_forward", "axis_up", "filter_glob", "split_mode", "check_existing"))
        if bpy.data.is_saved:
            import os
        #~
        keywords["vertexColor"] = self.vertexColor
        la.exportAsc(**keywords)
        return {'FINISHED'} 

class ExportUnrealXYZ(bpy.types.Operator, ExportHelper):
    """Save an ASC point cloud"""

    bl_idname = "export_scene.xyz"
    bl_label = 'Export Unreal XYZ'
    bl_options = {'PRESET'}

    filename_ext = ".xyz"
    filter_glob = StringProperty(
            default="*.xyz",
            options={'HIDDEN'},
            )

    def execute(self, context):
        import latk_blender as la
        keywords = self.as_keywords(ignore=("axis_forward", "axis_up", "filter_glob", "split_mode", "check_existing"))
        if bpy.data.is_saved:
            import os
        #~
        la.exportXyz(**keywords)
        return {'FINISHED'} 

class ExportSvg(bpy.types.Operator, ExportHelper):
    """Save an SVG SMIL File"""

    bl_idname = "export_scene.svg"
    bl_label = 'Export Svg'
    bl_options = {'PRESET'}

    filename_ext = ".svg"
    filter_glob = StringProperty(
            default="*.svg",
            options={'HIDDEN'},
            )

    def execute(self, context):
        import latk_blender as la
        #keywords = self.as_keywords(ignore=("axis_forward", "axis_up", "filter_glob", "split_mode", "check_existing", "bake"))
        keywords = self.as_keywords(ignore=("axis_forward", "axis_up", "filter_glob", "split_mode", "check_existing"))
        if bpy.data.is_saved:
            import os
        #~
        la.writeSvg(**keywords)
        return {'FINISHED'} 


class ExportAfterEffects(bpy.types.Operator, ExportHelper):
    """Save an After Effects JSX File"""

    bl_idname = "export_scene.aejsx"
    bl_label = 'Export After Effects JSX'
    bl_options = {'PRESET'}

    filename_ext = ".jsx"
    filter_glob = StringProperty(
            default="*.jsx",
            options={'HIDDEN'},
            )

    useNulls = BoolProperty(name="Use 3D Nulls", description="Use nulls to store 3D data in AE", default=False)

    def execute(self, context):
        import latk_blender as la
        #keywords = self.as_keywords(ignore=("axis_forward", "axis_up", "filter_glob", "split_mode", "check_existing", "bake"))
        keywords = self.as_keywords(ignore=("axis_forward", "axis_up", "filter_glob", "split_mode", "check_existing"))
        if bpy.data.is_saved:
            import os
        #~
        keywords["useNulls"] = self.useNulls
        la.writeAeJsx(**keywords)
        return {'FINISHED'} 


class ExportPainter(bpy.types.Operator, ExportHelper):
    """Save a Painter script"""

    bl_idname = "export_scene.painter"
    bl_label = 'Export Painter'
    bl_options = {'PRESET'}

    filename_ext = ".txt"
    filter_glob = StringProperty(
            default="*.txt",
            options={'HIDDEN'},
            )

    def execute(self, context):
        import latk_blender as la
        #keywords = self.as_keywords(ignore=("axis_forward", "axis_up", "filter_glob", "split_mode", "check_existing", "bake"))
        keywords = self.as_keywords(ignore=("axis_forward", "axis_up", "filter_glob", "split_mode", "check_existing"))
        if bpy.data.is_saved:
            import os
        #~
        la.writePainter(**keywords)
        return {'FINISHED'} 


# ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~
# ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~

class LatkProperties(bpy.types.PropertyGroup):
    """Properties for Latk"""
    bl_idname = "GREASE_PENCIL_PT_LatkProperties"

    bakeMesh = BoolProperty(
        name="Bake",
        description="Off: major speedup if you're staying in Blender. On: slower but keeps everything exportable",
        default=True
    )

    joinMesh = BoolProperty(
        name="Join",
        description="Join baked meshes",
        default=True
    )

    minRemapPressure = FloatProperty(
        name="Min",
        description="Minimum Remap Pressure",
        default=0.1
    )

    maxRemapPressure = FloatProperty(
        name="Max",
        description="Maximum Remap Pressure",
        default=1.0
    )

    remapPressureMode = EnumProperty(
        name="Remap Mode",
        items=(
            ("CLAMP_P", "Clamp Pressure", "Clamp pressure values below min or above max", 0),
            ("REMAP_P", "Remap Pressure", "Remap pressure values from 0-1 to min-max", 1),
            ("CLAMP_S", "Clamp Strength", "Clamp strength values below min or above max", 2),
            ("REMAP_S", "Remap Strength", "Remap strength values from 0-1 to min-max", 3)
        ),
        default="REMAP_P"
    )

    saveLayers = BoolProperty(
        name="Layers",
        description="Save every layer to its own file",
        default=False
    )

    thickness = FloatProperty(
        name="Thickness",
        description="Tube mesh thickness",
        default=0.1
    )

    resolution = IntProperty(
        name="Resolution",
        description="Tube mesh resolution",
        default=1
    )

    bevelResolution = IntProperty(
        name="Bevel Resolution",
        description="Tube mesh bevel resolution",
        default=0
    )

    decimate = FloatProperty(
        name="Decimate",
        description="Decimate mesh",
        default=0.1
    )

    strokeLength = IntProperty(
        name="Length",
        description="Group every n points into strokes",
        default=2
    )

    strokeGaps = FloatProperty(
        name="Gaps",
        description="Skip points greater than this distance away",
        default=10.0
    )

    shuffleOdds = FloatProperty(
        name="Odds",
        description="Odds of shuffling the points in a stroke",
        default=1.0
    )

    spreadPoints = FloatProperty(
        name="Spread",
        description="Distance to randomize points",
        default=0.1
    )

    numSplitFrames = IntProperty(
        name="Split Frames",
        description="Split layers if they have more than this many frames",
        default=3,
        soft_min=2
    )

    cleanFactor = FloatProperty(
        name="Clean Factor",
        description="Strength of clean method",
        default=0.1,
        soft_min=0.001,
        soft_max=0.999
    )

    writeStrokeSteps = IntProperty(
        name="Steps",
        description="Write-on steps",
        default=1
    )

    writeStrokePoints = IntProperty(
        name="Points",
        description="Write-on points per step",
        default=10
    )

    paletteLimit = IntProperty(
        name="Palette",
        description="Limit palette to this many colors",
        default=32
    )

    vertexColorName = StringProperty(
        name="VCol",
        description="Vertex color name for export",
        default="rgba"
    )

    remesh_mode = EnumProperty(
        name="Remesh Mode",
        items=(
            ("NONE", "None", "No remeshing curves", 0),
            ("HULL", "Hull", "Hull remesh", 1),
            ("PLANE", "Plane", "Plane remesh", 2),
            ("SHARP", "Sharp", "Sharp remesh", 3),
            ("SMOOTH", "Smooth", "Smooth remesh", 4),
            ("BLOCKS", "Blocks", "Blocks remesh", 5)
        ),
        default="NONE"
    )

    mesh_fill_mode = EnumProperty( 
        name="Fill As",
        items=(
            ("HULL", "Hull", "Hull", 0),
            ("PLANE", "Plane", "Plane", 1)
        ),
        default="HULL"
    )

    material_shader_mode = EnumProperty(
        name="Type",
        items=(
            ("DIFFUSE", "Diffuse", "Diffuse shader", 0),
            ("PRINCIPLED", "Principled", "Principled shader", 1),
            ("GLTF", "glTF", "glTF MR shader", 2),
            #("EMISSION", "Emission", "Emission shader", 3)
        ),
        default="PRINCIPLED"
    )

# https://docs.blender.org/api/blender_python_api_2_78_release/bpy.types.Panel.html
class LatkProperties_Panel(bpy.types.Panel):
    """Creates a Panel in the 3D View context"""
    bl_idname = "GREASE_PENCIL_PT_LatkPropertiesPanel"
    bl_space_type = 'VIEW_3D'
    bl_label = "Lightning Artist Toolkit"
    bl_region_type = 'UI'
    bl_context = "object"

    #def draw_header(self, context):
        #self.layout.prop(context.scene.freestyle_gpencil_export, "enable_latk", text="")

    def draw(self, context):
        layout = self.layout

        scene = context.scene
        latk = scene.latk_settings

        row = layout.row()
        row.operator("latk_button.gpmesh_singleframe")
     
        row = layout.row()
        row.prop(latk, "thickness")
        row.prop(latk, "resolution")

        row = layout.row()
        row.prop(latk, "bevelResolution")
        row.prop(latk, "decimate")

        row = layout.row()
        row.operator("latk_button.gpmesh")
        row.operator("latk_button.dn")

        row = layout.row()
        row.prop(latk, "bakeMesh")
        row.prop(latk, "joinMesh")
        row.prop(latk, "saveLayers")
        row.prop(latk, "paletteLimit")
        row.prop(latk, "vertexColorName")
        
        row = layout.row()
        row.prop(latk, "remesh_mode", expand=True)

        # ~ ~ ~ 

        row = layout.row()
        row.prop(latk, "mesh_fill_mode")
        row.prop(latk, "material_shader_mode")
        row.operator("latk_button.mtlshader")
        
        row = layout.row()
        row.operator("latk_button.booleanmod") 
        row.operator("latk_button.booleanmodminus") 
        row.operator("latk_button.simpleclean")

        row = layout.row()
        row.operator("latk_button.smoothmod") 
        row.operator("latk_button.subsurfmod") 
        row.operator("latk_button.decimatemod") 

        row = layout.row()
        row.operator("latk_button.bakeall")
        row.operator("latk_button.bakeanim")
        row.operator("latk_button.scopetimeline") 

        row = layout.row()
        row.operator("latk_button.hidetrue") 
        row.operator("latk_button.hidescale")
        row.operator("latk_button.makeloop") 

        row = layout.row()
        row.operator("latk_button.pointstoggle")
        row.operator("latk_button.matchfills") 
        row.operator("latk_button.makeroot") 

        row = layout.row()
        #row.operator("latk_button.refine")
        row.prop(latk, "cleanFactor")
        row.operator("latk_button.bigclean")

        row = layout.row()
        row.prop(latk, "numSplitFrames")
        row.operator("latk_button.splf")
        
        # ~ ~ ~ 

        row = layout.row()
        row.prop(latk, "minRemapPressure")
        row.prop(latk, "maxRemapPressure")
        row.prop(latk, "remapPressureMode")
        row.operator("latk_button.remappressure")

        row = layout.row()
        row.prop(latk, "strokeLength")
        row.prop(latk, "strokeGaps")
        row.prop(latk, "shuffleOdds")
        row.prop(latk, "spreadPoints")
        row.operator("latk_button.strokesfrommesh")

        '''
        row = layout.row()
        row.prop(latk, "writeStrokeSteps")
        row.prop(latk, "writeStrokePoints")
        row.operator("latk_button.writeonstrokes")
		'''
		
# ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~
# ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~

class Latk_Button_SimpleClean(bpy.types.Operator):
    """Clean up geometry"""
    bl_idname = "latk_button.simpleclean"
    bl_label = "Clean Mesh"
    bl_options = {'UNDO'}
    
    def execute(self, context):
        simpleClean()
        return {'FINISHED'}

class Latk_Button_ScopeTimeline(bpy.types.Operator):
    """Match timeline start and end to Grease Pencil"""
    bl_idname = "latk_button.scopetimeline"
    bl_label = "Scope"
    bl_options = {'UNDO'}
    
    def execute(self, context):
        resizeToFitGp()
        return {'FINISHED'}

class Latk_Button_MakeLoop(bpy.types.Operator):
    """Loop all latk keyframes"""
    bl_idname = "latk_button.makeloop"
    bl_label = "Loop"
    bl_options = {'UNDO'}
    
    def execute(self, context):
        makeLoop()
        return {'FINISHED'}

class Latk_Button_MakeRoot(bpy.types.Operator):
    """Parent GP layer to locator"""
    bl_idname = "latk_button.makeroot"
    bl_label = "Root"
    bl_options = {'UNDO'}
    
    def execute(self, context):
        makeLayerParent()
        return {'FINISHED'}

class Latk_Button_MatchFills(bpy.types.Operator):
    """Match fill colors to stroke colors"""
    bl_idname = "latk_button.matchfills"
    bl_label = "Fills"
    bl_options = {'UNDO'}
    
    def execute(self, context):
        matchFills()
        return {'FINISHED'}

class Latk_Button_HideScale(bpy.types.Operator):
    """Replace hide keyframes on latk objects with scale keyframes"""
    bl_idname = "latk_button.hidescale"
    bl_label = "Hide Scale"
    bl_options = {'UNDO'}
    
    def execute(self, context):
        hideFramesByScale()
        return {'FINISHED'}

class Latk_Button_BooleanMod(bpy.types.Operator):
    """Boolean union and bake"""
    bl_idname = "latk_button.booleanmod"
    bl_label = "Bool+"
    bl_options = {'UNDO'}
    
    def execute(self, context):
        booleanMod(op="union")
        return {'FINISHED'}

class Latk_Button_BooleanModMinus(bpy.types.Operator):
    """Boolean difference and bake"""
    bl_idname = "latk_button.booleanmodminus"
    bl_label = "Bool-"
    bl_options = {'UNDO'}
    
    def execute(self, context):
        booleanMod(op="difference")
        return {'FINISHED'}

class Latk_Button_SubsurfMod(bpy.types.Operator):
    """Subdivide one level and bake"""
    bl_idname = "latk_button.subsurfmod"
    bl_label = "Subd"
    bl_options = {'UNDO'}
    
    def execute(self, context):
        subsurfMod()
        return {'FINISHED'}

class Latk_Button_SmoothMod(bpy.types.Operator):
    """Smooth using defaults and bake"""
    bl_idname = "latk_button.smoothmod"
    bl_label = "Smooth"
    bl_options = {'UNDO'}
    
    def execute(self, context):
        smoothMod()
        return {'FINISHED'}

class Latk_Button_DecimateMod(bpy.types.Operator):
    """Decimate and bake"""
    bl_idname = "latk_button.decimatemod"
    bl_label = "Decimate"
    bl_options = {'UNDO'}
    
    def execute(self, context):
        latk_settings = bpy.context.scene.latk_settings
        decimateMod(_decimate=latk_settings.decimate)
        return {'FINISHED'}

class Latk_Button_HideTrue(bpy.types.Operator):
    """Hide or show selected"""
    bl_idname = "latk_button.hidetrue"
    bl_label = "Hide"
    bl_options = {'UNDO'}
    
    def execute(self, context):
        target = s()
        for obj in target:
            hideFrame(obj, currentFrame(), True)
        return {'FINISHED'}

class Latk_Button_Refine(bpy.types.Operator):
    """Refine all strokes"""
    bl_idname = "latk_button.refine"
    bl_label = "Refine GP"
    bl_options = {'UNDO'}
    
    def execute(self, context):
        la = fromGpToLatk()
        la.refine()
        fromLatkToGp(la, clearExisting=True)
        return {'FINISHED'}

'''
class Latk_Button_HideFalse(bpy.types.Operator):
    """Show selected"""
    bl_idname = "latk_button.hidefalse"
    bl_label = "Show"
    bl_options = {'UNDO'}
    
    def execute(self, context):
        target = s()
        for obj in target:
            hideFrame(obj,currentFrame(), False)
        return {'FINISHED'}
'''

class Latk_Button_Gpmesh(bpy.types.Operator):
    """Mesh all GP strokes. Takes a while"""
    bl_idname = "latk_button.gpmesh"
    bl_label = "MESH ALL"
    bl_options = {'UNDO'}
    
    def execute(self, context):
        latk_settings = bpy.context.scene.latk_settings
        #~
        doJoinMesh=False
        if (latk_settings.bakeMesh==True and latk_settings.joinMesh==True):
            doJoinMesh = True
        doHull=False
        if (latk_settings.mesh_fill_mode.lower() == "hull"):
            doHull = True
        #~
        gpMesh(_thickness=latk_settings.thickness, _remesh=latk_settings.remesh_mode.lower(), _resolution=latk_settings.resolution, _bevelResolution=latk_settings.bevelResolution, _decimate=latk_settings.decimate, _bakeMesh=latk_settings.bakeMesh, _joinMesh=doJoinMesh, _saveLayers=False, _vertexColorName=latk_settings.vertexColorName, _useHull=doHull)
        return {'FINISHED'}

class Latk_Button_RemapPressure(bpy.types.Operator):
    """Remap pressure or strength for all strokes"""
    bl_idname = "latk_button.remappressure"
    bl_label = "Pressure"
    bl_options = {'UNDO'}
    
    def execute(self, context):
        latk_settings = bpy.context.scene.latk_settings
        pressureRange(latk_settings.minRemapPressure, latk_settings.maxRemapPressure, latk_settings.remapPressureMode.lower())
        return {'FINISHED'}

class Latk_Button_WriteOnStrokes(bpy.types.Operator):
    """Create a sequence of write-on GP strokes"""
    bl_idname = "latk_button.writeonstrokes"
    bl_label = "Write-On"
    bl_options = {'UNDO'}
    
    def execute(self, context):
        latk_settings = bpy.context.scene.latk_settings
        writeOnStrokes(step=latk_settings.writeStrokeSteps, pointStep=latk_settings.writeStrokePoints)
        return {'FINISHED'}

class Latk_Button_StrokesFromMesh(bpy.types.Operator):
    """Generate GP strokes from a mesh"""
    bl_idname = "latk_button.strokesfrommesh"
    bl_label = "Strokes from Mesh"
    bl_options = {'UNDO'}
    
    def execute(self, context):
        latk_settings = bpy.context.scene.latk_settings
        meshToGp(strokeLength=latk_settings.strokeLength, strokeGaps=latk_settings.strokeGaps, shuffleOdds=latk_settings.shuffleOdds, spreadPoints=latk_settings.spreadPoints, limitPalette=latk_settings.paletteLimit)
        return {'FINISHED'}

class Latk_Button_PointsToggle(bpy.types.Operator):
    """Toggle points mode on"""
    bl_idname = "latk_button.pointstoggle"
    bl_label = "Points"
    bl_options = {'UNDO'}
    
    def execute(self, context):
        latk_settings = bpy.context.scene.latk_settings
        togglePoints()
        return {'FINISHED'}

'''
class Latk_Button_BakeSelected(bpy.types.Operator):
    """Bake selected curves to exportable meshes"""
    bl_idname = "latk_button.bakeselected"
    bl_label = "Curve Bake"
    bl_options = {'UNDO'}
    
    def execute(self, context):goo
        latk_settings = bpy.context.scene.latk_settings
        decimateAndBake(_decimate=latk_settings.decimate)
        return {'FINISHED'}
'''

class Latk_Button_BakeAllCurves(bpy.types.Operator):
    """Bake curves to exportable meshes"""
    bl_idname = "latk_button.bakeall"
    bl_label = "Curves Bake"
    bl_options = {'UNDO'}
    
    def execute(self, context):
        latk_settings = bpy.context.scene.latk_settings
        target = s()
        if (len(target) < 1): # all
            bakeAllCurvesToMesh(_decimate=latk_settings.decimate)
        else: # selected
            decimateAndBake(_decimate=latk_settings.decimate)
        return {'FINISHED'}

class Latk_Button_BakeAnim(bpy.types.Operator):
    """Bake keyframes with constraints"""
    bl_idname = "latk_button.bakeanim"
    bl_label = "Anim Bake"
    bl_options = {'UNDO'}
    
    def execute(self, context):
        target = s()
        if (len(target) < 1): # all
            target = bpy.data.objects
        toBake = []
        for obj in target:
            if (len(obj.constraints) > 0):
                toBake.append(obj)
        if (len(toBake) > 0):
            bakeAnimConstraint(target=toBake)
        return {'FINISHED'}

class Latk_Button_Gpmesh_SingleFrame(bpy.types.Operator):
    """Mesh a single frame"""
    bl_idname = "latk_button.gpmesh_singleframe"
    bl_label = "Mesh Frame"
    bl_options = {'UNDO'}

    def execute(self, context):
        latk_settings = bpy.context.scene.latk_settings
        #~
        doJoinMesh=False
        if (latk_settings.bakeMesh==True and latk_settings.joinMesh==True):
            doJoinMesh = True
        doHull=False
        if (latk_settings.mesh_fill_mode.lower() == "hull"):
            doHull = True
        #~
        gpMesh(_singleFrame=True, _animateFrames=False, _thickness=latk_settings.thickness, _remesh=latk_settings.remesh_mode.lower(), _resolution=latk_settings.resolution, _bevelResolution=latk_settings.bevelResolution, _decimate=latk_settings.decimate, _bakeMesh=latk_settings.bakeMesh, _joinMesh=doJoinMesh, _saveLayers=False, _vertexColorName=latk_settings.vertexColorName, _useHull=doHull)
        return {'FINISHED'}

class Latk_Button_Dn(bpy.types.Operator):
    """Delete all Latk-generated curves and meshes"""
    bl_idname = "latk_button.dn"
    bl_label = "Delete All"
    bl_options = {'UNDO'}
    
    def execute(self, context):
        deleteName("latk")
        return {'FINISHED'}

class Latk_Button_Splf(bpy.types.Operator):
    """Split GP stroke layers. Layers with fewer frames mesh faster"""
    bl_idname = "latk_button.splf"
    bl_label = "Split Layers"
    bl_options = {'UNDO'}
    
    def execute(self, context):
        latk_settings = bpy.context.scene.latk_settings
        splitLayersAboveFrameLimit(latk_settings.numSplitFrames)
        return {'FINISHED'}

class Latk_Button_BigClean(bpy.types.Operator):
    """Regenerate and simplify all strokes"""
    bl_idname = "latk_button.bigclean"
    bl_label = "Clean GP"
    bl_options = {'UNDO'}
    
    def execute(self, context):
        latk_settings = bpy.context.scene.latk_settings
        origStrokeCount = len(getAllStrokes())
        la = fromGpToLatk()
        la.clean(epsilon=latk_settings.cleanFactor)
        fromLatkToGp(la, clearExisting=True)
        strokeCount = len(getAllStrokes())
        self.report({'INFO'}, "Before: " + str(origStrokeCount) + " strokes, after: " + str(strokeCount) + " strokes.")
        return {'FINISHED'}

class Latk_Button_MtlShader(bpy.types.Operator):
    """Transfer parameters between Principled and Diffuse (default) shaders"""
    bl_idname = "latk_button.mtlshader"
    bl_label = "Shader"
    bl_options = {'UNDO'}
    
    def execute(self, context):
        latk_settings = bpy.context.scene.latk_settings
        target = s()
        if (len(target) < 1):
            setAllMtlShader(latk_settings.material_shader_mode.lower()) # do all
        else:
            setMtlShader(latk_settings.material_shader_mode.lower()) # do selected
        return {'FINISHED'}

# ~ ~ ~ 

def menu_func_import(self, context):
    self.layout.operator(ImportLatk.bl_idname, text="Latk Animation (.latk, .json)")
    #if (bpy.context.user_preferences.addons[__name__].preferences.extraFormats_TiltBrush == True):
    self.layout.operator(ImportTiltBrush.bl_idname, text="Latk - Tilt Brush (.tilt, .json)")
    #if (bpy.context.user_preferences.addons[__name__].preferences.extraFormats_ASC == True):
    self.layout.operator(ImportASC.bl_idname, text="Latk - ASC (.asc, .xyz)")
    #~
    '''
    if (bpy.context.user_preferences.addons[__name__].preferences.extraFormats_SculptrVR == True):
        self.layout.operator(ImportSculptrVR.bl_idname, text="Latk - SculptrVR (.csv)")
    if (bpy.context.user_preferences.addons[__name__].preferences.extraFormats_GML == True):
        self.layout.operator(ImportGml.bl_idname, text="Latk - GML (.gml)")
    if (bpy.context.user_preferences.addons[__name__].preferences.extraFormats_Painter == True):
        self.layout.operator(ImportPainter.bl_idname, text="Latk - Corel Painter (.txt)")
    if (bpy.context.user_preferences.addons[__name__].preferences.extraFormats_SVG == True):
        self.layout.operator(ImportSvg.bl_idname, text="Latk - SVG (.svg)")
    if (bpy.context.user_preferences.addons[__name__].preferences.extraFormats_Norman == True):
        self.layout.operator(ImportNorman.bl_idname, text="Latk - NormanVR (.json)")
    if (bpy.context.user_preferences.addons[__name__].preferences.extraFormats_VRDoodler == True):
        self.layout.operator(ImportVRDoodler.bl_idname, text="Latk - VRDoodler (.obj)")
    '''

def menu_func_export(self, context):
    self.layout.operator(ExportLatk.bl_idname, text="Latk Animation (.latk)")
    self.layout.operator(ExportLatkJson.bl_idname, text="Latk Animation (.json)")
    #if (bpy.context.user_preferences.addons[__name__].preferences.extraFormats_ASC == True):
    self.layout.operator(ExportASC.bl_idname, text="Latk - ASC (.asc)")
    #~
    '''
    if (bpy.context.user_preferences.addons[__name__].preferences.extraFormats_SculptrVR == True):
        self.layout.operator(ExportSculptrVR.bl_idname, text="Latk - SculptrVR (.csv)")
    if (bpy.context.user_preferences.addons[__name__].preferences.extraFormats_GML == True):
        self.layout.operator(ExportGml.bl_idname, text="Latk - GML (.gml)")
    if (bpy.context.user_preferences.addons[__name__].preferences.extraFormats_Painter == True):
        self.layout.operator(ExportPainter.bl_idname, text="Latk - Corel Painter (.txt)")
    if (bpy.context.user_preferences.addons[__name__].preferences.extraFormats_SVG == True):
        self.layout.operator(ExportSvg.bl_idname, text="Latk - SVG SMIL (.svg)")
    if (bpy.context.user_preferences.addons[__name__].preferences.extraFormats_AfterEffects == True):
        self.layout.operator(ExportAfterEffects.bl_idname, text="Latk - After Effects (.jsx)")        
    if (bpy.context.user_preferences.addons[__name__].preferences.extraFormats_FBXSequence == True):
        self.layout.operator(ExportFbxSequence.bl_idname, text="Latk - Sketchfab FBX Sequence (.fbx)")
    if (bpy.context.user_preferences.addons[__name__].preferences.extraFormats_UnrealXYZ == True):
        self.layout.operator(ExportUnrealXYZ.bl_idname, text="Latk - Unreal Point Cloud (.xyz)")
    '''

classes = (
    ImportLatk,
    ImportTiltBrush,
	ImportASC,
    ExportLatkJson,
    ExportLatk,
	ExportASC
)

'''
LightningArtistToolkitPreferences,
ImportNorman,
ImportVRDoodler,
ImportSvg,
ImportSculptrVR,
ImportPainter,
ImportGml,
ExportGml,
ExportFbxSequence,
ExportSculptrVR,
ExportUnrealXYZ,
ExportSvg,
ExportAfterEffects,
ExportPainter,
LatkProperties,
LatkProperties_Panel,
Latk_Button_SimpleClean,
Latk_Button_ScopeTimeline,
Latk_Button_MakeLoop,
Latk_Button_MakeRoot,
Latk_Button_MatchFills,
Latk_Button_HideScale,
Latk_Button_BooleanMod,
Latk_Button_BooleanModMinus,
Latk_Button_SubsurfMod,
Latk_Button_SmoothMod,
Latk_Button_DecimateMod,
Latk_Button_HideTrue,
Latk_Button_Refine,
Latk_Button_Gpmesh,
Latk_Button_RemapPressure,
Latk_Button_WriteOnStrokes,
Latk_Button_StrokesFromMesh,
Latk_Button_PointsToggle,
Latk_Button_BakeAllCurves,
Latk_Button_BakeAnim,
Latk_Button_Gpmesh_SingleFrame,
Latk_Button_Dn,
Latk_Button_Splf,
Latk_Button_BigClean,
Latk_Button_MtlShader
'''

def register():
    for cls in classes:
        bpy.utils.register_class(cls)   

    #bpy.types.Scene.latk_settings = PointerProperty(type=LatkProperties)
    bpy.types.TOPBAR_MT_file_import.append(menu_func_import)
    bpy.types.TOPBAR_MT_file_export.append(menu_func_export)

def unregister():
    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)

    #del bpy.types.Scene.latk_settings
    bpy.types.TOPBAR_MT_file_import.remove(menu_func_import)
    bpy.types.TOPBAR_MT_file_export.remove(menu_func_export)

if __name__ == "__main__":
    register()

# * * * * * * * * * * * * * * * * * * * * * * * * * *
# * * * * * * * * * * * * * * * * * * * * * * * * * *
# * * * * * * * * * * * * * * * * * * * * * * * * * *

