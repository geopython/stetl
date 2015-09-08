#!/bin/bash
#
# ETL for Top10NL using Stetl.
#
# Author: Just van den Broecke
#

# For substitutable args see all strings in {arg} in etl-top10nl.cfg  and example values in etl-top10.props


python ../../stetl/main.py -c etl-top10nl.cfg -a etl-top10nl.props

