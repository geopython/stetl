# -*- coding: utf-8 -*-
# Author: Just van den Broecke
#
try:
    from component import Component
except ImportError:
    from stetl.component import Component

class Filter(Component):
    """
    Maps input to output. Abstract base class for specific Filters.

    """

    def __init__(self, configdict, section, consumes, produces):
        Component.__init__(self, configdict, section, consumes, produces)

    def invoke(self, packet):
        return packet
