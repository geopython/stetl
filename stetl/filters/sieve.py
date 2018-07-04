#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Lets data Packets pass-through, "sieve", based on criteria in their data.
# See issue: https://github.com/geopython/stetl/issues/78
#
# A concrete example is AttrValueRecordSieve which sieves records matching
# specific attribute values. One can also think of Sieves based on XPath expressions
# (e.g. for XML, GML), or geospatial, based on for example WFS-like filters like bounding boxes.
#
# Author: Just van den Broecke
#
from stetl.component import Config
from stetl.filter import Filter
from stetl.util import Util
from stetl.packet import FORMAT

log = Util.get_log('Sieve')


class Sieve(Filter):
    """
    ABC for specific Sieves that pass-through, "sieve",  Packets based on criteria in their data.
    """

    def __init__(self, configdict, section, consumes, produces):
        Filter.__init__(self, configdict, section, consumes, produces)

    def invoke(self, packet):
        if packet.data is None:
            return packet
        return self.sieve(packet)

    def sieve(self, packet):
        """
        To be implemented in subclasses.
        :param packet:
        :return:
        """
        return packet


class AttrValueRecordSieve(Sieve):
    """
    Sieves by attr/value(s) in Record Packets.
    """

    @Config(ptype=str, required=True)
    def attr_name(self):
        """
        Name of attribute whose value(s) are to be sieved.
        """
        pass

    @Config(ptype=list, default=list(), required=False)
    def attr_values(self):
        """
        Value(s) for attribute to be to sieved. If empty any value is passed through (existence
        of attr_name is criterium).
        """
        pass

    def __init__(self, configdict, section):
        Sieve.__init__(self, configdict, section, consumes=[FORMAT.record_array, FORMAT.record], produces=[FORMAT.record_array, FORMAT.record])

    def sieve(self, packet):
        """
        Filter out Packets that are not matching designated attr value(s).
        :param packet:
        :return:
        """

        # Start with empty result: fill with matching records
        record_data = packet.data
        packet.data = None

        # Data can be list or single record
        if type(record_data) is list:
            packet.data = list()
            for record in record_data:
                if self.matches_attr(record):
                    packet.data.append(record)
        elif type(record_data) is dict:
            if self.matches_attr(record_data):
                packet.data = record_data

        return packet

    def matches_attr(self, record):
        # Attr not even in record: no use going on
        if self.attr_name not in record:
            return False

        # Match if no value
        if not self.attr_values:
            return True

        return record[self.attr_name] in self.attr_values
