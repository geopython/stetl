This example, or better a series of examples, shows an unconventional but exciting new
way for transforming source data into complex/rich XML/GML. Possibly "transforming"
is not the proper term but "substitution".

Enter the Jinja...Within many web-frameworks, the use of "templating" is common.
think of JSP (Java), ASP (.NET), PHP even in JavaScript (e.g. Mustache).
Within Python there are a zillion templating languages to choose from. From plain
built-in $string substitution up to fullfledged programming. Django Templating, Gensha, Mako.
See https://wiki.python.org/moin/Templating

Within Stetl we choose to support two languages for now, both derived from a single
TemplatingFilter class: String templating (see example 9) and Jinja2 templating.

This example shows several Jinja2 templating examples from basic to very advanced.
All are bundled within the single etl.cfg file as Stetl allows multiple ETL chains
defined in a single config file.

For all examples, the dirs are as follows:

- input/: all input files
- output/: all generated output files
- templates/: the Jinja2 templates and macros

EXAMPLE 1 - simple Jinja2 templating: JSON to XML
input/cities.json is converted to output/cities.xml using the template templates/cities-json2xml.jinja2

EXAMPLE 2 - more advanced Jinja2 templating : JSON to GML (
input/cities.json is converted to output/cities.gml (GML FeatureCollection) using the
template templates/cities-json2gml.jinja2
Shows the use of Jinja2 Globals (input/globals.json), global/static values that are
always available in the template and the use of Jinja2 Macros (template/macros.jinja2) for recurring
tasks.

EXAMPLE 3 - advanced Jinja2 templating - GeoJSON to GML - and reading from URL
input/cities-gjson.json is converted to output/cities-gjson.gml (GML FeatureCollection) using the
template templates/cities-gjson2gml.jinja2. Shows the use of advanced Jinja2 Filters within Stetl that
can transform GeoJSON Geometries to GML Geometries. Also shows that input and/or globals can be fetched from
a remote URL.

EXAMPLE 4 - data harmonization for INSPIRE: transform local Dutch address data to INSPIRE Annex I Addresses (AD)
input/addresses.csv is converted to output/inspire-addresses.gml (GML Spatial dataset) using the
template templates/addresses2inspire-ad.jinja2. Shows that data transformation for INSPIRE doesn't need to be
hard. Usually the source data is in tabular form, here a CSV file. The required data format
for INSPIRE is often "bloated" with boilerplate encodings. Here templating makes lots of sense.




