#!/bin/sh
#
# Shortcut to call Stetl main.py with etl config.
#
# Author: Just van den Broecke
#
stetl  -c etl.cfg -a "in_xml=input/cities.xml in_xsl=cities2gml.xsl out_xml=output/gmlcities.gml"


