.. _intro:

Intro
=====

Stetl, streaming ETL, pronounced "staedl", is a lightweight ETL-framework for the conversion of rich (such as GML)
geospatial data. Stetl is Open Source (GNU GPL v3).

Read a 5-minute introduction here: http://www.slideshare.net/justb4/5-minute-intro-to-setl and a longer presentation
here: http://www.slideshare.net/justb4/stetl-foss4g20131024v1.

Stetl originated in the `INSPIRE-FOSS project <http//www.inspire-foss.org>`_
and was originally created by `Just van den Broecke <http://nl.linkedin.com/in/justb4>`_.
Subsequently, Stetl evolved into a wider use
transforming Dutch GML-based datasets such as Top10NL, IMGEO/BGT (Large Scale Topography)
and IMKAD/BRK (Kadastral Data). Therefore Stetl now has a repository of its own at `GitHub <https://github.com/justb4/stetl>`_.

Stetl basically glues together existing parsing and transformation tools like `GDAL/OGR (ogr2ogr) <http://gdal.org>`_ and
`XSLT <http://en.wikipedia.org/wiki/XSLT>`_. By using native tools like `libxml2` and `libxslt` (via `Python lxml <http://lxml.de>`_)
Stetl is speed-optimized.

Stetl has (currently) no GUI. There are powerful Open Source ETL tools like `GeoKettle <http://www.spatialytics.org/projects/geokettle>`_
and Talend Geospatial with a GUI. Check these out. But some of us would like to stay close to the commandline, be Pythonic and
reuse existing tools 'close to the iron'.

So why en when to use Stetl.

* when ogr2ogr or XSLT alone cannot do the job
* when having to deal with complex GML as source or destination
* when you want to use simple command-line tooling or (Python) program integrations
* when you need speed
* when you are a `Pythonista`

Stetl is in particularly useful for INSPIRE-related transformations and other complex GML-related ETL.

Stetl was presented at FOSS4G 2013 in Nottingham, see http://2013.foss4g.org/conf/programme/presentations/156
and the slides: http://www.slideshare.net/justb4/stetl-foss4g20131024v1
