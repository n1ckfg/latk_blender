# ##### BEGIN GPL LICENSE BLOCK #####
#
#  This program is free software; you can redistribute it and/or
#  modify it under the terms of the GNU General Public License
#  as published by the Free Software Foundation; either version 2
#  of the License, or (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with this program; if not, write to the Free Software Foundation,
#  Inc., 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301, USA.
#
# ##### END GPL LICENSE BLOCK #####
 
bl_info = { ### required info block for add-on panel in Preferences
    "name": "Add-on Name",
    "author": "Your Name",
    "version": (0,1),
    "blender": (2, 72, 0),
    "location": "View3D > Object",
    "description": "Add-on description for Preferences panel",
    "category": "Object"} ### "location" advises user where the new functionality can be found, "category" is add-on group in Preferences panel
#### Help: http://wiki.blender.org/index.php/Dev:2.5/Py/Scripts/Guidelines/Addons

import bpy ### required for access to blender
#import mathutils ### you may need this for vector and other math
#### Help: http://www.blender.org/api/blender_python_api_2_72_release/mathutils.html

#def MyFunction(context, boolArg, intArg, floatvecArg): ### alternative function definition to use if arguments are passed, see execute() below
def MyFunction(context):
	print("Hello World")

class MyOperator(bpy.types.Operator): ### type of class definition - Operator, Panel, etc.
	'''Tooltip for MyOperator'''
	bl_idname = "object.my_operator" ### Internal ID name of this operator. Starts with operator group of bpy.ops., followed by dot, then lowercase name
	bl_label = "My Operator" ### interface name of this class
	bl_options = {"REGISTER", "UNDO"} ### register operator in info window, and enable undo. (To hide from search, use "INTERNAL" also.)
#### Help: http://www.blender.org/api/blender_python_api_2_72_release/bpy.types.Operator.html#bpy.types.Operator.bl_options

	### use operator properties to display buttons in Toolshelf, allowing user to set values for execute()
#	my_bool = bpy.props.BoolProperty(name="True or False", default=1, description="Boolean")
#	my_int = bpy.props.IntProperty(name="Enter Number:", default=1, description="Number", min=1, max=10000, subtype="NONE")
#	my_floatvec = bpy.props.FloatVectorProperty(name="XYZ Vector:", default=(0.0,0.0,0.0), min=0, max=10000, description="XYZ Vector", subtype="NONE")
#### Help: http://www.blender.org/api/blender_python_api_2_72_release/bpy.props.html

	@classmethod
	def poll(cls, context): ### poll handles context check, preventing a RuntimeError
		if context.object != None: ### check that an object is selected
			return context.object.select
		return False

	def execute(self, context): ### executes after invoke, possibly repeating as user adjusts values
		MyFunction(context)
#		MyFunction(context, self.my_bool, self.my_int, self.my_floatvec) ### alternative call, using properties defined earlier (adjust MyFunction to use it)
#### Help: http://www.blender.org/api/blender_python_api_2_72_release/bpy.types.Operator.html#bpy.types.Operator.report
		return {'FINISHED'}

	def invoke(self, context, event): ### invoke usually defines properties for execute(), with user input
#### Help: http://www.blender.org/api/blender_python_api_2_72_release/bpy.types.Event.html
		return self.execute(context)

def menu_draw(self, context):
#	self.layout.operator_context = 'INVOKE_DEFAULT' ### be sure to run invoke() before execute() to take user input
#### Help: http://www.blender.org/api/blender_python_api_2_72_release/bpy.ops.html#execution-context
	self.layout.operator(MyOperator.bl_idname, "My Operator") ### menu item for this class

addon_keymaps = [] ### store keymaps here to access after registration

def register():
	bpy.utils.register_module(__name__) ### module registration registers all classes
	bpy.types.VIEW3D_MT_object.append(menu_draw) ### add module menu item to menu (identify menus with mouse hover)

	wm = bpy.context.window_manager ### register the keymap
	km = wm.keyconfigs.addon.keymaps.new(name='3D View', space_type='VIEW_3D') ### space type where shortcut will work
#### Help: http://www.blender.org/api/blender_python_api_2_72_release/bpy.types.KeyMaps.html
	kmi = km.keymap_items.new(MyOperator.bl_idname, 'A', 'PRESS', shift=True, ctrl=True, alt=True)
#### Help: http://www.blender.org/api/blender_python_api_2_72_release/bpy.types.KeyMapItems.html
	addon_keymaps.append((km, kmi))

def unregister():
	bpy.types.VIEW3D_MT_object.remove(menu_draw) ### unregister must mirror register
	bpy.utils.unregister_module(__name__)

	for km, kmi in addon_keymaps: ### remove the keymap
		km.keymap_items.remove(kmi)
	addon_keymaps.clear()

if __name__ == '__main__': ### for use of this script in Blender Text window
	register()

