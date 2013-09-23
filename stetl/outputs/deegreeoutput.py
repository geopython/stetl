#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Output Components for deegree server storage (www.deegree.org).
#
# Author: Just van den Broecke
#
# NB deegree also supports WFS-T!
#
from stetl.postgis import PostGIS
from stetl.output import Output
from stetl.util import Util, etree
from stetl.packet import FORMAT
import os

log = Util.get_log('deegreeoutput')

class DeegreeBlobstoreOutput(Output):
    """
    Insert features into deegree Blobstore from an etree doc.

    consumes=FORMAT.etree_doc
    """
    def __init__(self, configdict, section):
        Output.__init__(self, configdict, section, consumes=FORMAT.etree_doc)
        self.overwrite = self.cfg.get_bool('overwrite')
        self.srid = self.cfg.get_int('srid', -1)
        self.feature_member_tag = self.cfg.get('feature_member_tag')
        self.feature_type_ids = {}

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

    def write(self, packet):
        if packet.data is None:
            return packet

        gml_doc = packet.data
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
            gmlMembers = childNode.xpath(
                ".//*[local-name() = 'Point']|.//*[local-name() = 'Polygon']|.//*[local-name() = 'Curve']|.//*[local-name() = 'Surface']|.//*[local-name() = 'MultiSurface']")
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
        return packet

#
class DeegreeFSLoaderOutput(Output):
    """
    Insert features via deegree using deegree's FSLoader tool from an etree doc.

    consumes=FORMAT.etree_doc
    """
    # d3toolbox FeatureStoreLoader -action insert -dataset ${DATASET} -format ${GML_VERSION} -fsconfig ${1} -idgen ${IDGEN_MODE} -workspace ${WORKSPACE}

    cmd_tmpl = '%s|FeatureStoreLoader|-action|insert|-dataset|%s|-format|%s|-fsconfig|%s|-idgen|%s|-workspace|%s'

    def __init__(self, configdict, section):
        Output.__init__(self, configdict, section, consumes=FORMAT.etree_doc)

    def write(self, packet):
        from subprocess import Popen, PIPE

        if packet.data is None:
            return packet

        gml_doc = packet.data
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
        return packet

        # print(result)

