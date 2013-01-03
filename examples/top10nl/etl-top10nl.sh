#!/bin/bash
#
# ETL for Top10NL using SETL.
#
# Author: Just van den Broecke
#

# For positional args see etl-top10nl.cfg
# <db> <host> <port> <user> <password> <schema> <tmp_dir> <split_size> <GML files, dirs paths etc>

# gml_files=/Users/just/geodata/top10nl/TOP10NL_GML_50D_Blokken_september_2012/GML_50D_Blokken/Top10NL_05Oost.gml

gml_files=input
python ../../src/main.py -c etl-top10nl.cfg top10nl localhost 5432 top10nl top10nl test temp 20 $gml_files


