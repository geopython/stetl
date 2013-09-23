# -*- coding: utf-8 -*-
#
# Example of user-defined component.
#
# Author:Just van den Broecke

from stetl.util import Util
from stetl.filter import Filter
from stetl.packet import FORMAT
from stetl.factory import factory
log = Util.get_log("osfilter")


class OrdSurveyGmlFilter(Filter):
    # Constructor
    def __init__(self, configdict, section):
        Filter.__init__(self, configdict, section, consumes=FORMAT.etree_element_stream, produces=FORMAT.etree_element_stream)

        # Create specific preparer object from given class name string
        self.prep_class = self.cfg.get('prep_class')
        self.prep_class = factory.class_forname(self.prep_class)
        self.preparer = self.prep_class('stetl')

    def invoke(self, packet):
        if packet.data is None:
            return packet

        # trivial implementation: Just let Astuntech osmgml preparer do the work
        feat_elm = packet.data[0]
        self.preparer._prepare_feat_elm(feat_elm)
        return packet
