#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Output classes for ETL.
#
# Author: Just van den Broecke
#
from setl.component import Component
from setl.util import  Util, etree

log = Util.get_log('output')

# Base class: Output Component
class Output(Component):
    # Constructor
    def __init__(self, configdict, section):
        Component.__init__(self, configdict, section)

        log.info("cfg = %s" % self.cfg.to_string())

    def invoke(self, packet):
        packet = self.write(packet)
        packet.consume()
        return packet

    def to_string(self, gml_doc, pretty_print=True, xml_declaration=True, encoding='utf-8'):
        return etree.tostring(gml_doc, pretty_print=pretty_print, xml_declaration = xml_declaration, encoding=encoding)

    def write(self, packet):
        if packet.data is None:
             return packet

        # Default: print to stdout
        print(self.to_string(packet.data))
        return packet
