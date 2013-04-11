#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Input classes for ETL.
#
# Author: Just van den Broecke
#
from stetl.util import Util
from stetl.component import Component

log = Util.get_log('input')

# Base class: Input Component
class Input(Component):
    # Constructor
    def __init__(self, configdict, section, produces):
        Component.__init__(self, configdict, section, consumes=None, produces=produces)

        log.info("cfg = %s" % self.cfg.to_string())

    def invoke(self, packet):
        return self.read(packet)

    def read(self, packet):
        return packet

