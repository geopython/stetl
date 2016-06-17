#!/bin/sh
#
# Test Stetl Docker image.
# Simple ETL for copying a file to standard output.
#
#
sudo docker run -v `pwd`:`pwd` -w `pwd`  -t -i justb4/stetl:latest -c etl.cfg


