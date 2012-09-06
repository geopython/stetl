#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Transformation modules.
#
# Author:Just van den Broecke

from util import Util, etree
from filter import Filter

log = Util.get_log("transformer")


# Base class: Output Component
class Transformer(Filter):
    # Constructor
    def __init__(self, configdict, section):
        Filter.__init__(self, configdict, section)

    def invoke(self, packet):
        return self.transform(packet)

    def transform(self, packet):
        return packet

class XsltTransformer(Transformer):
    # Constructor
    def __init__(self, configdict, section):
        Transformer.__init__(self, configdict, section)

        self.xslt_file_path = self.cfg.get('script')
        self.xslt_file = open(self.xslt_file_path, 'r')
        self.xslt_doc = etree.parse(self.xslt_file)
        self.xslt_obj = etree.XSLT(self.xslt_doc)
        self.xslt_file.close()

    def transform(self, packet):
        if packet.data is None:
            return packet

        log.info("XSLT Transform")
        packet.data = self.xslt_obj(packet.data)
        return packet

