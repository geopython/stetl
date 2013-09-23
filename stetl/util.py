# -*- coding: utf-8 -*-
#
# Utility functions and classes.
#
# Author:Just van den Broecke

import logging, os, glob, sys, types
from time import *

logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s %(name)s %(levelname)s %(message)s')

# Static utility methods
class Util:
    # http://wiki.tei-c.org/index.php/Remove-Namespaces.xsl
    xslt_strip_ns = '''<xsl:stylesheet version="1.0" xmlns:xsl="http://www.w3.org/1999/XSL/Transform">
    <xsl:output method="xml" indent="no"/>

    <xsl:template match="/|comment()|processing-instruction()">
        <xsl:copy>
          <xsl:apply-templates/>
        </xsl:copy>
    </xsl:template>

    <xsl:template match="*">
        <xsl:element name="{local-name()}">
          <xsl:apply-templates select="@*|node()"/>
        </xsl:element>
    </xsl:template>

    <xsl:template match="@*">
        <xsl:attribute name="{local-name()}">
          <xsl:value-of select="."/>
        </xsl:attribute>
    </xsl:template>
    </xsl:stylesheet>
    '''

    xslt_strip_ns_doc = False

    @staticmethod
    def get_log(name):
        log = logging.getLogger(name)
        log.setLevel(logging.DEBUG)
        return log

    @staticmethod
    def make_file_list(candidate_file, file_list=None, filename_pattern='*.[gxGX][mM][lL]', depth_search=False):

        if file_list is None:
            file_list = []

        candidate_file = candidate_file.strip()
        input_list = candidate_file.split(',')
        if len(input_list) > 1:
            for file in input_list:
                Util.make_file_list(file, file_list, filename_pattern, depth_search)
            return file_list

        if os.path.isdir(candidate_file):
            # Is a dir: get list
            matching_file_list = glob.glob(os.path.join(candidate_file, filename_pattern))
            for file in matching_file_list:
                # Matching file: append to file
                file_list.append(file)

            for dir in os.listdir(candidate_file):
                dir = os.path.join(candidate_file, dir)
                if os.path.isdir(dir):
                    Util.make_file_list(dir, file_list, filename_pattern, depth_search)

        else:
            # A single file or list of files
            matching_file_list = glob.glob(candidate_file)
            for file in matching_file_list:
                # Matching file: append to file
                file_list.append(file)

        return file_list

    # Start (global) + print timer: useful to time for processing and optimization
    @staticmethod
    def start_timer(message=""):
        log.info("Timer start: " + message)
        return time()

    # End (global) timer + print seconds passed: useful to time for processing and optimization
    @staticmethod
    def end_timer(start_time, message=""):
        log.info("Timer end: " + message + " time=" + str(round((time() - start_time), 0)) + " sec")

    # Convert a string to a dict
    @staticmethod
    def string_to_dict(s, separator='=', space='~'):
        # Convert string to dict: http://stackoverflow.com/a/1248990
        dict_arr = [x.split(separator) for x in s.split()]
        for x in dict_arr:
            x[1] = x[1].replace(space, ' ')

        return dict(dict_arr)


    # Remove all Namespaces from an etree Node
    # Handy for e.g. XPath expressions
    @staticmethod
    def stripNamespaces(node):
        if not Util.xslt_strip_ns_doc:
            Util.xslt_strip_ns_doc = etree.fromstring(Util.xslt_strip_ns)

        transform = etree.XSLT(Util.xslt_strip_ns_doc)
        return transform(node)


log = Util.get_log("util")

# GDAL/OGR Python Bindings not needed for now...
#import sys
#try:
#    from osgeo import ogr #apt-get install python-gdal
#except ImportError:
#    print("FATAAL: GDAL Python bindings not available, install e.g. with  'apt-get install python-gdal'")
#    sys.exit(-1)

try:
    from lxml import etree

    log.info("running with lxml.etree, good!")
except ImportError:
    try:
        # Python 2.5
        import xml.etree.cElementTree as etree

        log.warning("running with cElementTree on Python 2.5+ (suboptimal)")
    except ImportError:
        try:
            # Python 2.5
            import xml.etree.ElementTree as etree

            log.warning("running with ElementTree on Python 2.5+")
        except ImportError:
            try:
                # normal cElementTree install
                import cElementTree as etree

                log.warning("running with cElementTree")
            except ImportError:
                try:
                    # normal ElementTree install
                    import elementtree.ElementTree as etree

                    log.warning("running with ElementTree")
                except ImportError:
                    log.warning("Failed to import ElementTree from any known place")

try:
    from cStringIO import StringIO

    log.info("running with cStringIO, fabulous!")
except:
    from StringIO import StringIO

    log.warning("running with StringIO (this is suboptimal, try cStringIO")


class ConfigSection():
    def __init__(self, config_section):
        self.config_dict = dict(config_section)

    def get_dict(self):
        return self.config_dict

    def get(self, name, default=None):
        if not self.config_dict.has_key(name):
            return default
        return self.config_dict[name]

    def get_int(self, name, default=-1):
        result = self.get(name)
        if result is None:
            result = default
        else:
            result = int(result)
        return result

    # Get value as bool
    def get_bool(self, name, default=False):
        s = self.get(name)
        if s is None:
            result = default
        else:
            if s == 'false' or s == 'False':
                result = False
            else:
                if s == 'true' or s == 'True':
                    result = True
                else:
                    result = bool(s)

        return result

    # Get value as list
    def get_list(self, name, split_char=',', default=None):
        result = self.get(name)
        if result is None:
            result = default
        else:
            result = result.split(split_char)
        return result

    # Get value as tuple
    def get_tuple(self, name, split_char=',', default=None):
        result = self.get_list(name, split_char)
        if result is None:
            result = default
        else:
            result = tuple(result)
        return result

    def to_string(self):
        return repr(self.config_dict)

