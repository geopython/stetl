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
import json

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

        # OGR feature def
        self.feat_def = None

    def invoke(self, packet):

        if packet.data is None:
            packet.format = self.output_format
            return packet

        if self.converter_args is not None:
            self.converter(packet, self.converter_args)
        else:
            self.converter(packet)

        packet.format = self.output_format
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
        Use converter_args to determine XML tag names for features and GeoJSON feature id.
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
    def etree_doc2struct(packet, strip_space=True, strip_ns=True, sub=False, attr_prefix='', gml2ogr=True,
                         ogr2json=True):
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
    def etree_elem2struct(packet, strip_space=True, strip_ns=True, sub=False, attr_prefix='', gml2ogr=True,
                          ogr2json=True):
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

    # START geojson_feature
    @staticmethod
    def geojson_feature2ogr_feature(packet, converter_args=None):
        from stetl.util import ogr

        # str = json.dumps(packet.data)
        json_feat = packet.data
        json_geom = json_feat["geometry"]
        json_props = json_feat["properties"]

        # Create OGR Geometry from GeoJSON geom-fields
        geom_dict = dict()
        geom_dict["type"] = json_geom["type"]
        geom_dict["coordinates"] = json_geom["coordinates"]
        geom_str = json.dumps(geom_dict)
        ogr_geom = ogr.CreateGeometryFromJson(geom_str)

        # Once: create OGR Feature definition
        # TODO: assume all string-fields for now, may use type-mapping definition in converter_args
        comp = packet.component
        if comp.feat_def is None:
            comp.feat_def = ogr.FeatureDefn()

            field_def = ogr.FieldDefn("id", ogr.OFTString)
            comp.feat_def.AddFieldDefn(field_def)

            for field_name in json_props:

                # OGR needs UTF-8 internally
                if isinstance(field_name, unicode):
                    field_name = field_name.encode('utf8')

                field_def = ogr.FieldDefn(field_name, ogr.OFTString)
                comp.feat_def.AddFieldDefn(field_def)

            ogr_geom_type = ogr_geom.GetGeometryType()
            comp.feat_def.SetGeomType(ogr_geom_type)

        # Create and populate Feature with id, geom and attributes
        feature = ogr.Feature(comp.feat_def)
        json_id = json_feat["id"]
        if isinstance(json_id, unicode):
            json_id = json_id.encode('utf8')

        feature.SetField("id", json_id)
        feature.SetGeometry(ogr_geom)
        for field_name in json_props:

            # OGR needs UTF-8 internally
            field_value = json_props[field_name]
            if isinstance(field_value, unicode):
                field_value = field_value.encode('utf8')

            if not isinstance(field_value, basestring):
                field_value = str(field_value)

            # OGR needs UTF-8 internally
            if isinstance(field_name, unicode):
                field_name = field_name.encode('utf8')

            # print("id=%s k=%s v=%s" % (json_id, field_name, field_value))
            feature.SetField(field_name, field_value)

        packet.data = feature
        return packet

    # END geojson_feature

    # START geojson_collection

    @staticmethod
    def geojson_coll2ogr_feature_arr(packet, converter_args=None):
        json_feat_arr = packet.data["features"]
        ogr_feat_arr = list()

        for feat in json_feat_arr:
            packet.data = feat
            packet = FormatConverter.geojson_feature2ogr_feature(packet)
            ogr_feat_arr.append(packet.data)

        packet.data = ogr_feat_arr
        return packet

    # END geojson_collection

    # START ogr_feature

    @staticmethod
    def ogr_feature2struct(packet, converter_args=None):
        s = packet.data.ExportToJson()
        import ast
        # http://stackoverflow.com/questions/988228/converting-a-string-to-dictionary
        # ast.literal_eval("{'muffin' : 'lolz', 'foo' : 'kitty'}")
        packet.data = ast.literal_eval(s)

        return packet

    # END ogr_feature

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
    def record2record_array(packet, converter_args=None):
        if not hasattr(packet, 'arr'):
            packet.arr = list()

        if packet.data is not None:
            packet.arr.append(packet.data)
            packet.consume()

        # At end of stream or when max array size reached: close the array
        if packet.is_end_of_stream() is True or \
                (converter_args is not None and len(packet.arr) >= converter_args['max_len']):
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
    FORMAT.geojson_feature: {
        FORMAT.ogr_feature: FormatConverter.geojson_feature2ogr_feature
    },
    FORMAT.geojson_collection: {
        FORMAT.ogr_feature_array: FormatConverter.geojson_coll2ogr_feature_arr
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
    FORMAT.line_stream: {
        FORMAT.string: FormatConverter.no_op
    },
    FORMAT.xml_line_stream: {
        FORMAT.string: FormatConverter.no_op
    }
}
