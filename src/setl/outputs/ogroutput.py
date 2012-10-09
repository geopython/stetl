#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Output classes for ETL.
#
# Author: Just van den Broecke
#
import subprocess,types,os
from ..output import Output
from ..util import  Util
from .. packet import  FORMAT

log = Util.get_log('ogroutput')

# Output from GML etree doc to any OGR2OGR output
# using the GDAL/OGR ogr2ogr command
class Ogr2OgrOutput(Output):
    def __init__(self, configdict, section):
        Output.__init__(self, configdict, section, consumes=FORMAT.etree_doc)
        self.temp_file = self.cfg.get('temp_file')
        self.ogr2ogr_cmd = self.cfg.get('ogr2ogr_cmd')

    def save_doc(self, packet, file_path):
        if packet.data is None:
             return packet

        log.info('writing to file %s' % file_path)
        out_file = open(file_path, 'w')
        out_file.writelines(self.to_string(packet.data))
        out_file.close()
        log.info("written to %s" % file_path)
        return packet

    def execute_cmd(self, cmd):
        use_shell = True
        if os.name == 'nt':
            use_shell = False

        log.info("executing cmd=%s" % cmd)
        subprocess.call(cmd, shell=use_shell)

    def write(self, packet):
        if packet.data is None:
            return packet

        # Save the doc to a temp file
        self.save_doc(packet, self.temp_file)

        # Execute ogr2ogr
        self.execute_cmd(self.ogr2ogr_cmd)
        return packet

