#!/bin/sh
#
# Shortcut to call Stetl main.py with etl config.
#
# Author: Just van den Broecke
#
#
#

# Two ways to pass arguments to be substituted in the etl.cfg {arg} paramters

# Option 1: using command line args
stetl  -c etl.cfg -a "in_xml=input/cities.xml in_xsl=cities2gml.xsl out_xml=output/gmlcities.gml"

# Option 2: using a properties file
stetl  -c etl.cfg -a etl.args

# Option 3: multiple -a options e.g. overriding one or more default args (file)
stetl  -c etl.cfg -a etl.args -a "in_xml=input/amsterdam.xml"
