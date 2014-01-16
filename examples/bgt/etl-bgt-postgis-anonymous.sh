#!/bin/bash
#
# ETL for BGT using Stetl.
#
# Author: Just van den Broecke
# Modified: Thijs Brentjens
#
# PYTHONPATH=${PYTHONPATH}:../..

#input_file="input/20130814_GML_crotec_input.gml"
input_file="input/Maastricht_GML_20130924.gml"

# Databasse connection
host="localhost"
port="5432"
user="myusername"
database="mydatabasename"
password="mypassword"
schema="public"

stetl -c etl-bgt-postgis.cfg -a "gml_input=$input_file host=$host port=$port user=$user database=$database  password=$password schema=$schema max_in_memory_features=100000"

