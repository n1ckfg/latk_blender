@echo off

cd %~dp0

powershell -Command "Invoke-WebRequest https://fox-gieg.com/patches/github/n1ckfg/latk_ml_003/model/model.zip -OutFile model.zip"
powershell Expand-Archive model.zip -DestinationPath .
del model.zip

@pause