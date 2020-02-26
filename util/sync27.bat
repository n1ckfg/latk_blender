@echo off

cd..
git checkout 2.7
git merge origin/master
git push origin 2.7
git checkout master

@pause
