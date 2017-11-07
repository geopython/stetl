#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# POST data via WFS Transactional protocol (WFS-T).
#
# Author: Just van den Broecke
#
from stetl.component import Config
from stetl.output import Output
from stetl.util import Util
from stetl.packet import FORMAT
import httplib

log = Util.get_log('wfsoutput')


class WFSTOutput(Output):
    """
    Insert features via WFS-T (WFS Transaction) OGC protocol from an etree doc.

    consumes=FORMAT.etree_doc
    """

    # Start attribute config meta
    @Config(ptype=str, required=True, default=None)
    def wfs_host(self):
        """
        Hostname-part of URL e.g. geodata.ngr.nl.
        """
        pass

    @Config(ptype=str, required=False, default='80')
    def wfs_port(self):
        """
        Port-part of URL.
        """
        pass

    @Config(ptype=str, required=True, default=None)
    def wfs_path(self):
        """
        Path-part of URL e.g. '/bag/wfs'.
        """
        pass

    @Config(ptype=str, required=False, default='GenerateNew')
    def idgen(self):
        """
        Mode that WFS server generates new Id's for incoming Features.
        """
        pass

    # End attribute config meta

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
    headers = {"Content−type": 'Content-type: text/xml', "Accept": "text/xml"}

    def __init__(self, configdict, section):
        Output.__init__(self, configdict, section, consumes=FORMAT.etree_doc)

    def write(self, packet):
        if packet.data is None:
            return packet

        conn = httplib.HTTPConnection(self.wfs_host, self.wfs_port)
        conn.request("POST", self.wfs_path,
                     WFSTOutput.wfst_req % (self.idgen, packet.to_string()), WFSTOutput.headers)

        response = conn.getresponse()
        log.info('status=%s msg=%s' % (response.status, response.msg))
        log.info('response=%s' % response.read(1024))
        conn.close()
        return packet
