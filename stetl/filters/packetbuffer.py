# -*- coding: utf-8 -*-
#
# Packet buffering.
#
# Author:Just van den Broecke

import copy
from stetl.util import Util
from stetl.filter import Filter
from stetl.packet import FORMAT

log = Util.get_log("packetbuffer")


class PacketBuffer(Filter):
    """
    Buffers all incoming Packets, main use is unit-testing to inspect Packets after ETL is done.
    """

    # Constructor
    def __init__(self, configdict, section):
        Filter.__init__(self, configdict, section, consumes=FORMAT.any, produces=FORMAT.any)
        self.packet_list = []

    def invoke(self, packet):
        # Buffer Packet and pass-through, we need a deep copy as Packets may be cleared/reused
        self.packet_list.append(copy.copy(packet))
        return packet
