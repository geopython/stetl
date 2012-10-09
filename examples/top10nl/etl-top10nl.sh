#!/bin/bash
#
# ETL for Top10NL using SETL.
#
# Author: Just van den Broecke
#
# PYTHONPATH=${PYTHONPATH}:../..
python ../../src/main.py -c etl-top10nl.cfg
