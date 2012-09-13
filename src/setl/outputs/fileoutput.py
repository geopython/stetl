#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Output classes for ETL.
#
# Author: Just van den Broecke
#
from ..output import Output
from ..util import  Util
import os

log = Util.get_log('fileoutput')

# Pretty print XML to file
class FileOutput(Output):
    def __init__(self, configdict, section):
        Output.__init__(self, configdict, section)
        log.info("working dir %s" %os.getcwd())

    def write(self, packet):
        if packet.data is None:
             return packet

        file_path = self.cfg.get('file_path')
        log.info('writing to file %s' % file_path)
        out_file = open(file_path, 'w')
        out_file.writelines(self.to_string(packet.data))
        out_file.close()
        log.info("written to %s" % file_path)
        return packet

