# -*- coding: utf-8 -*-
#
# Input classes for fetching data via HTTP.
#
# Author: Just van den Broecke
#
import re
from urllib2 import Request, urlopen, URLError, HTTPError
import urllib

from stetl.component import Config
from stetl.input import Input
from stetl.util import Util
from stetl.packet import FORMAT

log = Util.get_log('httpinput')


class HttpInput(Input):
    """
    Fetch data from remote services like WFS via HTTP protocol.
    Base class: subclasses will do datatype-specific formatting of
    the returned data.

    produces=FORMAT.any
    """

    # Start attribute config meta
    # Applying Decorator pattern with the Config class to provide
    # read-only config values from the configured properties.

    @Config(ptype=str, default=None, required=True)
    def url(self):
        """
        The HTTP URL string.

        Required: True

        Default: None
        """
        pass


    @Config(ptype=dict, default=None, required=False)
    def parameters(self):
        """
        Flat JSON-like struct of the parameters to be appended to the url.

        Example: (parameters require quotes)::

            url = http://geodata.nationaalgeoregister.nl/natura2000/wfs
            parameters = {
                service : WFS,
                version : 1.1.0,
                request : GetFeature,
                srsName : EPSG:28992,
                outputFormat : text/xml; subtype=gml/2.1.2,
                typename : natura2000
            }

        Required: False

        Default: None
        """
        pass

    # End attribute config meta

    def __init__(self, configdict, section, produces=FORMAT.any):
        Input.__init__(self, configdict, section, produces)

        log.info("url=%s parameters=%s" % (self.url, self.parameters))

    def read_from_url(self, url, parameters=None):
        """
        Read the data from the URL.
        :param url: the url to fetch
        :param parameters: optional dict of query parameters
        :return:
        """
        # log.info('Fetch data from URL: %s ...' % url)

        req = Request(url)
        try:
            # Urlencode optional parameters
            query_string = None
            if parameters:
                query_string = urllib.urlencode(parameters)

            response = urlopen(req, query_string)
        except HTTPError as e:
            log.error('HTTPError fetching from URL %s: code=%d e=%s' % (url, e.code, e))
            raise e
        except URLError as e:
            log.error('URLError fetching from URL %s: reason=%s e=%s' % (url, e.reason, e))
            raise e

            # everything is fine
        return response.read()

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

        packet.data = self.format_data(self.read_from_url(self.url, self.parameters))
        self.url = None
        return packet

    def format_data(self, data):
        """
        Format response data, override in subclasses, defaults to returning original data.
        :param packet:
        :return:
        """
        return data


class ApacheDirInput(HttpInput):
    """
     Read file data from an Apache directory "index" HTML page.
     Uses http://stackoverflow.com/questions/686147/url-tree-walker-in-python
     produces=FORMAT.record. Each record contains file_name and file_data (other meta data like
     date time is too fragile over different Apache servers).
    """

    def __init__(self, configdict, section, produces=FORMAT.record):
        HttpInput.__init__(self, configdict, section, produces)
        # look for a link + a timestamp + a size ('-' for dir)
        # self.parse_re = re.compile('href="([^"]*)".*(..-...-.... ..:..).*?(\d+[^\s<]*|-)')
        # This appeared to be too fragile, e.g. different date formats per apache server

        # default file extension to filter
        self.file_ext = self.cfg.get('file_ext', 'xml')
        # default regular expresion for file
        self.file_reg_exp = self.cfg.get('file_reg_exp', 'href="([^"]*%s)"' % self.file_ext)
        self.parse_re = re.compile(self.file_reg_exp)
        self.file_list = None
        self.file_index = None

        if not self.url.endswith('/'):
            self.url += '/'

    def init(self):
        """
        Read the list of files from the Apache index URL.
        """
        # One time: get all files from remote Apache dir
        log.info('Init: fetching file list from URL: %s ...' % self.url)
        html = self.read_from_url(self.url)
        self.file_list = self.parse_re.findall(html)
        log.info('Found %4d file' % len(self.file_list) + 's' * (len(self.file_list) != 1))

    def next_file(self):
        """
        Return a tuple (name, date, size) with next file info.
        :return tuple:
        """

        if self.file_index is None:
            self.file_index = -1

        # At last file tuple ?
        if self.no_more_files():
            return None

        self.file_index += 1

        return self.file_list[self.file_index]

    def no_more_files(self):
        """
        More files left?.
        :return Boolean:
        """
        return self.file_index == len(self.file_list) - 1

    def read(self, packet):
        """
        Read the data from the URL.
        :param packet:
        :return:
        """
        file_name = self.next_file()

        file_name = self.filter_file(file_name)

        # All files done?
        if file_name is None and self.no_more_files() is True:
            packet.set_end_of_stream()
            log.info("EOF Apache dir files done, file_index=%d" % self.file_index)
            return packet

        if file_name is None:
            return packet

        # Process next file
        url = self.url + file_name
        log.info("Reading file_index=%d, file_name=%s " % (self.file_index, file_name))

        # Create record from file_name and file content
        packet.data = dict(file_name=file_name, file_data=self.read_from_url(url))

        return packet

    def filter_file(self, file_name):
        """
        Filter the file_name, e.g. to suppress reading, default: return file_name.
        :param file_name:
        :return string or None:
        """
        return file_name

