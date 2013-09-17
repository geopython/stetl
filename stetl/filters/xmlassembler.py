#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Splits stream of XML elements into etree docs.
#
# Author: Just van den Broecke
#
from stetl.util import Util, etree
from stetl.filter import Filter
from stetl.packet import FORMAT

log = Util.get_log('xmlassembler')

class XmlAssembler(Filter):
    """
    Split a stream of etree DOM XML elements (usually Features) into etree DOM docs.
    Consumes and buffers elements until max_elements reached, will then produce an etree doc.

    consumes=FORMAT.etree_element_stream, produces=FORMAT.etree_doc
    """
    xpath_base = "//*[local-name() = '%s']"

    # Constructor
    def __init__(self, configdict, section):
        Filter.__init__(self, configdict, section, consumes=FORMAT.etree_element_stream, produces=FORMAT.etree_doc)

        log.info("cfg = %s" % self.cfg.to_string())
        self.max_elements = self.cfg.get_int('max_elements', 10000)
        self.container_doc = self.cfg.get('container_doc')
        self.element_container_xpath = XmlAssembler.xpath_base % self.cfg.get('element_container_tag')
        self.total_element_count = 0
        self.element_arr = []

        # Reusable XML parser
        self.xml_parser = etree.XMLParser(remove_blank_text=True)

    def invoke(self, packet):
        if packet.data is not None:
            # Valid element: consume and handle
            self.consume_element(packet)

        if packet.is_end_of_stream() or packet.is_end_of_doc() or len(self.element_arr) >= self.max_elements:
            # EOF but still data in buffer: make doc
            # log.info("Flush doc")
            self.flush_elements(packet)

        return packet

    def consume_element(self, packet):
        # Always move the data (element) from packet
        element = packet.consume()

        if element is None or packet.is_end_of_stream() is True:
            return packet

        self.total_element_count += 1

        self.element_arr.append(element)
        return packet

    def flush_elements(self, packet):
        if len(self.element_arr) == 0:
            return packet

        # Start new doc (TODO clone)
        try:
            etree_doc = etree.fromstring(self.container_doc, self.xml_parser)
        except Exception, e:
            log.error("new container doc not OK")
            return packet

        parent_element = etree_doc.xpath(self.element_container_xpath)
        if len(parent_element) > 0:
            parent_element = parent_element[0]

        for element in self.element_arr:
            parent_element.append(element)

        log.info("xmldoc ready: elms=%d total_elms=%d" % (len(self.element_arr), self.total_element_count))
        packet.data = etree_doc
        self.element_arr = []
        return packet


