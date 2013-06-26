#!/bin/bash
#
# ETL for BGT using Stetl.
#
# Author: Just van den Broecke
#
# PYTHONPATH=${PYTHONPATH}:../..
python ../../stetl/main.py -c etl-bgt.cfg
