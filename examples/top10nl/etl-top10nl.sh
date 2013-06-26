#!/bin/bash
#
# ETL for Top10NL using Stetl.
#
# Author: Just van den Broecke
#

# For substitutable args see all strings in {arg} in etl-top10nl.cfg
# <db> <host> <port> <user> <password> <schema> <temp_dir> <max_features> <gml_files> <multi_opts>

# gml_files=/Users/just/geodata/top10nl/TOP10NL_GML_50D_Blokken_september_2012/GML_50D_Blokken/Top10NL_05Oost.gml

gml_files=input

# May use: these options
# Note: '~' is used a s space separator
# multi_opts=-splitlistfields~-maxsubfields 1
# multi_opts=-splitlistfields
# multi_opts=-fieldTypeToString~StringList
# multi_opts=~

multi="multi_opts=-fieldTypeToString~StringList"
python ../../stetl/main.py -c etl-top10nl.cfg -a "database=top10nl host=localhost port=5432 user=top10nl password=top10nl schema=test temp_dir=temp max_features=20 gml_files=$gml_files $multi"


