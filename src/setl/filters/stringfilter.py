# -*- coding: utf-8 -*-
#
# String filtering.
#
# Author:Just van den Broecke

from ..util import Util
from ..filter import Filter
from .. packet import  FORMAT

log = Util.get_log("stringfilter")

# Base class for any string filtering
class StringFilter(Filter):
    # Constructor
    def __init__(self, configdict, section, consumes, produces):
        Filter.__init__(self, configdict, section, consumes, produces)

    def invoke(self, packet):
        if packet.data is None:
            return packet
        return self.filter_string(packet)

    def filter_string(self, packet):
        pass

# String filtering using Python advanced String formatting
# The string should contain {0} {1} etc. These are substituted
# with configured 'format_args', a tuple of strings.
class StringSubstitutionFilter(StringFilter):
    # Constructor
    def __init__(self, configdict, section):
        StringFilter.__init__(self, configdict, section, consumes=FORMAT.string, produces=FORMAT.string)
        # Positional formatting of content according to Python String.format()
        self.format_args = self.cfg.get_tuple('format_args')

    def filter_string(self, packet):
        # String substitution based on Python String.format()
        packet.data = packet.data.format(*self.format_args)
        return packet




