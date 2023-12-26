@echo off

rem https://www.swig.org/Doc1.3/Windows.html

rem provide paths to
rem https://github.com/skeeto/w64devkit
rem https://www.swig.org/download.html

swig -python trace_skeleton.i

rem WINDOWS
rem https://github.com/LingDong-/skeleton-tracing/issues/14
rem gcc -fPIC -O3 -c trace_skeleton.c trace_skeleton_wrap.c -I/$(python3-config --cflags)
rem g++ -shared $(python3-config --cflags --ldflags) *.o -o _trace_skeleton.so
gcc -fPIC -O3 -c trace_skeleton.c trace_skeleton_wrap.c -I%HOMEDRIVE%%HOMEPATH%\AppData\Local\Programs\Python\Python310\include
g++ -shared *.o -o _trace_skeleton.pyd -L%HOMEDRIVE%%HOMEPATH%\AppData\Local\Programs\Python\Python310\libs -lpython310

rem quick tests
rem python3 -i -c "import trace_skeleton; trace_skeleton.trace('\0\0\0\1\1\1\0\0\0',3,3); print(trace_skeleton.len_polyline());"
rem python3 -i -c "import trace_skeleton; print(trace_skeleton.from_list([0,0,0,1,1,1,0,0,0],3,3))"

rem python3 example.py

@pause
