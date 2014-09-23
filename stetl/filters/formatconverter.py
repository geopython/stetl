#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Converts Stetl Packet FORMATs. This can be used to connect
# Stetl components with different output/input formats.
#
# Author:Just van den Broecke

from stetl.component import Config
from stetl.util import Util, etree
from stetl.filter import Filter
from stetl.packet import FORMAT

log = Util.get_log("formatconverter")


class FormatConverter(Filter):
    """
    Converts any packet format (if converter available).

    consumes=FORMAT.any, produces=FORMAT.any but actual formats
    are changed at initialization based on the input to output format to
    be converted.
    """

    # Start attribute config meta
    # Applying Decorator pattern with the Config class to provide
    # read-only config values from the configured properties.

    @Config(ptype=dict, default=None, required=False)
    def converter_args(self):
        """
        Custom converter-specific arguments.
        Type: dictionary
        Required: False
        Default: None
        """
        pass

    # End attribute config meta

    # Constructor
    def __init__(self, configdict, section):
        Filter.__init__(self, configdict, section, consumes=FORMAT.any, produces=FORMAT.any)
        self._output_format = self.output_format
        self._input_format = self._input_format

    def invoke(self, packet):
        # if packet.data is None:
        #     return packet

        # Any as output is always valid, just return
        if self.output_format == FORMAT.any:
            return packet

        # generate runtime error as we may have registered converters at init time...
        if self.input_format not in FORMAT_CONVERTERS.keys():
            raise NotImplementedError('No format converters found for input format %s' % self.input_format)

        # ASSERT converters present for input_format

        if self.output_format not in FORMAT_CONVERTERS[self.input_format].keys():
            raise NotImplementedError('No format converters found for input format %s to output format %s' % (
            self.input_format, self.output_format))

        packet.format = self.output_format
        if self.converter_args is not None:
            FORMAT_CONVERTERS[self.input_format][self.output_format](packet, self.converter_args)
        else:
            FORMAT_CONVERTERS[self.input_format][self.output_format](packet)

        return packet

    @staticmethod
    def add_converter(input_format, output_format, converter_fun):
        # Add to existing input format converters or create new
        if input_format not in FORMAT_CONVERTERS.keys():
            FORMAT_CONVERTERS[input_format] = {output_format: converter_fun}
        else:
            FORMAT_CONVERTERS[input_format][output_format] = converter_fun

    @staticmethod
    def no_op(packet):
        return packet

    @staticmethod
    def etree_doc2string(packet):
        if packet.data is None:
            return packet

        packet.data = etree.tostring(packet.data, pretty_print=True, xml_declaration=True)
        return packet

    @staticmethod
    def record2struct(packet, converter_args=None):
        if packet.data is None:
            return packet
        if converter_args is not None:
            struct = dict()
            struct[converter_args['top_name']] = packet.data
            packet.data = struct

        return packet

    @staticmethod
    def record2record_array(packet):
        if not hasattr(packet, 'arr'):
            packet.arr = list()

        if packet.is_end_of_stream() is True:
            packet.data = packet.arr
            return packet

        packet.arr.append(packet.data)
        packet.consume()
        return packet

    @staticmethod
    def record_array2struct(packet, converter_args=None):
        return FormatConverter.record2struct(packet, converter_args)

    @staticmethod
    def string2etree_doc(packet):
        if packet.data is None:
            return packet

        packet.data = etree.fromstring(packet.data)
        return packet


# 'xml_line_stream', 'etree_doc', 'etree_element_stream', 'etree_feature_array', 'xml_doc_as_string',
#  'string', 'record', 'geojson_struct', 'struct', 'any'
FORMAT_CONVERTERS = {
    FORMAT.xml_line_stream: {FORMAT.string: FormatConverter.no_op},
    FORMAT.etree_doc: {FORMAT.string: FormatConverter.etree_doc2string,
                       FORMAT.xml_doc_as_string: FormatConverter.etree_doc2string},
    FORMAT.xml_doc_as_string: {FORMAT.etree_doc: FormatConverter.string2etree_doc,
                               FORMAT.string: FormatConverter.no_op},
    FORMAT.string: {FORMAT.etree_doc: FormatConverter.string2etree_doc},
    FORMAT.record: {FORMAT.struct: FormatConverter.record2struct,
                    FORMAT.record_array: FormatConverter.record2record_array},
    FORMAT.record_array: {FORMAT.struct: FormatConverter.record_array2struct}
}
