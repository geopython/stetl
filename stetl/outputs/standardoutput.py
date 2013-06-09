# -*- coding: utf-8 -*-
#
# Output classes for ETL.
#
# Author: Just van den Broecke
#
from stetl.output import Output
from stetl.util import Util
from stetl.packet import FORMAT

log = Util.get_log('standardoutput')

# Pretty print XML to standard output
class StandardOutput(Output):
    def __init__(self, configdict, section):
        Output.__init__(self, configdict, section, consumes=FORMAT.any)

    def write(self, packet):
        if packet.data is None:
            return packet

        # Default: print to stdout
        print(str(packet.data))
        return packet

# Pretty print XML to standard output
class StandardXmlOutput(Output):
    def __init__(self, configdict, section):
        Output.__init__(self, configdict, section, consumes=FORMAT.etree_doc)

    def write(self, packet):
        if packet.data is None:
            return packet

        # Default: print to stdout
        print(self.to_string(packet.data))
        return packet

