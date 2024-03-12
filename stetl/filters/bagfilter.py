# BAG related filters

from stetl.component import Config
from stetl.util import Util
from stetl.filter import Filter
from stetl.packet import FORMAT

log = Util.get_log("bagfilter")


class LeveringFilter(Filter):
    """
    Convert Leveringsdocument-BAG-Extract.xml content to record for
    insertion into nlx_bag_info table.
    """

    @Config(ptype=str, default='sleutel', required=False)
    def key_column(self):
        """
        Column name for key
        """
        pass

    @Config(ptype=str, default='levering_xml', required=False)
    def key_value(self):
        """
        Column value for key
        """
        pass

    @Config(ptype=str, default='waarde', required=False)
    def value_column(self):
        """
        Column name for value
        """
        pass

    # Constructor
    def __init__(self, configdict, section, consumes=FORMAT.string, produces=FORMAT.record_array):
        Filter.__init__(self, configdict, section, consumes, produces)

    def invoke(self, packet):
        if packet.data is None or packet.is_end_of_stream():
            return packet

        with open(packet.data, 'rt') as f:
            data = f.read()

        record = {
            self.key_column: self.key_value,
            self.value_column: data,
        }

        # record_array is used to avoid ValueError:
        # https://github.com/geopython/stetl/issues/125
        packet.data = [record]

        return packet
