@echo off

cd /D %~dp0

git submodule init
git submodule update --init --recursive
git submodule sync
git submodule foreach git checkout master
git submodule foreach git reset --hard
git submodule foreach git pull origin master

cd build
build

@pause