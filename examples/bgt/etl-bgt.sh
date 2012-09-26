#!/bin/bash
#
# ETL for BGT using sETL.
#
# Author: Just van den Broecke
#
# PYTHONPATH=${PYTHONPATH}:../..
python ../../src/main.py -c etl-bgt.cfg
