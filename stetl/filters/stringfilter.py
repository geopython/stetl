# -*- coding: utf-8 -*-
#
# String filtering.
#
# Author:Just van den Broecke

from stetl.component import Config
from stetl.util import Util
from stetl.filter import Filter
from stetl.packet import FORMAT

log = Util.get_log("stringfilter")


class StringFilter(Filter):
    """
    Base class for any string filtering
    """

    # Constructor
    def __init__(self, configdict, section, consumes, produces):
        Filter.__init__(self, configdict, section, consumes, produces)

    def invoke(self, packet):
        if packet.data is None:
            return packet
        return self.filter_string(packet)

    def filter_string(self, packet):
        pass


class StringSubstitutionFilter(StringFilter):
    """
    String filtering using Python advanced String formatting.
    String should have substitutable values like {schema} {foo}
    format_args should be of the form format_args = schema:test foo:bar ...

    consumes=FORMAT.string, produces=FORMAT.string
    """

    @Config(ptype=str, default=None, required=True)
    def format_args(self):
        """
        Provides a list of format arguments used by the string substitution filter. Formatting of content according to Python String.format().
        String should have substitutable values like {schema} {foo}.

        Example: format_args = schema:test foo:bar
        """
        pass

    @Config(ptype=str, default=':', required=False)
    def separator(self):
        """
        Provides the separator to split the format argument names from their values.
        """
        pass

    # Constructor
    def __init__(self, configdict, section):
        StringFilter.__init__(self, configdict, section, consumes=FORMAT.string, produces=FORMAT.string)

        # Convert string to dict: http://stackoverflow.com/a/1248990
        self.format_args_dict = Util.string_to_dict(self.format_args, self.separator)

    def filter_string(self, packet):
        # String substitution based on Python String.format()
        packet.data = packet.data.format(**self.format_args_dict)
        return packet
