FROM python:2.7.14-alpine3.6

LABEL maintainer "Just van den Broecke <justb4@gmail.com>"

# These are default values,
# Override when running container via docker(-compose)

# General ENV settings
ENV LC_ALL "en_US.UTF-8"
ENV LANG "en_US.UTF-8"
ENV LANGUAGE "en_US.UTF-8"
ENV GDAL_VERSION 2.1.3

ARG TZ="Europe/Amsterdam"

# Core system installs/config
RUN \
    # Add edge repo
    # echo '@edge http://dl-cdn.alpinelinux.org/alpine/edge/main' >> /etc/apk/repositories && \
    # echo '@edge http://dl-cdn.alpinelinux.org/alpine/edge/community' >> /etc/apk/repositories && \
    echo '@edge http://dl-cdn.alpinelinux.org/alpine/edge/testing' >> /etc/apk/repositories && \

    # Update packages
    apk --no-cache upgrade \

	&& apk add --no-cache --virtual .build-deps \
		gcc \
		build-base \
		linux-headers \
		postgresql-dev \
		tzdata \
    && apk add --no-cache \
	    bash \
    && echo $TZ > /etc/timezone \
    && cp /usr/share/zoneinfo/$TZ /etc/localtime \
    && rm -rf /var/cache/apk/* /tmp/* /var/tmp/*

# App-specific installs/config
RUN apk add --no-cache \
	   expat \
	   expat-dev \
       libxml2-dev \
       libxslt-dev \
       postgresql-client \
	   py-lxml \
	   proj4-dev \
	   geos-dev \
	   gdal-dev \
	   py-gdal \
	   gdal \
    --repository http://nl.alpinelinux.org/alpine/edge/testing \
    && rm -rf /var/cache/apk/* /tmp/* /var/tmp/*

# May need to build APK ourselves  example:
# https://github.com/HBKEngineering/alpine-packages
# original is here: https://git.alpinelinux.org/cgit/aports/tree/testing/gdal/APKBUILD
# use Docker to build with Alpine APK SDK :
# https://github.com/andyshinn/docker-alpine-abuild

# Install GDAL by compile, takes extremely long!
# RUN \
# example at https://github.com/winsento/geoserver-alpine/blob/master/2.8/Dockerfile
#    wget http://download.osgeo.org/gdal/${GDAL_VERSION}/gdal-${GDAL_VERSION}.tar.gz -O /tmp/gdal.tar.gz && \
#    tar xzf /tmp/gdal.tar.gz -C /tmp && \
#    cd /tmp/gdal-${GDAL_VERSION} && ./configure  --prefix=/usr --with-curl=/usr/bin/curl-config --with-expat && make && make install

RUN \
	pip install -U pip  && \
	pip install \
		gdal==${GDAL_VERSION} \
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
	&& apk del .build-deps

# Allow docker run
# ENTRYPOINT ["/usr/local/bin/stetl"]
