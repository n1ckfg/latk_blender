@echo off

set BUILD_TARGET=..\latk_blender.py
cd /D %~dp0

del %BUILD_TARGET%

copy /b latk.py\latk.py+latk_main.py+latk_tools.py+latk_rw.py+latk_mtl.py+latk_mesh.py+latk_draw.py+latk_shortcuts.py+latk_ui.py+latk_tilt.py+latk_svg.py %BUILD_TARGET%

rem copy %BUILD_TARGET% "%homepath%\AppData\Roaming\Blender Foundation\Blender\2.77\scripts\addons"
rem copy %BUILD_TARGET% "%homepath%\AppData\Roaming\Blender Foundation\Blender\2.78\scripts\addons"
rem copy %BUILD_TARGET% "%homepath%\AppData\Roaming\Blender Foundation\Blender\2.79\scripts\addons"
rem copy %BUILD_TARGET% "%homepath%\AppData\Roaming\Blender Foundation\Blender\2.80\scripts\addons"
rem copy %BUILD_TARGET% "%homepath%\AppData\Roaming\Blender Foundation\Blender\2.81\scripts\addons"
rem copy %BUILD_TARGET% "%homepath%\AppData\Roaming\Blender Foundation\Blender\2.82\scripts\addons"
copy %BUILD_TARGET% "%homepath%\AppData\Roaming\Blender Foundation\Blender\2.83\scripts\addons"
copy %BUILD_TARGET% "%homepath%\AppData\Roaming\Blender Foundation\Blender\2.90\scripts\addons"
copy %BUILD_TARGET% "%homepath%\AppData\Roaming\Blender Foundation\Blender\2.91\scripts\addons"
copy %BUILD_TARGET% "%homepath%\AppData\Roaming\Blender Foundation\Blender\2.92\scripts\addons"

@pause