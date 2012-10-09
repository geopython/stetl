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
        self.file_list = Util.make_file_list(self.file_path)
        self.file_list_done = []

    def read(self, packet):
        if not len(self.file_list):
            return packet

        file_path = self.file_list.pop(0)
        # One-time read/parse only
        try:
            packet.data = etree.parse(file_path)
            log.info("file read and parsed OK : %s" % file_path)
        except Exception, e:
            log.info("file read and parsed NOT OK : %s" % file_path)

        # One-time read: we're all done
        packet.set_end_of_doc()
        if not len(self.file_list):
            log.info("all files done")
            packet.set_end_of_stream()

        self.file_list_done.append(file_path)
        return packet

class XmlLineStreamerFileInput(Input):
    # Constructor
    def __init__(self, configdict, section):
        Input.__init__(self, configdict, section, produces=FORMAT.xml_line_stream)
        self.file_path = self.cfg.get('file_path')
        self.file_list = Util.make_file_list(self.file_path)
        self.file_list_done = []
        self.file = None

    def read(self, packet):
        if not len(self.file_list) and self.file is None:
            packet.set_end_of_stream()
            log.info("EOF file list")
            return packet

        if self.file is None:
            self.cur_file_path = self.file_list.pop(0)
            self.file = open(self.cur_file_path, 'r')
            log.info("file opened : %s" % self.cur_file_path)

        if packet.is_end_of_stream():
            return packet

        # Assume valid line
        line = self.file.readline()
        if not line or line == '':
            packet.data = None

            packet.set_end_of_doc()
            log.info("EOF file")
            if self.cur_file_path is not None:
                self.file_list_done.append(self.cur_file_path)
                self.cur_file_path = None
                if not len(self.file_list):
                    packet.set_end_of_stream()
                    log.info("EOF file list")


            self.file = None

            return packet

        packet.data = line.decode('utf-8')
        return packet

