# -*- coding: utf-8 -*-
#
# Example of user-defined component.
#
# Author:Just van den Broecke

from util import Util
from filter import Filter
from packet import FORMAT

log = Util.get_log("myfilter")


class MyFilter(Filter):
    # Constructor
    def __init__(self, configdict, section):
        Filter.__init__(self, configdict, section, consumes=FORMAT.etree_doc, produces=FORMAT.etree_doc)

    def invoke(self, packet):
        if packet.data is None:
            return packet
        return self.do_something(packet)

    def do_something(self, packet):
        log.info("CALLING MyFilter OK!!!!")
        return packet

