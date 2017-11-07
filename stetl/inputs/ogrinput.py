#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Input classes for ETL via GDAL OGR.
#
# Author: Just van den Broecke
#
import subprocess
from stetl.component import Config
from stetl.util import Util, gdal, ogr
from stetl.input import Input
from stetl.packet import FORMAT

log = Util.get_log('ogrinput')


class OgrInput(Input):
    """
    Direct GDAL OGR input via Python OGR wrapper. Via the Python API http://gdal.org/python
    an OGR data source is accessed and from each layer the Features are read.
    Each Layer corresponds to a "doc", so for multi-layer sources the 'end-of-doc' flag is
    set after a Layer has been read.

    This input can read almost any geospatial dataformat. One can use the features directly
    in a Stetl Filter or use a converter to e.g. convert to GeoJSON structures.

    produces=FORMAT.ogr_feature or FORMAT.ogr_feature_array (all features)
    """

    # Start attribute config meta
    # Applying Decorator pattern with the Config class to provide
    # read-only config values from the configured properties.

    @Config(ptype=str, default=None, required=True)
    def data_source(self):
        """
        String denoting the OGR datasource. Usually a path to a file like "path/rivers.shp" or connection string
        to PostgreSQL like "PG: host=localhost dbname='rivers' user='postgres'".
        """
        pass

    @Config(ptype=str, default=None, required=False)
    def source_format(self):
        """
        Instructs GDAL to use driver by that name to open datasource. Not required for
        many standard formats that are self-describing like ESRI Shapefile.

        Examples: 'PostgreSQL', 'GeoJSON' etc
        """
        pass

    @Config(ptype=dict, default=None, required=False)
    def source_options(self):
        """
        Custom datasource-specific options. Used in gdal.SetConfigOption().
        """
        pass

    @Config(ptype=str, default=None, required=False)
    def sql(self):
        """
        String with SQL query. Mandatory for PostgreSQL OGR source.
        """
        pass

    # End attribute config meta

    # Constructor
    def __init__(self, configdict, section):
        Input.__init__(self, configdict, section, produces=[FORMAT.ogr_feature, FORMAT.ogr_feature_array])

    def init(self):

        self.ogr = ogr
        # http://trac.osgeo.org/gdal/wiki/PythonGotchas
        self.gdal = gdal
        self.gdal.UseExceptions()
        log.info("Using GDAL/OGR version: %d" % int(gdal.VersionInfo('VERSION_NUM')))

        # GDAL error handler function
        # http://pcjericks.github.io/py-gdalogr-cookbook/gdal_general.html
        def gdal_error_handler(err_class, err_num, err_msg):
            err_type = {
                gdal.CE_None: 'None',
                gdal.CE_Debug: 'Debug',
                gdal.CE_Warning: 'Warning',
                gdal.CE_Failure: 'Failure',
                gdal.CE_Fatal: 'Fatal'
            }
            err_msg = err_msg.replace('\n', ' ')
            err_class = err_type.get(err_class, 'None')
            log.error('Error Number: %s, Type: %s, Msg: %s' % (err_num, err_class, err_msg))

        # install error handler
        self.gdal.PushErrorHandler(gdal_error_handler)

        # Raise a dummy error for testing
        # self.gdal.Error(1, 2, 'test error')

        if self.source_options:
            for k in self.source_options:
                self.gdal.SetConfigOption(k, self.source_options[k])

        # Open OGR data source in read-only mode.
        if self.source_format:
            self.data_source_p = ogr.GetDriverByName(self.source_format).Open(self.data_source, 0)
        else:
            self.data_source_p = self.ogr.Open(self.data_source, 0)

        # Report failure if failed
        if self.data_source_p is None:
            log.error("Cannot open OGR datasource: %s with the following drivers." % self.data_source)

            for iDriver in range(self.ogr.GetDriverCount()):
                log.info("  ->  " + self.ogr.GetDriver(iDriver).GetName())

            raise Exception()
        else:
            # Open ok: initialize
            self.layer = None

            if self.sql:
                self.layer_count = 1
                self.layer_idx = -1
            else:
                self.layer_count = self.data_source_p.GetLayerCount()
                self.layer_idx = 0

            log.info("Opened OGR source ok: %s layer count=%d" % (self.data_source, self.layer_count))

    def read(self, packet):
        if not self.data_source_p:
            log.info("End reading from: %s" % self.data_source)
            return packet

        if self.layer is None:
            if self.sql and self.layer_idx == -1:
                # PostgreSQL: Layer is gotten via Query
                # http://trac.osgeo.org/postgis/wiki/UsersWikiOGR
                self.layer = self.data_source_p.ExecuteSQL(self.sql)
                self.layer_idx = 0
            elif self.layer_idx < self.layer_count:
                self.layer = self.data_source_p.GetLayer(self.layer_idx)
                self.layer_idx += 1
                if self.layer is None:
                    log.error("Could not fetch layer %d" % 0)
                    raise Exception()
                log.info("Start reading from OGR Source: %s, Layer: %s" % (self.data_source, self.layer.GetName()))
            else:
                # No more Layers left: cleanup
                packet.set_end_of_stream()
                log.info("Closing OGR source: %s" % self.data_source)
                # Destroy not required anymore: http://trac.osgeo.org/gdal/wiki/PythonGotchas
                # self.data_source_p.Destroy()
                self.data_source_p = None
                return packet

        # Return all features from Layer (ogr_feature_array) or next feature (ogr_feature)
        if self.output_format == FORMAT.ogr_feature_array:
            # Assemble all features
            features = list()
            for feature in self.layer:
                features.append(feature)

            packet.data = features
            log.info("End reading all features from Layer: %s count=%d" % (self.layer.GetName(), len(features)))
            packet.set_end_of_doc()
            self.layer = None
        else:
            # Next feature
            feature = self.layer.GetNextFeature()
            if feature:
                packet.data = feature
            else:
                log.info("End reading from Layer: %s" % self.layer.GetName())
                packet.set_end_of_doc()
                self.layer = None

        return packet


