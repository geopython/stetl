# -*- coding: utf-8 -*-
#
# Input classes for ETL via HTTP.
#
# Author: Just van den Broecke
#
from stetl.input import Input
from stetl.util import Util
from stetl.packet import FORMAT
import urllib
import urllib2


log = Util.get_log('httpinput')


class HttpInput(Input):
    """
     Input via HTTP protocol.

     produces=FORMAT.any
    """

    def __init__(self, configdict, section, produces=FORMAT.any):
        Input.__init__(self, configdict, section, produces)

        # url and optional parameters
        self.url = self.cfg.get('url')
        self.parameters = self.cfg.get('parameters')

        # http://docs.python.org/2/howto/urllib2.html
        self.query_string = None
        if self.parameters:
            # http://stackoverflow.com/questions/988228/converting-a-string-to-dictionary
            import ast
            self.parameters = ast.literal_eval(self.parameters)
            self.query_string = urllib.urlencode(self.parameters)

        log.info("url=%s" % self.url)


    def read(self, packet):
        """
        Read the data from the URL.
        :param packet:
        :return:
        """
        # Done with URL ?
        if self.url is None:
            packet.set_end_of_stream()
            log.info("EOF URL reading done")
            return packet

        request = urllib2.Request(self.url, self.query_string)
        response = urllib2.urlopen(request)

        packet.data = self.format_data(response.read())
        self.url = None
        return packet

    def format_data(self, data):
        """
        Format response data, default do nothing.
        :param packet:
        :return:
        """
        return data

