swig -python trace_skeleton.i

# OS X
PYTHON_VERSION=3.10
PYTHON_VERSION_FULL=3.10.6
#PYTHON_PATH=/usr/local/Cellar/python@$PYTHON_VERSION/$PYTHON_VERSION_FULL/Frameworks/Python.framework/Versions/$PYTHON_VERSION
PYTHON_PATH=~/.pyenv/versions/$PYTHON_VERSION_FULL
PYTHON_INCLUDE=$PYTHON_PATH/include/python$PYTHON_VERSION
PYTHON_LIB=$PYTHON_PATH/lib/libpython$PYTHON_VERSION.a

gcc -O3 -c trace_skeleton.c trace_skeleton_wrap.c -I$PYTHON_INCLUDE
gcc $(python3-config --ldflags) -dynamiclib *.o -o _trace_skeleton.so -I$PYTHON_LIB -undefined dynamic_lookup

# quick tests
# python3 -i -c "import trace_skeleton; trace_skeleton.trace('\0\0\0\1\1\1\0\0\0',3,3); print(trace_skeleton.len_polyline());"
# python3 -i -c "import trace_skeleton; print(trace_skeleton.from_list([0,0,0,1,1,1,0,0,0],3,3))"

#python3 example.py