class OgrPostgisInput(Input):
    """
     Input from PostGIS via ogr2ogr command. For now hardcoded to produce an ogr GML line stream.
     OgrInput may be a better alternative.

     Alternatives: either stetl.input.PostgresqlInput or stetl.input.OgrInput.

     produces=FORMAT.xml_line_stream
    """

    # Start attribute config meta
    @Config(ptype=str, required=False, default='localhost')
    def in_pg_host(self):
        """
        Host of input DB.
        """
        pass

    @Config(ptype=str, required=False, default='5432')
    def in_pg_port(self):
        """
        Port of input DB.
        """
        pass

    @Config(ptype=str, required=True, default=None)
    def in_pg_db(self):
        """
        Database name input DB.

        """
        pass

    @Config(ptype=str, required=False, default=None)
    def in_pg_schema(self):
        """
        DB Schema name input DB.
        """
        pass

    @Config(ptype=str, required=False, default='postgres')
    def in_pg_user(self):
        """
        User input DB.
        """
        pass

    @Config(ptype=str, required=False, default='postgres')
    def in_pg_password(self):
        """
        Password input DB.
        """
        pass

    @Config(ptype=str, required=False, default=None)
    def in_srs(self):
        """
        SRS (projection) (ogr2ogr -s_srs) input DB e.g. 'EPSG:28992'.
        """
        pass

    @Config(ptype=str, required=False, default=None)
    def in_pg_sql(self):
        """
        The input query (string) to fire.
        """
        pass

    @Config(ptype=str, required=False, default=None)
    def out_srs(self):
        """
        Target SRS (ogr2ogr -t_srs) code output stream.
        """
        pass

    @Config(ptype=str, required=False, default='2')
    def out_dimension(self):
        """
        Dimension (OGR: DIM=N) of features in output stream.
        """
        pass

    @Config(ptype=str, required=False, default=None)
    def out_gml_format(self):
        """
        GML format OGR name in output stream, e.g. 'GML3'.
        """
        pass

    @Config(ptype=str, required=False, default=None)
    def out_layer_name(self):
        """
        New Layer name (ogr2ogr -nln) output stream, e.g. 'address'.
        """
        pass

    @Config(ptype=str, required=False, default=None)
    def out_geotype(self):
        """
        OGR Geometry type new layer in output stream, e.g. POINT.
        """
        pass

    # End attribute config meta

    # TODO make this template configurable so we can have generic ogr2ogr input....
    pg_conn_tmpl = "PG:host=%s dbname=%s active_schema=%s user=%s password=%s port=%s"
    cmd_tmpl = 'ogr2ogr|-t_srs|%s|-s_srs|%s|-f|GML|%s|-dsco|FORMAT=%s|-lco|DIM=%s|%s|-SQL|%s|-nln|%s|%s'

    # Constructor
    def __init__(self, configdict, section):
        Input.__init__(self, configdict, section, produces=FORMAT.xml_line_stream)

    def init(self):
        self.ogr_process = None
        self.eof_stdout = False
        self.eof_stderr = False
        self.out_file = '/vsistdout/'

        #
        # Build ogr2ogr command line
        #
        # PostGIS PG: options
        self.pg = OgrPostgisInput.pg_conn_tmpl % (
            self.in_pg_host, self.in_pg_db, self.in_pg_schema, self.in_pg_user, self.in_pg_password, self.in_pg_port)

        # Entire ogr2ogr command line
        self.cmd = OgrPostgisInput.cmd_tmpl % (
            self.out_srs, self.in_srs, self.out_file, self.out_gml_format, self.out_dimension, self.pg, self.in_pg_sql,
            self.out_layer_name, self.out_geotype)

        # Make array to make it easy for Popen with quotes etc
        self.cmd = self.cmd.split('|')

    def exec_cmd(self):
        log.info("start ogr2ogr cmd = %s" % repr(self.cmd))
        self.ogr_process = subprocess.Popen(self.cmd,
                                            shell=False,
                                            stdout=subprocess.PIPE,
                                            stderr=subprocess.PIPE)

        err_line = self.readline_err()
        if err_line:
            log.warning('ogr2ogr: %s ' % err_line)

            #        exit_code = self.ogr_process.returncode

    def readline(self):
        if self.eof_stdout is True:
            return None

        line = self.ogr_process.stdout.readline()
        if not line:
            self.eof_stdout = True
            log.info("EOF stdout")
            return None

        line = line.decode('utf-8')
        return line

    def readline_err(self):
        if self.eof_stderr is True:
            return None

        line = self.ogr_process.stderr.readline()
        if not line:
            self.eof_stderr = True
            log.info("EOF stderr")
            return None

        return line

    def read(self, packet):
        if packet.is_end_of_stream():
            return packet

        # First time here : spawn the ogr2ogr command
        if self.ogr_process is None:
            # New splitter for each layer
            self.exec_cmd()

        packet.data = self.readline()
        if not packet.data:
            err_line = self.readline_err()
            if err_line:
                log.warning('ogr2ogr: %s ' % err_line)

            packet.set_end_of_stream()
            log.info('EOF ogr2ogr output')

        return packet
