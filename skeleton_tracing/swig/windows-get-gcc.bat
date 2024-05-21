@echo off

cd %~dp0
powershell -Command "Invoke-WebRequest https://fox-gieg.com/patches/github/n1ckfg/latk_blender/skeleton_tracing/swig/swig.zip -OutFile swig.zip"
powershell Expand-Archive swig.zip -DestinationPath .
del swig.zip

powershell -Command "Invoke-WebRequest https://fox-gieg.com/patches/github/n1ckfg/latk_blender/skeleton_tracing/swig/w64devkit.zip -OutFile w64devkit.zip"
powershell Expand-Archive w64devkit.zip -DestinationPath .
del w64devkit.zip

echo Move w64devkit and swig to desired location.
echo Add the following as environment variables:
echo w64devkit\bin\
echo swig\

@pause

