#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Transformation modules.
#
# Author:Just van den Broecke

from util import ConfigSection, Util, etree
from component import Component

log = Util.get_log("transformer")

# Base class: Output Component
class Transformer(Component):
    # Constructor
    def __init__(self, configdict, section):
        Component.__init__(self, configdict, section)
        log.info("cfg = %s" % self.cfg.to_string())

    def invoke(self, doc):
        return self.transform(doc)

    def transform(self, gml_doc):
        return None

class XsltTransformer(Transformer):
    # Constructor
    def __init__(self, configdict, section):
        Transformer.__init__(self, configdict, section)

        self.xslt_file_path = self.cfg.get('script')
        self.xslt_file = open(self.xslt_file_path, 'r')
        self.xslt_doc = etree.parse(self.xslt_file)
        self.xslt_obj = etree.XSLT(self.xslt_doc)
        self.xslt_file.close()

    def transform(self, doc):
        log.info("XSLT Transform")
        return self.xslt_obj(doc)

