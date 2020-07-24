FROM debian:buster-slim

LABEL maintainer="Just van den Broecke <justb4@gmail.com>"

#
# ARGS
#
ARG TIMEZONE="Europe/Amsterdam"
ARG LOCALE="en_US.UTF-8"

ARG ADD_PYTHON_DEB_PACKAGES=""
ARG ADD_PYTHON_PIP_PACKAGES=""

# Tricky: must match installed GDAL version (2.1.2 on Stretch, 2.4.0 on Buster)
ARG GDAL_PYTHON_BINDINGS_VERSION="2.4.0"

#
# ENV settings
#
ENV TZ=${TIMEZONE} \
   DEBIAN_FRONTEND="noninteractive" \
   BUILD_DEPS="tzdata build-essential apt-utils libgdal-dev python3-pip python3-setuptools python3-dev" \
   PYTHON_CORE_PACKAGES="locales python3-requests libgdal20 python3-gdal gdal-bin python3-tz python3-numpy python3-pandas python3-setuptools python3-lxml python3-psycopg2 python3-jinja2" \
   PYTHON_EXTRA_DEB_PACKAGES="${ADD_PYTHON_DEB_PACKAGES}"  \
   PYTHON_EXTRA_PIP_PACKAGES="${ADD_PYTHON_PIP_PACKAGES}"

# Add Source Code
ADD . /stetl

# Set time right and configure timezone and locale
RUN \
	apt-get update \
	&& apt-get --no-install-recommends install  -y \
		${BUILD_DEPS} \
	    ${PYTHON_CORE_PACKAGES} \
	    ${PYTHON_EXTRA_DEB_PACKAGES} \
	# Timezone
	&& cp /usr/share/zoneinfo/${TZ} /etc/localtime\
	&& dpkg-reconfigure tzdata \
	# Locale
	&& sed -i -e "s/# ${LOCALE} UTF-8/${LOCALE} UTF-8/" /etc/locale.gen \
    && dpkg-reconfigure --frontend=noninteractive locales \
    && update-locale LANG=${LOCALE} \
    && pip3 install GDAL==${GDAL_PYTHON_BINDINGS_VERSION} ${PYTHON_EXTRA_PIP_PACKAGES} \
	# Install and Remove build-related packages for smaller image size
	&& cd /stetl \
		&& python3 setup.py install  \
		&& apt-get remove --purge ${BUILD_DEPS} -y \
		&& apt autoremove -y  \
        && rm -rf /var/lib/apt/lists/*

ENV LANG="${LOCALE}" LANGUAGE="${LOCALE}"
RUN echo "For ${TZ} date=`date`" && echo "Locale=`locale`"

# Run examples
# docker run --rm -it geopython/stetl stetl
# docker run --rm -v $(pwd):/work -w /work geopython/stetl:2.0 stetl -c etl.cfg
