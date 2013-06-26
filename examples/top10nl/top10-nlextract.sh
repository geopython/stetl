#!/bin/sh
#
# Auteur: Just van den Broecke
# Test script om Stetl resultaten met NLExtract te  vergelijken
#
TOP10NL_HOME=/Users/just/project/ogg/nlextract/git/top10nl
TOP10NL_BIN=$TOP10NL_HOME/bin
TOP10NL_TEST_TMP=tmp_nlx

# Temp dir voor gesplitste GML files and .gfs bestanden
/bin/rm -rf $TOP10NL_TEST_TMP
mkdir $TOP10NL_TEST_TMP

# loopt vast op XML parsing met NLX (315 MB)
# GML_FILE=/Users/just/geodata/top10nl/TOP10NL_GML_Filechunks_september_2012/GML_Filechunks/Top10NL_000001.gml
# GML_FILE=/Users/just/geodata/top10nl/TOP10NL_GML_Filechunks_september_2012/GML_Filechunks/Top10NL_000002.gml
GML_FILE=/Users/just/geodata/top10nl/TOP10NL_GML_50D_Blokken_september_2012/GML_50D_Blokken/Top10NL_05Oost.gml
GML_FILE=input
python $TOP10NL_BIN/top10extract.py $GML_FILE --dir $TOP10NL_TEST_TMP
