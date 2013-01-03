#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Main SETL program.
#
# Author: Just van den Broecke
#
from setl.etl import ETL
from setl.util import Util
import argparse #apt-get install python-argparse

log = Util.get_log('main')

def main():
    argparser = argparse.ArgumentParser(description='Invoke sETL')
    argparser.add_argument('args', type=str, help='optional override settings', metavar='args', nargs='*')
    argparser.add_argument('-c ',  '--config', type=str,   help='ETL config file in .ini format' , dest='config_file', default='etl.cfg')
    args = argparser.parse_args()

    # Do the ETL
    etl = ETL(args, args.args)
    etl.run()

if __name__ == "__main__":
    main()
