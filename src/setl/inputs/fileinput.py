#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Input classes for ETL.
#
# Author: Just van den Broecke
#
from .. util import Util,etree
from .. input import Input
from .. packet import  FORMAT

log = Util.get_log('fileinput')

class XmlFileInput(Input):
    # Constructor
    def __init__(self, configdict, section):
        Input.__init__(self, configdict, section, produces=FORMAT.etree_doc)
        self.file_path = self.cfg.get('file_path')

    def read(self, packet):
        # One-time read/parse only
        try:
            packet.data = etree.parse(self.file_path)
            log.info("file read and parsed OK : %s" % self.file_path)
        except Exception, e:
            log.info("file read and parsed NOT OK : %s" % self.file_path)

        # One-time read: we're all done
        packet.set_end_of_doc()
        packet.set_end_of_stream()

        return packet


class XmlLineStreamerFileInput(Input):
    # Constructor
    def __init__(self, configdict, section):
        Input.__init__(self, configdict, section, produces=FORMAT.xml_line_stream)
        self.file_path = self.cfg.get('file_path')
        self.file = None

    def read(self, packet):
        if self.file is None:
            self.file = open(self.file_path, 'r')

        if packet.is_end_of_stream():
            return packet

        # Assume valid line
        line = self.file.readline()
        if not line or line == '':
            packet.data = None
            packet.set_end_of_stream()
            log.info("EOF file")
            return packet

        packet.data = line.decode('utf-8')
        return packet

