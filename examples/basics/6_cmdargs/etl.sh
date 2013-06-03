#!/bin/sh
#
# Shortcut to call stETL main.py with etl config.
#
# Author: Just van den Broecke
#
python ../../../stetl/main.py -c etl.cfg -a "in_xml=input/cities.xml in_xsl=cities2gml.xsl out_xml=output/gmlcities.gml"


