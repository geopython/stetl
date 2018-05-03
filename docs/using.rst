.. _using:

Using Stetl
===========

This section explains how to use Stetl for your ETL. It assumes Stetl is installed and
you are able to run the examples. It may be useful to study some of the examples,
especially the core ones found in the `examples/basics directory <https://github.com/geopython/stetl/tree/master/examples/basics>`_.
These examples start numbering from 1, building up more complex ETL cases like `(INSPIRE) transformation using
Jinja2 Templating <https://github.com/geopython/stetl/tree/master/examples/basics/10_jinja2_templating>`_.

In addition there are example cases like the Dutch
Topo map (Top10NL) ETL in the `examples/top10nl directory <https://github.com/geopython/stetl/tree/master/examples/top10nl>`_ .

The core concepts of Stetl remain pretty simple: an input resource like a file or a database table is
mapped to an output resource (also a file, a database, a remote HTTP server etc) via one or more filters.
The input, filters  and output are connected in a pipeline called a `processing chain` or Chain.
This is a bit similar to a current in electrical engineering: an input flows
through several filters, that each modify the current. In our case the current is (geospatial) data.
Stetl design follows the so-called `Pipes and Filters Architectural Pattern <http://webcem01.cem.itesm.mx:8005/apps/s200911/tc3003/notes_pipes_and_filters/>`_.

Stetl Config
------------

Stetl components (Inputs, Filters, Outputs) and their interconnection (the Pipeline/Chain)
are specified in a Stetl config file. The file format follows the Python ``.ini`` file-format.

To illustrate, let's look at the example `2_xslt <https://github.com/geopython/stetl/tree/master/examples/basics/2_xslt>`_.
This example takes the input file ``input/cities.xml`` and transforms this file to a valid GML file called
``output/gmlcities.gml``. The Stetl config file looks as follows. ::

	[etl]
	chains = input_xml_file|transformer_xslt|output_file

	[input_xml_file]
	class = inputs.fileinput.XmlFileInput
	file_path = input/cities.xml

	[transformer_xslt]
	class = filters.xsltfilter.XsltFilter
	script = cities2gml.xsl

	[output_file]
	class = outputs.fileoutput.FileOutput
	file_path = output/gmlcities.gml

Most of the sections in this ini-file specify a Stetl component: an Input, Filter or Output component.
Each component is specified by its (Python) class and per-component specific parameters.
For example ``[input_xml_file]`` uses the class  :class:`inputs.fileinput.XmlFileInput` reading and parsing the
file ``input/cities.xml`` specified by the ``file_path`` property.  ``[transformer_xslt]`` is a Filter that
applies XSLT with the script file  ``cities2gml.xsl`` that is in the same directory. The ``[output_file]``
component specifies the output, in this case a file.

These components are coupled in a Stetl `Chain` using the special .ini section ``[etl]``. That section specifies one
or more processing chains. Each Chain is specified by the names of the component sections, their interconnection using
a the Unix pipe symbol "|".

So the above Chain is ``input_xml_file|transformer_xslt|output_file``. The names
of the component sections like ``[input_xml_file]`` are arbitrary.

Note: since v1.1.0 a datastream can be split (see below) to multiple ``Outputs`` using ``()`` like : ::

	[etl]
	chains = input_xml_file|transformer_xslt|(output_gml_file)(output_wfs)

Or multiple Input streams can be combined/merged like: ::

	[etl]
	chains = (input_http_api_1) (input_http_api_2) | data_transformer | output_db

It is even possible to have both Splitting and Merging together with filtering: ::

	[etl]
	chains = (input_http_api_1 | cleaner_filter) (input_http_api_2) | data_transformer | (output_db) (output_file)


Configuring Components
----------------------

Most Stetl Components, i.e. inputs, filters, outputs, have properties that can be configured within their
respective [section] in the config file. But what are the possible properties, values and defaults?
This is documented within each Component class using the ``@Config`` decorator much similar to the standard Python
``@property``, only with
some more intelligence for type conversions, defaults, required presence and documentation.
It is loosely based on https://wiki.python.org/moin/PythonDecoratorLibrary#Cached_Properties and Bruce Eckel's
http://www.artima.com/weblogs/viewpost.jsp?thread=240845 with a fix/hack for Sphinx documentation.

