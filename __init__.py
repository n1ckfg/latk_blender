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
