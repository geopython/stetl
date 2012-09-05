#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Input classes for ETL.
#
# Author: Just van den Broecke
#
import subprocess
from util import Util, ConfigSection, etree
from gmlsplitter import GmlSplitter
from component import Component

log = Util.get_log('input')

# Base class: Input Component
class Input(Component):
    # Constructor
    def __init__(self, configdict, section):
        Component.__init__(self, configdict, section)

        log.info("cfg = %s" % self.cfg.to_string())

    def invoke(self, doc=None):
        return self.read()

    def read(self):
        return None


class XmlFileInput(Input):
    # Constructor
    def __init__(self, configdict, section):
        Input.__init__(self, configdict, section)
        self.file_path = self.cfg.get('file_path')
        self.doc = None

    def read(self):
        # One-time read/parse only
        if self.doc is not None:
            return None

        try:
            self.doc = etree.parse(self.file_path)
            log.info("file read and parsed OK : %s" % self.file_path)
        except Exception, e:
            log.info("file read and parsed NOT OK : %s" % self.file_path)
        return self.doc


class BigXmlFileInput(Input):
    # Constructor
    def __init__(self, configdict, section):
        Input.__init__(self, configdict, section)
        self.file_path = self.cfg.get('file_path')
        self.doc = None
        self.file = None
        # Reusable XML parser
        self.xml_parser = etree.XMLParser(remove_blank_text=True)

    def buffer_to_doc(self, buffer):

        # Process/transform data in buffer
        buffer.seek(0)
        try:
            self.gml_doc = etree.parse(buffer, self.xml_parser)
#            print buffer.getvalue()
        except Exception, e:
            bufStr = buffer.getvalue()
            if not bufStr:
                log.info("parse buffer empty: content=[%s]" % bufStr)
            else:
                print bufStr
                log.error("error in buffer parsing %s" % str(e))
                raise
        buffer.close()

    def readline(self):
        if self.eof_stdout is True:
            return None

        line = self.file.readline()
        if not line or line == '':
            self.eof_stdout = True
            log.info("EOF file")
            return None

        line = line.decode('utf-8')
        return line

    def read(self):
        if self.file is None:
            self.file = open(self.file_path, 'r')
            self.eof_stdout = False
            self.gml_splitter = GmlSplitter(self.configdict)

        self.gml_doc = None
        while 1:
            line = self.readline()
#            print '|' + line
            if line is None:
                buffer = self.gml_splitter.buffer
                if buffer is not None:
                    # EOF but still data in buffer: make doc
                    log.info("Last Buffer")
                    self.buffer_to_doc(buffer)

                break
            else:
                # Valid line: push to the splitter
                # If buffer filled process it
                buffer = self.gml_splitter.push_line(line)
                if buffer is not None:
                    self.buffer_to_doc(buffer)
                    break

        return self.gml_doc