See for example the :class:`stetl.inputs.fileinput.FileInput` documentation.

For class authors: this information is added
via the Python Decorators much similar to ``@property``. The :class:`stetl.component.Config`
is used to define read-only properties for each Component instance. For example, ::

	class FileInput(Input):
	    """
	    Abstract base class for specific FileInputs, use derived classes.
	    """

	    # Start attribute config meta
	    # Applying Decorator pattern with the Config class to provide
	    # read-only config values from the configured properties.

	    @Config(ptype=str, default=None, required=False)
	    def file_path(self):
	        """
	        Path to file or files or URLs: can be a dir or files or URLs
	        or even multiple, comma separated. For URLs only JSON is supported now.
	        """
	        pass

	    @Config(ptype=str, default='*.[gxGX][mM][lL]', required=False)
	    def filename_pattern(self):
	        """
	        Filename pattern according to Python ``glob.glob`` for example:
	        '\\*.[gxGX][mM][lL]'
	        """
	        pass

	    @Config(ptype=bool, default=False, required=False)
	    def depth_search(self):
	        """
	        Should we recurse into sub-directories to find files?
	        """
	        pass

	    # End attribute config meta

	    def __init__(self, configdict, section, produces):
	        Input.__init__(self, configdict, section, produces)

	        # Create the list of files to be used as input
	        self.file_list = Util.make_file_list(self.file_path, None, self.filename_pattern, self.depth_search)

This defines three configurable properties for the class FileInput.
Each ``@Config`` has three parameters: ``ptype``, the Python type (``str``, ``list``, ``dict``, ``bool``, ``int``),
``default`` (default value if not present) and ``required`` (if property in mandatory or optional).

Within the config one can set specific
config values like, ::

    [input_xml_file]
    class = inputs.fileinput.XmlFileInput
    file_path = input/cities.xml

This automagically assigns ``file_path`` to ``self.file_path`` without any custom code and assigns the
default value to ``filename_pattern``. Automatic checks are performed: if ``file_path`` (``required=True``) is present, if its type is string.
In some cases type conversions may be applied e.g. when type is ``dict`` or ``list``. It is guarded that the value is not
overwritten and the docstrings will appear in the auto-generated documentation, each entry prepended with a ``CONFIG`` tag.

Running Stetl
-------------

The above ETL spec can be found in the file ``etl.cfg``. Now Stetl can be run, simply by typing ::

	stetl -c etl.cfg

Stetl will parse ``etl.cfg``, create all Components by their class name and link them in a Chain and execute
that Chain. Of course this example is very trivial, as we could just call XSLT without Stetl. But it becomes interesting
with more complex transformations.

Suppose we want to convert the resulting GML to an `ESRI Shapefile`. As we cannot use GDAL ``ogr2ogr`` on the input
file, we need to combine XSLT and `ogr2ogr`. See example
`3_shape <https://github.com/geopython/stetl/tree/master/examples/basics/3_shape>`_. Now we replace the output
by using `outputs.ogroutput.Ogr2OgrOutput`, which can execute any `ogr2ogr` command, converting
whatever it gets as input from the previous Filter in the Chain. ::

	[etl]
	chains = input_xml_file|transformer_xslt|output_ogr_shape

	[input_xml_file]
	class = inputs.fileinput.XmlFileInput
	file_path = input/cities.xml

	[transformer_xslt]
	class = filters.xsltfilter.XsltFilter
	script = cities2gml.xsl

	# The ogr2ogr command-line. May be split over multiple lines for readability.
	# Backslashes not required in that case.
	[output_ogr_shape]
	class = outputs.ogroutput.Ogr2OgrOutput
	temp_file = temp/gmlcities.gml
	ogr2ogr_cmd = ogr2ogr
		-overwrite
		-f "ESRI Shapefile"
		-a_srs epsg:4326
		output/gmlcities.shp
		temp/gmlcities.gml

.. _run_docker:

Using Docker
~~~~~~~~~~~~

