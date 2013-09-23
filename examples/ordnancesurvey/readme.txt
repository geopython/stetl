This example is a proof of concept to load UK Ordnance Survey Mastermap GML into PostGIS using
Astun Technology Loader config and GML manipulation unaltered.  A small sample of UK Mastermap data has been extracted from
a sample download provided by Ordnance Survey. The full file has also been
sucessfully loaded and is called: 58116-SX9192-2c1.gml.

Files:

- input/osmm-topo-small.gml the input file
- stetl config: stetl.cfg
- Stetl Filter: python/osmmfilter.py, calling the unaltered prep_osmgml.py from Astun Tech
- command (Linux/Mac): etl.sh
- output: to PostGIS and into the file output/osmm_topo_prepared.gml
- gfs/ determines the mapping to PostGIS of the prepared data
- postgres/*.sql - scripts to setup/init the PG DB (called by Stetl)

How this works:
On calling etl.sh Stetl will read the config file stetl.cfg,
substituting any commandline parameters (-a option) passed to it.
Stetl will then assemble and execute the specified Chains under the
[etl] section:

The Chain "input_sql_pre|schema_name_filter|output_postgres" will initialize the DB and setup
all required tables/indexes from the files under postgres/*.sql.

The Chain "input_big_gml_files|osmm_filter|xml_assembler|output_file" will read the input file(s) from
the directory input/, stream the feature elements to its output. The "osmm_filter" will
receive each feature element, calling the configured "preparer" in prep_osmgml.py. Finally
the "output_file" component will write the result to the file under output/.

The Chain "input_big_gml_files|osmm_filter|xml_assembler|output_ogr2ogr" does the samen, only it will
write the results to PostGIS using the gfs/ mapping file. NB: in Stetl 1.0.4 still with a temp file
but we will change this.

Links:
- Astuntech Loader - https://github.com/AstunTechnology/Loader
- Ordnance Survey UK - http://www.ordnancesurvey.co.uk/