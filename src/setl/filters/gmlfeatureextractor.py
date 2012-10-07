#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Extracts collections of etree GML features from an GML etree document.
#
# Author: Just van den Broecke
#
from ..util import Util
from ..filter import Filter
from .. packet import  FORMAT

log = Util.get_log('gmlfeatureextractor')

class GmlFeatureExtractor(Filter):
    xpath_base = "//*[local-name() = '%s']"

    # Constructor
    def __init__(self, configdict, section='gml_feature_extractor'):
        Filter.__init__(self, configdict, section, consumes=FORMAT.etree_doc, produces=FORMAT.etree_feature_array)

        log.info("cfg = %s" % self.cfg.to_string())

        self.feature_tags = self.cfg.get('feature_tags').split(',')
        self.total_features = 0
        self.xpath_expression = ''
        index = 0
        for feature_tag in self.feature_tags:
            if index > 0:
                self.xpath_expression += '|'
            self.xpath_expression += GmlFeatureExtractor.xpath_base % feature_tag
            index += 1

    def invoke(self, packet):
        if packet.data is None:
            return packet

        packet.data = packet.data.xpath(self.xpath_expression)
        self.total_features += len(packet.data)
        log.info('extracted %d features from GML etree doc (total = %d)' % (len(packet.data), self.total_features))
        return packet