The most convenient way to run Stetl is via Docker. See the installation instructions at
:ref:`install_docker`. A full example can be viewed in the Smart Emission project:
https://github.com/Geonovum/smartemission/tree/master/etl.

In the simplest case you run a Stetl Docker container from your own built image or the Dockerhub-provided
one, `geopython/stetl:<version> stetl <https://hub.docker.com/r/geopython/stetl>`_ as follows (`latest` version):  ::

	sudo docker run -v <host dir>:<container dir> -w <work dir> geopython/stetl:latest stetl <any Stetl arguments>

For example within the current directory you may have an ``etl.cfg`` Stetl file: ::

	WORK_DIR=`pwd`
	sudo docker run -v ${WORK_DIR}:${WORK_DIR} -w ${WORK_DIR} geopython/stetl:latest stetl -c etl.cfg

A more advanced setup would be (network-)linking to a PostGIS Docker image
like `kartoza/postgis <https://hub.docker.com/r/kartoza/postgis/>`_: ::

	# First run Postgis, remains running,
	sudo docker run --name postgis -d -t kartoza/postgis:9.4-2.1

	# Then later run Stetl
	STETL_ARGS="-c etl.cfg -a local.args"
	WORK_DIR="`pwd`"

	sudo docker run --name stetl --link postgis:postgis -v ${WORK_DIR}:${WORK_DIR} -w ${WORK_DIR} geopython/stetl:latest stetl ${STETL_ARGS}

The last example is used within the SmartEmission project. Also with more detail and keeping
all dynamic data (like PostGIS DB), your Stetl config and results, and logs within the host.
For PostGIS see: https://github.com/Geonovum/smartemission/tree/master/services/postgis
and Stetl see: https://github.com/Geonovum/smartemission/tree/master/etl.

Even better is to use `docker-compose`.

Stetl Integration
-----------------

Note: one can also run Stetl via its main ETL class: :class:`stetl.etl.ETL`.
This may be useful for integrations in for example Python programs
or even OGC WPS servers (planned).

Reusable Stetl Configs
----------------------
What we saw in the last example is that it is hard to reuse this `etl.cfg`
when we have for example a different input file
or want to map to different output files.
For this Stetl supports `config parameter substitution`.

Dynamic or secret (e.g. database credentials) parameters in `etl.cfg` are declared
symbolically and substituted at runtime via the commandline or the OS environment.

A variable is declared between curly brackets like `{out_xml}`. See
example `6_cmdargs <https://github.com/geopython/stetl/tree/master/examples/basics/6_cmdargs>`_. ::

	[etl]
	chains = input_xml_file|transformer_xslt|output_file

	[input_xml_file]
	class = inputs.fileinput.XmlFileInput
	file_path = {in_xml}

	[transformer_xslt]
	class = filters.xsltfilter.XsltFilter
	script = {in_xsl}

	[output_file]
	class = outputs.fileoutput.FileOutput
	file_path = {out_xml}

Note the symbolic input, xsl and output files. We can now perform
the ETL using the `stetl -a option` in two basic ways.
One, passing the arguments on the commandline, like ::

	stetl -c etl.cfg -a "in_xml=input/cities.xml in_xsl=cities2gml.xsl out_xml=output/gmlcities.gml"

Two, passing the arguments in a properties file, here called `etl.args` (the name of the suffix .args is not significant, could be .env as well). ::

	stetl -c etl.cfg -a etl.args

Where the content of the `etl.args` properties file is: ::

	# Arguments in properties file
	in_xml=input/cities.xml
	in_xsl=cities2gml.xsl
	out_xml=output/gmlcities.gml

It is also possible to specify **multiple -a arguments**. This provides for situations
where a `default.args` contains all default arguments and a `my.args` or explicit `-a` settings
that override the default values in `default.args`. Overriding is determined by the order of
the `-a` arguments. Examples: ::

	stetl -c etl.cfg -a default.args -a my.args
	stetl -c etl.cfg -a default.args -a "db_user=docker db_password=pass"
	stetl -c etl.cfg -a default.args -a db_user=docker -a db_password=pass

