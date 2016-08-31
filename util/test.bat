@echo off

cd %~dp0
"C:\Program Files\blender\blender" "C:\Users\nick\Desktop\blender_scenes\first_jenny_v002.blend" --background --python mesh_maker.py

@pause