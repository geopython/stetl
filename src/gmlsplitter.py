#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Splits stream of GML (from OGR) into buffers.
#
# Author: Just van den Broecke
#
import codecs
import optparse
from ConfigParser import ConfigParser
from util import Util, ConfigSection, etree, StringIO
from component import Component

log = Util.get_log('gmlsplitter')

class GmlSplitter(Component):

    # Constructor
    def __init__(self, configdict, section='gml_splitter'):
        Component.__init__(self, configdict, section)

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
        self.total_feature_count = 0

        # End of file is line with end_container_tag
        self.end_container_tag = '</%s' % self.container_tag

        # Derive start and end tags from feature_tags
#        for feature_tag in self.feature_tags:
#            self.start_feature_markers.append('<%s' % feature_tag)
#            self.end_feature_markers.append('</%s>' % feature_tag)
        self.expect_end_feature_markers = []
        self.expect_end_feature_tag = None
        self.buffer = None
        self.eof = False

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

    def push_line(self, line):
        # Assume GML lines with single tag per line !!
        # This is ok for e.g. OGR output
        # TODO we need to become more sophisticated when no newlines in XML

        if self.eof:
            return None

        # Start new buffer filling
        if self.buffer is None and self.eof is False:
            self.buffer = self.init_buf()
            self.feature_count = 0
            self.in_heading = True

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
            if self.expect_end_feature_tag is not None:
                self.buffer.write(line)

            # If endtag of feature found may also indicate buffer filled with max_features
            if self.is_end_feature(line) is True:
                # Start or end tag of ogr:feature  element
                self.in_heading = False

                if self.feature_count >= self.max_features and self.expect_end_feature_tag is None:
                    self.buffer.write(self.end_container)
                    buffer = self.buffer
                    self.buffer = None
                    log.info("Buffer filled feat_count = %d total_feat_count= %d" % (self.feature_count, self.total_feature_count))
                    self.feature_count = 0
                    return buffer

            # Last tag (end of container) reaching
            if line.find(self.end_container_tag) >= 0:
                if self.buffer is not None and self.feature_count > 0:
                    self.buffer.write(self.end_container)
                    buffer = self.buffer
                    self.buffer = None
                    self.eof = True
                    log.info("Buffer filled (EOF) feat_count = %d total_feat_count= %d" % (self.feature_count, self.total_feature_count))
                    self.feature_count = 0
                    return buffer

        return None


    def process_file(self, file_name):
        file_in = codecs.open(file_name, 'r', 'utf-8')
        line = file_in.readline()

        while line:
            buffer = self.push_line(line)
            if buffer:
                print buffer.getvalue()
            line = file_in.readline()


def main():
    usage = "usage: %prog [options]"
    parser = optparse.OptionParser(usage)
    parser.add_option("-c", "--config", action="store", type="string", dest="config_file",
                     default="etl.cfg",
                      help="ETL config file")

    options, args = parser.parse_args()
    config_file = options.config_file
    configdict = ConfigParser()

    try:
        configdict.read(config_file)
    except:
        log.warning("ik kan " + str(config_file) + " wel vinden maar niet inlezen.")

    options, args = parser.parse_args()
    file_name = '/dev/stdin'
    if len(args) == 1:
        log.info("args[0]=%s" % args[0])
        file_name = args[0]

    gml_splitter = GmlSplitter(configdict)
    gml_splitter.process_file(file_name)

if __name__ == "__main__":
    main()
