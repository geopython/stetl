#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Main Stetl program.
#
# Author: Just van den Broecke
#
from etl import ETL
from factory import factory
from util import Util
from version import __version__
import argparse  # apt-get install python-argparse
import inspect
import os
import sys

log = Util.get_log('main')


def parse_args(args_list):
    log.info("Stetl version = %s" % __version__)

    argparser = argparse.ArgumentParser(description='Invoke Stetl')
    argparser.add_argument('-c ', '--config', type=str, help='ETL config file in .ini format', dest='config_file',
                           required=False)

    argparser.add_argument('-s ', '--section', type=str, help='Section in the config file to execute, default is [etl]',
                           dest='config_section', required=False)

    argparser.add_argument('-a ', '--args', type=str,
                           help='Arguments or .properties files to be substituted for symbolic {argN}s in Stetl config file,\
                                as -a "arg1=foo arg2=bar" and/or -a args.properties, multiple -a options are possible',
                           dest='config_args', required=False, action='append')

    argparser.add_argument('-d ', '--doc', type=str,
                           help='Get component documentation like its configuration parameters, e.g. stetl doc stetl.inputs.fileinput.FileInput',
                           dest='doc_args', required=False)

    args = argparser.parse_args(args_list)

    if args.config_args:
        args_total = dict()
        for arg in args.config_args:
            if os.path.isfile(arg):
                log.info('Found args file at: %s' % arg)
                args_total = Util.merge_two_dicts(args_total, Util.propsfile_to_dict(arg))
            else:
                # Convert string to dict: http://stackoverflow.com/a/1248990
                args_total = Util.merge_two_dicts(args_total, Util.string_to_dict(arg))

        args.config_args = args_total

    return args


# DEPRECATED, now using @Config which also documents with Sphinx
def print_config_attrs(clazz):
    skip = ['Filter', 'Input', 'Output', 'Component']
    for base in clazz.__bases__:

        if base.__name__ not in skip:
            print_config_attrs(base)

    """Print documentation for Attr object"""

    module_name, _, class_name = clazz.__name__.rpartition('.')
    # print 'From class: %s' % class_name

    attr_count = 0
    for member in clazz.__dict__.keys():
        if member.startswith('cfg_'):
            config_obj = clazz.__dict__[member]
            print ('----------------------------------------------')
            print ('NAME: %s' % member.replace('cfg_', ''))
            print ('MANDATORY: %s' % config_obj.mandatory)
            print ('TYPE: %s' % str(config_obj.type))
            print ('\n%s' % config_obj.doc)
            print ('\nDEFAULT: %s' % str(config_obj.default))
            attr_count += 1

    if attr_count == 0:
        print ('No config attributes or class not yet documented')


def print_classes(package):
    # is_module = inspect.ismodule(class_name)
    import inputs
    import pkgutil
    package = inputs
    for importer, modname, ispkg in pkgutil.walk_packages(path=package.__path__,
                                                          prefix=package.__name__ + '.',
                                                          onerror=lambda x: None):
        print('stetl.' + modname)
        for name, data in inspect.getmembers(modname, inspect.isclass):
            if name == '__builtins__':
                continue
            print name, data


# DEPRECATED, now using @Config which also documents with Sphinx
def print_doc(class_name):
    """Print documentation for class in particular config options"""
    # print_classes(class_name)
    # return

    try:
        # class object from module.class name
        class_obj = factory.class_forname(class_name)
        print ('DOCUMENTATION\n')
        print ('CLASS: %s' % class_name)
        print (class_obj.__doc__)
        # print ('\nConfiguration attributes: \n')
        # print_config_attrs(class_obj)

    except Exception, e:
        log.error("cannot print info class named '%s' e=%s - you made a typo?" % (class_name, str(e)))
        raise e


def main():
    """The `main` function, to be called from commandline, like `python src/main.py -c etl.cfg`.

    Args:
       -c  --config <config_file>  the Stetl config file.
       -s  --section <section_name> the section in the Stetl config (ini) file to execute (default is [etl]).
       -a  --args <arglist> sero or more substitutable args for symbolic, {arg}, values in Stetl config file, in format -a arg1=foo -a arg2=bar etc.
       -d  --doc <class> Get component documentation like its configuration parameters, e.g. stetl --doc stetl.inputs.fileinput.FileInput
       -h  --help get help info

    """

    # Pass arguments explicitly, facilitates testing
    args = parse_args(sys.argv[1:])

    if args.config_file:
        # Do the ETL
        etl = ETL(vars(args), args.config_args)
        etl.run()

    elif args.doc_args:
        print_doc(args.doc_args)
    else:
        print('Unknown option, try stetl -h for help')


if __name__ == "__main__":
    main()
