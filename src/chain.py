#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Chain class: holds pipeline of components.
#
# Author: Just van den Broecke
#

from factory import factory
from packet import Packet
from util import Util

log = Util.get_log('chain')

# Holder for single invokable pipeline of components
class Chain:
    def __init__(self, chain_str, config_dict):
        self.first_comp = None
        self.cur_comp = None
        self.config_dict = config_dict
        self.chain_str = chain_str

    def assemble(self):
        log.info('Assembling Chain: %s...' % self.chain_str)

        # Create linked list of input/filter/output (ETL Component) objects
        chain_str_arr = self.chain_str.split('|')
        for etl_section_name in chain_str_arr:
            # Create the ETL component by name and properties
            etl_comp = factory.create_obj(self.config_dict, etl_section_name)
            self.add(etl_comp)
 
    def add(self, etl_comp):
        if not self.first_comp:
            self.first_comp = etl_comp
        else:
            # Already component(s) in chain add to current
            self.cur_comp.next = etl_comp
            
        # Remember current
        self.cur_comp = etl_comp       

    def run(self):
        log.info('Running Chain: %s' % self.chain_str)

        # One time init for entire Chain
        self.first_comp.do_init()

        # Do ETL as long as input available in Packet
        packet = Packet()
        while not packet.is_end_of_stream():
            try:
                # Invoke the first component to start the chain
                packet = self.first_comp.process(packet)
            except (Exception), e:
                log.error("Fatal Error in ETL: %s"% str(e))
                break

        # One time exit for entire Chain
        self.first_comp.do_exit()
        log.info('DONE %s ' % self.chain_str)
