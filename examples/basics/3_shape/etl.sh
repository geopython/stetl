#!/bin/sh
#
# Shortcut to call SETL main.py with etl config.
#
# Author: Just van den Broecke
#
rm -rf output/* temp/*
python ../../../src/main.py -c etl.cfg


