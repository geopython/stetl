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
        self.format = FORMAT.any

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

# Simple enum emulation NOT ANY MORE: TOO INVOLVED AND INFLEXIBLE: use Strings with predefined ones in FORMAT.*
# See http://stackoverflow.com/questions/1969005/enumerations-in-python
# class Enum(object):
#     def __init__(self, *keys):
#         self.__dict__.update(zip(keys, range(len(keys))))

# The data types allowed to pass in Packets, "any" can be used as wildcard
# FORMAT = Enum('xml_line_stream', 'etree_doc', 'etree_element_stream', 'etree_feature_array', 'xml_doc_as_string',
#              'string', 'record', 'geojson_struct', 'struct', 'any')


class FORMAT:
    none = 'none'
    xml_line_stream = 'xml_line_stream'
    etree_doc = 'etree_doc'
    etree_element_stream = 'etree_element_stream'
    etree_feature_array = 'etree_feature_array'
    xml_doc_as_string = 'xml_doc_as_string'
    string = 'string'
    record = 'record'
    record_array = 'record_array'
    struct = 'struct'
    geojson_struct = 'geojson_struct'
    any = 'any'

    @staticmethod
    def add_format(fmt):
        # Add to existing formats via class dict
        FORMAT.__dict__[fmt] = fmt
