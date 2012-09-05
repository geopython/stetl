#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Output classes for ETL.
#
# Author: Just van den Broecke
#
from postgis import PostGIS
from component import Component
from util import  Util, etree
import os
import httplib

log = Util.get_log('output')

# Base class: Output Component
class Output(Component):
    # Constructor
    def __init__(self, configdict, section):
        Component.__init__(self, configdict, section)

        log.info("cfg = %s" % self.cfg.to_string())

    def invoke(self, doc):
        self.write(doc)
        return None

    def to_string(self, gml_doc, pretty_print=True, xml_declaration=True, encoding='utf-8'):
        return etree.tostring(gml_doc, pretty_print=pretty_print, xml_declaration = xml_declaration, encoding=encoding)

    def write(self, gml_doc):
        print(self.to_string(gml_doc))

# Pretty print XML to file
class FileOutput(Output):
    def __init__(self, configdict, section):
        Output.__init__(self, configdict, section)
        log.info("working dir %s" %os.getcwd())

    def write(self, gml_doc):
        file_path = self.cfg.get('file_path')
        log.info('writing to file %s' % file_path)
        out_file = open(file_path, 'w')
        out_file.writelines(self.to_string(gml_doc))
        out_file.close()
        log.info("written to %s" % file_path)

# Insert features into deegree Blobstore
class DeegreeBlobstoreOutput(Output):

    def __init__(self, configdict, section):
        Output.__init__(self, configdict, section)
        self.overwrite = self.cfg.get_bool('overwrite')
        self.srid = self.cfg.get_int('srid', -1)
        self.feature_member_tag = self.cfg.get('feature_member_tag')
        self.feature_type_ids = {}
        self.init()

    def init(self):
        self.get_feature_types()
        if self.overwrite:
            self.delete_features()
            # not required for now
            self.pg_srs_constraint()

    def get_feature_types(self):
        log.info('reading all featuretypes from DB')
        db = PostGIS(self.cfg.get_dict())
        db.connect()
        sql = "SELECT id,qname FROM feature_types"
        db.execute(sql)
        cur = db.cursor
        for record in cur:
            self.feature_type_ids[record[1]] = record[0]

    def delete_features(self):
        log.info('deleting ALL features in DB')
        db = PostGIS(self.cfg.get_dict())
        db.tx_execute("TRUNCATE gml_objects")

    def pg_srs_constraint(self):
        log.info('set srs constraint')
        db = PostGIS(self.cfg.get_dict())
        srid = self.srid
        sql = "ALTER TABLE gml_objects DROP CONSTRAINT enforce_srid_gml_bounded_by;"
        db.tx_execute(sql)
        sql = "ALTER TABLE gml_objects ADD CONSTRAINT enforce_srid_gml_bounded_by CHECK  (st_srid(gml_bounded_by) = (%s));" % srid
        db.tx_execute(sql)

    def write(self, gml_doc):
        log.info('inserting features in DB')
        db = PostGIS(self.cfg.get_dict())
        db.connect()
#        print self.to_string(gml_doc, False, False)
#        NS = {'base': 'urn:x-inspire:specification:gmlas:BaseTypes:3.2', 'gml': 'http://www.opengis.net/gml/3.2'}
#        featureMembers = gml_doc.xpath('//base:member/*', namespaces=NS)
        featureMembers = gml_doc.xpath("//*[local-name() = '%s']/*" % self.feature_member_tag)
        count = 0
        gml_ns = None
        for childNode in featureMembers:
            if gml_ns is None:
                if childNode.nsmap.has_key('gml'):
                    gml_ns = childNode.nsmap['gml']
                else:
                    if childNode.nsmap.has_key('GML'):
                        gml_ns = childNode.nsmap['GML']

            gml_id = childNode.get('{%s}id' % gml_ns)
            feature_type_id = self.feature_type_ids[childNode.tag]

            # Find a GML geometry in the GML NS
            ogrGeomWKT = None
