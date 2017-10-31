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
from stetl.component import Config
from stetl.output import Output
from stetl.util import Util, gdal, ogr, osr
from stetl.packet import FORMAT

log = Util.get_log('ogroutput')


class OgrOutput(Output):
    """
    Direct GDAL OGR output via Python OGR wrapper. Via the Python API http://gdal.org/python
    OGR Features are written.

    This output can write almost any geospatial, OGR-defined, dataformat.

    consumes=FORMAT.ogr_feature or FORMAT.ogr_feature_array
    """

    # Start attribute config meta
    # Applying Decorator pattern with the Config class to provide
    # read-only config values from the configured properties.

    @Config(ptype=bool, default=False, required=False)
    def append(self):
        """
        Add to destination destination if it extists (ogr2ogr -append option).
        """

        pass

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

    @Config(ptype=list, default=[], required=False)
    def dest_create_options(self):
        """
        Creation options.

        Examples: ..
        """
        pass

    @Config(ptype=dict, default=None, required=False)
    def dest_options(self):
        """
        Custom data destination-specific options. Used in gdal.SetConfigOption().
        """
        pass

    @Config(ptype=list, default=[], required=False)
    def layer_create_options(self):
        """
        Options for newly created layer (-lco).
        """

        pass

    @Config(ptype=str, default=None, required=True)
    def new_layer_name(self):
        """
        Layer name for layer created in the destination source.

        """

        pass

    @Config(ptype=bool, default=False, required=False)
    def overwrite(self):
        """
        Overwrite destination if it extists (ogr2ogr -overwrite option).
        """

        pass

    @Config(ptype=str, default=None, required=False)
    def target_srs(self):
        """
        SRS (projection) for the target.
        """
        pass

    @Config(ptype=str, default=None, required=False)
    def sql(self):
        """
        String with SQL query. Mandatory for PostgreSQL OGR dest.
        """
        pass

    # End attribute config meta

    # Constructor
    def __init__(self, configdict, section):
        Output.__init__(self, configdict, section, consumes=[FORMAT.ogr_feature, FORMAT.ogr_feature_array])

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

        self.update = self.overwrite or self.append

        if self.dest_options:
            for k in self.dest_options:
                self.gdal.SetConfigOption(k, self.dest_options[k])

        self.dest_driver = None
        self.dest_fd = None

        # Loosely based on https://github.com/OSGeo/gdal/blob/trunk/gdal/swig/python/samples/ogr2ogr.py

        # /* -------------------------------------------------------------------- */
        # /*      Try opening the output data source as an existing, writable      */
        # /* -------------------------------------------------------------------- */
        if self.update:
            # Try opening in update mode
            self.dest_fd = ogr.Open(self.dest_data_source, True)

            if self.dest_fd is not None:
                if len(self.dest_create_options) > 0:
                    log.warn("Datasource creation options ignored since an existing datasource being updated.")

                self.dest_driver = self.dest_fd.GetDriver()
                if self.overwrite:
                    self.dest_driver.DeleteDataSource(self.dest_data_source)
                    self.dest_fd = None
                    self.dest_driver = None
                    self.update = False

        # /* -------------------------------------------------------------------- */
        # /*      Find the output driver.                                         */
        # /* -------------------------------------------------------------------- */
        if self.dest_driver is None:

            # Open OGR data dest in write-only mode.
            self.dest_driver = ogr.GetDriverByName(self.dest_format)

            # Report failure if failed
            if self.dest_driver is None:
                log.error("Cannot open OGR data destination: %s with the following drivers." % self.dest_data_source)

                for iDriver in range(self.ogr.GetDriverCount()):
                    log.info("  ->  " + self.ogr.GetDriver(iDriver).GetName())

                raise Exception()

            if self.dest_driver.TestCapability(ogr.ODrCCreateDataSource) is False:
                log.error("%s driver does not support data source creation." % self.dest_format)
                raise Exception()

        # /* -------------------------------------------------------------------- */
        # /*      Create the output data source.                                  */
        # /* -------------------------------------------------------------------- */
        if self.dest_fd is None:
            self.dest_fd = self.dest_driver.CreateDataSource(self.dest_data_source, options=self.dest_create_options)
            if self.dest_fd is None:
                log.error("%s driver failed to create %s" % (self.dest_format, self.dest_data_source))
                raise Exception()

        # /* -------------------------------------------------------------------- */
        # /*      Parse the output SRS definition if possible.                    */
        # /* -------------------------------------------------------------------- */
        output_srs_ref = None
        if self.target_srs is not None:
            output_srs_ref = osr.SpatialReference()
            if output_srs_ref.SetFromUserInput(self.target_srs) != 0:
                log.error("Failed to process SRS definition: %s" % self.target_srs)
            raise Exception()

        self.layer = self.dest_fd.CreateLayer(self.new_layer_name, output_srs_ref, ogr.wkbUnknown,
                                              self.layer_create_options)
        self.feature_def = None

        log.info("Opened OGR dest ok: %s " % self.dest_data_source)

    def write(self, packet):

        # Are we all done?
        if packet.data is None or self.dest_fd is None:
            self.write_end(packet)
            return packet

        if self.layer is None:
            log.info("No Layer, end writing to: %s" % self.dest_data_source)
            return packet

        # Assume ogr_feature_array input, otherwise convert ogr_feature to list
        if type(packet.data) is list:
            # Write feature collection to OGR Layer output
            for feature in packet.data:
                self.write_feature(feature)

            self.write_end(packet)

        else:
            # Write single feature to OGR Layer output
            if packet.end_of_stream or packet.end_of_doc:
                self.write_end(packet)
                return packet

            self.write_feature(packet.data)

        return packet

    def write_feature(self, feature):

        # Set the Layer Feature Definition once, using the first feature received
        if self.feature_def is None:
            self.feature_def = feature.GetDefnRef()
            field_count = self.feature_def.GetFieldCount()
            for i in range(0, field_count):
                field_def = self.feature_def.GetFieldDefn(i)
                self.layer.CreateField(field_def)

        # Write Feature to the Layer
        self.layer.CreateFeature(feature)

        # Dispose memory
        feature.Destroy()

    def write_end(self, packet):
        # Destroy not required anymore: http://trac.osgeo.org/gdal/wiki/PythonGotchas
        # self.dest_fd.Destroy()
        log.info("End writing to: %s" % self.dest_data_source)
        self.dest_fd = None
        self.layer = None
        return packet


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
        self.spatial_extent = self.cfg.get('spatial_extent')
        self.ogr2ogr_cmd = self.cfg.get('ogr2ogr_cmd').replace('\\\n', ' ').replace('\n', ' ')
        if self.spatial_extent:
            self.ogr2ogr_cmd += ' -spat ' + self.spatial_extent
        self.first_run = True

    def save_doc(self, packet, file_path):
        if packet.data is None:
            return packet

        log.info('writing to file %s' % file_path)
        out_file = open(file_path, 'w')
        out_file.writelines(packet.to_string())
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
