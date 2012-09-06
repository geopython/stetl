#!/bin/bash
#
# ETL for BGT using sETL.
#
# Author: Just van den Broecke
#
export PYTHONPATH=${PYTHONPATH}:../..
python ../../setl/main.py -c etl-bgt.cfg
