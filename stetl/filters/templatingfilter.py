#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Transformation of any input using Python Templating as
# meant in: https://wiki.python.org/moin/Templating.
# A TemplatingFilter typically is configured with a template file.
# The input is typically the Template context, the variables to be substituted.
# The output is a string passed to the next Filter or Output.
#
# Author:Just van den Broecke

from stetl.util import Util
from stetl.component import Attr
from stetl.filter import Filter
from stetl.packet import FORMAT
from string import Template

log = Util.get_log("templatingfilter")


class TemplatingFilter(Filter):
    """
    Abstract base class for specific template-based filters.
    See https://wiki.python.org/moin/Templating
    Subclasses implement a specific template language like Python string.Template, Mako, Genshi, Jinja2,

    consumes=FORMAT.any, produces=FORMAT.string
    """

    # Constructor
    def __init__(self, configdict, section, consumes=FORMAT.any, produces=FORMAT.string):
        Filter.__init__(self, configdict, section, consumes, produces)

    def invoke(self, packet):
        if packet.data is None:
            return packet
        return self.render(packet)

    def render(self, packet):
        return packet

class StringTemplatingFilter(TemplatingFilter):
    """
    Implements Templating using Python's internal string.Template.
    A template string or file should be configured. The input record
    contains the actual values to be substituted in the template string.
    Output is a regular string.

    consumes=FORMAT.record, produces=FORMAT.string
    """

    # Start attribute config meta
    cfg_template_file = Attr(str, False, None,
    "path to template file (one of template_file or template_string needs to be configured)")

    cfg_template_string = Attr(str, False, None,
    "template as string (one of template_file or template_string needs to be configured)")

    def __init__(self, configdict, section):
        TemplatingFilter.__init__(self, configdict, section, consumes=FORMAT.record)
        self.template_file = self.cfg.get('template_file', StringTemplatingFilter.cfg_template_file.default)
        self.template_string = self.cfg.get('template_string', StringTemplatingFilter.cfg_template_string.default)

    def init(self):
        # Init once
        if self.template_file is not None:
            # Get template string from file content
            log.info('Init: reading template file %s ..." % self.template_file')
            template_fp = open(self.template_file, 'r')
            self.template_string = template_fp.read()
            template_fp.close()
            log.info("template file read OK: %s" % self.template_file)
        elif self.template_string is None:
            # If no file present, template_string should have been configured
            err_s = 'One of template_file or template_string needs to be configured'
            log.error(err_s)
            raise ValueError('One of template_file or template_string needs to be configured')

        # Create a standard Python string.Template
        self.template = Template(self.template_string)

    def exit(self):
        log.info('Exit: templating')

    def render(self, packet):
        packet.data = self.template.substitute(packet.data)
        return packet

