# -*- coding: utf-8 -*-
#
# Chain class: holds pipeline of components.
#
# Author: Just van den Broecke
#

from factory import factory
from packet import Packet
from util import Util
from splitter import Splitter
from merger import Merger

log = Util.get_log('chain')


class Chain:
    """
    Holder for single invokable pipeline of components
    A Chain is basically a singly linked list of Components
    Each Component executes a part of the total ETL.
    Data along the Chain is passed within a Packet object.
    The compatibility of input and output for linked
    Components is checked when adding a Component to the Chain.
    """

    def __init__(self, chain_str, config_dict):
        self.first_comp = None
        self.cur_comp = None
        self.config_dict = config_dict
        self.chain_str = chain_str.strip()

    def assemble(self):
        """
        Builder method: build a Chain of linked Components
        :return:
        """
        log.info('Assembling Chain: %s...' % self.chain_str)

        # Create linked list of input/filter/output (ETL Component) objects
        chain_str = self.chain_str
        sub_comps = []
        while chain_str:
            chain_str = chain_str.strip()

            # Check and handle Splitter construct
            # e.g. input_xml_file |(transformer_xslt|output_file) (output_std) (transformer_xslt|output_std)
            if chain_str.startswith('('):
                etl_section_name, chain_str = chain_str.split(')', 1)
                etl_section_name = etl_section_name.strip('(')

                # Check for subchain (split at Filter level)
                if '|' in etl_section_name:
                    # Have subchain: use Chain to assemble
                    sub_chain = Chain(etl_section_name, self.config_dict)
                    sub_chain.assemble()
                    child_comp = sub_chain.first_comp
                else:
                    # Single component (Output) to split
                    child_comp = factory.create_obj(self.config_dict, etl_section_name.strip())

                # Assemble Components (can be subchains) for Splitter later
                sub_comps.append(child_comp)
                if '(' in chain_str:
                    # Still components (subchains) to assemble for Splitter
                    continue

            if len(sub_comps) > 0:
                if chain_str.startswith('|'):
                    # Next component is Merger with children
                    etl_comp = Merger(self.config_dict, sub_comps)
                    dummy, chain_str = chain_str.split('|', 1)
                else:
                    # Next component is Splitter with children
                    etl_comp = Splitter(self.config_dict, sub_comps)
                sub_comps = []
            else:

                # "Normal" case: regular Components piped in Chain
                if '|' in chain_str:
                    # More than one component in remaining Chain
                    etl_section_name, chain_str = chain_str.split('|', 1)
                else:
                    # Last element, we're done!
                    etl_section_name = chain_str
                    chain_str = None

                # Create the ETL component by name and properties
                etl_comp = factory.create_obj(self.config_dict, etl_section_name.strip())

            # Add component to end of Chain
            self.add(etl_comp)

    def add(self, etl_comp):
        """
        Add component to end of Chain
        :param etl_comp:
        :return:
        """
        if not self.first_comp:
            self.first_comp = etl_comp
        else:
            # Already component(s) in chain add to current
            self.cur_comp.add_next(etl_comp)

        # Remember current
        self.cur_comp = etl_comp

    def get_by_class(self, clazz):
        """
        Get Component instance from Chain by class, mainly for testing.
        :param clazz:
        :return Component:
        """
        cur_comp = self.first_comp
        while cur_comp:
            if cur_comp.__class__ == clazz:
                return cur_comp

            # Try next in Chain
            cur_comp = cur_comp.next

        return None

    def get_by_id(self, id):
        """
        Get Component instance from Chain, mainly for testing.
        :param name:
        :return Component:
        """
        cur_comp = self.first_comp
        while cur_comp:
            if cur_comp.get_id() == id:
                return cur_comp

            # Try next in Chain
            cur_comp = cur_comp.next

        return None

    def get_by_index(self, index):
        """
        Get Component instance from Chain by position/index in Chain, mainly for testing.
        :param clazz:
        :return Component:
        """
        cur_comp = self.first_comp
        i = 0
        while cur_comp and i < index:
            # Try next in Chain
            cur_comp = cur_comp.next
            i += 1

        return cur_comp

    def run(self):
        """
        Run the ETL Chain.
        :return:
        """
        log.info('Running Chain: %s' % self.chain_str)

        # One time init for entire Chain
        self.first_comp.do_init()

        # Do ETL as long as input available in Packet
        packet = Packet()
        rounds = 0
        try:
            while not packet.is_end_of_stream():
                # try:
                # Invoke the first component to start the chain
                packet.init()
                packet = self.first_comp.process(packet)
                rounds += 1
                #            except (Exception), e:
                #                log.error("Fatal Error in ETL: %s"% str(e))
                #                break
        finally:
            # Always one time exit for entire Chain
            self.first_comp.do_exit()

        log.info('DONE - %d rounds - chain=%s ' % (rounds, self.chain_str))
