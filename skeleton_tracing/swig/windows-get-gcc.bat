@echo off

cd %~dp0
powershell -Command "Invoke-WebRequest https://github.com/skeeto/w64devkit/releases/download/v1.20.0/w64devkit-1.20.0.zip -OutFile w64devkit.zip"
powershell Expand-Archive w64devkit.zip -DestinationPath .
del w64devkit.zip

echo Move w64devkit to desired location and add bin directory as environment variable.

@pause

