.. _cases:

Cases
=====

This chapter lists various cases/projects where Stetl is used.

NLExtract
---------

NLExtract https://nlextract.nl is a development project that aims to provide ETL-tooling for all
Dutch Open Geo-Datasets, in particular the country wide
"Key Registries" (Dutch: Basisregistraties) like Cadastral Parcels (BRK), Topography (BRT+BGT) and
Buildings and Addresses (BAG). These datasets are provided as XML/GML. The ETL mostly provides
a transformation to PostGIS. For all Key Registries, except for the BAG, Stetl is used, basically
as-is, without extra (Python) programming.  See also the NLExtract GitHub:
https://github.com/nlextract/NLExtract

Adresses and Buildings (BAG v2)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

BAG version 1 ETL was developed as a custom Python program.
In 2021 Dutch Kadaster released BAG version 2.
For NLExtract a moment to switch ETL for BAG to Stetl.
In particular use is made of the recent (v3.2.1+) GDAL/OGR LVBAG Driver and Python bindings for GDAL
VSI `/vsizip` file handling.

See https://github.com/nlextract/NLExtract/tree/master/bagv2/etl and the Stetl conf at
https://github.com/nlextract/NLExtract/tree/master/bagv2/etl/conf/

Topography (BRT)
~~~~~~~~~~~~~~~~

Includes ETL for 5 scale levels: TOP10NL through TOP1000NL.

See https://github.com/nlextract/NLExtract/tree/master/brt/top10nl/etl and the Stetl conf at e.g.
https://github.com/nlextract/NLExtract/tree/master/brt/top10nl/etl/conf/

Detailed Topography (BGT)
~~~~~~~~~~~~~~~~~~~~~~~~~

This is a very large and heavy dataset based on CityGML. Stetl streaming ETL is
here at its best.

See https://github.com/nlextract/NLExtract/tree/master/bgt and the Stetl conf at
https://github.com/nlextract/NLExtract/blob/master/bgt/etl/conf/

Cadastral Parcels (BRK)
~~~~~~~~~~~~~~~~~~~~~~~

See https://github.com/nlextract/NLExtract/tree/master/brk/etl
and the Stetl conf at https://github.com/nlextract/NLExtract/tree/master/brk/etl/conf

INSPIRE
-------

These were the origins of Stetl. This project was sponsored by Kadaster.
See https://github.com/justb4/inspire-foss. The ETL involved the transformation of Dutch Key Registries (see above)
to harmonized INSPIRE GML according to the Annexes.

Addresses
~~~~~~~~~

BAG to INSPIRE Addresses Annex II Theme.

See https://github.com/justb4/inspire-foss/blob/master/etl/NL.Kadaster/Addresses/

Ordnance Survey
---------------

A successful Proof-of-Concept to convert Ordnance Survey Mastermap GML to PostGIS:

https://github.com/geopython/stetl/tree/master/examples/ordnancesurvey

SOSPilot
--------

A SensorWeb project by Geonovum, see http://sensors.geonovum.nl.

Dutch AQ to WFS/WMS(-Time) and SOS
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Stetl was used
for ETL from Dutch Air Quality Data from RIVM (XML) to WMS(-Time), WFS and SOS.
The latter was effected by SOS-Transactional publication. Documentation at
http://sospilot.readthedocs.org and ETL on GitHub at
https://github.com/Geonovum/sospilot/tree/master/src/rivm-lml

Dutch AQ to EAI Reporting
~~~~~~~~~~~~~~~~~~~~~~~~~

Stetl was used to generate XML-based reports for the EU EAI:

https://github.com/Geonovum/sospilot/tree/master/src/aq-report

This involved the first use of Jinja2 templating for complex XML/GML generation.

Smart Emission
--------------

Sensors for air quality, meteo and audio  at civilians. Project by University of Nijmegen/Gemeente Nijmegen with participation
by Geonovum. Stetl is used to transform a low-level sensor API to PostGIS and later on WMS/WFS/SOS and the SensorThings API.
Also InfluxDB output is developed here.

This is also an example how to use a Stetl Docker image:

See https://github.com/Geonovum/smartemission/tree/master/etl
