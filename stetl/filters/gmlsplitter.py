#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Splits stream of GML lines into etree docs.
#
# Author: Just van den Broecke
#
import codecs
from stetl.util import Util, etree, StringIO
from stetl.filter import Filter
from stetl.packet import FORMAT

log = Util.get_log('gmlsplitter')

class GmlSplitter(Filter):
    """
    Split a stream of text XML lines into documents
    DEPRECATED: use the more robust XmlElementStreamerFileInput+XmlAssembler instead!!!
    TODO phase out

    consumes=FORMAT.xml_line_stream, produces=FORMAT.etree_doc
    """
    def __init__(self, configdict, section='gml_splitter'):
        Filter.__init__(self, configdict, section, consumes=FORMAT.xml_line_stream, produces=FORMAT.etree_doc)

        log.info("cfg = %s" % self.cfg.to_string())
        self.max_features = self.cfg.get_int('max_features', 10000)
        # File preamble
        self.start_container = self.cfg.get('start_container')
        # File postamble
        self.end_container = self.cfg.get('end_container')
        self.container_tag = self.cfg.get('container_tag')
        #        self.feature_tags = self.cfg.get('feature_tags').split(',')
        self.start_feature_markers = self.cfg.get('start_feature_markers').split(',')
        self.end_feature_markers = self.cfg.get('end_feature_markers').split(',')
        self.feature_count = 0
        self.total_feature_count = 0
        self.in_heading = True

        # End of file is line with end_container_tag
        self.end_container_tag = '</%s' % self.container_tag

        # Derive start and end tags from feature_tags
        #        for feature_tag in self.feature_tags:
        #            self.start_feature_markers.append('<%s' % feature_tag)
        #            self.end_feature_markers.append('</%s>' % feature_tag)
        self.expect_end_feature_markers = []
        self.expect_end_feature_tag = None
        self.buffer = None
        # Reusable XML parser
        self.xml_parser = etree.XMLParser(remove_blank_text=True)

    def invoke(self, packet):
        if packet.data is None:
            if (packet.is_end_of_stream() or packet.is_end_of_doc()) and self.buffer:
                # EOF but still data in buffer: make doc
                log.info("Last Buffer")
                self.buffer_to_doc(packet)
        else:
            # Valid line: push to the splitter
            # If buffer filled process it
            self.push_line(packet)
            if packet.is_end_of_doc() is True:
                self.buffer_to_doc(packet)

        return packet

    def push_line(self, packet):
        # Assume GML lines with single tag per line !!
        # This is ok for e.g. OGR output
        # TODO we need to become more sophisticated when no newlines in XML

        line = packet.consume()

        if packet.is_end_of_stream() is True:
            return packet

        # Start new buffer filling
        if self.buffer is None:
            self.buffer = self.init_buf()
            self.feature_count = 0
            self.in_heading = True
            packet.set_end_of_doc(False)

        if self.is_start_feature(line) is True:
            if self.in_heading:
                # First time: we are in heading
                # Write container start
                self.buffer.write(self.start_container)
                self.in_heading = False

            self.buffer.write(line)
            self.buffer.write('<!-- Feature #%s -->\n' % self.feature_count)

        else:
            # If within feature or end-of-feature: write
            if self.expect_end_feature_tag is not None and packet.is_end_of_doc() is False:
                self.buffer.write(line)

            # If endtag of feature found may also indicate buffer filled with max_features
            if self.is_end_feature(line) is True:
                # Start or end tag of ogr:feature  element
                if self.feature_count >= self.max_features and self.expect_end_feature_tag is None:
                    self.buffer.write(self.end_container)
                    log.info("Buffer filled feat_count = %d total_feat_count= %d" % (
                        self.feature_count, self.total_feature_count))
                    self.feature_count = 0
                    packet.set_end_of_doc()
                    return packet

            # Last tag (end of container) reaching
            if line.find(self.end_container_tag) >= 0:
                if self.buffer is not None and self.feature_count > 0:
                    self.buffer.write(self.end_container)
                    log.info("Buffer filled (EOF) feat_count = %d total_feat_count= %d" % (
                        self.feature_count, self.total_feature_count))
                    self.feature_count = 0
                    packet.set_end_of_doc()
                    return packet

        return packet

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

    def init_buf(self):
        buffer = StringIO()
        buffer = codecs.getwriter("utf8")(buffer)
        return buffer

    def is_start_feature(self, line):
        index = 0
        for feature_tag in self.start_feature_markers:
            if line.find(feature_tag) >= 0:
                # found it ! Now we expect the end tag for this start_tag
                self.expect_end_feature_tag = self.end_feature_markers[index]
                self.expect_end_feature_markers.append(self.expect_end_feature_tag)
                self.feature_count += 1
                self.total_feature_count += 1
                return True

            # Not found: next tag
            index += 1

        # Nothing found
        return False

    def is_end_feature(self, line):
        # Not even within a feature ?
        if self.expect_end_feature_tag is None:
            return False

        # ASSERTION: one or more expect_end_feature_tag set, thus within feature

        # End-of-feature reached ?
        if line.find(self.expect_end_feature_tag) >= 0:
            self.expect_end_feature_tag = None
            self.expect_end_feature_markers.pop()
            if len(self.expect_end_feature_markers) > 0:
                # Set expected end-tag to last in list
                self.expect_end_feature_tag = self.expect_end_feature_markers[-1]

            return True

        # Still within feature
        return False

