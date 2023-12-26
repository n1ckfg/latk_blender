swig -python trace_skeleton.i

# UBUNTU
# https://github.com/LingDong-/skeleton-tracing/issues/14
gcc -fPIC -O3 -c trace_skeleton.c trace_skeleton_wrap.c -I/$(python3-config --cflags)
g++ -shared $(python3-config --cflags --ldflags) *.o -o _trace_skeleton.so

# quick tests
# python3 -i -c "import trace_skeleton; trace_skeleton.trace('\0\0\0\1\1\1\0\0\0',3,3); print(trace_skeleton.len_polyline());"
# python3 -i -c "import trace_skeleton; print(trace_skeleton.from_list([0,0,0,1,1,1,0,0,0],3,3))"

#python3 example.py