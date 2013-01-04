#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Chain class: holds pipeline of components.
#
# Author: Just van den Broecke
#

from setl.factory import factory
from setl.packet import Packet
from setl.util import Util

log = Util.get_log('chain')

# Holder for single invokable pipeline of components
# A Chain is basically a singly linked list of Components
# Each Component executes a part of the total ETL.
# Data along the Chain is passed within a Packet object.
# The compatibility of input and output for linked
# Components is checked when adding a Component to the Chain.
class Chain:
    def __init__(self, chain_str, config_dict):
        self.first_comp = None
        self.cur_comp = None
        self.config_dict = config_dict
        self.chain_str = chain_str

    # Builder method: build a Chain of linked Components
    def assemble(self):
        log.info('Assembling Chain: %s...' % self.chain_str)

        # Create linked list of input/filter/output (ETL Component) objects
        chain_str_arr = self.chain_str.split('|')
        for etl_section_name in chain_str_arr:
            # Create the ETL component by name and properties
            etl_comp = factory.create_obj(self.config_dict, etl_section_name)

            # Add component to end of Chain
            self.add(etl_comp)

    # Add component to end of Chain
    def add(self, etl_comp):
        if not self.first_comp:
            self.first_comp = etl_comp
        else:
            # Already component(s) in chain add to current
            self.cur_comp.next = etl_comp

            if not self.cur_comp.is_compatible():
                raise ValueError('Incompatible components linked: %s and %s' % (str(self.cur_comp), str(self.cur_comp.next)))

        # Remember current
        self.cur_comp = etl_comp       

    def run(self):
        log.info('Running Chain: %s' % self.chain_str)

        # One time init for entire Chain
        self.first_comp.do_init()

        # Do ETL as long as input available in Packet
        packet = Packet()
        while not packet.is_end_of_stream():
#            try:
                # Invoke the first component to start the chain
                packet.init()
                packet = self.first_comp.process(packet)
#            except (Exception), e:
#                log.error("Fatal Error in ETL: %s"% str(e))
#                break

        # One time exit for entire Chain
        self.first_comp.do_exit()
        log.info('DONE %s ' % self.chain_str)
