#!/bin/sh
#
# ETL for copying a file to standard output.
#
# Shortcut to call Stetl main.py with etl config.
#
stetl=stetl

# PYTHONPATH=${PYTHONPATH}:../../..
# stetl=../../../stetl/main.py

$stetl  -c etl.cfg

