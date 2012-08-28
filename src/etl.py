#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Main ETL program.
#
# Author: Just van den Broecke
#
import codecs
import optparse
from ConfigParser import ConfigParser
from util import Util, etree, StringIO
from factory import factory

log = Util.get_log('etl')

class ETL:

    def __init__(self):
        usage = "usage: %prog [options]"
        parser = optparse.OptionParser(usage)
        parser.add_option("-c", "--config", action="store", type="string", dest="config_file",
                          default="etl.cfg",
                          help="ETL config file")

        self.options, args = parser.parse_args()

        # Get config file path
        config_file = self.options.config_file
        log.info("config_file = %s" % config_file)
        self.configdict = ConfigParser()
        try:
            # parse config file
            self.configdict.read(config_file)
        except:
            log.warning("Found " + str(config_file) + " but cannot read it.")

    def run(self):
        # The main ETL processing
        log.info("START")

        etl_chain = self.configdict.get('etl', 'chain').split('|')
        if not etl_chain:
            raise ValueError('ETL chain entry not defined in section [etl]')

        # Create input/transformer/output (ETL Component) objects
        etl_comps = []
        for etl_section in etl_chain:
            etl_comps.append(factory.create_obj(self.configdict, etl_section))

        # Do ETL as long as input available
        while 1:
            # Input
            doc = etl_comps[0].invoke()

            # Halt when no input available any more
            if doc is None:
                 log.info("DONE")
                 break

            # Processing : invoke the chain of Transformers and Output Components
            for i in range(1, len(etl_comps)):
                doc = etl_comps[i].invoke(doc)

def main():
    # Do the ETL
    etl = ETL()
    etl.run()

if __name__ == "__main__":
    main()
