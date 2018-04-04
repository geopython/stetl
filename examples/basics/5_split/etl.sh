#!/bin/sh
#
# Shortcut to call Stetl main.py with etl config.
#
# Author: Just van den Broecke
#
stetl=stetl

PYTHONPATH=${PYTHONPATH}:../../..
# stetl=../../../stetl/main.py
$stetl  -c etl.cfg


