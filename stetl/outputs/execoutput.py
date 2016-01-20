# -*- coding: utf-8 -*-
#
# Output classes for ETL, executing commands.
#
# Author: Frank Steggink
#
import subprocess
import os
import shutil
from stetl.component import Config
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

    # Start attribute config meta
    # Applying Decorator pattern with the Config class to provide
    # read-only config values from the configured properties.

    @Config(ptype=str, default=None, required=True)
    def dest_data_source(self):
        """
        String denoting the OGR data destination. Usually a path to a file like "path/rivers.shp" or connection string
        to PostgreSQL like "PG: host=localhost dbname='rivers' user='postgres'".

        Required: True

        Default: None
        """
        pass

    @Config(ptype=str, default=None, required=False)
    def dest_format(self):
        """
        Instructs GDAL to use driver by that name to open data destination. Not required for
        many standard formats that are self-describing like ESRI Shapefile.

        Examples: 'PostgreSQL', 'GeoJSON' etc

        Required: False

        Default: None
        """
        pass

    @Config(ptype=list, default=[], required=False)
    def lco(self):
        """
        Options for newly created layer (-lco).

        Type: list

        Required: False

        Default: []
        """

        pass

    @Config(ptype=list, default=None, required=False)
    def spatial_extent(self):
        """
        Spatial extent (-spat), to pass as xmin ymin xmax ymax

        Type: list

        Required: False

        Default: []
        """
        pass

    @Config(ptype=str, default=None, required=False)
    def gfs_template(self):
        """
        Name of GFS template file to use during loading. Passed to ogr2ogr as
        --config GML_GFS_TEMPLATE <name>

        Required: False

        Default: None
        """
        pass

    @Config(ptype=list, default=None, required=False)
    def options(self):
        """
        Miscellaneous options to pass to ogr2ogr.

        Required: False

        Default: None
        """
        pass

    @Config(ptype=bool, default=False, required=False)
    def cleanup_input(self):
        """
        Flag to indicate whether the input file to ogr2ogr should be cleaned up.

        Type: boolean

        Required: False

        Default: False
        """

        pass

    # End attribute config meta

    def __init__(self, configdict, section):
        ExecOutput.__init__(self, configdict, section, consumes=FORMAT.string)

        # For creating tables the GFS file needs to be newer than
        # the .gml file. -lco GML_GFS_TEMPLATE somehow does not work
        # so we copy the .gfs file each time with the .gml file with
        # the same base name
        self.lco = self.cfg.get('lco')
        self.gfs_template = self.cfg.get('gfs_template')
        spatial_extent = self.cfg.get('spatial_extent')
        options = self.cfg.get('options')
        
        dest_format = self.cfg.get('dest_format')
        dest_data_source = self.cfg.get('dest_data_source')
        
        if not dest_format:
            raise ValueError('Verplichte parameter dest_format ontbreekt')
        if not dest_data_source:
            raise ValueError('Verplichte parameter dest_data_source ontbreekt')
                
        self.ogr2ogr_cmd = 'ogr2ogr -f ' + dest_format + ' ' + dest_data_source
        
        if spatial_extent:
            self.ogr2ogr_cmd += ' -spat ' + spatial_extent
        if options:
            self.ogr2ogr_cmd += ' ' + options
        self.cleanup_input = self.cfg.get('cleanup_input')
            
        self.first_run = True

    def write(self, packet):
        if packet.data is None:
            return packet

        # Execute ogr2ogr
        ogr2ogr_cmd = self.ogr2ogr_cmd
        if self.lco and self.first_run is True:
            ogr2ogr_cmd += ' ' + self.lco
            self.first_run = False
            
        import os.path

        if type(packet.data) is list:
            for item in packet.data:
                self.execute(ogr2ogr_cmd, item)
        else:
            self.execute(ogr2ogr_cmd, packet.data)

        return packet
        
    def execute(self, ogr2ogr_cmd, file_path):
        # Copy the .gfs file if required, use the same base name
        # so ogr2ogr will pick it up.
        if self.gfs_template:
            file_ext = os.path.splitext(file_path)
            gfs_path = file_ext[0] + '.gfs'
            shutil.copy(self.gfs_template, gfs_path)
            
        # Append file name to command as last argument
        self.execute_cmd(ogr2ogr_cmd + ' ' + file_path)
            
        if self.cleanup_input:
            os.remove(file_path)
            if self.gfs_template:
                os.remove(gfs_path)
    
