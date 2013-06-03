#!/bin/sh
#
# Shortcut to run all basic examples.
#

for dir in `echo [0-9]*`; do
	cd $dir
	./etl.sh
	cd ..
done



