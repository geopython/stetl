# -*- coding: utf-8 -*-
#
# Main ETL program.
#
# Author: Just van den Broecke
#
import os
import re
import sys
from ConfigParser import ConfigParser
import version
from util import Util
from chain import Chain
import StringIO

log = Util.get_log('ETL')


class ETL:
    """The main class: builds ETL Chains with connected Components from a config and let them run.

    Usually this class is called via :mod:`main`  but it may be called directly for direct integration.

    """

    CONFIG_DIR = None

    def __init__(self, options_dict, args_dict=None):
        """
        :param options_dict: dictionary with options, now only config_file files with path to config file
        :param args_dict: optional dictionary with arguments to be substituted for symbolic values in config
        :return:

        Assume path to config .ini file is in options dict
        """
        # args_dict is optional and is used to do string substitutions in options_dict.config file

        log.info("INIT - Stetl version is %s" % str(version.__version__))

        self.options_dict = options_dict
        config_file = self.options_dict.get('config_file')

        if config_file is None or not os.path.isfile(config_file):
            log.error('No config file found at: %s' % config_file)
            sys.exit(1)

        ETL.CONFIG_DIR = os.path.dirname(os.path.abspath(config_file))
        log.info("Config/working dir = %s" % ETL.CONFIG_DIR)

        self.configdict = ConfigParser()

        sys.path.append(ETL.CONFIG_DIR)

        config_str = ''
        try:
            # Get config file as string
            log.info("Reading config_file = %s" % config_file)
            f = open(config_file, 'r')
            config_str = f.read()
            f.close()
        except Exception as e:
            log.error("Cannot read config file: err=%s" % str(e))
            raise e

        args_names = list()
        try:
            # Optional: expand symbolic arguments from args_dict and or OS Env
            # ignore errors here as { .. } may appear at random.

            # Parse unique list of argument names from config file string.
            # https://www.machinelearningplus.com/python/python-regex-tutorial-examples/
            args_names = list(set(re.findall('{[A-Z|a-z]\w+}', config_str)))
            args_names = [name.split('{')[1].split('}')[0] for name in args_names]

            # Optional: expand from equivalent env vars
            args_dict = self.env_expand_args_dict(args_dict, args_names)

            # In general all arg names should be present in args dict
            for args_name in args_names:
                if args_name not in args_dict:
                    log.warn("Arg not found in args nor environment: name=%s" % args_name)
                    # raise Exception("name=%s" % args_name)

        except Exception as e:
            log.warn("Expanding config arguments (non fatal yet): %s" % str(e))

        try:
            if args_dict:
                log.info("Substituting %d args in config file from args_dict: %s" % (len(args_names), str(args_names)))

                # Do replacements  see http://docs.python.org/2/library/string.html#formatstrings
                # and render substituted config string
                config_str = config_str.format(**args_dict)

                log.info("Substituting args OK")

        except Exception as e:
            log.error("Error substituting config arguments: err=%s" % str(e))
            raise e

        try:
            # Put Config string into buffer (readfp() needs a readline() method)
            config_buf = StringIO.StringIO(config_str)

            # Parse config from file buffer
            self.configdict.readfp(config_buf, config_file)
        except Exception as e:
            log.error("Error populating config dict from config string: err=%s" % str(e))
            raise e

    def env_expand_args_dict(self, args_dict, args_names):
        """
        Expand values in dict with equivalent values from the
        OS Env. NB vars in OS Env should be prefixed with `STETL_` or `stetl_`
        as to get overrides by accident.

        :return: expanded args_dict or None
        """
        env_dict = os.environ
        for name in env_dict:
            args_key = '_'.join(name.split('_')[1:])
            if name.lower().startswith('stetl_') and args_key in args_names:
                # Get real key, e.g. "STETL_HOST" becomes "HOST"
                # "stetl_host" becomes "host".
                args_value = env_dict[name]
                if not args_dict:
                    args_dict = dict()

                # Set: optionally override any existing value
                args_dict[args_key] = args_value
                log.info("Set/override from env var: %s" % name)

        return args_dict

    def run(self):
        # The main ETL processing
        log.info("START")
        t1 = Util.start_timer("total ETL")

        # Get the ETL Chain pipeline config strings
        # Default is to use the section [etl], but may be overidden on cmd line

        config_section = self.options_dict.get('config_section')
        if config_section is None:
            config_section = 'etl'

        chains_str = self.configdict.get(config_section, 'chains')
        if not chains_str:
            raise ValueError('ETL chain entry not defined in section [etl]')

        # Multiple Chains may be specified in the config
        chains_str_arr = chains_str.split(',')
        for chain_str in chains_str_arr:
            # Build single Chain of components and let it run
            chain = Chain(chain_str, self.configdict)
            chain.assemble()

            # Run the ETL for this Chain
            chain.run()

        Util.end_timer(t1, "total ETL")

        log.info("ALL DONE")
