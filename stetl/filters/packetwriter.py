# -*- coding: utf-8 -*-
#
# Writes the payload of a packet as a string to a file.
# Based on outputs.fileoutput.FileOutput.
#
# Author: Frank Steggink
#
from stetl.component import Config
from stetl.filter import Filter
from stetl.util import Util
from stetl.packet import FORMAT

import os

log = Util.get_log('packetwriter')


class PacketWriter(Filter):
    """
    Writes the payload of a packet as a string to a file.

    consumes=FORMAT.any, produces=FORMAT.string
    """

    # Start attribute config meta
    @Config(ptype=str, default=None, required=True)
    def file_path(self):
        """
        File path to write content to.
        """
        pass

    # End attribute config meta

    # Constructor
    def __init__(self, configdict, section):
        Filter.__init__(self, configdict, section, consumes=FORMAT.any, produces=FORMAT.string)
        log.info("working dir %s" % os.getcwd())

    def invoke(self, packet):
        if packet.data is None:
            return packet

        file_path = self.cfg.get('file_path')
        return self.write_file(packet, file_path)

    def write_file(self, packet, file_path):
        log.info('writing to file %s' % file_path)
        out_file = open(file_path, 'w')

        out_file.write(packet.to_string())

        out_file.close()
        log.info("written to %s" % file_path)

        packet.data = file_path
        return packet
