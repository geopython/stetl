# -*- coding: utf-8 -*-
#
# Unit of data streamed through ETL chain.
#
# Author: Just van den Broecke
#

class Packet:
    """
    Represents units of (any) data and status passed along Chain of Components.

    """
    def __init__(self, data=None):
        self.init(data)

    def init(self, data=None):
        self.data = None
        self.meta = {}
        self.end_of_stream = False
        self.end_of_doc = False

    def consume(self):
        data = self.data
        self.data = None
        return data

    def is_end_of_stream(self):
        return self.end_of_stream

    def is_end_of_doc(self):
        return self.end_of_doc

    def set_end_of_stream(self, val=True):
        self.end_of_stream = val

    def set_end_of_doc(self, val=True):
        self.end_of_doc = val

# Simple enum emulation
# See http://stackoverflow.com/questions/1969005/enumerations-in-python
class Enum(object):
    def __init__(self, *keys):
        self.__dict__.update(zip(keys, range(len(keys))))

# The data types allowed to pass in Packets, "any" can be used as wildcard
FORMAT = Enum('xml_line_stream', 'etree_doc', 'etree_element_stream', 'etree_feature_array', 'xml_doc_as_string',
              'string', 'any')
