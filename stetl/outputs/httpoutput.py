#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Output classes for ETL.
#
# Author: Just van den Broecke
#
from stetl.output import Output
from stetl.util import Util
from stetl.packet import FORMAT
import httplib

log = Util.get_log('httpoutput')

class HttpOutput(Output):
    """
    Output via HTTP protocol, usually via POST.

    consumes=FORMAT.etree_doc
    """

    headers = {"Content−type": "Content-type: text/xml", "Accept": "text/xml"}

    def __init__(self, configdict, section, consumes=FORMAT.any):
        Output.__init__(self, configdict, section, consumes)
        self.host = self.cfg.get('host')
        self.port = self.cfg.get('port', '80')
        self.path = self.cfg.get('path')
        self.method = self.cfg.get('method', 'POST')

        # If we receive a list(), should we create a HTTP req for each member?
        self.list_fanout = self.cfg.get_bool('list_fanout', True)

    def create_payload(self, packet):
        return packet.data

    def get_headers(self, packet):
        return HttpOutput.headers

    def post(self, packet, payload, headers):

        conn = httplib.HTTPConnection(self.host, self.port)
        conn.request(self.method, self.path, payload, headers)

        response = conn.getresponse()
        log.info('status=%s msg=%s' % (response.status, response.msg))
        log.info('response=%s' % response.read(1024))
        conn.close()
        return packet

    def write(self, packet):
        if packet.data is None:
            return packet

        if type(packet.data) is list and self.list_fanout is True:
                # Multiple records in list, save original
                original_data = packet.data
                for data_elm in original_data:
                    packet.data = data_elm
                    self.post(packet, self.create_payload(packet), self.get_headers(packet))
                    packet.data = original_data

        else:
            # Regular, single data element or list_fanout is False
            self.post(packet, self.create_payload(packet), self.get_headers(packet))

        return packet
