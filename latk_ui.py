# http://michelanders.blogspot.ca/p/creating-blender-26-python-add-on.html
def MyFunction(context):
    print("Hello World")

class LightingArtist(bpy.types.Operator):
    bl_idname = "object.lightning_artist"
    bl_label = "Lightning Artist"
    bl_options = {'REGISTER', 'UNDO'}
    #~
    @classmethod
    def poll(cls, context): ### poll handles context check, preventing a RuntimeError
        if context.object != None: ### check that an object is selected
            return context.object.select
        return False
    #~
    def execute(self, context): ### executes after invoke, possibly repeating as user adjusts values
        MyFunction(context)
        return {'FINISHED'}
    #~
    def invoke(self, context, event): ### invoke usually defines properties for execute(), with user input
        return self.execute(context)

def menu_draw(self, context):
    self.layout.operator(LightingArtist.bl_idname, "LightningArtist") ### menu item for this class

def register():
    bpy.utils.register_module(__name__) ### module registration registers all classes
    bpy.types.VIEW3D_MT_object.append(menu_draw) ### add module menu item to menu (identify menus with mouse hover)

def unregister():
    bpy.types.VIEW3D_MT_object.remove(menu_draw) ### unregister must mirror register
    bpy.utils.unregister_module(__name__)

if __name__ == "__main__":
    register()

# * * * * * * * * * * * * * * * * * * * * * * * * * *
# * * * * * * * * * * * * * * * * * * * * * * * * * *
# * * * * * * * * * * * * * * * * * * * * * * * * * *

# END
