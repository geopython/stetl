# -*- coding: utf-8 -*-
#
# Trivial Filter that lowercases feature property names.
# Shows how easy it is to use OGRInput, converting OGR Objects to
# to a GeoJSON structure for simple data access.
#
# Author:Just van den Broecke

from stetl.filter import Filter
from stetl.packet import FORMAT


class ToLowerFilter(Filter):
    def __init__(self, configdict, section):
        Filter.__init__(self, configdict, section, consumes=FORMAT.geojson_collection, produces=FORMAT.geojson_collection)

    def invoke(self, packet):
        if packet.data:
            for feature in packet.data['features']:
                properties = feature['properties']
                feature['properties'] = {}
                for prop_key in properties:
                    # Make field names lowercase
                    feature['properties'][prop_key.lower()] = properties[prop_key]

        return packet

