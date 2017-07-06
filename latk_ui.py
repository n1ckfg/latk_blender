# 9 of 9. UI

class ImportLatk(bpy.types.Operator, ImportHelper):
    """Load a Latk File"""
    bl_idname = "import_scene.latk"
    bl_label = "Import Latk"
    bl_options = {'PRESET', 'UNDO'}

    filename_ext = ".json"
    filter_glob = StringProperty(
            default="*.json;*.latk",
            options={'HIDDEN'},
            )

    def execute(self, context):
        import latk as la
        keywords = self.as_keywords(ignore=("axis_forward", "axis_up", "filter_glob", "split_mode"))
        if bpy.data.is_saved and context.user_preferences.filepaths.use_relative_paths:
            import os
            #keywords["relpath"] = os.path.dirname(bpy.data.filepath)
        #~
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

class ExportLatk(bpy.types.Operator, ExportHelper):
    """Save a Latk File"""

    bl_idname = "export_scene.latk"
    bl_label = 'Export Latk'
    bl_options = {'PRESET'}

    filename_ext = ".json"
    filter_glob = StringProperty(
            default="*.json;*.latk",
            options={'HIDDEN'},
            )

    bake = BoolProperty(name="Bake Frames", description="Bake Keyframes to All Frames", default=True)

    def execute(self, context):
        import latk as la
        keywords = self.as_keywords(ignore=("axis_forward", "axis_up", "filter_glob", "split_mode", "check_existing", "bake"))
        if bpy.data.is_saved and context.user_preferences.filepaths.use_relative_paths:
            import os
            #keywords["relpath"] = os.path.dirname(bpy.data.filepath)
        #~
        keywords["bake"] = self.bake
        #~
        la.writeBrushStrokes(**keywords)
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

class ImportGml(bpy.types.Operator, ImportHelper):
    """Load a Gml File"""
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
    """Save an SVG SMIL File"""

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
    """Save an SVG SMIL File"""

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

def menu_func_import(self, context):
    self.layout.operator(ImportLatk.bl_idname, text="Latk Animation (.json)")
    self.layout.operator(ImportGml.bl_idname, text="Graffiti Markup Language (.gml)")

def menu_func_export(self, context):
    self.layout.operator(ExportLatk.bl_idname, text="Latk Animation (.json)")
    #self.layout.operator(ExportGml.bl_idname, text="Graffiti Markup Language (.gml)")
    self.layout.operator(ExportSvg.bl_idname, text="SVG SMIL Animation (.svg)")
    self.layout.operator(ExportPainter.bl_idname, text="Corel Painter Script (.txt)")

def register():
    bpy.utils.register_module(__name__)

    bpy.types.INFO_MT_file_import.append(menu_func_import)
    bpy.types.INFO_MT_file_export.append(menu_func_export)

def unregister():
    bpy.utils.unregister_module(__name__)

    bpy.types.INFO_MT_file_import.remove(menu_func_import)
    bpy.types.INFO_MT_file_export.remove(menu_func_export)

if __name__ == "__main__":
    register()

# * * * * * * * * * * * * * * * * * * * * * * * * * *
# * * * * * * * * * * * * * * * * * * * * * * * * * *
# * * * * * * * * * * * * * * * * * * * * * * * * * *

# END