It is also possible to pass these key/value pairs via OS Environment variables.
This is especially handy in Docker-based deployments like Docker Compose and Kubernetes.
In this case the variable names need to be prepended with `STETL_` or `stetl_` as
to not mix-up with other non-related OS-env vars. A mixture of commandline args (file)
and environment vars is possible. The rule is that
*OS Environment variables always override/overrule arguments specified with -a option(s)*.

For example, the above args could also be passed as follows: ::

	export stetl_in_xml="input/cities.xml"
	export stetl_in_xsl="cities2gml.xsl"
	export stetl_out_xml="output/gmlcities.gml"
	stetl -c etl.cfg

or only override the input file name `in_xml` from `etl.args`: ::

	export stetl_in_xml="input/cities2.xml"
	stetl -c etl.cfg -a etl.args

or even with multiple `-a args`: ::

	export stetl_in_xml="input/cities2.xml"
	stetl -c etl.cfg -a etl.args -a my.args

This makes an ETL chain highly reusable.
A very elaborate Stetl config with parameter substitution can be seen in the
`Top10NL ETL <https://github.com/geopython/stetl/blob/master/examples/top10nl/etl-top10nl.cfg>`_.

Connection Compatibility
------------------------

During ETL Chain processing Components typically pass data to a next :class:`stetl.component.Component` .
A :class:`stetl.filter.Filter`  Component both consumes and produces data, Inputs produce data and
Outputs only consume data.

Data and status flows as :class:`stetl.packet.Packet` objects between the Components. The type of the data in these Packets needs
to be compatible only between two coupled Components.
Stetl does not define one unifying data structure, but leaves this to the Components themselves.

Each Component provides the type of data it `consumes` (Filters, Outputs) and/or `produces` (Inputs, Filters).
This is indicated in its class definition using the `consumes` and `produces` object constructor parameters.
Some Components can produce and/or consume multiple data types, like a single stream of `records` or a `record array`.
In those cases the `produces` or `consumes` parameter can be a list (array) of data types.

During `Chain` construction Stetl will check for compatible formats when connecting `Components`.
If one of the formats is a list of formats, the actual format is determined by:

#. explicit setting: the actual `input_format` and/or `output_format` is set in the Component .ini configuration
#. no setting provided: the first format in the list is taken as default

Stetl will only check if these input and output-formats for connecting Components are compatible
when constructing a Chain.

The following data types are currently symbolically defined in the :class:`stetl.packet.FORMAT` class:

- ``any`` - 'catch-all' type, may be any of the types below.

- ``etree_doc`` - a complete in-memory XML DOM structure using the ``lxml`` etree

- ``etree_element`` - each Packet contains a single DOM Element (usually a Feature) in ``lxml`` etree format

- ``etree_feature_array`` - each Packet contains an array of DOM Elements (usually Features) in ``lxml`` etree format

- ``geojson_feature`` - as ``struct`` but following naming conventions for a single Feature according to the GeoJSON spec: http://geojson.org

- ``geojson_collection`` - as ``struct`` but following naming conventions for a FeatureCollection according to the GeoJSON spec: http://geojson.org

- ``ogr_feature`` - a single Feature object from an OGR source (via Python SWIG wrapper)

- ``ogr_feature_array`` - a Python list (array) of a single Feature objects from an OGR source

- ``record`` - a Python ``dict`` (hashmap)

- ``record_array`` - a Python list (array) of ``dict``

- ``string``- a general string

- ``struct`` - a JSON-like generic tree structure

- ``xml_doc_as_string`` - a string representation of a complete XML document

- ``xml_line_stream`` - each Packet contains a line (string) from an XML file or string representation (DEPRECATED)


Many components, in particular Filters, are able to transform data formats.
For example the `XmlElementStreamerFileInput` can produce an
`etree_element`, a subsequent `XmlAssembler` can create small in-memory `etree_doc` s that
can be fed into an `XsltFilter`, which outputs a transformed `etree_doc`. The type `any` is a catch-all,
for example used for printing any object to standard output in the :class:`stetl.packet.Component`.
An `etree_element` may also be interesting to be able to process single features.

