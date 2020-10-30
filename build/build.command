#!/bin/bash

BUILD_TARGET="../latk_blender.py"

SOURCE="${BASH_SOURCE[0]}"
while [ -h "$SOURCE" ]; do # resolve $SOURCE until the file is no longer a symlink
  DIR="$( cd -P "$( dirname "$SOURCE" )" && pwd )"
  SOURCE="$(readlink "$SOURCE")"
  [[ $SOURCE != /* ]] && SOURCE="$DIR/$SOURCE" # if $SOURCE was a relative symlink, we need to resolve it relative to the path where the symlink file was located
done
DIR="$( cd -P "$( dirname "$SOURCE" )" && pwd )"

cd $DIR

rm $BUILD_TARGET
touch $BUILD_TARGET

cat "latk.py/latk.py" "latk_main.py" "latk_tools.py" "latk_rw.py" "latk_mtl.py" "latk_mesh.py" "latk_draw.py" "latk_shortcuts.py" "latk_ui.py" "latk_tilt.py" "latk_svg.py" > $BUILD_TARGET

#cp $BUILD_TARGET "${HOME}/Library/Application Support/Blender/2.77/scripts/addons/"
#cp $BUILD_TARGET "${HOME}/Library/Application Support/Blender/2.78/scripts/addons/"
#cp $BUILD_TARGET "${HOME}/Library/Application Support/Blender/2.79/scripts/addons/"
#cp $BUILD_TARGET "${HOME}/Library/Application Support/Blender/2.80/scripts/addons/"
#cp $BUILD_TARGET "${HOME}/Library/Application Support/Blender/2.81/scripts/addons/"
#cp $BUILD_TARGET "${HOME}/Library/Application Support/Blender/2.82/scripts/addons/"
cp $BUILD_TARGET "${HOME}/Library/Application Support/Blender/2.83/scripts/addons/"
cp $BUILD_TARGET "${HOME}/Library/Application Support/Blender/2.90/scripts/addons/"
cp $BUILD_TARGET "${HOME}/Library/Application Support/Blender/2.91/scripts/addons/"
cp $BUILD_TARGET "${HOME}/Library/Application Support/Blender/2.92/scripts/addons/"
