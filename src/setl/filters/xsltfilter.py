#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Transformation of an etree doc with XSLT.
#
# Author:Just van den Broecke

from ..util import Util, etree
from ..filter import Filter
from .. packet import  FORMAT

log = Util.get_log("xsltfilter")

class XsltFilter(Filter):
    # Constructor
    def __init__(self, configdict, section):
        Filter.__init__(self, configdict, section, consumes=FORMAT.etree_doc, produces=FORMAT.etree_doc)

        self.xslt_file_path = self.cfg.get('script')
        self.xslt_file = open(self.xslt_file_path, 'r')
        # Parse XSLT file only once
        self.xslt_doc = etree.parse(self.xslt_file)
        self.xslt_obj = etree.XSLT(self.xslt_doc)
        self.xslt_file.close()

    def invoke(self, packet):
        if packet.data is None:
            return packet
        return self.transform(packet)

    def transform(self, packet):
        log.info("XSLT Transform")
        packet.data = self.xslt_obj(packet.data)
        return packet

