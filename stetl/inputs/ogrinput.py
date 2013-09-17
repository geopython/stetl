#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Input classes for ETL via GDAL OGR.
#
# Author: Just van den Broecke
#
import subprocess
from stetl.util import Util
from stetl.input import Input
from stetl.packet import FORMAT

log = Util.get_log('ogrinput')


class OgrPostgisInput(Input):
    """
     Input from PostGIS via ogr2ogr command.
     TODO: look to use Fiona or direct OGR via Python.

     produces=FORMAT.xml_line_stream
    """

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

        in_pg_host = self.cfg.get('in_pg_host', 'localhost')
        in_pg_db = self.cfg.get('in_pg_db')
        in_pg_schema = self.cfg.get('in_pg_schema', 'public')
        in_pg_user = self.cfg.get('in_pg_user', 'postgres')
        in_pg_password = self.cfg.get('in_pg_password', 'postgres')
        in_pg_port = self.cfg.get('in_pg_port', '5432')
        in_srs = self.cfg.get('in_srs')
        in_pg_sql = self.cfg.get('in_pg_sql')

        out_srs = self.cfg.get('out_srs')
        out_file = '/vsistdout/'
        out_gml_format = self.cfg.get('out_gml_format')
        out_dimension = self.cfg.get('out_dimension', '2')
        out_layer_name = self.cfg.get('out_layer_name')
        out_geotype = self.cfg.get('out_geotype', '')

        #
        # Build ogr2ogr command line
        #
        # PostGIS PG: options
        self.pg = OgrPostgisInput.pg_conn_tmpl % (
        in_pg_host, in_pg_db, in_pg_schema, in_pg_user, in_pg_password, in_pg_port)

        # Entire ogr2ogr command line
        self.cmd = OgrPostgisInput.cmd_tmpl % (
            out_srs, in_srs, out_file, out_gml_format, out_dimension, self.pg, in_pg_sql, out_layer_name, out_geotype)

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



