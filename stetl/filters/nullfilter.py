# -*- coding: utf-8 -*-
#
# Filter that does noting, just passes any data through.
#
# Author:Just van den Broecke

from stetl.util import Util
from stetl.filter import Filter
from stetl.packet import FORMAT

log = Util.get_log("nullfilter")


class NullFilter(Filter):
    """
    Pass-through Filter, does nothing. Mainly used in Test Cases.
    """

    # Constructor
    def __init__(self, configdict, section, consumes=FORMAT.any, produces=FORMAT.any):
        Filter.__init__(self, configdict, section, consumes, produces)

    def invoke(self, packet):
        return packet
