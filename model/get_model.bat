@echo off

cd %~dp0

powershell -Command "Invoke-WebRequest https://fox-gieg.com/patches/github/n1ckfg/latk_blender/model/model.zip -OutFile model.zip"
powershell Expand-Archive model.zip -DestinationPath .
del model.zip

rem @pause