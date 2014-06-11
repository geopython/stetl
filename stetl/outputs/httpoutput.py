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
import base64

log = Util.get_log('httpoutput')

class HttpOutput(Output):
    """
    Output via HTTP protocol, usually via POST.

    consumes=FORMAT.etree_doc
    """
    def __init__(self, configdict, section, consumes=FORMAT.any):
        Output.__init__(self, configdict, section, consumes)
        self.host = self.cfg.get('host')
        self.port = self.cfg.get('port', '80')
        self.path = self.cfg.get('path')
        self.method = self.cfg.get('method', 'POST')
        self.user = self.cfg.get('user', None)
        self.password = self.cfg.get('password', None)
        self.content_type = self.cfg.get('content_type', 'text/xml')
        # self.accept_type = self.cfg.get('accept_type', self.content_type)

        # If we receive a list(), should we create a HTTP req for each member?
        self.list_fanout = self.cfg.get_bool('list_fanout', True)
        self.req_nr = 0

    def create_payload(self, packet):
        return packet.data

    def post(self, packet, payload):
        self.req_nr += 1

        webservice = httplib.HTTP(self.host)
        # write your headers
        webservice.putrequest(self.method, self.path)
        webservice.putheader("Host", self.host)
        webservice.putheader("User-Agent", "Stetl Python http")
        webservice.putheader("Content-Type", self.content_type)
        # webservice.putheader("Accept", self.accept_type)
        webservice.putheader("Content-Length", "%d" % len(payload))

        # basic auth: http://mozgovipc.blogspot.nl/2012/06/python-http-basic-authentication-with.html
        # base64 encode the username and password
        # write the Authorization header like: 'Basic base64encode(username + ':' + password)
        if self.user is not None:
            auth = base64.encodestring('%s:%s' % (self.user, self.password)).replace('\n', '')
            webservice.putheader("Authorization", "Basic %s" % auth)

        webservice.endheaders()
        webservice.send(payload)

        # get the response
        statuscode, statusmessage, header = webservice.getreply()
        log.info("Req nr %d - response status: code=%d msg=%s" % (self.req_nr, statuscode, statusmessage))
        if statuscode != 200:
            log.error("Headers: %s" % str(header))
            res = webservice.getfile().read()
            log.info('Content: %s' % res)

        # conn = httplib.HTTPConnection(self.host, self.port)
        # conn.request(self.method, self.path, payload, headers)

        # response = conn.getresponse()
        # log.info('status=%s msg=%s' % (response.status, response.msg))
        # log.info('response=%s' % response.read(1024))
        # conn.close()
        return packet

    def write(self, packet):
        if packet.data is None:
            return packet

        if type(packet.data) is list and self.list_fanout is True:
                # Multiple records in list, save original
                original_data = packet.data
                for data_elm in original_data:
                    packet.data = data_elm
                    self.post(packet, self.create_payload(packet))
                    packet.data = original_data

        else:
            # Regular, single data element or list_fanout is False
            self.post(packet, self.create_payload(packet))

        return packet
