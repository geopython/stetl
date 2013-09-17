#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Filter: XML validation.
#
# NB: you need to have installed libxml2 2.8.0 or newer!
# Older libxml2 versions like 2.7.8 have a bug which causes failure in GML Schema
# parsing. See https://bugzilla.gnome.org/show_bug.cgi?id=630130
#
# Author:Just van den Broecke
#
from stetl.util import Util, etree
from stetl.filter import Filter
from stetl.packet import FORMAT

log = Util.get_log("xmlvalidator")


class XmlSchemaValidator(Filter):
    """
    Validates an etree doc and prints result to log.

    consumes=FORMAT.etree_doc, produces=FORMAT.etree_doc
    """

    # Constructor
    def __init__(self, configdict, section):
        Filter.__init__(self, configdict, section, consumes=FORMAT.etree_doc, produces=FORMAT.etree_doc)
        self.enabled = self.cfg.get_bool('enabled', True)
        self.xsd = self.cfg.get('xsd')
        log.info("Building the Schema once with (GML XSD) dependencies for schema=%s (be patient...)" % self.xsd)
        self.schema = etree.XMLSchema(etree.parse(self.xsd))

    def invoke(self, packet):
        if packet.data is None or not self.enabled:
            return packet
        return self.validate(packet)

    def validate(self, packet):
        log.info("Validating doc against schema=%s ..." % self.xsd)
        result = self.schema.validate(packet.data)
        log.info("Validation result: %s" % str(result))
        return packet
