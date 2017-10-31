# -*- coding: utf-8 -*-
#
# Unit of data streamed through ETL chain.
#
# Author: Just van den Broecke
#
from util import etree
import json


class Packet:
    """
    Represents units of (any) data and status passed along Chain of Components.

    """

    def __init__(self, data=None):
        self.init(data)

    def init(self, data=None):
        self.data = None
        self.meta = {}
        self.component = None
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

    def to_string(self, args=dict):
        if self.data is None:
            return ''

        # TODO: jumptable
        if self.format == FORMAT.etree_doc:
            s = etree.tostring(self.data, pretty_print=True, xml_declaration=True, encoding='utf-8')
        elif self.format == FORMAT.struct or self.format == FORMAT.geojson_collection or self.format == FORMAT.geojson_feature:
            s = json.dumps(self.data, sort_keys=False, indent=4, separators=(',', ': '))
        elif self.format == FORMAT.ogr_feature:
            s = self.data.ExportToJson()
        else:
            s = str(self.data)
        return s


# Simple enum emulation NOT ANY MORE: TOO INVOLVED AND INFLEXIBLE: use Strings with predefined ones in FORMAT.*
# See http://stackoverflow.com/questions/1969005/enumerations-in-python
# class Enum(object):
#     def __init__(self, *keys):
#         self.__dict__.update(zip(keys, range(len(keys))))

# The data types allowed to pass in Packets, "any" can be used as wildcard
# FORMAT = Enum('xml_line_stream', 'etree_doc', 'etree_element', 'etree_feature_array', 'xml_doc_as_string',
#              'string', 'record', 'geojson_collection', 'struct', 'any')


class FORMAT:
    """
    Format of Packet (enumeration).

    Current possible values:

    * 'none'
    * 'xml_line_stream'
    * 'line_stream'
    * 'etree_doc'
    * 'etree_element'
    * 'etree_feature_array'
    * 'xml_doc_as_string'
    * 'string'
    * 'record'
    * 'record_array'
    * 'struct'
    * 'geojson_feature'
    * 'geojson_collection'
    * 'ogr_feature'
    * 'ogr_feature_array'
    * 'any'

    """
    none = 'none'
    xml_line_stream = 'xml_line_stream'
    line_stream = 'line_stream'
    etree_doc = 'etree_doc'
    etree_element = 'etree_element'
    etree_feature_array = 'etree_feature_array'
    xml_doc_as_string = 'xml_doc_as_string'
    string = 'string'
    record = 'record'
    record_array = 'record_array'
    struct = 'struct'
    geojson_feature = 'geojson_feature'
    geojson_collection = 'geojson_collection'
    ogr_feature = 'ogr_feature'
    ogr_feature_array = 'ogr_feature_array'
    any = 'any'

    @staticmethod
    def add_format(fmt):
        # Add to existing formats via class dict
        FORMAT.__dict__[fmt] = fmt
