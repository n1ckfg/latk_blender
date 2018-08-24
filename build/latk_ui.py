# 10 of 10. UI

class LightningArtistToolkitPreferences(bpy.types.AddonPreferences):
    bl_idname = __name__
    
    extraFormats = bpy.props.BoolProperty(
        name = 'Third-Party Formats',
        description = "Add menu items to import and export third-party formats."
    )

    def draw(self, context):
        layout = self.layout
        layout.label("Add menu items to import and export third-party formats:")
        layout.prop(self, "extraFormats")

'''
class OBJECT_OT_latk_prefs(Operator):
    """Display example preferences"""
    bl_idname = "object.latk_prefs"
    bl_label = "Latk Preferences"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        user_preferences = context.user_preferences
        addon_prefs = user_preferences.addons[__name__].preferences
        return {'FINISHED'}
'''

class ImportLatk(bpy.types.Operator, ImportHelper):
    """Load a Latk File"""
    resizeTimeline = BoolProperty(name="Resize Timeline", description="Set in and out points", default=True)

    bl_idname = "import_scene.latk"
    bl_label = "Import Latk"
    bl_options = {'PRESET', 'UNDO'}

    filename_ext = ".json"
    filter_glob = StringProperty(
            default="*.latk;*.json;*.zip",
            options={'HIDDEN'},
            )

    def execute(self, context):
        import latk as la
        keywords = self.as_keywords(ignore=("axis_forward", "axis_up", "filter_glob", "split_mode", "resizeTimeline"))
        if bpy.data.is_saved and context.user_preferences.filepaths.use_relative_paths:
            import os
            #keywords["relpath"] = os.path.dirname(bpy.data.filepath)
        #~
        keywords["resizeTimeline"] = self.resizeTimeline
        la.readBrushStrokes(**keywords)
        return {'FINISHED'}

    '''
    def execute(self, context):
        # print("Selected: " + context.active_object.name)
        from . import import_obj

        if self.split_mode == 'OFF':
            self.use_split_objects = False
            self.use_split_groups = False
        else:
            self.use_groups_as_vgroups = False

        keywords = self.as_keywords(ignore=("axis_forward",
                                            "axis_up",
                                            "filter_glob",
                                            "split_mode",
                                            ))

        global_matrix = axis_conversion(from_forward=self.axis_forward,
                                        from_up=self.axis_up,
                                        ).to_4x4()
        keywords["global_matrix"] = global_matrix

        if bpy.data.is_saved and context.user_preferences.filepaths.use_relative_paths:
            import os
            keywords["relpath"] = os.path.dirname(bpy.data.filepath)

        return import_obj.load(context, **keywords)

    def draw(self, context):
        layout = self.layout
    '''

class ExportLatkJson(bpy.types.Operator, ExportHelper): # TODO combine into one class
    """Save a Latk Json File"""

    bake = BoolProperty(name="Bake Frames", description="Bake Keyframes to All Frames", default=True)

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
        keywords = self.as_keywords(ignore=("axis_forward", "axis_up", "filter_glob", "split_mode", "check_existing", "bake"))
        if bpy.data.is_saved and context.user_preferences.filepaths.use_relative_paths:
            import os
            #keywords["relpath"] = os.path.dirname(bpy.data.filepath)
        #~
        keywords["bake"] = self.bake
        #~
        la.writeBrushStrokes(**keywords, zipped=False)
        return {'FINISHED'}

class ExportLatk(bpy.types.Operator, ExportHelper):  # TODO combine into one class
    """Save a Latk File"""

    bake = BoolProperty(name="Bake Frames", description="Bake Keyframes to All Frames", default=True)

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
        keywords = self.as_keywords(ignore=("axis_forward", "axis_up", "filter_glob", "split_mode", "check_existing", "bake"))
        if bpy.data.is_saved and context.user_preferences.filepaths.use_relative_paths:
            import os
            #keywords["relpath"] = os.path.dirname(bpy.data.filepath)
        #~
        keywords["bake"] = self.bake
        #~
        la.writeBrushStrokes(**keywords, zipped=True)
        return {'FINISHED'}

    '''
    path_mode = path_reference_mode

    check_extension = True

    def execute(self, context):
        from . import export_obj

        from mathutils import Matrix
        keywords = self.as_keywords(ignore=("axis_forward",
                                            "axis_up",
                                            "global_scale",
                                            "check_existing",
                                            "filter_glob",
                                            ))

        global_matrix = (Matrix.Scale(self.global_scale, 4) *
                         axis_conversion(to_forward=self.axis_forward,
                                         to_up=self.axis_up,
                                         ).to_4x4())

        keywords["global_matrix"] = global_matrix
        return export_obj.save(context, **keywords)
    '''

# ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ 

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
            #keywords["relpath"] = os.path.dirname(bpy.data.filepath)
        #~
        la.importNorman(**keywords)
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

    splitStrokes = BoolProperty(name="Split Strokes", description="Split Strokes on Layers", default=True)

    def execute(self, context):
        import latk as la
        keywords = self.as_keywords(ignore=("axis_forward", "axis_up", "filter_glob", "split_mode", "splitStrokes"))
        if bpy.data.is_saved and context.user_preferences.filepaths.use_relative_paths:
            import os
            #keywords["relpath"] = os.path.dirname(bpy.data.filepath)
        #~
        keywords["splitStrokes"] = self.splitStrokes
        #~
        la.gmlParser(**keywords)
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

    make2d = BoolProperty(name="Make 2D", description="Project Coordinates to Camera View", default=True)

    def execute(self, context):
        import latk as la
        #keywords = self.as_keywords(ignore=("axis_forward", "axis_up", "filter_glob", "split_mode", "check_existing", "bake"))
        keywords = self.as_keywords(ignore=("axis_forward", "axis_up", "filter_glob", "split_mode", "check_existing"))
        if bpy.data.is_saved and context.user_preferences.filepaths.use_relative_paths:
            import os
            #keywords["relpath"] = os.path.dirname(bpy.data.filepath)
        #~
        keywords["make2d"] = self.make2d
        #~
        la.writeGml(**keywords)
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

    #bake = BoolProperty(name="Bake Frames", description="Bake Keyframes to All Frames", default=True)

    def execute(self, context):
        import latk as la
        #keywords = self.as_keywords(ignore=("axis_forward", "axis_up", "filter_glob", "split_mode", "check_existing", "bake"))
        keywords = self.as_keywords(ignore=("axis_forward", "axis_up", "filter_glob", "split_mode", "check_existing"))
        if bpy.data.is_saved and context.user_preferences.filepaths.use_relative_paths:
            import os
            #keywords["relpath"] = os.path.dirname(bpy.data.filepath)
        #~
        #keywords["bake"] = self.bake
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

    #bake = BoolProperty(name="Bake Frames", description="Bake Keyframes to All Frames", default=True)

    def execute(self, context):
        import latk as la
        #keywords = self.as_keywords(ignore=("axis_forward", "axis_up", "filter_glob", "split_mode", "check_existing", "bake"))
        keywords = self.as_keywords(ignore=("axis_forward", "axis_up", "filter_glob", "split_mode", "check_existing"))
        if bpy.data.is_saved and context.user_preferences.filepaths.use_relative_paths:
            import os
            #keywords["relpath"] = os.path.dirname(bpy.data.filepath)
        #~
        #keywords["bake"] = self.bake
        #~
        la.writePainter(**keywords)
        return {'FINISHED'} 

# ~ ~ ~ 

class FreestyleGPencil(bpy.types.PropertyGroup):
    """Properties for the Freestyle to Grease Pencil exporter"""
    bl_idname = "RENDER_PT_gpencil_export"

    use_freestyle_gpencil_export = BoolProperty(
        name="Grease Pencil Export",
        description="Export Freestyle edges to Grease Pencil"
    )
    '''
    draw_mode = EnumProperty(
        name="Draw Mode",
        items=(
            # ('2DSPACE', "2D Space", "Export a single frame", 0),
            ('3DSPACE', "3D Space", "Export an animation", 1),
            # ('2DIMAGE', "2D Image", "", 2),
            ('SCREEN', "Screen", "", 3),
            ),
        default='3DSPACE'
    )
    '''
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
    bl_label = "Freestyle to Grease Pencil"
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

        #row = layout.row()
        #row.prop(gp, "draw_mode", expand=True)

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

# ~ ~ ~ 

