#!/bin/bash
#
# Shortcut to run all basic examples.
#

for dir in `echo [0-9]*`; do
	pushd $dir
	echo "==== running etl.sh for $dir ===="
	./etl.sh
	popd
done
