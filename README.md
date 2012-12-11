This is the sETL framework. The 'S' stands for Simple or Spatial or Streaming ETL. sETL is Open Source (GNU GPL v3).
Read a 5-minute introduction here: http://www.slideshare.net/justb4/5-minute-intro-to-setl and a longer presentation
here: http://www.slideshare.net/justb4/setl-preparing-rich-gml-data-for-deegree.

sETL originated in the INSPIRE-FOSS project (www.inspire-foss.org)
and was created by Just van den Broecke. Since sETL evolved into a wider use like 
transforming Dutch GML-based datasets such as IMGEO/BGT (Large Scale Topography) 
and IMKAD/BRK (Kadastral Data) it has now a repo of its own.

sETL basically glues together existing parsing and transformation tools like GDAL/OGR (ogr2ogr) and XSLT.
By using native tools like libxml and libxslt (via Python lxml) SETL is speed-optimized.
There are offcourse existing Open Source ETL tools like GeoKettle and Talend Geospatial, but
in many cases a simpler/bulk ETL is required. 

So why en when to use sETL. 
- when ogr2ogr or XSLT alone cannot do the job
- when GeoKettle/Talend is too heavy/complex 
- when FME is too expensive, too closed and/or too slow ;-)
- when having to deal with complex GML as source or destination

So sETL is in particularly useful for INSPIRE-related transformations and other complex GML-related ETL.

sETL has a similar design as Spring (Java) and other modern frameworks based on IoC (Inversion of COntrol, http://en.wikipedia.org/wiki/Inversion_of_Control).
A configuration file (in Python config format) specifies your chain of ETL steps.
This chain is formed by a series of Python modules/objects and their parameters. These are 
symbolically specified in the config file. You just invoke etl.py the main program with a config file.
The config file specifies the input modules (e.g. PostGIS), transformers (e.g. XSLT) and outputs (e.g. a GML file or even
WFS-T a geospatial protocol to publish GML to a server).

There is special support now for output to the deegree WFS server (http://deegree.org), either directly in
a so called GML Blobstore, via deegree "FSLoader" tool or via WFS-T publishing. The latter is in theory
supported for other WFS server products like GeoServer and MapServer.

sETL has been proven to handle 10's of millions of objects without any memory issues.
This is achieved through a technique called "streaming and splitting". 
For example: using the OgrPostgisInput module an GML stream can be generated from the database.
A component called the GmlSplitter can split this stream into managable chunks (like 20000 features) 
and feed this upstream into the ETL chain.

More to follow...see some examples under the examples dir.

Another example in http://code.google.com/p/inspire-foss/source/browse/trunk/etl/NL.Kadaster/Addresses
(Dutch Addresses (BAG) to INSPIRE Addresses)


