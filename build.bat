@echo off

set BUILD_TARGET=build\latk.py
cd %cd%

del %BUILD_TARGET%

copy /b latk_main.py+latk_tools.py+latk_rw.py+latk_mesh.py+latk_test.py %BUILD_TARGET%

copy %BUILD_TARGET% "%homepath%\AppData\Roaming\Blender Foundation\Blender\2.77\scripts\addons"
@pause