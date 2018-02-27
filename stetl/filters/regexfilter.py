#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Extracts data from a string using a regular expression and generates a record.
#
# Author: Frank Steggink

from stetl.component import Config
from stetl.filter import Filter
from stetl.packet import FORMAT
from stetl.util import Util
import re

log = Util.get_log("regexfilter")


class RegexFilter(Filter):
    """
    Extracts data from a string using a regular expression and returns the named groups as a record.
    consumes=FORMAT.string, produces=FORMAT.record
    """

    # Start attribute config meta
    # Applying Decorator pattern with the Config class to provide
    # read-only config values from the configured properties.

    @Config(ptype=str, default=None, required=True)
    def pattern_string(self):
        """
        Regex pattern string. Should contain named groups.
        """
        pass

    # End attribute config meta

    # Constructor
    def __init__(self, configdict, section, consumes=FORMAT.string, produces=FORMAT.record):
        Filter.__init__(self, configdict, section, consumes, produces)

        self.regex_object = re.compile(self.pattern_string, re.S)

    def init(self):
        log.info('Init: regex filter')
        if self.pattern_string is None:
            # If no pattern_string is present:
            err_s = 'The pattern_string needs to be configured'
            log.error(err_s)
            raise ValueError('The pattern_string needs to be configured')

    def exit(self):
        log.info('Exit: regex filter')

    def invoke(self, packet):
        if packet.data is None:
            return packet

        m = self.regex_object.match(packet.data)
        if m is not None:
            packet.data = m.groupdict()
        else:
            packet.data = {}

        return packet
