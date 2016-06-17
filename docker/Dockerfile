FROM ubuntu:14.04
# FROM python:2.7  would be preferred but trickier
# TODO: use a more lightweight Linux distro than Ubuntu

MAINTAINER just@justobjects.nl

# Configure timezone and locale
ARG IMAGE_TIMEZONE="Europe/Amsterdam"
# set time right adn configure timezone and locale
RUN echo "$IMAGE_TIMEZONE" > /etc/timezone && \
	dpkg-reconfigure -f noninteractive tzdata

# Optional: Use local cached debs from host (saves your bandwidth!)
# Change ip below to that of your apt-cacher-ng host
# Or comment this line out if you do not with to use caching
# ADD 71-apt-cacher-ng /etc/apt/apt.conf.d/71-apt-cacher-ng

RUN export DEBIAN_FRONTEND=noninteractive TERM=linux && \
  echo 'debconf debconf/frontend select Noninteractive' | debconf-set-selections

RUN apt-get update && \
	apt-get install -y software-properties-common

# Use UbuntuGIS for latest GDAL, Proj.4, GEOS etc
RUN apt-add-repository ppa:ubuntugis/ubuntugis-unstable
RUN apt-get update && \
	apt-get install -y git \
    libproj0 \
    libgeos-dev \
    python-lxml \
    python-gdal \
    libgdal-dev \
    build-essential \
    python-dev \
    python-setuptools

# Get latest Stetl from git
RUN git clone https://github.com/justb4/stetl /opt/stetl

# Use Stetl installer
RUN cd /opt/stetl; python setup.py install

# Allow docker run
ENTRYPOINT ["/usr/local/bin/stetl"]
