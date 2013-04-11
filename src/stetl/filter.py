# -*- coding: utf-8 -*-
# Author: Just van den Broecke
#
from stetl.component import Component

# Base class: Filter
class Filter(Component):
    # Constructor
    def __init__(self, configdict, section, consumes, produces):
        Component.__init__(self, configdict, section, consumes, produces)

    def invoke(self, packet):
        return packet

