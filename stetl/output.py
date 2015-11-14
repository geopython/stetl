# -*- coding: utf-8 -*-
#
# Output base class for ETL.
#
# Author: Just van den Broecke
#

try:
    from component import Component
except ImportError:
    from .component import Component
try:
    from util import Util, etree
except ImportError:
    from .util import Util, etree

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
