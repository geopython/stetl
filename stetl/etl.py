# -*- coding: utf-8 -*-
#
# Main ETL program.
#
# Author: Just van den Broecke
#
import os
import sys
try:
    from ConfigParser import ConfigParser
except ImportError:
    from configparser import ConfigParser
try:
    from version import __version__
except ImportError:
    from .version import __version__
try:
    from util import Util
except ImportError:
    from .util import Util
try:
    from chain import Chain
except ImportError:
    from .chain import Chain
try:
    import StringIO
except ImportError:
    from io import StringIO

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

        log.info("INIT - Stetl version is %s" % __version__)

        self.options_dict = options_dict
        config_file = self.options_dict.get('config_file')

        if config_file is None or not os.path.isfile(config_file):
            log.error('No config file found at: %s' % config_file)
            sys.exit(1)

        ETL.CONFIG_DIR = os.path.dirname(os.path.abspath(config_file))
        log.info("Config/working dir =%s" % ETL.CONFIG_DIR)

        self.configdict = ConfigParser()

        sys.path.append(ETL.CONFIG_DIR)

        try:
            log.info("Reading config_file = %s" % config_file)
            if args_dict:
                log.info("Substituting %d args in config file from args_dict: %s" % (len(args_dict), str(args_dict)))
                # Get config file as string
                f = open(config_file, 'r')
                config_str = f.read()
                f.close()

                # Do replacements  see http://docs.python.org/2/library/string.html#formatstrings
                config_str = config_str.format(**args_dict)

                log.info("Substituting args OK")
                # Put Config string into buffer (readfp() needs a readline() method)
                config_buf = StringIO.StringIO(config_str)

                # Parse config from file buffer
                self.configdict.readfp(config_buf, config_file)
            else:
                # Parse config file directly
                self.configdict.read(config_file)
        except (Exception) as e:
            log.error("Fatal Error reading config file: err=%s" % str(e))


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
            chain = Chain(chain_str.strip(), self.configdict)
            chain.assemble()

            # Run the ETL for this Chain
            chain.run()

        Util.end_timer(t1, "total ETL")

        log.info("ALL DONE")
