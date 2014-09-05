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
import os

log = Util.get_log("templatingfilter")


class TemplatingFilter(Filter):
    """
    Abstract base class for specific template-based filters.
    See https://wiki.python.org/moin/Templating
    Subclasses implement a specific template language like Python string.Template, Mako, Genshi, Jinja2,

    consumes=FORMAT.any, produces=FORMAT.string
    """

    # Start attribute config meta
    cfg_template_file = Attr(str, False, None,
    "path to template file (one of template_file or template_string needs to be configured)")

    cfg_template_string = Attr(str, False, None,
    "template as string (one of template_file or template_string needs to be configured)")

    # Constructor
    def __init__(self, configdict, section, consumes=FORMAT.any, produces=FORMAT.string):
        Filter.__init__(self, configdict, section, consumes, produces)
        self.template_file = self.cfg.get('template_file', StringTemplatingFilter.cfg_template_file.default)
        self.template_string = self.cfg.get('template_string', StringTemplatingFilter.cfg_template_string.default)

    def init(self):
        log.info('Init: templating')
        if self.template_file is None and self.template_string is None:
            # If no file present nor template_string error:
            err_s = 'One of template_file or template_string needs to be configured'
            log.error(err_s)
            raise ValueError('One of template_file or template_string needs to be configured')

        self.create_template()

    def exit(self):
        log.info('Exit: templating')
        self.destroy_template()

    def create_template(self):
        pass

    def destroy_template(self):
        pass

    def invoke(self, packet):
        if packet.data is None:
            return packet
        return self.render_template(packet)

    def render_template(self, packet):
        pass

class StringTemplatingFilter(TemplatingFilter):
    """
    Implements Templating using Python's internal string.Template.
    A template string or file should be configured. The input record
    contains the actual values to be substituted in the template string.
    Output is a regular string.

    consumes=FORMAT.record, produces=FORMAT.string
    """

    def __init__(self, configdict, section):
        TemplatingFilter.__init__(self, configdict, section, consumes=FORMAT.record)

    def create_template(self):
        # Init once
        if self.template_file is not None:
            # Get template string from file content, otherwise assume template_string is populated
            log.info('Init: reading template file %s ..." % self.template_file')
            template_fp = open(self.template_file, 'r')
            self.template_string = template_fp.read()
            template_fp.close()
            log.info("template file read OK: %s" % self.template_file)

        # Create a standard Python string.Template
        self.template = Template(self.template_string)

    def render_template(self, packet):
        packet.data = self.template.substitute(packet.data)
        return packet

class Jinja2TemplatingFilter(TemplatingFilter):
    """
    Implements Templating using Jinja2. Jinja2 http://jinja.pocoo.org,
    is a modern and designer-friendly templating language for Python
    modelled after Django’s templates. A 'struct' format as input provides
    a tree-like structure that could originate from a JSON file or REST service.
    This input struct provides all the variables to be inserted into the template.
    The template itself can be configured in this component as a Jinja2 string or -file.
    An optional 'template_search_paths' provides a list of directories from which templates
    can be fethced. Default is the current working directory. Via the optional 'globals_path'
    a JSON structure can be inserted into the Template environment. The variables in this
    globals struture are typically "boilerplate" constants like: id-prefixes, point of contacts etc.

    consumes=FORMAT.struct, produces=FORMAT.string
    """

    cfg_template_search_paths = Attr(str, False, [os.getcwd()],
    "list of directories where to search for templates, default is current working directory only")

    cfg_template_globals_path = Attr(str, False, None,
    "JSON file with global variables that can be used anywhere in template")

    def __init__(self, configdict, section):
        TemplatingFilter.__init__(self, configdict, section, consumes=FORMAT.struct)
        self.template_search_paths = self.cfg.get_list('template_search_paths', default=Jinja2TemplatingFilter.cfg_template_search_paths.default)
        self.template_globals_path = self.cfg.get('template_globals_path', default=Jinja2TemplatingFilter.cfg_template_globals_path.default)
        self.template_globals = None

    def create_template(self):
        try:
            from jinja2 import Environment, FileSystemLoader
        except Exception, e:
            log.error('Cannot import modules from Jinja2, err= %s; You probably need to install Jinja2 first, see http://jinja.pocoo.org', str(e))
            raise e

        # Check for a file with global variables configured in json format
        # TODO get globals in other formats like XML and possibly from a web service
        if self.template_globals_path is not None:
            try:
                log.info('Read JSON file: %s', self.template_globals_path)
                import json

                with open(self.template_globals_path) as template_globals_fp:
                    self.template_globals = json.load(template_globals_fp)
            except Exception, e:
                log.error('Cannot read JSON file, err= %s', str(e))
                raise e

        # Load and Init Template once
        loader = FileSystemLoader(self.template_search_paths)
        self.jinja2_env = Environment(loader=loader, extensions=['jinja2.ext.do'], lstrip_blocks=True, trim_blocks=True)

        # Register additional Filters on the template environment by updating the filters dict:
        # Somehow min and max of list are not present
        self.jinja2_env.filters['maximum'] = max
        self.jinja2_env.filters['minimum'] = min

        if self.template_file is not None:
            # Get template string from file content and pass optional globals into context
            self.template = self.jinja2_env.get_template(self.template_file, globals=self.template_globals)
            log.info("template file read and template created OK: %s" % self.template_file)
        elif self.template_string is None:
            # If no file present, template_string should have been configured
            self.template = self.jinja2_env.from_string(self.template_string, globals=self.template_globals)

    def render_template(self, packet):
        packet.data = self.template.render(packet.data)
        return packet

