FROM ubuntu:16.04

MAINTAINER just@justobjects.nl

# Configure timezone and locale
ARG IMAGE_TIMEZONE="Europe/Amsterdam"

# Set time right and configure timezone and locale
RUN \
	apt-get update && \
	apt-get install -y tzdata && \
	echo "$IMAGE_TIMEZONE" > /etc/timezone && \
	dpkg-reconfigure -f noninteractive tzdata && \
	export DEBIAN_FRONTEND=noninteractive TERM=linux && \
    echo 'debconf debconf/frontend select Noninteractive' | debconf-set-selections

# Use UbuntuGIS for latest GDAL, Proj.4, GEOS etc
RUN \
	apt-get install -y software-properties-common && \
	apt-add-repository ppa:ubuntugis/ubuntugis-unstable && \
	apt-get update && \
	apt-get install -y \
		git \
	    libgeos-dev \
	    python-lxml \
	    libxml2-dev libxslt-dev \
	    python-gdal \
	    libgdal-dev \
	    build-essential \
	    python-dev \
	    python-setuptools \
	    python-pip \
	    gdal-bin

# Add Python extra packages
RUN \
	pip install \
		pytz \
		requests \
		geohash \
		Cython \
		numpy \
		pandas \
		scipy \
		scikit-learn==0.18  \
		influxdb \
		seaborn \
		matplotlib \
		nose2 \
		mock

# Get latest Stetl from git and use Stetl installer
RUN \
	git clone https://github.com/geopython/stetl /opt/stetl && \
	cd /opt/stetl && \
    python setup.py install && \
    nose2

# Allow docker run
ENTRYPOINT ["/usr/local/bin/stetl"]
