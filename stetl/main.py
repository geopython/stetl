#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Main Stetl program.
#
# Author: Just van den Broecke
#
from etl import ETL
from util import Util
from version import __version__
import argparse #apt-get install python-argparse

log = Util.get_log('main')

def parse_args():
    log.info("Stetl version = %s" % __version__)

    argparser = argparse.ArgumentParser(description='Invoke Stetl')
    argparser.add_argument('-c ', '--config', type=str, help='ETL config file in .ini format', dest='config_file',
                           required=True)

    argparser.add_argument('-s ', '--section', type=str, help='Section in the config file to execute, default is [etl]',
                           dest='config_section', required=False)

    argparser.add_argument('-a ', '--args', type=str,
                           help='Arguments to be substituted for {argN}s in config file, as "arg1=foo arg2=bar" etc',
                           dest='config_args', required=False)

    args = argparser.parse_args()

    if args.config_args:
        # Convert string to dict: http://stackoverflow.com/a/1248990
        args.config_args = Util.string_to_dict(args.config_args)

    return args

def main():
    """The `main` function, to be called from commandline, like `python src/main.py -c etl.cfg`.

    Args:
       -c  --config <config_file>  the Stetl config file.
       -s  --section <section_name> the section in the Stetl config (ini) file to execute (default is [etl]).
       -a  --args <arglist> substitutable args for symbolic, {arg}, values in Stetl config file, in format "arg1=foo arg2=bar" etc.

    """
    args = parse_args()

    # Do the ETL
    etl = ETL(vars(args), args.config_args)
    etl.run()


if __name__ == "__main__":
    main()
