# Stetl Examples - Basics

The directories below each show the most basic examples for Stetl.
The examples build up from simple to more complex by directory number prefix.

As a general Stetl-health test you may run all examples using `./runall.sh`.

* 1_copystd - just copy an XML file to standard output
* 2_xslt - transform an input XML file to a GML file
* 3_shape - transform an input XML file to a GML in memory etree and output to a Shape file
* 4_validate - use of the validator filter after generating the GML doc
* 5_split - split the input XML file before transforming to GML and output to multiple GML files
* 6_cmdargs - reuse ETL config file by substituting symbolic variables via command line (-a) arguments or properties file
* 7_mycomponent - adding custom/user-defined Input, Filter and/or Output Components
* 8_wfs - fetch input data from WFS and process it
* 9_string_templating - transform using standard Python string template with CSV input vars
* 10_jinja2_templating - transform using standard Jinja2 http://jinja.pocoo.org Templating
* 11_formatconvert - adapt incompatible inputs to outputs via the FormatConvertFilter
* 12_gdal_ogr - direct OgrInput (and later output)
* 13_dbinput - input from SQL sources, here SLQLite Input
* 14_logfileinput - input from Apache Logfile
* 15_splitter - Splitter Component: split Chain over multiple outputs or sub-Chains
* 16_merger - Merger Component: combines multiple inputs into single input
