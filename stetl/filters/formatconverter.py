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
    Converts (almost) any packet format (if converter available).

    consumes=FORMAT.any, produces=FORMAT.any but actual formats
    are changed at initialization based on the input to output format to
    be converted via the input_format and output_format config parameters.
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
        self.converter = None

    def init(self):
        if self.output_format == FORMAT.any:
            # Any as output is always valid, do nothing
            self.converter = FormatConverter.no_op
            return

        # generate runtime error as we may have registered converters at init time...
        if self.input_format not in FORMAT_CONVERTERS.keys():
            raise NotImplementedError('No format converters found for input format %s' % self.input_format)

        # ASSERTION: converters present for input_format

        if self.output_format not in FORMAT_CONVERTERS[self.input_format].keys():
            raise NotImplementedError('No format converters found for input format %s to output format %s' % (
                self.input_format, self.output_format))

        # ASSERTION: converters present for input_format and output_format

        # Lookup and assign the active converter
        self.converter = FORMAT_CONVERTERS[self.input_format][self.output_format]

    def invoke(self, packet):
        packet.format = self.output_format

        if packet.data is None:
            return packet

        if self.converter_args is not None:
            self.converter(packet, self.converter_args)
        else:
            self.converter(packet)

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

    # START etree_doc
    @staticmethod
    def etree_doc2geojson_collection(packet, converter_args=None):
        """
        Use converter_args to determine XML tagnames for features and GeoJSON feature id.
        For example

           converter_args = {
            'root_tag': 'FeatureCollection',
            'feature_tag': 'featureMember',
            'feature_id_attr': 'fid'
            }

        :param packet:
        :param converter_args:
        :return:
        """
        packet.data = packet.data.getroot()
        packet = FormatConverter.etree_elem2struct(packet)
        feature_coll = {'type': 'FeatureCollection', 'features': []}

        root_tag = 'FeatureCollection'
        feature_tag = 'featureMember'
        if converter_args:
            root_tag = converter_args['root_tag']
            feature_tag = converter_args['feature_tag']

        features = packet.data[root_tag][feature_tag]
        for feature in features:
            packet.data = feature
            packet = FormatConverter.struct2geojson_feature(packet, converter_args)
            feature_coll['features'].append(packet.data)

        packet.data = feature_coll
        return packet

    @staticmethod
    def etree_doc2string(packet):
        packet.data = etree.tostring(packet.data, pretty_print=True, xml_declaration=True)
        return packet

    @staticmethod
    def etree_doc2struct(packet, strip_space=True, strip_ns=True, sub=False, attr_prefix='', gml2ogr=True, ogr2json=True):
        """
        :param packet:
        :param strip_space:
        :param strip_ns:
        :param sub:
        :param attr_prefix:
        :param gml2ogr:
        :param ogr2json:
        :return:
        """
        packet.data = packet.data.getroot()
        return FormatConverter.etree_elem2struct(packet, strip_space, strip_ns, sub, attr_prefix, gml2ogr, ogr2json)

    # END etree_doc

    # START etree_elem
    @staticmethod
    def etree_elem2geojson_feature(packet, converter_args=None):
        """

        """
        packet = FormatConverter.etree_elem2struct(packet, converter_args)
        packet = FormatConverter.struct2geojson_feature(packet, converter_args)

        return packet

    @staticmethod
    def etree_elem2struct(packet, strip_space=True, strip_ns=True, sub=False, attr_prefix='', gml2ogr=True, ogr2json=True):
        """
        :param packet:
        :param strip_space:
        :param strip_ns:
        :param sub:
        :param attr_prefix:
        :param gml2ogr:
        :param ogr2json:
        :return:
        """
        packet.data = Util.elem_to_dict(packet.data, strip_space, strip_ns, sub, attr_prefix, gml2ogr, ogr2json)
        return packet

    # END etree_elem

    @staticmethod
    def ogr_feature2struct(packet, converter_args=None):
        s = packet.data.ExportToJson()
        import ast
        # http://stackoverflow.com/questions/988228/converting-a-string-to-dictionary
        # ast.literal_eval("{'muffin' : 'lolz', 'foo' : 'kitty'}")
        packet.data = ast.literal_eval(s)

        return packet

    @staticmethod
    def ogr_feature_arr2geojson_coll(packet, converter_args=None):
        # See http://geojson.org/geojson-spec.html
        geojson_coll = {'type': 'FeatureCollection', 'features': []}
        import ast
        for feature in packet.data:
            geojson_coll['features'].append(ast.literal_eval(feature.ExportToJson()))

        packet.data = geojson_coll

        return packet

    @staticmethod
    def record2struct(packet, converter_args=None):
        if converter_args is not None:
            struct = dict()
            struct[converter_args['top_name']] = packet.data
            packet.data = struct

        return packet

    @staticmethod
    def record2record_array(packet):
        if not hasattr(packet, 'arr'):
            packet.arr = list()

        if packet.data is not None:
            packet.arr.append(packet.data)
            packet.consume()

        if packet.is_end_of_stream() is True:
            # End of stream reached: assembled record array
            packet.data = packet.arr
            packet.arr = list()

        return packet

    @staticmethod
    def record_array2struct(packet, converter_args=None):
        return FormatConverter.record2struct(packet, converter_args)

    @staticmethod
    def string2etree_doc(packet):
        packet.data = etree.fromstring(packet.data)
        return packet

    @staticmethod
    def struct2string(packet):
        packet.data = packet.to_string()
        return packet

    @staticmethod
    def struct2geojson_feature(packet, converter_args=None):
        key, feature_struct = packet.data.popitem()
        feature = {'type': 'feature', 'properties': {}}

        id_field = None
        if converter_args:
            id_field = converter_args['feature_id_attr']

        for attr_name in feature_struct:
            val = feature_struct[attr_name]
            if attr_name == 'geometry':
                feature['geometry'] = val
            elif attr_name == id_field:
                feature['id'] = val
            else:
                feature['properties'][attr_name] = val

        packet.data = feature
        return packet