class LatkProperties(bpy.types.PropertyGroup):
    """Properties for Latk"""
    bl_idname = "GREASE_PENCIL_PT_LatkProperties"

    bakeMesh = BoolProperty(
    	name="Auto Bake Curves",
    	description="Off: major speedup if you're staying in Blender. On: slow but keeps everything exportable.",
    	default=False
    )

    saveLayers = BoolProperty(
    	name="Save Layers",
    	description="Save every layer to its own file.",
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

    '''
    hide_mode = EnumProperty(
        name="Hide Mode",
        items=(
            ("HIDE", "Hide", "Hide inactive frames", 0),
            ("SCALE", "Scale", "Scale inactive frames", 1)
        ),
        default="HIDE"
    )
    '''

    material_set_mode = EnumProperty(
        name="Affects",
        items=(
            ("ALL", "All", "All materials", 0),
            ("SELECTED", "Selected", "Selected materials", 1)
        ),
        default="ALL"
    )

    material_shader_mode = EnumProperty(
        name="Shader",
        items=(
            ("DIFFUSE", "Diffuse", "Diffuse shader", 0),
            #("EMISSION", "Emission", "Emission shader", 1),
            ("PRINCIPLED", "Principled", "Principled shader", 1) #2)
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

        #row = layout.row()
        #row.prop(latk, "hide_mode", expand=True)

        row = layout.row()
        row.prop(latk, "remesh_mode", expand=True)

        # ~ ~ ~ 

        row = layout.row()
        row.operator("latk_button.mtlshader")

        row = layout.row()
        row.prop(latk, "material_set_mode")
        row.prop(latk, "material_shader_mode")

        # ~ ~ ~ 

        row = layout.row()
        row.prop(latk, "writeStrokeSteps")
        row.prop(latk, "writeStrokePoints")
        row.operator("latk_button.writeonstrokes")

        row = layout.row()
        row.prop(latk, "numSplitFrames")
        row.operator("latk_button.splf")

        row = layout.row()
        row.operator("latk_button.bakeselected")
        #row.operator("latk_button.bakeall")
        row.operator("latk_button.strokesfrommesh")

        row = layout.row()
        row.prop(latk, "bakeMesh")
        row.prop(latk, "saveLayers")
        row.prop(latk, "vertexColorName")

class Latk_Button_Gpmesh(bpy.types.Operator):
    """Mesh all GP strokes. Takes a while.."""
    bl_idname = "latk_button.gpmesh"
    bl_label = "MESH ALL"
    bl_options = {'UNDO'}
    
    def execute(self, context):
        latk_settings = bpy.context.scene.latk_settings
        gpMesh(_thickness=latk_settings.thickness, _remesh=latk_settings.remesh_mode.lower(), _resolution=latk_settings.resolution, _bevelResolution=latk_settings.bevelResolution, _decimate=latk_settings.decimate, _bakeMesh=latk_settings.bakeMesh, _joinMesh=latk_settings.bakeMesh, _saveLayers=False, _vertexColorName=latk_settings.vertexColorName)
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
        meshToGp()
        return {'FINISHED'}

class Latk_Button_BakeSelected(bpy.types.Operator):
    """Bake selected curves to exportable meshes"""
    bl_idname = "latk_button.bakeselected"
    bl_label = "Bake Curve"
    bl_options = {'UNDO'}
    
    def execute(self, context):
        latk_settings = bpy.context.scene.latk_settings
        decimateAndBake(_decimate=latk_settings.decimate)
        return {'FINISHED'}

'''
class Latk_Button_BakeAllCurves(bpy.types.Operator):
    """Bake all curves to exportable meshes"""
    bl_idname = "latk_button.bakeall"
    bl_label = "Bake All Curves"
    bl_options = {'UNDO'}
    
    def execute(self, context):
        latk_settings = bpy.context.scene.latk_settings
        target = matchName("latk")
        decimateAndBake(target, _decimate=latk_settings.decimate)
        return {'FINISHED'}
'''

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
    bl_label = "Material Set"
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
    if (bpy.context.user_preferences.addons[__name__].preferences.extraFormats == True):
        self.layout.operator(ImportGml.bl_idname, text="Latk - GML (.gml)")
        self.layout.operator(ImportNorman.bl_idname, text="Latk - Norman (.json)")

def menu_func_export(self, context):
    self.layout.operator(ExportLatkJson.bl_idname, text="Latk Animation (.json)")
    self.layout.operator(ExportLatk.bl_idname, text="Latk Animation (.latk)")
    if (bpy.context.user_preferences.addons[__name__].preferences.extraFormats == True):
        #self.layout.operator(ExportGml.bl_idname, text="Latk - GML (.gml)")
        self.layout.operator(ExportSvg.bl_idname, text="Latk - SVG SMIL (.svg)")
        self.layout.operator(ExportPainter.bl_idname, text="Latk - Corel Painter (.txt)")

#classes = (FreestyleGPencil, FreestyleGPencil_Panel)

def register():
    bpy.utils.register_module(__name__)

    bpy.types.Scene.latk_settings = PointerProperty(type=LatkProperties)
    bpy.types.INFO_MT_file_import.append(menu_func_import)
    bpy.types.INFO_MT_file_export.append(menu_func_export)

    # freestyle
    #for cls in classes:
        #bpy.utils.register_class(cls)
    bpy.types.Scene.freestyle_gpencil_export = PointerProperty(type=FreestyleGPencil)
    #~
    parameter_editor.callbacks_lineset_pre.append(export_fill)
    parameter_editor.callbacks_lineset_post.append(export_stroke)
    # bpy.app.handlers.render_post.append(export_stroke)
    #print("anew")

def unregister():
    bpy.utils.unregister_module(__name__)

    del bpy.types.Scene.latk_settings
    bpy.types.INFO_MT_file_import.remove(menu_func_import)
    bpy.types.INFO_MT_file_export.remove(menu_func_export)

    # freestyle
    #for cls in classes:
        #bpy.utils.register_class(cls)
    del bpy.types.Scene.freestyle_gpencil_export
    #~
    parameter_editor.callbacks_lineset_pre.remove(export_fill)
    parameter_editor.callbacks_lineset_post.remove(export_stroke)

if __name__ == "__main__":
    register()

# * * * * * * * * * * * * * * * * * * * * * * * * * *
# * * * * * * * * * * * * * * * * * * * * * * * * * *
# * * * * * * * * * * * * * * * * * * * * * * * * * *

# END
