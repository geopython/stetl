# -*- coding: utf-8 -*-
#
# Splitter Component base class for ETL.
#
# Author: Just van den Broecke
#

import random
from util import Util
from component import Component

log = Util.get_log('splitter')


class Splitter(Component):
    """
    Component that splits a single input to multiple output Components.
    Use this for example to produce multiple output file formats (GML, GeoJSON etc)
    or to publish to multiple remote services (SOS, SensorThings API) or for simple
    debugging: target Output and StandardOutput.
    """

    def __init__(self, config_dict, child_list):
        # Assemble child list
        children = []
        section_name = ''
        for child in child_list:
            section_name += '-%s_%d' % (child.get_id(), random.randrange(0, 100000))
            children.append(child)

        # Add ourselves to config for compat with Component
        config_dict.add_section(section_name)

        # We use the in/out formats of first child, will be compat chcked later
        Component.__init__(self, config_dict, section_name, consumes=children[0]._input_format,
                           produces=children[0]._output_format)

        # Component sets self.next to None...
        self.next = children

    def add_next(self, next_component):
        # We use child list, maybe to be used later
        pass

    # Check our compatibility with our child Components
    def is_compatible(self):
        for comp in self.next:
            if not comp.is_compatible():
                return False
        return True

    def process(self, packet):
        # Defer processing to our child Components
        data = packet.data
        for comp in self.next:
            packet.data = data
            comp.process(packet)
        return packet

    def do_init(self):
        for comp in self.next:
            comp.do_init()

    def do_exit(self):
        # Notify all child comps that we exit
        for comp in self.next:
            comp.do_exit()

    def before_invoke(self, packet):
        """
        Called just before Component invoke.
        """
        for comp in self.next:
            if not comp.before_invoke(packet):
                return False
        return True

    def after_invoke(self, packet):
        """
        Called right after Component invoke.
        """
        for comp in self.next:
            if not comp.after_invoke(packet):
                return False
        return True

    def after_chain_invoke(self, packet):
        """
        Called right after entire Component Chain invoke.
        """
        for comp in self.next:
            if not comp.after_chain_invoke(packet):
                return False
        return True

    def invoke(self, packet):
        for comp in self.next:
            packet = comp.invoke(packet)
        return packet

    def init(self):
        for comp in self.next:
            comp.init()

    def exit(self):
        for comp in self.next:
            comp.exit()
