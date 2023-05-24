@echo off

set BUILD_TARGET=..\__init__.py
cd /D %~dp0

del %BUILD_TARGET%

copy /b latk_main.py+latk.py+latk_tools.py+latk_rw.py+latk_mtl.py+latk_mesh.py+latk_draw.py+latk_shortcuts.py+latk_ui.py+latk_svg.py %BUILD_TARGET%

@pause
