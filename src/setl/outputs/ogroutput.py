#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Output classes for ETL.
#
# Author: Just van den Broecke
#
import subprocess
from ..output import Output
from ..util import  Util
from .. packet import  FORMAT

log = Util.get_log('ogroutput')

# Output from GML input to any OGR output
# using the GDAL/OGR ogr2ogr command
class Ogr2OgrOutput(Output):
    def __init__(self, configdict, section):
        Output.__init__(self, configdict, section, consumes=FORMAT.etree_feature_array)
        self.ogr2ogr_cmd = self.cfg.get('ogr2ogr_cmd')
        self.ogr_process = None

    def write(self, packet):
        if packet.data is None:
            return packet

        # First time here : spawn the ogr2ogr command
        if self.ogr_process is None:
            log.info("start ogr2ogr cmd = %s" % repr(self.ogr2ogr_cmd))
            self.ogr_process = subprocess.Popen(self.ogr2ogr_cmd,
                                            shell=True,
                                            stdin=subprocess.PIPE)

        feature_arr = packet.consume()
        for feature in feature_arr:
            str = self.to_string(feature)
            self.ogr_process.stdin.write(str)

        if packet.is_end_of_stream():
             self.ogr_process.stdin.flush()

        return packet

