FROM python:2.7.14-slim-stretch

LABEL maintainer "Just van den Broecke <justb4@gmail.com>"

# General ENV settings
ENV LC_ALL "en_US.UTF-8"
ENV LC_TYPE "en_US.UTF-8"
ENV LANG "en_US.UTF-8"
ENV LANGUAGE "en_US.UTF-8"
ENV GDAL_VERSION 2.1.0
ENV BUILD_DEPS "tzdata build-essential locales apt-utils"
ENV DEBIAN_FRONTEND noninteractive

ARG TZ="Europe/Amsterdam"

# Set time right and configure timezone and locale
RUN \
	apt-get update && \
	apt-get install -y ${BUILD_DEPS} && \

	# Timezone
	echo "${TZ}" > /etc/timezone && \
	cp /usr/share/zoneinfo/${TZ} /etc/localtime && \
	dpkg-reconfigure -f noninteractive tzdata && \

	# Locale
	echo "LANG=${LANG}" >/etc/default/locale && \
	echo "${LANG} UTF-8" > /etc/locale.gen && \
    locale-gen && \
    dpkg-reconfigure locales && \
    /usr/sbin/update-locale LANG=${LANG}

# App-specific installs/config
RUN apt-get install -y \
		python-lxml \
		libgdal-dev \
		python-gdal \
		gdal-bin

RUN \
	apt-get install -y build-essential && \
	pip install -U pip  && \
	pip install \
		gdal==`gdalinfo --version | cut -d' ' -f2 | cut -d',' -f1` \
		# gdal==2.2.0 \
		psycopg2==2.7.3.2 \
		Jinja2==2.9.6 \
		lxml==4.1.0 \
		nose2 \
		mock

# Add Source Code
ADD . /stetl

# Install and Remove build-related packages for smaller image size
RUN cd /stetl \
	&& python setup.py install  \
	&& nose2 \
	&& apt-get purge ${BUILD_DEPS} -y \
	&& apt autoremove -y

RUN \
	echo "For ${TZ} date=`date`" && \
	echo "locale=`locale`"

# Allow docker run
# ENTRYPOINT ["/usr/local/bin/stetl"]
