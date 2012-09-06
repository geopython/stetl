#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Utility functions and classes.
#
# Author:Just van den Broecke

import logging

logging.basicConfig(level=logging.INFO,
                     format='%(asctime)s %(name)s %(levelname)s %(message)s')

class Util:
    @staticmethod
    def get_log(name):
        log = logging.getLogger(name)
        log.setLevel(logging.DEBUG)
        return log

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
  log.info("running with lxml.etree")
except ImportError:
  try:
    # Python 2.5
    import xml.etree.cElementTree as etree
    log.warning("running with cElementTree on Python 2.5+")
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
    log.info("running with cStringIO")
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

    def get_bool(self, name, default=False):
        result = self.get(name)
        if result is None:
            result = default
        else:
            if result == 'false' or result == 'False':
                result = False
            else:
                result = bool(result)
        return result

    def to_string(self):
        return repr(self.config_dict)


