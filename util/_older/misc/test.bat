@echo off

cd %~dp0
"C:\Program Files\blender\blender" "C:\Users\nick\Desktop\vertex_color_test.blend" --background --python mesh_color.py

@pause