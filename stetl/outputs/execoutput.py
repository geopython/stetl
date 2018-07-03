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

    @Config(ptype=str, default='', required=False)
    def env_args(self):
        """
        Provides of list of environment variables which will be used when executing the given command.

        Example: env_args = pgpassword=postgres othersetting=value~with~spaces
        """
        pass

    @Config(ptype=str, default='=', required=False)
    def env_separator(self):
        """
        Provides the separator to split the environment variable names from their values.
        """
        pass

    def __init__(self, configdict, section, consumes):
        Output.__init__(self, configdict, section, consumes)

    def write(self, packet):
        return packet

    def execute_cmd(self, cmd):
        env_vars = Util.string_to_dict(self.env_args, self.env_separator)
        old_environ = os.environ.copy()

        try:
            os.environ.update(env_vars)
            log.info("executing cmd=%s" % cmd)
            subprocess.call(cmd, shell=True)
            log.info("execute done")
        finally:
            os.environ = old_environ


class CommandExecOutput(ExecOutput):
    """
    Executes an arbitrary command.

    consumes=FORMAT.string
    """

    def __init__(self, configdict, section):
        ExecOutput.__init__(self, configdict, section, consumes=FORMAT.string)

    def write(self, packet):
        if packet.data is not None:
            self.execute_cmd(packet.data)

        return packet


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
        """
        pass

    @Config(ptype=str, default=None, required=False)
    def dest_format(self):
        """
        Instructs GDAL to use driver by that name to open data destination. Not required for
        many standard formats that are self-describing like ESRI Shapefile.

        Examples: 'PostgreSQL', 'GeoJSON' etc
        """
        pass

    @Config(ptype=str, default=None, required=False)
    def lco(self):
        """
        Options for newly created layer (-lco).
        """

        pass

    @Config(ptype=str, default=None, required=False)
    def spatial_extent(self):
        """
        Spatial extent (-spat), to pass as xmin ymin xmax ymax
        """
        pass

    @Config(ptype=str, default=None, required=False)
    def gfs_template(self):
        """
        Name of GFS template file to use during loading. Passed to ogr2ogr as
        --config GML_GFS_TEMPLATE <name>
        """
        pass

    @Config(ptype=str, default=None, required=False)
    def options(self):
        """
        Miscellaneous options to pass to ogr2ogr.
        """
        pass

    @Config(ptype=bool, default=False, required=False)
    def cleanup_input(self):
        """
        Flag to indicate whether the input file to ogr2ogr should be cleaned up.
        """

        pass

    # End attribute config meta

    def __init__(self, configdict, section):
        ExecOutput.__init__(self, configdict, section, consumes=FORMAT.string)

        self.ogr2ogr_cmd = 'ogr2ogr -f ' + self.dest_format + ' ' + self.dest_data_source

        if self.spatial_extent:
            self.ogr2ogr_cmd += ' -spat ' + self.spatial_extent
        if self.options:
            self.ogr2ogr_cmd += ' ' + self.options

        self.first_run = True

    def write(self, packet):
        if packet.data is None:
            return packet

        # Execute ogr2ogr
        ogr2ogr_cmd = self.ogr2ogr_cmd
        if self.lco and self.first_run is True:
            ogr2ogr_cmd += ' ' + self.lco
            self.first_run = False

        if type(packet.data) is list:
            for item in packet.data:
                self.execute(ogr2ogr_cmd, item)
        else:
            self.execute(ogr2ogr_cmd, packet.data)

        return packet

    def execute(self, ogr2ogr_cmd, file_path):

        # For creating tables the GFS file needs to be newer than
        # the .gml file. -lco GML_GFS_TEMPLATE somehow does not work
        # so we copy the .gfs file each time with the .gml file with
        # the same base name
        # Copy the .gfs file if required, use the same base name
        # so ogr2ogr will pick it up.
        # Always assemble the GFS path, in case it is provided from outside.
        file_ext = os.path.splitext(file_path)
        gfs_path = file_ext[0] + '.gfs'
        if self.gfs_template:
            shutil.copy(self.gfs_template, gfs_path)

        # Append file name to command as last argument
        self.execute_cmd(ogr2ogr_cmd + ' ' + file_path)

        if self.cleanup_input:
            os.remove(file_path)
            if gfs_path and os.path.exists(gfs_path):
                os.remove(gfs_path)