class OgrPostgisInput(Input):
    pg_conn_tmpl = "PG:host=%s dbname=%s active_schema=%s user=%s password=%s port=%s"
    cmd_tmpl = 'ogr2ogr|-t_srs|%s|-s_srs|%s|-f|GML|%s|-dsco|FORMAT=%s|-lco|DIM=%s|%s|-SQL|%s|-nln|%s|%s'

    # Constructor
    def __init__(self, configdict, section):
        Input.__init__(self, configdict, section)
        self.init()

    def init(self):
    #        self.cmd='ogr2ogr|-t_srs|EPSG:4258|-s_srs|EPSG:28992|-f|GML|/vsistdout/|-dsco|FORMAT=GML3|-lco|DIM=2|%s|-SQL|%s|-nln|adres|POINT'
        host = self.cfg.get('host', 'localhost')
        db = self.cfg.get('database')
        schema = self.cfg.get('schema', 'public')
        user = self.cfg.get('user', 'postgres')
        password = self.cfg.get('password', 'postgres')
        port = self.cfg.get('port', '5432')

        self.pg = OgrPostgisInput.pg_conn_tmpl % (host, db, schema, user, password, port)
        self.layer_names = self.cfg.get('layers').split(',')
        self.gml_splitter = None
        self.layer_index = -1
        # Reusable XML parser
        self.xml_parser = etree.XMLParser(remove_blank_text=True)

    def get_layer_names(self):
        return self.layer_names

    def exec_layer(self, db_layer_section):
        lcfg = ConfigSection(self.configdict.items(db_layer_section))
        log.info("run_layer section = [%s] name = [%s]" % (db_layer_section, lcfg.get('name')))
        t_srs = self.cfg.get('t_srs')
        s_srs = self.cfg.get('s_srs')
        gml_out_file = lcfg.get('gml_out_file')
        gml_format = lcfg.get('gml_format')
        dimension = lcfg.get('dimension')
        sql = lcfg.get('sql')
        new_layer_name = lcfg.get('new_layer_name')
        geotype = lcfg.get('geotype', '')

        # Bouw ogr2ogr commando
        cmd = OgrPostgisInput.cmd_tmpl % (
            t_srs, s_srs, gml_out_file, gml_format, dimension, self.pg, sql, new_layer_name, geotype)
        cmd = cmd.split('|')
        self.exec_cmd(cmd)

    def exec_cmd(self, cmd):
        log.info("start ogr2ogr cmd = %s" % repr(cmd))
        self.eof_stdout = False
        self.eof_stderr = False
        self.process = subprocess.Popen(cmd,
                                        shell=False,
                                        stdout=subprocess.PIPE,
                                        stderr=subprocess.PIPE)

    #        exit_code = self.process.returncode

    def readline(self):
        if self.eof_stdout is True:
            return None

        line = self.process.stdout.readline()
        if not line:
            self.eof_stdout = True
            log.info("EOF stdout")
            return None

        line = line.decode('utf-8')
        return line

    def readline_err(self):
        if self.eof_stderr is True:
            return None

        line = self.process.stderr.readline()
        if not line:
            self.eof_stderr = True
            log.info("EOF stderr")
            return None

        return line

    def read(self):
        if self.layer_index < 0:
            self.layer_index = 0

        if self.layer_index >= len(self.layer_names):
            return None

        if self.gml_splitter is None:
            # New splitter for each layer
            self.gml_splitter = GmlSplitter(self.configdict)
            self.exec_layer(self.layer_names[self.layer_index])

        self.gml_doc = None
        while 1:
            line = self.readline()
            if not line:
                line = self.readline_err()
                if not line:
                    log.info("EOF Layer %s" % self.layer_names[self.layer_index])
                    buffer = self.gml_splitter.buffer
                    if buffer is not None:
                        # EOF but still data in buffer: make doc
                        log.info("Buffer ready layer = %s" % self.layer_names[self.layer_index])
                        self.buffer_to_doc(buffer)

                    self.nextLayer()
                    break
            else:
                # Valid line: push to the splitter
                # If buffer filled process it
                buffer = self.gml_splitter.push_line(line)
                if buffer is not None:
                    self.buffer_to_doc(buffer)

                    # GMLSplitter may have reached end-of-container
                    # Proceed to next layer
                    if self.gml_splitter.eof is True:
                        self.nextLayer()

                    break

        return self.gml_doc

    def nextLayer(self):
        self.layer_index += 1
        self.gml_splitter = None

    def buffer_to_doc(self, buffer):
        # Process/transform data in buffer
        buffer.seek(0)
        # bufStr = buffer.getvalue()
        # log.info("parse buffer: content=[%s]" % bufStr)
        self.gml_doc = etree.parse(buffer, self.xml_parser)
        buffer.close()

    def process_layer(self, layer_name):
        self.exec_layer(layer_name)

        while 1:
            line = self.readline()
            if not line:
                line = self.readline_err()
                if not line:
                    log.info("EOF All")
                    break
            print line

    def process(self):
        layer_names = self.get_layer_names()
        for layer_name in layer_names:
            self.process_layer(layer_name)


