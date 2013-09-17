#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Input classes for ETL.
#
# Author: Just van den Broecke
#
import codecs
import re

from stetl.postgis import PostGIS
from stetl.input import Input
from stetl.util import Util, etree, StringIO
from stetl.packet import FORMAT

log = Util.get_log('deegreeinput')

class DeegreeBlobstoreInput(Input):
    """
    Read features from deegree Blobstore DB into an etree doc.

    produces=FORMAT.etree_doc
    """

    def __init__(self, configdict, section):
        Input.__init__(self, configdict, section, produces=FORMAT.etree_doc)
        self.max_features_per_doc = self.cfg.get_int('max_features_per_doc', 10000)
        self.start_container = self.cfg.get('start_container')
        self.end_container = self.cfg.get('end_container')
        self.start_feature_tag = self.cfg.get('start_feature_tag')
        self.end_feature_tag = self.cfg.get('end_feature_tag')
        self.cur_feature_blob = None
        self.rowcount = 0

        # http://www.mkyong.com/regular-expressions/how-to-extract-html-links-with-regular-expression/
        self.regex_xlink_href = re.compile("\\s*(?i)xlink:href\\s*=\\s*(\"#([^\"]*\")|'#[^']*'|(#[^'\">\\s]+))")

        self.db = None
        self.xlink_db = None
        self.buffer = None
        self.feature_count = 0
        # Reusable XML parser
        self.xml_parser = etree.XMLParser(remove_blank_text=True)

    def init(self):
        pass

    def read(self, packet):
        if packet.is_end_of_stream():
            return packet

        if self.db is None:
            # First time read
            log.info("reading records from blobstore..")
            self.db = PostGIS(self.cfg.get_dict())
            self.db.connect()
            sql = self.cfg.get('sql')
            self.rowcount = self.db.execute(sql)
            self.cur = self.db.cursor
            log.info("Read records rowcount=%d" % self.rowcount)

            # Init separate connection to fetch objects referenced by xlink:href
            self.xlink_db = PostGIS(self.cfg.get_dict())
            self.xlink_db.connect()

        # Query active
        while self.cur is not None:
            if self.buffer is None:
                self.buffer = self.init_buf()
                self.buffer.write(self.start_container)

            # Get next blob record
            record = self.cur.fetchone()

            # End of all records
            if record is None:
                # End of records: start closing
                self.buffer.write(self.end_container)
                self.cur = None
                self.db.commit()

                # Only create doc if there are features in the buffer
                if self.feature_count > 0:
                    self.buffer_to_doc(packet)
                packet.set_end_of_doc()
                break
            else:
                # New record: embed feature blob in feature tags and write to buffer
                feature_blob = self.write_feature(record)

                # If we have local xlinks: fetch the related features as well from the DB and
                # output them within the same document (local href resolvable)
                # TODO: in some cases we may need to be recursive (xlinks in xlinked features...)

                # First construct a single query for all xlinks
                xlink_sql = None
                for xlink in self.regex_xlink_href.finditer(feature_blob):
                    gml_id = xlink.group(1).strip('"').strip('#')
                    # We don't want multiple occurences of the same xlinked feature
                    if gml_id in self.xlink_ids:
                        continue

                    self.xlink_ids.add(gml_id)
                    if xlink_sql is None:
                        xlink_sql = "SELECT binary_object from gml_objects where gml_id = '%s'" % gml_id
                    else:
                        xlink_sql += "OR gml_id = '%s'" % gml_id

                # Should we retrieve and write xlinked features?
                if xlink_sql is not None:
                    # Fetch from DB
                    self.xlink_db.execute(xlink_sql)
                    while True:
                        # Get next blob record
                        xlink_record = self.xlink_db.cursor.fetchone()
                        if xlink_record is None:
                            break
                        self.write_feature(xlink_record)

                # Should we output a doc
                if self.feature_count >= self.max_features_per_doc:
                    # End of records: create XML doc
                    self.buffer.write(self.end_container)
                    self.buffer_to_doc(packet)
                    break

        if self.cur is None:
            # All records handled: close off
            packet.set_end_of_stream()
            # log.info("[%s]" % packet.data)

        return packet

    def write_feature(self, record):
        feature_blob = str(record[0])

        # Write start-tag, blob element, end-tag
        self.buffer.write(self.start_feature_tag)
        self.buffer.write(feature_blob)
        self.buffer.write(self.end_feature_tag)
        self.feature_count += 1
        return feature_blob

    def init_buf(self):
        buffer = StringIO()
        buffer = codecs.getwriter("utf8")(buffer)
        self.feature_count = 0
        self.xlink_ids = set()
        return buffer

    def buffer_to_doc(self, packet):
        # Process/transform data in buffer
        self.buffer.seek(0)
        try:
            # print '[' + self.buffer.getvalue() + ']'
            packet.data = etree.parse(self.buffer, self.xml_parser)
        #            print buffer.getvalue()
        except Exception, e:
            bufStr = self.buffer.getvalue()
            if not bufStr:
                log.info("parse buffer empty: content=[%s]" % bufStr)
            else:
                log.error("error in buffer parsing %s" % str(e))
                print bufStr
                raise
        self.buffer.close()
        self.buffer = None

