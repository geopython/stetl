#!/bin/bash
#
# ETL for BGT using Stetl.
#
# Author: Just van den Broecke
#
# PYTHONPATH=${PYTHONPATH}:../..

input_file="input/20130814_GML_crotec_input.gml"
# input_file=/Users/just/project/stetl/contrib/duiv/data/20130814_GML_crotec_result.xml
output_file="output/20130814_GML_crotec_output.gml"
# output_file="/Users/just/project/stetl/contrib/duiv/data/20130814_GML_crotec_output.gml"

stetl -c etl-bgt.cfg -a "gml_input=$input_file gml_output=$output_file max_in_memory_features=100000"

