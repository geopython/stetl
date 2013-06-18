.. _intro:

Intro
=====

Stetl, streaming ETL, pronounced "staedl", is a lightweight ETL-framework for the conversion of rich (such as GML)
geospatial data. Stetl is Open Source (GNU GPL v3).

Read a 5-minute introduction here: http://www.slideshare.net/justb4/5-minute-intro-to-setl and a longer presentation
here: http://www.slideshare.net/justb4/stetl-bolsena2013800v1.

Stetl originated in the `INSPIRE-FOSS project <http//www.inspire-foss.org>`_
and was originally created by Just van den Broecke. Since Stetl evolved into a wider use like
transforming Dutch GML-based datasets such as Top10NL, IMGEO/BGT (Large Scale Topography)
and IMKAD/BRK (Kadastral Data) it has now a repository of its own.

Stetl basically glues together existing parsing and transformation tools like `GDAL/OGR (ogr2ogr) <http://gdal.org>`_ and XSLT.
By using native tools like `libxml2` and `libxslt` (via `Python lxml <http://lxml.de>`_) Stetl is speed-optimized.
There are off course existing Open Source ETL tools like GeoKettle and Talend Geospatial, but
in many cases a simpler/bulk ETL can do the job.

So why en when to use Stetl.

* when ogr2ogr or XSLT alone cannot do the job
* when GeoKettle/Talend is too heavy/complex
* when FME is too expensive, too closed and/or too slow ;-)
* when having to deal with complex GML as source or destination

So Stetl is in particularly useful for INSPIRE-related transformations and other complex GML-related ETL.
