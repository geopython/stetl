# -*- coding: utf-8 -*-
#
# Output classes for ETL, executing commands.
#
# Author: Frank Steggink
#
import subprocess
import os
import shutil
from stetl.output import Output
from stetl.util import Util
from stetl.packet import FORMAT

log = Util.get_log('execoutput')


class ExecOutput(Output):
    """
    Executes any command (abstract base class).
    """

    def __init__(self, configdict, section, consumes):
        Output.__init__(self, configdict, section, consumes)

    def write(self, packet):
        return packet

    def execute_cmd(self, cmd):
        use_shell = True
        if os.name == 'nt':
            use_shell = False

        log.info("executing cmd=%s" % cmd)
        subprocess.call(cmd, shell=use_shell)
        log.info("execute done")

        
class Ogr2OgrExecOutput(ExecOutput):
    """
    Executes an Ogr2Ogr command.
    Input is a file name to be processed.
    Output by calling Ogr2Ogr command.

    consumes=FORMAT.string
    """

    def __init__(self, configdict, section):
        ExecOutput.__init__(self, configdict, section, consumes=FORMAT.string)

        # For creating tables the GFS file needs to be newer than
        # the .gml file. -lco GML_GFS_TEMPLATE somehow does not work
        # so we copy the .gfs file each time with the .gml file with
        # the same base name
        self.lco = self.cfg.get('lco')
        self.spatial_extent = self.cfg.get('spatial_extent')
        options = self.cfg.get('options')
        
        dest_format = self.cfg.get('dest_format')
        dest_data_source = self.cfg.get('dest_data_source')
        
        if not dest_format:
            raise ValueError('Verplichte parameter dest_format ontbreekt')
        if not dest_data_source:
            raise ValueError('Verplichte parameter dest_data_source ontbreekt')
                
        self.ogr2ogr_cmd = 'ogr2ogr -f ' + dest_format + ' ' + dest_data_source
        
        if self.spatial_extent:
            self.ogr2ogr_cmd += ' -spat ' + self.spatial_extent
        if options:
            self.ogr2ogr_cmd += ' ' + options
            
        self.first_run = True

    def write(self, packet):
        if packet.data is None:
            return packet

        # Execute ogr2ogr
        ogr2ogr_cmd = self.ogr2ogr_cmd
        if self.lco and self.first_run is True:
            ogr2ogr_cmd += ' ' + self.lco
            self.first_run = False

        for item in packet.data:
            # Append file name to command as last argument
            self.execute_cmd(ogr2ogr_cmd + ' ' + item)
        return packet