# 'xml_line_stream', 'etree_doc', 'etree_element', 'etree_feature_array', 'xml_doc_as_string',
#  'string', 'record', 'record_array', 'geojson_collection', geojson_feature', 'struct',
# 'ogr_feature', 'ogr_feature_array', 'any'
FORMAT_CONVERTERS = {
    FORMAT.etree_doc: {
        FORMAT.geojson_collection: FormatConverter.etree_doc2geojson_collection,
        FORMAT.string: FormatConverter.etree_doc2string,
        FORMAT.struct: FormatConverter.etree_doc2struct,
        FORMAT.xml_doc_as_string: FormatConverter.etree_doc2string
    },
    FORMAT.etree_element: {
        FORMAT.geojson_feature: FormatConverter.etree_elem2geojson_feature,
        FORMAT.string: FormatConverter.etree_doc2string,
        FORMAT.struct: FormatConverter.etree_elem2struct,
        FORMAT.xml_doc_as_string: FormatConverter.etree_doc2string
    },
    FORMAT.ogr_feature: {
        FORMAT.geojson_feature: FormatConverter.ogr_feature2struct,
        FORMAT.struct: FormatConverter.ogr_feature2struct
    },
    FORMAT.ogr_feature_array: {
        FORMAT.geojson_collection: FormatConverter.ogr_feature_arr2geojson_coll
    },
    FORMAT.record: {
        FORMAT.struct: FormatConverter.record2struct,
        FORMAT.record_array: FormatConverter.record2record_array
    },
    FORMAT.record_array: {
        FORMAT.struct: FormatConverter.record_array2struct
    },
    FORMAT.string: {
        FORMAT.etree_doc: FormatConverter.string2etree_doc,
        FORMAT.xml_doc_as_string: FormatConverter.no_op
    },
    FORMAT.struct: {
        FORMAT.string: FormatConverter.struct2string,
        FORMAT.geojson_feature: FormatConverter.struct2geojson_feature
    },
    FORMAT.xml_doc_as_string: {
        FORMAT.etree_doc: FormatConverter.string2etree_doc,
        FORMAT.string: FormatConverter.no_op
    },
    FORMAT.xml_line_stream: {
        FORMAT.string: FormatConverter.no_op
    }
}
