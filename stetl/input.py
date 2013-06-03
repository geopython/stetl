# -*- coding: utf-8 -*-
#
# Input classes for ETL.
#
# Author: Just van den Broecke
#
from util import Util
from component import Component

log = Util.get_log('input')


class Input(Component):
    """
    Abstract Base class for all Input Components.

    """

    def __init__(self, configdict, section, produces):
        Component.__init__(self, configdict, section, consumes=None, produces=produces)

        log.info("cfg = %s" % self.cfg.to_string())

    def invoke(self, packet):
        return self.read(packet)

    def read(self, packet):
        return packet

