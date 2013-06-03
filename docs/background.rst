.. _background:

Background
==========

The text below gives some introduction to ETL, the
rationale why Stetl was developed and where and how it attempts to fit in.

Data conversion combined with model and coordinate transformation
from a source to a target datastore (files, databases) is a recurring task
in almost every geospatial project.
This process is often referred to as `ETL (Extract Transform Load) <http://en.wikipedia.org/wiki/Extract,_transform,_load>`_.
Source and/or target geo-data formats are increasingly encoded as `GML (Geography Markup Language) <http://en.wikipedia.org/wiki/Geography_Markup_Language>`_,
either as flat records, so called Simple Features, but more and more using
domain-specific, object oriented `OGC/ISO GML Application Schema's <http://en.wikipedia.org/wiki/Geography_Markup_Language#Application_schema>`_.

GML Application Schema's are for example heavily used within the `INSPIRE Data Harmonization <http://inspire.ec.europa.eu/>`_
effort in Europe.
Many National Mapping and Cadastral Agencies (NMCAs) use GML-encoded datasets as their bulk
format for download and exchange and via Web Feature Services (WFSs).
As geospatial professionals we are often confronted with ETL-tasks involving (complex) GML
or worse: "GML-lookalikes", which are often XML Schema's embedded with GML-namespaced elements.

Luckily, in many cases `GDAL/OGR <http://gdal.org>`_, the Swiss Army Knife for geo-data conversion,
can do the job. If `"ogr2ogr" <http://www.gdal.org/ogr2ogr.html>`_ sounds like gibberish to you, check out http://gdal.org !
But when complex, some say rich, GML Application Schema's are involved,
data conversion can be a daunting task when GDAL/OGR alone is not sufficient.
Firstly, often complex data model transformations have to be applied.
In addition we may be confronted with the bulkiness of
GML: Megabyte/Gigabyte-files, deeply nested elements where the nuggets, the actual attribute values,
reside, trees of .zip files and possibly more nasty surprises once we have unboxed a GML-delivery.
High resource consumption in memory and CPU and long processing hours, up to complete machine-lockup, can be the
the side-effects of naive GML-processing.

Within the FOSS4G world we can resort to higher level,
GUI-based, ETL-tools such as GeoKettle, Humboldt tools and Talend GeoSpatial. These are very powerful
tools by themselves, check them out as well. Some of us, like the author, like to stay closer
to GDAL/OGR, to XSLT for model transforms, some command line tools and some Python scripting, but without
having to write a complete, ad-hoc ETL-program each time. This is the space where Stetl tries to fit in,
so read on.

So we already have great FOSS tools for XML/GML parsing, data-conversion and
model-transformation like GDAL/OGR (ogr2ogr!), XSLT (Extensible
Stylesheet Language Transformations, for transforming XML) and native XML-parsing libraries like libxml2.
Each individual tool/library is extremely powerful and performant by itself.
But we would like to combine of these tools. Take for example flat, national adres data in a PostGIS
database that we need to transform to multiple INSPIRE Application Schema GML files.
Each individual FOSS tool can handle part of the ETL: ogr2ogr for converting
from PostGIS (including coordinate tranformation) into to simple feature GML,
XSLT (xsltproc/libxslt) to transform
the resulting flat GML to rich INSPIRE GML. But with millions of addresses we cannot
simply use a single GML memory datastructure (DOM) or single intermediate GML-file.

Add Python and a configuration convention to this equation and we have
Stetl: Streaming ETL. Stetl is a lightweight, geospatial ETL (Extract Transform Load)
framework written in Python. ETL-processing with Stetl is driven from a configuration
file. Within a Stetl configuration file a chain of ETL-processing modules
is declared through which the data flows ("streams"). A module may be an input,
filter or output module. Modules have input and output data types declared such that only
compatible modules can be connected. However, Stetl does not define a grand internal data structure
to which all data is mapped as many ETL-tools do. Data formats are kept close to the
external tools that Stetl uses. Stetl comes with pre-defined modules for GML-parsing,
XSLT processing, XSD Validation, PostGIS/OGR input and output, GML-splitting and many more.
Stetl calls on the above tools like OGR, libxslt and libxml2 via their native interfaces.
Stetl is even more speed-optimized as no intermediate file-storage
is used and through other means such as native string buffers.
For example large XML/GML-files can be split into manageable
documents and streamed into an XSLT filter module. Stetl-modules are off course extensible
and can be user-defined. Reusable ETL-configurations invoked through parameterized commandline scripts
can be defined without programming.

Stetl evolved from and is used within the INSPIRE-FOSS project (http://inspire-foss.org).
Here for example, Dutch national addresses (BAG) were transformed into INSPIRE Addresses GML
(files and database). Special Stetl integration modules are available to extract and publish
data from/to a deegree WFS and deegree "Blobstore-database". The combination Stetl/deegree is an ideal
setup for INSPIRE deployments.

Other Dutch national datasets like Top10NL and BGT (Dutch topo vector datasets)
have been completely and successfully transformed. Work is in progress to use Stetl as
the basis for NLExtract (http://nlextract.nl), a project that provides ETL tools for Dutch
open geo-datasets. Stetl development is now (april 2013) in an initial phase and takes place in
GitHub. The current version is workable but we hope to present a v1.0 at FOSS4G with more
documentation and as a standard Python Package via PyPi. The main link is:
http://stetl.org (now links to GitHub).
To get started find some basic examples here: https://github.com/justb4/stetl/tree/master/examples/basics.


