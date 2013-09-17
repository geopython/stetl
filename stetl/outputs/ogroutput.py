#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Output classes for ETL.
#
# Author: Just van den Broecke
#
import subprocess
import os
import shutil
from stetl.output import Output
from stetl.util import Util
from stetl.packet import FORMAT

log = Util.get_log('ogroutput')

class Ogr2OgrOutput(Output):
    """
    Output from GML etree doc to any OGR2OGR output using the GDAL/OGR ogr2ogr command

    consumes=FORMAT.etree_doc
    """

    def __init__(self, configdict, section):
        Output.__init__(self, configdict, section, consumes=FORMAT.etree_doc)
        self.temp_file = self.cfg.get('temp_file')

        # For creating tables the GFS file needs to be newer than
        # the .gml file. -lco GML_GFS_TEMPLATE somehow does not work
        # so we copy the .gfs file each time with the .gml file with
        # the same base name
        self.gfs_file = self.cfg.get('gfs_file')
        self.lco = self.cfg.get('lco')
        self.ogr2ogr_cmd = self.cfg.get('ogr2ogr_cmd').replace('\\\n', ' ').replace('\n', ' ')
        self.first_run = True

    def save_doc(self, packet, file_path):
        if packet.data is None:
            return packet

        log.info('writing to file %s' % file_path)
        out_file = open(file_path, 'w')
        out_file.writelines(self.to_string(packet.data))
        out_file.close()

        # Copy the .gfs file if required, use the same base name
        # so ogr2ogr will pick it up.
        if self.gfs_file:
            file_ext = os.path.splitext(file_path)
            shutil.copy(self.gfs_file, file_ext[0] + '.gfs')

        log.info("written to %s" % file_path)
        return packet

    def execute_cmd(self, cmd):
        use_shell = True
        if os.name == 'nt':
            use_shell = False

        log.info("executing cmd=%s" % cmd)
        subprocess.call(cmd, shell=use_shell)
        log.info("execute done")

    def write(self, packet):
        if packet.data is None:
            return packet

        # Save the doc to a temp file
        self.save_doc(packet, self.temp_file)

        # Execute ogr2ogr
        ogr2ogr_cmd = self.ogr2ogr_cmd
        if self.lco and self.first_run is True:
            ogr2ogr_cmd += ' ' + self.lco
            self.first_run = False

        self.execute_cmd(ogr2ogr_cmd)
        return packet

