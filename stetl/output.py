# -*- coding: utf-8 -*-
#
# Output base class for ETL.
#
# Author: Just van den Broecke
#
from component import Component
from util import Util

log = Util.get_log('output')


class Output(Component):
    """
    Abstract Base class for all Output Components.

    """

    def __init__(self, configdict, section, consumes):
        Component.__init__(self, configdict, section, consumes=consumes, produces=None)
        log.info("cfg = %s" % self.cfg.to_string())

    def invoke(self, packet):
        packet = self.write(packet)
        packet.consume()
        return packet

    def write(self, packet):
        return packet
