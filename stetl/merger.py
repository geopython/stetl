# -*- coding: utf-8 -*-
#
# Merger Component base class for ETL.
#
# Author: Just van den Broecke
#

import random
from util import Util
from component import Component

log = Util.get_log('merger')


class Merger(Component):
    """
    Component that merges multiple Input Components into a single Component.
    Use this for example to combine multiple input streams like API endpoints.
    NB this Component can only be used for Inputs.
    """

    def __init__(self, config_dict, child_list):
        # Assemble child list
        self.children = []
        section_name = ''
        for child in child_list:
            section_name += '-%s_%d' % (child.get_id(), random.randrange(0, 100000))
            self.children.append(child)

        # Add ourselves to config for compat with Component
        config_dict.add_section(section_name)

        # We use the in/out formats of first child, will be compat-checked later
        Component.__init__(self, config_dict, section_name, consumes=self.children[0]._input_format,
                           produces=self.children[0]._output_format)

        self.end_count = len(self.children)

    def add_next(self, next_component):
        for comp in self.children:
            # Couple Child Component's .next directly to our next
            comp.add_next(next_component)

        # Remember next
        self.next = next_component

    # Check compatibility with our child Components
    def is_compatible(self):
        for comp in self.children:
            if not comp.is_compatible():
                return False
        return True

    def process(self, packet):
        # Defer processing to children
        # and track of End-of-Stream Packets

        for comp in self.children:
            # Skip inactive child Components
            if not comp.next:
                continue

            # Defer to child
            comp.process(packet)

            # Keep track of End-of-Stream
            if packet.is_end_of_stream():
                # deactivate Child by unlinking
                # otherwise we'll keep getting EoS
                comp.next = None
                self.end_count -= 1

            # Re-init to start afresh again
            packet.init()

        # Only if all children have End-of-Stream
        # declare the Packet returned EoS.
        if self.end_count == 0:
            packet.set_end_of_stream()
            
        return packet

    def do_init(self):
        for comp in self.children:
            # Only init the child, without
            # initing upstream Components via Chain
            comp.next = None
            comp.do_init()
            comp.next = self.next

        # init upstream Components once
        self.next.do_init()

    def do_exit(self):
        for comp in self.children:
            # Only exit the child, without
            # exiting upstream Components via Chain
            comp.next = None
            comp.do_exit()
            
        # exit upstream Components once
        self.next.do_exit()
