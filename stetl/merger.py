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
    The Merger will embed Child Components to which actions are delegated.
    A Child Component may be a sub-Chain e.g. (Input|Filter|Filter..) sequence.
    Hence the "next" should be coupled to the last Component in that sub-Chain with
    the degenerate case where the sub-Chain is a single (Input) Component.
    NB this Component can only be used for Inputs.
    """

    def __init__(self, config_dict, child_list):
        # Assemble child list
        self.children = []
        section_name = ''
        for child in child_list:
            section_name += '-%s_%d' % (child.get_id(), random.randrange(0, 100000))

            # A Child can be a sub-Chain: each child is tuple: [0] is first
            # [1] is last in sub-Chain. child[0] === child[1] if child is single Component.
            # Need to remember both first and last in order to link/unlink subchain.
            # So we store the Child as a tuple of (first, last).
            self.children.append((child, child.get_last()))

        # Add ourselves to config for compat with Component
        config_dict.add_section(section_name)

        # We use the in/out formats of first child, will be compat-checked later
        Component.__init__(self, config_dict, section_name, consumes=self.first(self.children[0])._input_format,
                           produces=self.last(self.children[0])._output_format)

        self.end_count = len(self.children)

    def add_next(self, next_component):
        for child in self.children:
            # Couple Child Component's last .next directly to our next
            self.last(child).add_next(next_component)

        # Remember next
        self.next = next_component

    def first(self, child):
        """
        Get first Component in Child sub-Chain.
        :param child:
        :return: first Component
        """
        return child[0]

    def last(self, child):
        """
        Get last Component in Child sub-Chain.
        :param child:
        :return: last Component
        """
        return child[1]

    # Check compatibility with our child Components
    def is_compatible(self):
        for child in self.children:
            # Last in subchain must be compatible
            if not self.last(child).is_compatible():
                return False
        return True

    def process(self, packet):
        # Defer processing to children
        # and track of End-of-Stream Packets

        for child in self.children:
            # Skip inactive child Components
            if not self.last(child).next:
                continue

            # Defer to child
            self.first(child).process(packet)

            # Keep track of End-of-Stream
            if packet.is_end_of_stream():
                # deactivate Child by unlinking
                # otherwise we'll keep getting EoS
                self.last(child).next = None
                self.end_count -= 1

            # Re-init to start afresh again
            packet.init()

        # Only if all children have End-of-Stream
        # declare the Packet returned EoS.
        if self.end_count == 0:
            packet.set_end_of_stream()

        return packet

    def do_init(self):
        for child in self.children:
            # Only init the child, without
            # initing upstream Components via Chain
            self.last(child).next = None
            self.first(child).do_init()
            self.last(child).next = self.next

        # init upstream Components once
        self.next.do_init()

    def do_exit(self):
        for child in self.children:
            # Only exit the child, without
            # exiting upstream Components via Chain
            self.last(child).next = None
            self.first(child).do_exit()

        # exit upstream Components once
        self.next.do_exit()
