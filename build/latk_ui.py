# 10 of 10. UI

class LightningArtistToolkitPreferences(bpy.types.AddonPreferences):
    bl_idname = __name__
    
    extraFormats_TiltBrush = bpy.props.BoolProperty(
        name = 'Tilt Brush',
        description = "Tilt Brush import",
        default = True
    )

    extraFormats_GML = bpy.props.BoolProperty(
        name = 'GML',
        description = "Graffiti Markup Language import/export",
        default = False
    )

    extraFormats_ASC = bpy.props.BoolProperty(
        name = 'ASC Point Cloud',
        description = "ASC point cloud import/export",
        default = False
    )

    extraFormats_Painter = bpy.props.BoolProperty(
        name = 'Corel Painter',
        description = "Corel Painter script import/export",
        default = False
    )

    extraFormats_SVG = bpy.props.BoolProperty(
        name = 'SVG SMIL',
        description = "SVG SMIL export (experimental)",
        default = False
    )

    extraFormats_Norman = bpy.props.BoolProperty(
        name = 'NormanVR',
        description = "NormanVR import (experimental)",
        default = False
    )

    extraFormats_VRDoodler = bpy.props.BoolProperty(
        name = 'VRDoodler',
        description = "VRDoodler import",
        default = False
    )

    extraFormats_FBXSequence = bpy.props.BoolProperty(
        name = 'FBX Sequence',
        description = "FBX Sequence export",
        default = False
    )

    extraFormats_SculptrVR = bpy.props.BoolProperty(
        name = 'SculptrVR CSV',
        description = "SculptrVR CSV import/export",
        default = True
    )

    def draw(self, context):
        layout = self.layout
        layout.label("Add menu items to import:")
        layout.prop(self, "extraFormats_TiltBrush")
        layout.prop(self, "extraFormats_SculptrVR")
        layout.prop(self, "extraFormats_ASC")
        layout.prop(self, "extraFormats_GML")
        layout.prop(self, "extraFormats_Painter")
        layout.prop(self, "extraFormats_Norman")
        layout.prop(self, "extraFormats_VRDoodler")
        #~
        layout.label("Add menu items to export:")
        layout.prop(self, "extraFormats_SculptrVR")
        layout.prop(self, "extraFormats_ASC")
        layout.prop(self, "extraFormats_GML")
        layout.prop(self, "extraFormats_Painter")
        layout.prop(self, "extraFormats_SVG")
        layout.prop(self, "extraFormats_FBXSequence")


class ImportLatk(bpy.types.Operator, ImportHelper):
    """Load a Latk File"""
    resizeTimeline = BoolProperty(name="Resize Timeline", description="Set in and out points", default=True)

    bl_idname = "import_scene.latk"
    bl_label = "Import Latk"
    bl_options = {'PRESET', 'UNDO'}

    filename_ext = ".json"
    filter_glob = StringProperty(
            default="*.latk;*.json",
            options={'HIDDEN'},
            )

    def execute(self, context):
        import latk as la
        keywords = self.as_keywords(ignore=("axis_forward", "axis_up", "filter_glob", "split_mode", "resizeTimeline"))
        if bpy.data.is_saved and context.user_preferences.filepaths.use_relative_paths:
            import os
        #~
        keywords["resizeTimeline"] = self.resizeTimeline
        la.readBrushStrokes(**keywords)
        return {'FINISHED'}


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
        import latk as la
        keywords = self.as_keywords(ignore=("axis_forward", "axis_up", "filter_glob", "split_mode"))
        if bpy.data.is_saved and context.user_preferences.filepaths.use_relative_paths:
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
        import latk as la
        keywords = self.as_keywords(ignore=("axis_forward", "axis_up", "filter_glob", "split_mode"))
        if bpy.data.is_saved and context.user_preferences.filepaths.use_relative_paths:
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
        import latk as la
        keywords = self.as_keywords(ignore=("axis_forward", "axis_up", "filter_glob", "split_mode"))
        if bpy.data.is_saved and context.user_preferences.filepaths.use_relative_paths:
            import os
        #~
        la.importVRDoodler(**keywords)
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

    strokeLength = IntProperty(name="Points per Stroke", description="Group every n points into strokes", default=1)

    def execute(self, context):
        import latk as la
        keywords = self.as_keywords(ignore=("axis_forward", "axis_up", "filter_glob", "split_mode"))
        if bpy.data.is_saved and context.user_preferences.filepaths.use_relative_paths:
            import os
        #~
        keywords["strokeLength"] = self.strokeLength
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
        import latk as la
        keywords = self.as_keywords(ignore=("axis_forward", "axis_up", "filter_glob", "split_mode"))
        if bpy.data.is_saved and context.user_preferences.filepaths.use_relative_paths:
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
        import latk as la
        keywords = self.as_keywords(ignore=("axis_forward", "axis_up", "filter_glob", "split_mode"))
        if bpy.data.is_saved and context.user_preferences.filepaths.use_relative_paths:
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
        import latk as la
        keywords = self.as_keywords(ignore=("axis_forward", "axis_up", "filter_glob", "split_mode", "splitStrokes", "sequenceAnim"))
        if bpy.data.is_saved and context.user_preferences.filepaths.use_relative_paths:
            import os
        #~
        keywords["splitStrokes"] = self.splitStrokes
        keywords["sequenceAnim"] = self.sequenceAnim
        #~
        la.gmlParser(**keywords)
        return {'FINISHED'} 


# ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~


class ExportLatkJson(bpy.types.Operator, ExportHelper): # TODO combine into one class
    """Save a Latk Json File"""

    bake = BoolProperty(name="Bake Frames", description="Bake Keyframes to All Frames", default=False)
    roundValues = BoolProperty(name="Limit Precision", description="Round Values to Reduce Filesize", default=False)    
    numPlaces = IntProperty(name="Number Places", description="Number of Decimal Places", default=7)

    bl_idname = "export_scene.latkjson"
    bl_label = 'Export Latk Json'
    bl_options = {'PRESET'}

    filename_ext = ".json"

    filter_glob = StringProperty(
            default="*.json",
            options={'HIDDEN'},
            )

    def execute(self, context):
        import latk as la
        keywords = self.as_keywords(ignore=("axis_forward", "axis_up", "filter_glob", "split_mode", "check_existing", "bake", "roundValues", "numPlaces"))
        if bpy.data.is_saved and context.user_preferences.filepaths.use_relative_paths:
            import os
        #~
        keywords["bake"] = self.bake
        keywords["roundValues"] = self.roundValues
        keywords["numPlaces"] = self.numPlaces
        #~
        la.writeBrushStrokes(**keywords, zipped=False)
        return {'FINISHED'}

class ExportLatk(bpy.types.Operator, ExportHelper):  # TODO combine into one class
    """Save a Latk File"""

    bake = BoolProperty(name="Bake Frames", description="Bake Keyframes to All Frames", default=False)
    roundValues = BoolProperty(name="Limit Precision", description="Round Values to Reduce Filesize", default=False)    
    numPlaces = IntProperty(name="Number Places", description="Number of Decimal Places", default=7)

    bl_idname = "export_scene.latk"
    bl_label = 'Export Latk'
    bl_options = {'PRESET'}

    filename_ext = ".latk"

    filter_glob = StringProperty(
            default="*.latk",
            options={'HIDDEN'},
            )

    def execute(self, context):
        import latk as la
        keywords = self.as_keywords(ignore=("axis_forward", "axis_up", "filter_glob", "split_mode", "check_existing", "bake", "roundValues", "numPlaces"))
        if bpy.data.is_saved and context.user_preferences.filepaths.use_relative_paths:
            import os
        #~
        keywords["bake"] = self.bake
        keywords["roundValues"] = self.roundValues
        keywords["numPlaces"] = self.numPlaces
        #~
        la.writeBrushStrokes(**keywords, zipped=True)
        return {'FINISHED'}


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
        import latk as la
        keywords = self.as_keywords(ignore=("axis_forward", "axis_up", "filter_glob", "split_mode", "check_existing"))
        if bpy.data.is_saved and context.user_preferences.filepaths.use_relative_paths:
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
        import latk as la
        keywords = self.as_keywords(ignore=("axis_forward", "axis_up", "filter_glob", "split_mode", "check_existing"))
        if bpy.data.is_saved and context.user_preferences.filepaths.use_relative_paths:
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
        import latk as la
        keywords = self.as_keywords(ignore=("axis_forward", "axis_up", "filter_glob", "split_mode", "check_existing"))
        if bpy.data.is_saved and context.user_preferences.filepaths.use_relative_paths:
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

    def execute(self, context):
        import latk as la
        keywords = self.as_keywords(ignore=("axis_forward", "axis_up", "filter_glob", "split_mode", "check_existing"))
        if bpy.data.is_saved and context.user_preferences.filepaths.use_relative_paths:
            import os
        #~
        la.exportAsc(**keywords)
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
        import latk as la
        #keywords = self.as_keywords(ignore=("axis_forward", "axis_up", "filter_glob", "split_mode", "check_existing", "bake"))
        keywords = self.as_keywords(ignore=("axis_forward", "axis_up", "filter_glob", "split_mode", "check_existing"))
        if bpy.data.is_saved and context.user_preferences.filepaths.use_relative_paths:
            import os
        #~
        la.writeSvg(**keywords)
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
        import latk as la
        #keywords = self.as_keywords(ignore=("axis_forward", "axis_up", "filter_glob", "split_mode", "check_existing", "bake"))
        keywords = self.as_keywords(ignore=("axis_forward", "axis_up", "filter_glob", "split_mode", "check_existing"))
        if bpy.data.is_saved and context.user_preferences.filepaths.use_relative_paths:
            import os
        #~
        la.writePainter(**keywords)
        return {'FINISHED'} 


# ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~
# ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~


class FreestyleGPencil(bpy.types.PropertyGroup):
    """Properties for the Freestyle to Grease Pencil exporter"""
    bl_idname = "RENDER_PT_gpencil_export"

    use_freestyle_gpencil_export = BoolProperty(
        name="Grease Pencil Export",
        description="Export Freestyle edges to Grease Pencil"
    )

    use_fill = BoolProperty(
        name="Fill",
        description="Fill the contour with the object's material color",
        default=False
    )

    use_connecting = BoolProperty(
        name="Connecting Strokes",
        description="Connect all vertices with strokes",
        default=False
    )

    visible_only = BoolProperty(
        name="Visible Only",
        description="Only render visible lines",
        default=True
    )

    use_overwrite = BoolProperty(
        name="Overwrite",
        description="Remove the GPencil strokes from previous renders before a new render",
        default=False
    )

    vertexHitbox = FloatProperty(
        name="Vertex Hitbox",
        description="How close a GP stroke needs to be to a vertex",
        default=1.5
    )

    numColPlaces = IntProperty(
        name="Color Places",
        description="How many decimal places used to find matching colors",
        default=5,
    )

    numMaxColors = IntProperty(
        name="Max Colors",
        description="How many colors are in the Grease Pencil palette",
        default=16
    )

    doClearPalette = BoolProperty(
        name="Clear Palette",
        description="Delete palette before beginning a new render",
        default=False
    )

class FreestyleGPencil_Panel(bpy.types.Panel):
    """Creates a Panel in the render context of the properties editor"""
    bl_idname = "RENDER_PT_FreestyleGPencilPanel"
    bl_space_type = 'PROPERTIES'
    bl_label = "Latk Freestyle"
    bl_region_type = 'WINDOW'
    bl_context = "render"

    def draw_header(self, context):
        self.layout.prop(context.scene.freestyle_gpencil_export, "use_freestyle_gpencil_export", text="")

    def draw(self, context):
        layout = self.layout

        scene = context.scene
        gp = scene.freestyle_gpencil_export
        freestyle = scene.render.layers.active.freestyle_settings

        layout.active = (gp.use_freestyle_gpencil_export and freestyle.mode != 'SCRIPT')

        row = layout.row()
        row.prop(gp, "numColPlaces")
        row.prop(gp, "numMaxColors")

        row = layout.row()
        #row.prop(svg, "split_at_invisible")
        row.prop(gp, "use_fill")
        row.prop(gp, "use_overwrite")
        row.prop(gp, "doClearPalette")

        row = layout.row()
        row.prop(gp, "visible_only")
        row.prop(gp, "use_connecting")
        row.prop(gp, "vertexHitbox")


# ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~
# ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~


class LatkProperties(bpy.types.PropertyGroup):
    """Properties for Latk"""
    bl_idname = "GREASE_PENCIL_PT_LatkProperties"

    bakeMesh = BoolProperty(
        name="Auto Bake",
        description="Off: major speedup if you're staying in Blender. On: slow but keeps everything exportable",
        default=False
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
        name="Save Layers",
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
        default=20
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

    vertexColorName = StringProperty(
        name="Vertex Color",
        description="Vertex color name for export",
        default="rgba"
    )

    remesh_mode = EnumProperty(
        name="Remesh Mode",
        items=(
            ("NONE", "No Remesh", "No remeshing curves", 0),
            ("SHARP", "Sharp", "Sharp remesh", 1),
            ("SMOOTH", "Smooth", "Smooth remesh", 2),
            ("BLOCKS", "Blocks", "Blocks remesh", 3)
        ),
        default="NONE"
    )

    material_set_mode = EnumProperty( 
        name="Affect",
        items=(
            ("ALL", "All", "All materials", 0),
            ("SELECTED", "Selected", "Selected materials", 1)
        ),
        default="ALL"
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
        row.prop(latk, "saveLayers")
        row.prop(latk, "vertexColorName")
        
        row = layout.row()
        row.prop(latk, "remesh_mode", expand=True)

        row = layout.row()
        row.prop(latk, "material_set_mode")
        row.prop(latk, "material_shader_mode")
        row.operator("latk_button.mtlshader")

        # ~ ~ ~ 

        row = layout.row()
        row.operator("latk_button.booleanmod") 
        row.operator("latk_button.booleanmodminus") 
        row.operator("latk_button.smoothmod") 
        row.operator("latk_button.subsurfmod") 

        row = layout.row()
        row.operator("latk_button.hidetrue") 
        row.operator("latk_button.hidefalse") 
        row.operator("latk_button.makeloop") 
        row.operator("latk_button.scopetimeline") 
        row.operator("latk_button.makeroot") 

        row = layout.row()
        row.operator("latk_button.bakeselected")
        row.operator("latk_button.bakeall")
        row.operator("latk_button.bakeanim")
        row.operator("latk_button.hidescale")
        
        row = layout.row()
        row.prop(latk, "strokeLength")
        row.prop(latk, "strokeGaps")
        row.prop(latk, "shuffleOdds")
        row.prop(latk, "spreadPoints")
        #row.prop(latk, "fast_colors")
        row.operator("latk_button.strokesfrommesh")

        # ~ ~ ~ 

        row = layout.row()
        row.prop(latk, "writeStrokeSteps")
        row.prop(latk, "writeStrokePoints")
        row.operator("latk_button.writeonstrokes")
        row.operator("latk_button.pointstoggle")

        row = layout.row()
        row.prop(latk, "numSplitFrames")
        row.operator("latk_button.splf")

        row = layout.row()
        row.prop(latk, "minRemapPressure")
        row.prop(latk, "maxRemapPressure")
        row.prop(latk, "remapPressureMode")
        row.operator("latk_button.remappressure")


# ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~
# ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~

class Latk_Button_ScopeTimeline(bpy.types.Operator):
    """Loop all latk keyframes"""
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
    """Parent all latk objects to locator"""
    bl_idname = "latk_button.makeroot"
    bl_label = "Root"
    bl_options = {'UNDO'}
    
    def execute(self, context):
        makeRoot()
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

class Latk_Button_HideTrue(bpy.types.Operator):
    """Boolean union and bake"""
    bl_idname = "latk_button.hidetrue"
    bl_label = "Hide"
    bl_options = {'UNDO'}
    
    def execute(self, context):
        target = s()
        for obj in target:
            hideFrame(obj,currentFrame(), True)
        return {'FINISHED'}

class Latk_Button_HideFalse(bpy.types.Operator):
    """Boolean union and bake"""
    bl_idname = "latk_button.hidefalse"
    bl_label = "Show"
    bl_options = {'UNDO'}
    
    def execute(self, context):
        target = s()
        for obj in target:
            hideFrame(obj,currentFrame(), False)
        return {'FINISHED'}

class Latk_Button_Gpmesh(bpy.types.Operator):
    """Mesh all GP strokes. Takes a while.."""
    bl_idname = "latk_button.gpmesh"
    bl_label = "MESH ALL"
    bl_options = {'UNDO'}
    
    def execute(self, context):
        latk_settings = bpy.context.scene.latk_settings
        gpMesh(_thickness=latk_settings.thickness, _remesh=latk_settings.remesh_mode.lower(), _resolution=latk_settings.resolution, _bevelResolution=latk_settings.bevelResolution, _decimate=latk_settings.decimate, _bakeMesh=latk_settings.bakeMesh, _joinMesh=latk_settings.bakeMesh, _saveLayers=False, _vertexColorName=latk_settings.vertexColorName)
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
        meshToGp(strokeLength=latk_settings.strokeLength, strokeGaps=latk_settings.strokeGaps, shuffleOdds=latk_settings.shuffleOdds, spreadPoints=latk_settings.spreadPoints)
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

class Latk_Button_BakeSelected(bpy.types.Operator):
    """Bake selected curves to exportable meshes"""
    bl_idname = "latk_button.bakeselected"
    bl_label = "Curve Bake"
    bl_options = {'UNDO'}
    
    def execute(self, context):
        latk_settings = bpy.context.scene.latk_settings
        decimateAndBake(_decimate=latk_settings.decimate)
        return {'FINISHED'}

class Latk_Button_BakeAllCurves(bpy.types.Operator):
    """Bake all curves to exportable meshes"""
    bl_idname = "latk_button.bakeall"
    bl_label = "Curves Bake"
    bl_options = {'UNDO'}
    
    def execute(self, context):
        latk_settings = bpy.context.scene.latk_settings
        bakeAllCurvesToMesh(_decimate=latk_settings.decimate)
        return {'FINISHED'}

class Latk_Button_BakeAnim(bpy.types.Operator):
    """Bake keyframes with constraints"""
    bl_idname = "latk_button.bakeanim"
    bl_label = "Anim Bake"
    bl_options = {'UNDO'}
    
    def execute(self, context):
        latk_settings = bpy.context.scene.latk_settings
        bakeAnimConstraint()
        return {'FINISHED'}

class Latk_Button_Gpmesh_SingleFrame(bpy.types.Operator):
    """Mesh a single frame. Great for fast previews"""
    bl_idname = "latk_button.gpmesh_singleframe"
    bl_label = "Mesh Frame"
    bl_options = {'UNDO'}

    def execute(self, context):
        latk_settings = bpy.context.scene.latk_settings
        gpMesh(_singleFrame=True, _animateFrames=False, _thickness=latk_settings.thickness, _remesh=latk_settings.remesh_mode.lower(), _resolution=latk_settings.resolution, _bevelResolution=latk_settings.bevelResolution, _decimate=latk_settings.decimate, _bakeMesh=latk_settings.bakeMesh, _joinMesh=latk_settings.bakeMesh, _saveLayers=False, _vertexColorName=latk_settings.vertexColorName)
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

class Latk_Button_MtlShader(bpy.types.Operator):
    """Transfer parameters between Principled and Diffuse (default) shaders"""
    bl_idname = "latk_button.mtlshader"
    bl_label = "Shader"
    bl_options = {'UNDO'}
    
    def execute(self, context):
        latk_settings = bpy.context.scene.latk_settings
        if (latk_settings.material_set_mode.lower() == "all"):
            setAllMtlShader(latk_settings.material_shader_mode.lower())
        elif (latk_settings.material_set_mode.lower() == "selected"):
            setMtlShader(latk_settings.material_shader_mode.lower())
        return {'FINISHED'}

# ~ ~ ~ 

def menu_func_import(self, context):
    self.layout.operator(ImportLatk.bl_idname, text="Latk Animation (.latk, .json)")
    #~
    if (bpy.context.user_preferences.addons[__name__].preferences.extraFormats_TiltBrush == True):
        self.layout.operator(ImportTiltBrush.bl_idname, text="Latk - Tilt Brush (.tilt, .json)")
    if (bpy.context.user_preferences.addons[__name__].preferences.extraFormats_SculptrVR == True):
        self.layout.operator(ImportSculptrVR.bl_idname, text="Latk - SculptrVR (.csv)")
    if (bpy.context.user_preferences.addons[__name__].preferences.extraFormats_ASC == True):
        self.layout.operator(ImportASC.bl_idname, text="Latk - ASC (.asc, .xyz)")
    if (bpy.context.user_preferences.addons[__name__].preferences.extraFormats_GML == True):
        self.layout.operator(ImportGml.bl_idname, text="Latk - GML (.gml)")
    if (bpy.context.user_preferences.addons[__name__].preferences.extraFormats_Painter == True):
        self.layout.operator(ImportPainter.bl_idname, text="Latk - Corel Painter (.txt)")
    if (bpy.context.user_preferences.addons[__name__].preferences.extraFormats_Norman == True):
        self.layout.operator(ImportNorman.bl_idname, text="Latk - NormanVR (.json)")
    if (bpy.context.user_preferences.addons[__name__].preferences.extraFormats_VRDoodler == True):
        self.layout.operator(ImportVRDoodler.bl_idname, text="Latk - VRDoodler (.obj)")

def menu_func_export(self, context):
    self.layout.operator(ExportLatk.bl_idname, text="Latk Animation (.latk)")
    self.layout.operator(ExportLatkJson.bl_idname, text="Latk Animation (.json)")
    #~
    if (bpy.context.user_preferences.addons[__name__].preferences.extraFormats_SculptrVR == True):
        self.layout.operator(ExportSculptrVR.bl_idname, text="Latk - SculptrVR (.csv)")
    if (bpy.context.user_preferences.addons[__name__].preferences.extraFormats_ASC == True):
        self.layout.operator(ExportASC.bl_idname, text="Latk - ASC (.asc)")
    if (bpy.context.user_preferences.addons[__name__].preferences.extraFormats_GML == True):
        self.layout.operator(ExportGml.bl_idname, text="Latk - GML (.gml)")
    if (bpy.context.user_preferences.addons[__name__].preferences.extraFormats_Painter == True):
        self.layout.operator(ExportPainter.bl_idname, text="Latk - Corel Painter (.txt)")
    if (bpy.context.user_preferences.addons[__name__].preferences.extraFormats_SVG == True):
        self.layout.operator(ExportSvg.bl_idname, text="Latk - SVG SMIL (.svg)")
    if (bpy.context.user_preferences.addons[__name__].preferences.extraFormats_FBXSequence == True):
        self.layout.operator(ExportFbxSequence.bl_idname, text="Latk - FBX Sequence (.fbx)")

def register():
    bpy.utils.register_module(__name__)

    bpy.types.Scene.latk_settings = PointerProperty(type=LatkProperties)
    bpy.types.INFO_MT_file_import.append(menu_func_import)
    bpy.types.INFO_MT_file_export.append(menu_func_export)

    bpy.types.Scene.freestyle_gpencil_export = PointerProperty(type=FreestyleGPencil)
    
    parameter_editor.callbacks_lineset_pre.append(export_fill)
    parameter_editor.callbacks_lineset_post.append(export_stroke)

def unregister():
    bpy.utils.unregister_module(__name__)

    del bpy.types.Scene.latk_settings
    bpy.types.INFO_MT_file_import.remove(menu_func_import)
    bpy.types.INFO_MT_file_export.remove(menu_func_export)

    del bpy.types.Scene.freestyle_gpencil_export
    
    parameter_editor.callbacks_lineset_pre.remove(export_fill)
    parameter_editor.callbacks_lineset_post.remove(export_stroke)

if __name__ == "__main__":
    register()

# * * * * * * * * * * * * * * * * * * * * * * * * * *
# * * * * * * * * * * * * * * * * * * * * * * * * * *
# * * * * * * * * * * * * * * * * * * * * * * * * * *

