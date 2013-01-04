This example shows how to convert the Dutch national topo dataset Top10NL (v1.1.1) GML into
PostGIS.

The entire ETL is driven through the file etl-top10nl.cfg
The script etl-top10nl.sh is a shortcut to call main.py.

This example also uses the "custom parameters" feature.

A config file will in many cases have parameters that are varying
often: database parameters, input file names etc. To prevent making
a new config file for each variant and to allow higher level programs
to have their own parameterization convention, a simple string substitution
mechanism is used:

parameters within the .cfg file that are provided externally can be specified
with Python-based formatting values, e.g. {host}, {port}. Using main.py -a option
these values are substituted, for example:

    main.py -c myetl.cfg -a "host=localhost port=5432"

There are 3 chains:
- SQL pre-processing: dropping tables, optionally creating a (non-public) PG schema
- the actual ETL-chain, using GML streaming, assembling, XSLT and finally ogr2ogr
- SQL post-processing : removing duplicates

See also etl-top10nl.cfg and etl-top10nl.sh for more details.

(top10-nlextract.sh is here for testing/comparing with the existing ETL via
nlextract.nl).

To test: a PostGIS database named top10nl with same user/pw needs to exist.
