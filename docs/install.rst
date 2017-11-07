.. _install:

Installation
============

Stetl currently only runs with Python 2 (2.7+). `Work is underway <https://github.com/geopython/stetl/pull/27>`_ for Python3 support.

Easiest is to first install the Stetl-dependencies (see below) and then
install and maintain Stetl on your system as a Python package (pip is preferred). ::

    (sudo) pip install stetl
    or
    easy_install stetl

Alternatively you can download Stetl from
Github: by cloning (preferred) or downloading: https://github.com/geopython/stetl/archive/master.zip
and then install locally  ::

	(sudo) python setup.py install

Try the examples first. This should work on Linuxes and Mac OSX.

Windows installation may be more involved depending on your local Python setup. Platform-specific
installations below.

You may also want to download the complete .tar.gz distro from PyPi:
https://pypi.python.org/pypi/Stetl . This includes the examples and tests.

**Docker**

Since version 1.0.9 Stetl also can be installed and run via `Docker <http://docker.com>`_. See
:ref:`install_docker` below.

**Debian/Ubuntu**

Thanks to Bas Couwenberg, work is performed to provide Stetl as Debian packages on both Debian and Ubuntu, see details:
https://packages.debian.org/search?keywords=stetl (Debian) and
https://launchpad.net/ubuntu/+source/python-stetl (Ubuntu, Xenial and later).
Stetl is split into 2 packages ``python-stetl``, the Python framework and ``stetl`` the command line utility.
NB the versions of these packages may be older than when installing Stetl via `pip` from PyPi
or directly from GitHub. Always check this first.

Dependencies
------------

Stetl depends on the following Python packages:

* GDAL (v2+) bindings for Python
* psycopg2 (PostgreSQL client)
* lxml
* Jinja2 templating

``GDAL`` Python binding requires the native GDAL/OGR libs and tools (version 2+) to be installed.

``lxml`` http://lxml.de/installation.html requires the native (C) libraries:

* libxslt (required by lxml)
* libxml2 with Python bindings (required by lxml)

When using the ``Jinja2`` templating filter, ``Jinja2TemplatingFilter``, see http://jinja.pocoo.org:

* Python Jinja2 package

Platform-specific guidelines for dependencies follow next.

Linux
~~~~~

For Debian-based distro's like Ubuntu and Debian itself, most packages should be able to be installed via apt-get.

Tip: to get latest versions of GDAL and other Open Source geospatial software, best is
to add the `UbuntuGIS Repository <https://wiki.ubuntu.com/UbuntuGIS>`_.
Below a setup that works in Ubuntu 16.04 Xenial using Debian/Ubuntu packages. In some cases you may
choose to install the same packages via `pip` to have more recent versions like for `lxml`.

- Python dependencies: ::

	apt-get install python-setuptools
	apt-get install python-dev
	apt-get install python-pip
	pip install --upgrade pip
	
- ``libxml2/libxslt`` libs are usually already installed. Together with Python ``lxml``, the total install for ``lxml`` is: ::

	apt-get install python-libxml2
	apt-get install python-libxslt1
	apt-get install libxml2-dev libxslt1-dev lib32z1-dev
	apt-get install python-lxml

- ``GDAL`` (http://gdal.org) version 2+ with Python bindings: ::

	# Add UbuntuGIS repo to get latest GDAL, at least v2 on Ubuntu 16.04, Xenial.
	add-apt-repository ppa:ubuntugis/ubuntugis-unstable
	apt-get update
	apt-get install gdal-bin
	gdalinfo --version
	# should show something like: GDAL 2.2.1, released 2017/06/23

	apt-get install python-gdal

- the PostgreSQL client library for Python ``psycopg2``: ::

	apt-get install python-psycopg2

- for ``Jinja2``: ::

	apt-get install python-jinja2


Mac OSX
~~~~~~~

Dependencies can best be installed via `Homebrew <http://brew.sh/>`_.

Windows
~~~~~~~

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

Run Unit Tests
--------------

You can run unit tests to completely verify your installation. First install some extra packages: ::

	pip install -r requirements-dev.txt

Then run the tests using `nose2`. ::

	nose2

.. _install_docker:

Install with Docker
-------------------

The fastest way to use Stetl is via `Docker <http://docker.com>`_. The Stetl Docker Image is lightweight,
compressed just over 100MB, based on a Debian "slim" Docker Image.

Your environment needs to be
setup to use Docker and probably you want to use some tooling like `Vagrant <https://www.vagrantup.com/>`_. The author uses
a combination of VirtualBox with Ubuntu and Vagrant on Mac OSX to run Docker, but this
is a bit out of scope here.

Assuming you have a working Docker environment, there are two ways to install Stetl with Docker:

* build a Docker image yourself using the Dockerfile in https://github.com/geopython/stetl/blob/master/Dockerfile
* use a prebuilt public Stetl Docker image from Docker Hub: https://hub.docker.com/r/geopython/stetl

When rebuilding you can add build arguments for your environment, defaults:  ::

	ARG TIMEZONE="Europe/Amsterdam"
	ARG LOCALE="en_US.UTF-8"
	ARG ADD_PYTHON_DEB_PACKAGES=""
	ARG ADD_PYTHON_PIP_PACKAGES=""

For example building with extra Python packages: ::

	docker build --build-arg ADD_PYTHON_DEB_PACKAGES="python-requests python-tz" -t geopython/stetl:latest .
	docker build --build-arg ADD_PYTHON_PIP_PACKAGES="scikit-learn==0.18 influxdb" -t geopython/stetl:latest .

Or you may extend the Stetl Dockerfile with your own Dockerfile.

For running Stetl using Docker see  :ref:`run_docker`.
