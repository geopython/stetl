FROM python:2.7.14-alpine3.6

LABEL maintainer "Just van den Broecke <justb4@gmail.com>"

# These are default values,
# Override when running container via docker(-compose)

# General ENV settings
ENV LC_ALL "en_US.UTF-8"
ENV LANG "en_US.UTF-8"
ENV LANGUAGE "en_US.UTF-8"

ARG TZ="Europe/Amsterdam"

RUN apk add --no-cache --virtual .build-deps gcc build-base linux-headers postgresql-dev \
    && apk add --no-cache \
    bash \
    vim \
    tzdata \
    && echo $TZ > /etc/timezone \
    && cp /usr/share/zoneinfo/$TZ /etc/localtime \
    && rm -rf /var/cache/apk/* /tmp/* /var/tmp/*

RUN apk add --no-cache \
	   expat \
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

RUN pip install gdal==2.1.3 \
	&& pip install Jinja2 \
	&& pip install lxml \
	&& pip install nose2 \
	&& pip install mock

# Add Source Code
ADD . /stetl

# Install and Remove build-related packages for smaller image size
RUN cd /stetl \
	&& python setup.py install  \
	&& apk del .build-deps

# Allow docker run
# ENTRYPOINT ["/usr/local/bin/stetl"]