#            gmlMembers = childNode.xpath(".//gml:Point|.//gml:Curve|.//gml:Surface|.//gml:MultiSurface", namespaces=NS)
            gmlMembers = childNode.xpath(".//*[local-name() = 'Point']|.//*[local-name() = 'Polygon']|.//*[local-name() = 'Curve']|.//*[local-name() = 'Surface']|.//*[local-name() = 'MultiSurface']")
            geom_str = None
            for gmlMember in gmlMembers:
                if geom_str is None:
                    geom_str = etree.tostring(gmlMember)
            #                   no need for GDAL Python bindings for now, maybe when we'll optimize with COPY iso INSERT
            #                    ogrGeom = ogr.CreateGeometryFromGML(str(gmlStr))
            #                    if ogrGeom is not None:
            #                        ogrGeomWKT = ogrGeom.ExportToWkt()
            #                        if ogrGeomWKT is not None:
            #                            break

            blob = etree.tostring(childNode, pretty_print=False, xml_declaration=False, encoding='UTF-8')

            if geom_str is None:
                sql = "INSERT INTO gml_objects(gml_id, ft_type, binary_object) VALUES (%s, %s, %s)"
                parameters = (gml_id, feature_type_id, db.make_bytea(blob))
            else:
                # ST_SetSRID(ST_GeomFromGML(%s)),-1)
                sql = "INSERT INTO gml_objects(gml_id, ft_type, binary_object, gml_bounded_by) VALUES (%s, %s, %s, ST_SetSRID( ST_GeomFromGML(%s),%s) )"
                parameters = (gml_id, feature_type_id, db.make_bytea(blob), geom_str, self.srid)

            if db.execute(sql, parameters) == -1:
                log.error("feat num# = %d error inserting feature blob=%s (but continuing)" % (count, blob))

                # will fail but we will close connection also
                db.commit()

                # proceed...
                log.info('retrying to proceed with remaining features...')
                db = PostGIS(self.cfg.get_dict())
                db.connect()
                count = 0


            count += 1

        exception = db.commit()
        if exception is not None:
            log.error("error in commit")

        log.info("inserted %s features" % count)

# Insert features via deegree FSLoader
class DeegreeFSLoaderOutput(Output):
    # d3toolbox FeatureStoreLoader -action insert -dataset ${DATASET} -format ${GML_VERSION} -fsconfig ${1} -idgen ${IDGEN_MODE} -workspace ${WORKSPACE}

    cmd_tmpl = '%s|FeatureStoreLoader|-action|insert|-dataset|%s|-format|%s|-fsconfig|%s|-idgen|%s|-workspace|%s'

    def __init__(self, configdict, section):
        Output.__init__(self, configdict, section)

    def write(self, gml_doc):
        from subprocess import Popen, PIPE

        d3tools_path = self.cfg.get('d3tools_path')
        workspace_path = self.cfg.get('workspace_path')
        feature_store = self.cfg.get('feature_store')
        format = self.cfg.get('format', 'GML_32')
        idgen = self.cfg.get('idgen', 'USE_EXISTING')
        java_opts = self.cfg.get('java_opts', "-Xms128m -Xmx1024m")
        dataset = self.cfg.get('dataset_path', '/dev/stdin')
        os.putenv("JAVA_OPTS", java_opts)

        d3tools = d3tools_path + '/bin/d3toolbox'
        cmd = DeegreeFSLoaderOutput.cmd_tmpl % (d3tools, dataset, format, feature_store, idgen, workspace_path)
        cmd = cmd.split('|')

        p = Popen(cmd, stdin=PIPE)

        p.stdin.write(self.to_string(gml_doc))

        result = p.communicate()[0]

         # print(result)

# Insert features via WFS-T (WFS Transaction) OGC protocol
class WFSTOutput(Output):
    wfst_req = '''<?xml version="1.0" encoding="UTF-8"?>
<wfs:Transaction version="1.1.0" service="WFS"
                 xmlns:wfs="http://www.opengis.net/wfs"
                 xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
                 xsi:schemaLocation="http://www.opengis.net/wfs http://schemas.opengis.net/wfs/1.1.0/wfs.xsd">

    <wfs:Insert handle="insert" idgen="%s">
    %s
    </wfs:Insert>
</wfs:Transaction>
    '''
    headers = {"Content−type" : 'Content-type: text/xml',"Accept":"text/xml"}

    def __init__(self, configdict, section):
        Output.__init__(self, configdict, section)
        self.wfs_host = self.cfg.get('host')
        self.wfs_port = self.cfg.get('port', '80')
        self.wfs_path = self.cfg.get('path')
        self.idgen = self.cfg.get('idgen', 'GenerateNew')

    def write(self, gml_doc):

        conn = httplib.HTTPConnection(self.wfs_host, self.wfs_port)
        conn.request("POST", self.wfs_path, WFSTOutput.wfst_req % (self.idgen, self.to_string(gml_doc, False, False)), WFSTOutput.headers)

        response = conn.getresponse()
        log.info('status=%s msg=%s' % (response.status, response.msg))
        log.info('response=%s' % response.read(1024))
        conn.close()
