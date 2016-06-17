.. _install:

Installation
============

Easiest is to first install the Stetl-dependencies (see below) and then
install and maintain Stetl on your system as a Python package (pip is preferred). ::

    (sudo) pip install stetl
    or
    easy_install stetl

Alternatively you can download Stetl from
Github: by cloning (preferred) or downloading: https://github.com/justb4/stetl/archive/master.zip
and then install locally  ::

	(sudo) python setup.py install

Try the examples first. This should work on Linuxes and Mac OSX.
Windows installation may be more involved depending on your local Python setup. Platform-specific
installations below.

You may also want to download the complete .tar.gz distro from PyPi:
https://pypi.python.org/pypi/Stetl . This includes the examples and tests.

**Docker:** Since version 1.0.9 Stetl also can be installed and run via `Docker <http://docker.com>`_. See
:ref:`install_docker` below.

Dependencies
------------

Stetl depends on the following Python packages:

* GDAL bindings for Python
* psycopg2 (PostgreSQL client)
* lxml

``GDAL`` requires the native GDAL/OGR tools to be installed.

``lxml`` http://lxml.de/installation.html requires the native (C) libraries:

* libxslt (required by lxml)
* libxml2 (required by lxml)

When using the ``Jinja2`` templating filter, ``Jinja2TemplatingFilter``, see http://jinja.pocoo.org:

* Python Jinja2 package

Linux
-----

Most packages should be able to be installed by apt-get or Python ``pip`` or ``easy_install``.


- Optional: Python package dependencies
  ::

   sudo apt-get install python-setuptools
   sudo apt-get install python-dev
   sudo apt-get install libpq-dev

- ``libxml2/libxslt`` libs are usually already installed. Together with Python ``lxml``
  the total install for ``lxml`` is.
  ::

   apt-get of yum install libxml2
   apt-get of yum install libxslt1.1
   apt-get of yum install python-lxml

- GDAL (http://gdal.org) with Python bindings
  ::

   apt-get of yum install gdal-bin
   apt-get of yum install python-gdal

- the PostgreSQL client library for Python ``psycopg2``
  ::

   sudo easy_install psycopg2

- Python package ``argparse`` if you have Python < 2.7
  ::

   sudo easy_install argparse


Windows
-------

Best is to install GDAL and python using the OSGeo4W Installer from http://trac.osgeo.org/osgeo4w.

* Download and run the OSGeo4W Installer
* Choose ``Advanced Install``
* On the ``Select Packages`` page expand ``Commandline_Utilities`` and Select from the list ``gdal`` and ``python``
* (``psycopg2``??)
* Install ``easy_install`` to allow you to install ``lxml``
* Download the ``ez_setup.py`` script
* Open the OSGeo4W Shell (Start > Programs > OSGeo4W > OSGeo4W > OSGeo4W Shell)
* Change to the folder that you downloaded ``ez_setup.py`` to (if you downloaded to C:\Temp then run cd C:\Temp)
* Install ``easy_install`` by running python ``ez_setup.py``
* To install ``lxml`` with easy_install run ``easy_install lxml``

Only Psycopg2 needs explicit installation. Many install via: http://www.stickpeople.com/projects/python/win-psycopg.
Once the above has been installed you should have everything required to run Stetl.

Alternatively you may use Portable GIS. Still you will need to manually install psycopg2.
See http://www.archaeogeek.com/portable-gis.html for details.

Test Installation
-----------------

If you installed via Python 'pip' you can check if you run the latest version ::

    stetl -h

You should get meaningful output like ::

	2013-09-16 18:25:12,093 util INFO running with lxml.etree, good!
	2013-09-16 18:25:12,100 util INFO running with cStringIO, fabulous!
	2013-09-16 18:25:12,122 main INFO Stetl version = 1.0.3
	usage: stetl [-h] -c  CONFIG_FILE [-s  CONFIG_SECTION] [-a  CONFIG_ARGS]

Especially check the Stetl version number.

Try running the examples when running with a downloaded distro. ::

	cd examples/basics
	./runall.sh

Look for any error messages in your output.

.. _install_docker:

Install with Docker
-------------------

One of the cleanest ways to use Stetl is via `Docker <http://docker.com>`_. Your environment needs to be
setup to use Docker and probably you want to use some tooling like `Vagrant <https://www.vagrantup.com/>`_. The author uses
a combination of VirtualBox with Ubuntu and Vagrant on Mac OSX to run Docker, but this
is a bit out of scope here.

Assuming you have a working Docker environment, there are two ways to install Stetl with Docker:

* build a Docker image yourself using the Dockerfile in https://github.com/justb4/stetl/tree/master/docker
* use a prebuilt public Stetl Docker image: https://hub.docker.com/r/justb4/stetl

For running Stetl using Docker see  :ref:`run_docker`.