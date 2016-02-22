# Stetl - Streaming ETL

Stetl, streaming ETL, pronounced "staedl", is a lightweight ETL-framework for the conversion of rich (as GML)
geospatial data conversion. Stetl is Open Source (GNU GPL v3).

## Documentation

The main website and documentation can be found on http://stetl.org (or http://stetl.readthedocs.org).
Read a 5-minute introduction here: http://www.slideshare.net/justb4/5-minute-intro-to-setl and a longer presentation
here: http://www.slideshare.net/justb4/stetl-foss4g20131024v1.
Stetl was presented at several occasions like the
FOSS4G 2013 in Nottingham http://2013.foss4g.org.

## Origins
Stetl originated in the INSPIRE-FOSS project (www.inspire-foss.org)
and was created by Just van den Broecke. Since Stetl evolved into a wider use like
transforming Dutch GML-based datasets such as IMGEO/BGT (Large Scale Topography) 
and IMKAD/BRK (Cadastral Data) it has now a repo of its own.

## Design 

Stetl basically glues together existing parsing and transformation tools like GDAL/OGR (ogr2ogr) and XSLT.
By using native tools like libxml and libxslt (via Python lxml) Stetl is speed-optimized.

Stetl has a similar design as Spring (Java) and other modern frameworks based on IoC (Inversion of Control, http://en.wikipedia.org/wiki/Inversion_of_Control).
A configuration file (in Python config format) specifies your chain of ETL steps.
This chain is formed by a series of Python modules/objects and their parameters. These are 
symbolically specified in the config file. You just invoke etl.py the main program with a config file.
The config file specifies the input modules (e.g. PostGIS), transformers (e.g. XSLT) and outputs (e.g. a GML file or even
WFS-T a geospatial protocol to publish GML to a server).

Stetl has been proven to handle 10's of millions of objects without any memory issues.
This is achieved through a technique called "streaming and splitting". 
For example: using the OgrPostgisInput module an GML stream can be generated from the database.
A component called the GmlSplitter can split this stream into managable chunks (like 20000 features) 
and feed this upstream into the ETL chain.

## Examples

Stetl has been found in particularly useful for INSPIRE-related transformations and other complex GML-related ETL.

See examples under the examples dir.

Another example in http://code.google.com/p/inspire-foss/source/browse/trunk/etl/NL.Kadaster/Addresses
(Dutch Addresses (BAG) to INSPIRE Addresses)

## Contributing

Anyone and everyone is welcome to contribute. Please take a moment to
review the [guidelines for contributing](CONTRIBUTING.md).

* [Bug reports](CONTRIBUTING.md#bugs)
* [Feature requests](CONTRIBUTING.md#features)
* [Pull requests](CONTRIBUTING.md#pull-requests)

## Finally

The word "stetl" is also an alternative writing for "shtetl":
http://en.wikipedia.org/wiki/Stetl : "...Material things were neither disdained nor
extremely praised in the shtetl. Learning and education were the ultimate measures of worth in the eyes of the community,
while money was secondary to status..."



