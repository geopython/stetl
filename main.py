#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Main ETL program.
#
# Author: Just van den Broecke
#
from setl.etl import ETL

def main():
    # Do the ETL
    etl = ETL()
    etl.run()

if __name__ == "__main__":
    main()
