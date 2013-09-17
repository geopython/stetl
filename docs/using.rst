.. _using:

Using Stetl
===========

This section explains how to use Stetl for your ETL. It assumes Stetl is installed and
you are able to run the examples. It may be useful to study some of the examples,
especially the core ones found in the `examples/basics directory <https://github.com/justb4/stetl/tree/master/examples/basics>`_.
These examples start numbering from 1, building up more complex ETL cases like the Dutch
Topo map (Top10NL) ETL in the `examples/top10nl directory <https://github.com/justb4/stetl/tree/master/examples/top10nl>`_ .

The core concepts of Stetl though are pretty simple: an input resource (file, database etc) is
mapped to an output resource (file database, etc) via a set of Python components
that are connected as a `processing chain`. A bit like in electrical engineering: an input flows
through several filters, that each modify the current. In our case the current is geospatial information.

Stetl Config
------------
The particular components (inputs, filters, outputs) and their interconnection
are specified in a Stetl config file. The file format follows the Python `.ini file-format`.
To illustrate let's look at the example `2_xslt <https://github.com/justb4/stetl/tree/master/examples/basics/2_xslt>`_.
This example takes an input .xml file and transforms this file to a valid GML file. The Stetl config file looks as follows. ::

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
For example `[input_xml_file]` uses the class  `inputs.fileinput.XmlFileInput` reading and parsing the
file `input/cities.xml` specified by the `file_path` property.  `[transformer_xslt]` is a Filter that
applies XSLT with the script file  `cities2gml.xsl` that is in the same directory. The `[output_file]`
component specifies the output, in this case a file.

These components are coupled in a Stetl `Chain` using the special .ini section `[etl]`. That section specifies one
or more chains. Each Chain is specified by the names of the component sections, their interconnection using
a '|', the Unix pipe symbol. So the above chain is `input_xml_file|transformer_xslt|output_file`. The names
of the component sections are arbitrary.

Running Stetl
-------------

The above ETL spec can be found in the file `etl.cfg`. Now Stetl can be run, simply by typing ::

	stetl -c etl.cfg

Stetl will parse `etl.cfg`, create all Components by their class name and link them in a Chain and execute
that Chain. Offcourse this example is very trivial, as we could just call XSLT without Stetl. But it becomes interesting
with more complex transformations.

Suppose we want to convert the resulting GML to an ESRI Shapefile. As we cannot use GDAL `ogr2ogr` on the input
file, we need to combine XSLT and `ogr2ogr`. See example
`3_shape <https://github.com/justb4/stetl/tree/master/examples/basics/3_shape>`_. Now we replace the output
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

Stetl Integration
-----------------

Note: one can also run Stetl via its main ETL class: :class:`stetl.etl.ETL`.
This may be useful for integrations in for example Python programs
or even OGC WPS servers.

Reusable Stetl Configs
----------------------
What we saw in the last example is that it is hard to reuse this `etl.cfg` when we have for example a different input file
or want to map to different output files. For this Stetl supports `parameter substitution`. See
example `6_cmdargs <https://github.com/justb4/stetl/tree/master/examples/basics/6_cmdargs>`_. ::

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

Note the symbolic input, xsl and output files. We can now perform this ETL using the `stetl -a option`. ::

	stetl -c etl.cfg -a "in_xml=input/cities.xml in_xsl=cities2gml.xsl out_xml=output/gmlcities.gml".

This makes an ETL chain highly reusable. A very elaborate Stetl config with parameter substitution can be seen in the
`Top10NL ETL <https://github.com/justb4/stetl/blob/master/examples/top10nl/etl-top10nl.cfg>`_.

Connection Compatibility
------------------------

Components typically pass data to a next :class:`stetl.component.Component` .
A :class:`stetl.filter.Filter`  Component both consumes and produces data, Inputs produce data and
Outputs consume data.

Data and status flows as :class:`stetl.packet.Packet` objects between the Components. The type of the data in these Packets needs
to be compatible only between two coupled Components.
Stetl does not define one single data structure, but leaves this to the Components themselves.
For XML-based data the `etree_doc`, a complete DOM-document, is used by many components, but also ordinary strings.
Each Component will indicate the type of data it `consumes` and/or `produces`.
Stetl will only check if these input and output-types for connecting Components are compatible
when constructing a Chain.

The following data types are currently symbolically defined in the :class:`stetl.packet.Packet` file: ::

	'xml_line_stream', 'etree_doc', 'etree_element_stream', 'etree_feature_array', 'xml_doc_as_string', 'string', 'any'

Many components, in particular Filters are able to transform one data type to another type.
For example the `XmlElementStreamerFileInput` can produce an
`etree_element_stream`, a subsequent `XmlAssembler` can create small in-memory `etree_doc` s that
can be fed into an `XsltFilter`, which outputs a transformed `etree_doc`. The type `any` is a catch-all,
for example used for printing any object to standard output in the :class:`stetl.packet.Component`.
An `etree_element_stream` may also be interesting to be able to process single features.

Multiple Chains
---------------

Usually a complete ETL will require multiple steps/commands. For example we need to create
a database, maybe tables and/or making tables empty. Also we may need to do postprocessing, like
removing duplicates in a table etc. In order to have repeatable/reusable ETL without any
manual steps, we can specify multiple Chains within a single Stetl config.
The syntax is via comma-separation. Chains are executed in order. We can even reuse the
specified components from within the same file. Each will have a separate instance within a Chain.

For example in the `Top10NL example <https://github.com/justb4/stetl/blob/master/examples/top10nl/etl-top10nl.cfg>`_  we see three Chains: ::

		[etl]
		chains = input_sql_pre|schema_name_filter|output_postgres,
				input_big_gml_files|xml_assembler|transformer_xslt|output_ogr2ogr,
				input_sql_post|schema_name_filter|output_postgres

Here the Chain `input_sql_pre|schema_name_filter|output_postgres` sets up a PostgreSQL schema and
creates tables.  `input_big_gml_files|xml_assembler|transformer_xslt|output_ogr2ogr` does the actual ETL and
`input_sql_post|schema_name_filter|output_postgres` does some PostgreSQL postprocessing.

















