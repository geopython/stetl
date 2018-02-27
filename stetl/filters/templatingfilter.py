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

from stetl.util import Util, ogr, osr
from stetl.component import Config
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
    # Applying Decorator pattern with the Config class to provide
    # read-only config values from the configured properties.

    @Config(ptype=str, default=None, required=False)
    def template_file(self):
        """
        Path to template file. One of template_file or template_string needs to be configured.
        """
        pass

    @Config(ptype=str, default=None, required=False)
    def template_string(self):
        """
        Template string. One of template_file or template_string needs to be configured.
        """
        pass

    # End attribute config meta

    # Constructor
    def __init__(self, configdict, section, consumes=FORMAT.any, produces=FORMAT.string):
        Filter.__init__(self, configdict, section, consumes, produces)

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
        '''
        To be overridden in subclasses.
        '''
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
    contains the actual values to be substituted in the template string as a record (key/value pairs).
    Output is a regular string.

    consumes=FORMAT.record or FORMAT.record_array, produces=FORMAT.string
    """

    @Config(ptype=bool, default=False, required=False)
    def safe_substitution(self):
        """
        Apply safe substitution? With this method, string.Template.safe_substitute will be invoked, instead of
        string.Template.substitute. If placeholders are missing from mapping and keywords, instead of raising an
        exception, the original placeholder will appear in the resulting string intact.
        """
        pass

    def __init__(self, configdict, section):
        TemplatingFilter.__init__(self, configdict, section, consumes=[FORMAT.record, FORMAT.record_array])

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
        if self.safe_substitution:
            if type(packet.data) is list:
                packet.data = [self.template.safe_substitute(item) for item in packet.data]
            else:
                packet.data = self.template.safe_substitute(packet.data)
        else:
            if type(packet.data) is list:
                packet.data = [self.template.substitute(item) for item in packet.data]
            else:
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

    # Start attribute config meta
    # Applying Decorator pattern with the Config class to provide
    # read-only config values from the configured properties.

    @Config(ptype=str, default=None, required=False)
    def template_search_paths(self):
        """
        List of directories where to search for templates, default is current working directory only.
        """
        pass

    @Config(ptype=str, default=None, required=False)
    def template_globals_path(self):
        """
        One or more JSON files or URLs with global variables that can be used anywhere in template.
        Multiple files will be merged into one globals dictionary
        """
        pass

    # End attribute config meta

    json_package = None
    ogr_package = ogr
    osr_package = osr

    def __init__(self, configdict, section):
        TemplatingFilter.__init__(self, configdict, section, consumes=[FORMAT.struct, FORMAT.geojson_collection])

    def create_template(self):
        try:
            from jinja2 import Environment, FileSystemLoader
        except Exception as e:
            log.error(
                'Cannot import modules from Jinja2, err= %s; You probably need to install Jinja2 first, see http://jinja.pocoo.org',
                str(e))
            raise e

        import json

        Jinja2TemplatingFilter.json_package = json

        # Check for a file with global variables configured in json format
        # TODO get globals in other formats like XML and possibly from a web service
        template_globals = None
        if self.template_globals_path is not None:
            globals_path_list = self.template_globals_path.strip().split(',')

            for file_path in globals_path_list:

                try:
                    log.info('Read JSON file with globals from: %s', file_path)
                    # Globals can come from local file or remote URL
                    if file_path.startswith('http'):
                        import urllib2

                        fp = urllib2.urlopen(file_path)
                        globals_struct = json.loads(fp.read())
                    else:
                        with open(file_path) as data_file:
                            globals_struct = json.load(data_file)

                    # First file: starts a globals dict, additional globals are merged into that dict
                    if template_globals is None:
                        template_globals = globals_struct
                    else:
                        template_globals.update(globals_struct)

                except Exception, e:
                    log.error('Cannot read JSON file, err= %s', str(e))
                    raise e

        # Load and Init Template once
        loader = FileSystemLoader(self.template_search_paths or [os.getcwd()])
        self.jinja2_env = Environment(loader=loader, extensions=['jinja2.ext.do'], lstrip_blocks=True, trim_blocks=True)

        # Register additional Filters on the template environment by updating the filters dict:
        self.add_env_filters(self.jinja2_env)

        if self.template_file is not None:
            # Get template string from file content and pass optional globals into context
            self.template = self.jinja2_env.get_template(self.template_file, globals=template_globals)
            log.info("template file read and template created OK: %s" % self.template_file)
        elif self.template_string is None:
            # If no file present, template_string should have been configured
            self.template = self.jinja2_env.from_string(self.template_string, globals=template_globals)

    def render_template(self, packet):
        packet.data = self.template.render(packet.data)
        return packet

    def add_env_filters(self, jinja2_env):
        '''Register additional Filters on the template environment by updating the filters dict:
        Somehow min and max of list are not present so add them as well.
        '''
        jinja2_env.filters['maximum'] = max
        jinja2_env.filters['minimum'] = min
        jinja2_env.filters['geojson2gml'] = Jinja2TemplatingFilter.geojson2gml_filter

    @staticmethod
    def import_ogr():
        if Jinja2TemplatingFilter.ogr_package is None:
            log.error(
                'Cannot import Python ogr package; You probably need to install GDAL/OGR Python bindings, see https://pypi.python.org/pypi/GDAL')
            raise ImportError

    @staticmethod
    def create_spatial_ref(crs):
        # "crs": {
        #    "type": "EPSG",
        #    "properties": {
        #        "code": "4326"
        #    }
        spatial_ref = Jinja2TemplatingFilter.osr_package.SpatialReference()
        if type(crs) is dict and crs['type'] == 'EPSG':
            # from the GeoJSON source data, though in future deprecated
            spatial_ref.ImportFromEPSG(int(crs['properties']['code']))
        elif type(crs) is str:
            # Like "EPSG:4326"
            spatial_ref.SetFromUserInput(crs)
        elif type(crs) is int:
            # Like 4326
            spatial_ref.ImportFromEPSG(crs)
        return spatial_ref

    @staticmethod
    def geojson2gml_filter(value, source_crs=4326, target_crs=None, gml_id=None, gml_format='GML2', gml_longsrs='NO'):
        """
        Jinja2 custom Filter: generates any GML geometry from a GeoJSON geometry.
        By specifying a target_crs we can even reproject from the source CRS.
        The gml_format=GML2|GML3 determines the general GML form: e.g. pos/posList
        or coordinates. gml_longsrs=YES|NO determines the srsName format like EPSG:4326 or
        urn:ogc:def:crs:EPSG::4326 (long).
        """
        # Import Python OGR lib once
        Jinja2TemplatingFilter.import_ogr()

        try:
            # Create an OGR geometry from a GeoJSON string
            geojson_str = Jinja2TemplatingFilter.json_package.dumps(value)
            geom = Jinja2TemplatingFilter.ogr_package.CreateGeometryFromJson(geojson_str)

            # Create and assign CRS from source CRS
            source_spatial_ref = Jinja2TemplatingFilter.create_spatial_ref(source_crs)
            geom.AssignSpatialReference(source_spatial_ref)

            # Optional: reproject Geometry from source CRS to target CRS
            if target_crs is not None:
                target_spatial_ref = Jinja2TemplatingFilter.create_spatial_ref(target_crs)
                transform = Jinja2TemplatingFilter.osr_package.CoordinateTransformation(source_spatial_ref,
                                                                                        target_spatial_ref)
                geom.Transform(transform)

            # Generate the GML Geometry elements as string, GMLID is optional
            options = ['FORMAT=%s' % gml_format, 'GML3_LONGSRS=%s' % gml_longsrs]
            if gml_id is not None:
                options.append('GMLID=%s' % gml_id)

            gml_str = geom.ExportToGML(options=options)
        except Exception, e:
            gml_str = 'Failure in CreateGeometryFromJson or ExportToGML, err= %s; check your data and Stetl log' % str(
                e)
            log.error(gml_str)

        return gml_str
