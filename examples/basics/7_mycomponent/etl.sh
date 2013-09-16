#!/bin/sh
#
# ETL for copying a file to standard output with custom component.
#
# Shortcut to call Stetl main.py with etl config.
#

# Usually requried in order to have Python find your package
PYTHONPATH=.:$PYTHONPATH

stetl -c etl.cfg

