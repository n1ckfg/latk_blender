#!/bin/bash

BUILD_TARGET="build/latk.py"

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

FILE_NAMES=( "latk_main.py" "latk_tools.py" "latk_rw.py" "latk_mesh.py" )

#for i in "${FILE_NAMES[@]}"
#do
	#:
	#cat $i > lightning_artist.py
#done

cat ${FILE_NAMES[0]} ${FILE_NAMES[1]} ${FILE_NAMES[2]} ${FILE_NAMES[3]} > $BUILD_TARGET

cp $BUILD_TARGET "${HOME}/Library/Application Support/Blender/2.77/scripts/addons/"
