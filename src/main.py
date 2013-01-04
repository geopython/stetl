#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Main sETL program.
#
# Author: Just van den Broecke
#
from setl.etl import ETL
from setl.util import Util
import argparse #apt-get install python-argparse

log = Util.get_log('main')

def main():
    argparser = argparse.ArgumentParser(description='Invoke sETL')
    argparser.add_argument('-c ',  '--config', type=str,   help='ETL config file in .ini format' , dest='config_file', required=True)
    argparser.add_argument('-a ',  '--args', type=str,   help='Arguments to be substituted for {argN}s in config file, as "arg1=foo arg2=bar" etc' , dest='config_args', required=False)
    args = argparser.parse_args()

    if args.config_args:
        # Convert string to dict: http://stackoverflow.com/a/1248990
        args.config_args = Util.string_to_dict(args.config_args)

    # Do the ETL
    etl = ETL(args, args.config_args)
    etl.run()

if __name__ == "__main__":
    main()