Starting with Stetl 1.0.7 a new :class:`stetl.filters.formatconverter.FormatConverterFilter` class provides a Stetl Filter
to allow almost any conversion between otherwise incompatible Components.

TODO: the Packet typing system is still under constant review and extension. Soon it will be possible
to add new data types and converters. We have deliberately chosen not to define a single internal datatype
like a "Feature", both for flexibility and performance reasons.

Multiple Chains
---------------

Usually a complete ETL will require multiple steps/commands. For example we need to create
a database, maybe tables and/or making tables empty. Also we may need to do postprocessing, like
removing duplicates in a table etc. In order to have repeatable/reusable ETL without any
manual steps, we can specify multiple Chains within a single Stetl config.
The syntax: chains are separated by commas (steps are sill separated by pipe symbols). 

Chains are executed in order. We can even reuse the
specified components from within the same file. Each will have a separate instance within a Chain.

For example in the `Top10NL example <https://github.com/geopython/stetl/blob/master/examples/top10nl/etl-top10nl.cfg>`_
we see three Chains::

		[etl]
		chains = input_sql_pre|schema_name_filter|output_postgres,
				input_big_gml_files|xml_assembler|transformer_xslt|output_ogr2ogr,
				input_sql_post|schema_name_filter|output_postgres

Here the Chain `input_sql_pre|schema_name_filter|output_postgres` sets up a PostgreSQL schema and
creates tables.  `input_big_gml_files|xml_assembler|transformer_xslt|output_ogr2ogr` does the actual ETL and
`input_sql_post|schema_name_filter|output_postgres` does some PostgreSQL postprocessing.

Chain Splitting
---------------

In some cases we may want to split processed data to multiple ``Filters`` or ``Outputs``.
For example to produce output files in multiple formats like GML, GeoJSON etc
or to publish converted (Filtered) data to multiple remote services (SOS, SensorThings API)
or just for simple debugging to a target ``Output`` and ``StandardOutput``.

See issue https://github.com/geopython/stetl/issues/35 and
the `Chain Split example <https://github.com/geopython/stetl/tree/master/examples/basics/15_splitter>`_.

Here the Chains are split by using ``()`` in the ETL Chain definition: ::

	# Transform input xml to valid GML file using an XSLT filter and pass to multiple outputs.
	# Below are two Chains: simple Output splitting and splitting to 3 sub-Chains at Filter level.

	[etl]
	chains = input_xml_file | transformer_xslt |(output_file)(output_std),
	         input_xml_file | (transformer_xslt|output_file) (output_std) (transformer_xslt|output_std)


	[input_xml_file]
	class = inputs.fileinput.XmlFileInput
	file_path = input/cities.xml

	[transformer_xslt]
	class = filters.xsltfilter.XsltFilter
	script = cities2gml.xsl

	[output_file]
	class = outputs.fileoutput.FileOutput
	file_path = output/gmlcities.gml

	[output_std]
	class = outputs.standardoutput.StandardOutput

Chain Merging
-------------

In some cases we may want to merge (combine, join) multiple input streams.

For example to harvest data from multiple HTTP REST APIs, or to realize a `Filter` that
integrates data from two data-sources.

See issue https://github.com/geopython/stetl/issues/59 and
the `Chain Merge example <https://github.com/geopython/stetl/tree/master/examples/basics/16_merger>`_.

Here the Chains are merged by using ``()`` notation in the ETL Chain definition, possibly even combined with Splitting
Outputs: ::

	# Merge two inputs into single Filter.

	[etl]
	chains = (input_1) (input_2)|transformer_xslt|output_std,
			 (input_1) (input_2)|transformer_xslt|(output_file)(output_std)


	[input_1]
	class = inputs.fileinput.XmlFileInput
	file_path = input1/cities.xml

	[input_2]
	class = inputs.fileinput.XmlFileInput
	file_path = input2/cities.xml

	[transformer_xslt]
	class = filters.xsltfilter.XsltFilter
	script = cities2gml.xsl

	[output_file]
	class = outputs.fileoutput.FileOutput
	file_path = output/gmlcities.gml

	[output_std]
	class = outputs.standardoutput.StandardOutput
