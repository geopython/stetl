#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Base classes for HTTP output like WFS-T and SOS-T or any other HTTP writing service.
#
# Author: Just van den Broecke
#
from stetl.output import Output
from stetl.util import Util
from stetl.packet import FORMAT
from stetl.component import Config
import httplib
import base64

log = Util.get_log('httpoutput')


class HttpOutput(Output):
    """
    Output via HTTP protocol, usually via POST.

    consumes=FORMAT.any
    """

    @Config(ptype=str, default=None, required=True)
    def host(self):
        """
        The hostname/IP addr for target request.
        """
        pass

    @Config(ptype=int, default=80, required=False)
    def port(self):
        """
        The port number for target request.
        """
        pass

    @Config(ptype=str, default='/', required=False)
    def path(self):
        """
        The path number for target request.
        """
        pass

    @Config(ptype=str, default='POST', required=False)
    def method(self):
        """
        The HTTP method for target request.
        """
        pass

    @Config(ptype=str, default='text/xml', required=False)
    def content_type(self):
        """
        The HTTP ContentType request header for target request.
        """
        pass

    @Config(ptype=str, default=None, required=False)
    def user(self):
        """
        The Username for HTTP basic auth for target request.
        """
        pass

    @Config(ptype=str, default=None, required=False)
    def password(self):
        """
        The Password for HTTP basic auth for target request.
        """
        pass

    @Config(ptype=bool, default=True, required=False)
    def list_fanout(self):
        """
        If we consume a list(), should we create a HTTP req for each member?
        """
        pass

    def __init__(self, configdict, section, consumes=FORMAT.any):
        Output.__init__(self, configdict, section, consumes)
        # self.accept_type = self.cfg.get('accept_type', self.content_type)
        self.req_nr = 0

    def create_payload(self, packet):
        """
        Create a HTTP body payload like for POST of an XML or JSON message.
        Subclasses like WFS and SOS override.
        :param packet:
        :return payload as string:
        """
        return packet.data

    def post(self, packet, payload):
        self.req_nr += 1

        webservice = httplib.HTTP(self.host, self.port)
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
        if statuscode == 200:
            res = webservice.getfile().read()
        elif statuscode == 204:
            res = ''
        else:
            log.error("Headers: %s" % str(header))
            res = webservice.getfile().read()
            log.info('Content: %s' % res)

        return statuscode, statusmessage, res

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
