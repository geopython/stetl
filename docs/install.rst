.. _install:

Installation
============

(To be finalized, a rough version below)

(A Python package is in progress. For now download Stetl from
Github: https://github.com/justb4/stetl/archive/master.zip
run  ::

	(sudo) python setup.py install

and try the examples first.)

Dependencies
------------

Stetl depends on the following Python packages:

* GDAL
* psycopg2
* lxml

`GDAL` requires the native GDAL/OGR tools to be installed.

`lxml` http://lxml.de/installation.html requires the native (C) libraries:

* libxslt (required by lxml)
* libxml2 (required by lxml)

Linux
-----

Most packages should be able to be installed by apt-get or Python `pip` or `easy_install`.


- Optional: Python package dependencies
  ::

   sudo apt-get install python-setuptools
   sudo apt-get install python-dev
   sudo apt-get install libpq-dev

- libxml2/libxslt libs are usually already installed. Together with Python lxml
  the total install for `lxml` is.
  ::

   apt-get of yum install libxml2
   apt-get of yum install libxslt1.1
   apt-get of yum install python-lxml

- GDAL (http://gdal.org) with Python bindings
  ::

   apt-get of yum install gdal-bin
   apt-get of yum install python-gdal

- de PostgreSQL python bibliotheek psycopg2
  ::

   sudo easy_install psycopg2

- Python package "argparse" if you have Python < 2.7
  ::

   sudo easy_install argparse


Windows
-------

Best is to install GDAL and python using the OSGeo4W Installer from http://trac.osgeo.org/osgeo4w.

* Download and run the OSGeo4W Installer
* Choose `Advanced Install`
* On the `Select Packages` page expand `Commandline_Utilities` and Select from the list `gdal` and `python`
* (`psycopg2`??)
* Install `easy_instal`l to allow you to install `lxml`
* Download the `ez_setup.py` script
* Open the OSGeo4W Shell (Start > Programs > OSGeo4W > OSGeo4W > OSGeo4W Shell)
* Change to the folder that you downloaded `ez_setup.py` to (if you downloaded to C:\Temp then run cd C:\Temp)
* Install `easy_install` by running python `ez_setup.py`
* To install `lxml` with easy_install run `easy_install lxml`

Once the above has been installed you should have everything required to run Stetl.

Test Installation
-----------------

cd examples/basics
./runall.sh

Look for any error messages in your output.






