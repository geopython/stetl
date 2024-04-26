FROM ghcr.io/osgeo/gdal:ubuntu-small-3.8.5

LABEL maintainer="Just van den Broecke <justb4@gmail.com>"

# ARGS
ARG TIMEZONE="Europe/Amsterdam"
ARG LANG="en_US"
ARG LOCALE="en_US.UTF-8"
ARG POSTGRES_VERSION="11"
ARG ADD_DEB_PACKAGES=""
ARG ADD_PIP_PACKAGES=""

# not for now: python3-openpyxl python3-openpyxl python3-tz python3-numpy python3-pandas python3-xlrd
# pypi: wrapt
# ENV settings
ENV TZ=${TIMEZONE} \
   DEBIAN_FRONTEND="noninteractive" \
   DEB_PACKAGES="wget openssh-client postgresql-client-${POSTGRES_VERSION} locales tzdata python3-cov-core python3-deprecated python3-flake8 python3-jinja2 python3-lxml python3-markupsafe python3-nose2 python3-psycopg2 python3-sphinx" \
   APT_KEY_DONT_WARN_ON_DANGEROUS_USAGE="DontWarn"

# https://www.ubuntuupdates.org/ppa/postgresql?dist=focal-pgdg need PG client version 10
# old: 	curl -fsSL https://www.postgresql.org/media/keys/ACCC4CF8.asc | apt-key add -
# https://www.ubuntuupdates.org/ppa/postgresql?
# or use ARGS for other versions
RUN \
	apt-get update && apt-get --no-install-recommends install -y gnupg ca-certificates \
    && curl https://www.postgresql.org/media/keys/ACCC4CF8.asc | gpg --dearmor | tee /etc/apt/trusted.gpg.d/apt.postgresql.org.gpg >/dev/null \
	&& sh -c 'echo "deb http://apt.postgresql.org/pub/repos/apt/ jammy-pgdg main" >> /etc/apt/sources.list.d/postgresql.list' \
	&& apt-get -y update \
	&& apt-get --no-install-recommends install -y ${DEB_PACKAGES} ${ADD_DEB_PACKAGES} \
    && locale-gen ${LOCALE} && dpkg-reconfigure --frontend=noninteractive locales \
	&& cp /usr/share/zoneinfo/${TZ} /etc/localtime \
	&& dpkg-reconfigure --frontend=noninteractive tzdata \
    && echo "For ${TZ} date=`date`" && echo "Locale=`locale`"

# Add and install Source Code
ADD . /stetl
WORKDIR /stetl
# Most if not all deps already installed in Ubuntu (apt) python3-* packages
RUN export REQUIREMENTS_FILE=requirements-unversioned.txt && python3 setup.py install


# RUN cp /stetl/bin/stetl /usr/local/bin

# Run examples
# docker run --rm -it geopython/stetl stetl
# docker run --rm -v $(pwd):/work -w /work geopython/stetl:2.0 stetl -c etl.cfg


#FROM debian:buster-slim
#
#LABEL maintainer="Just van den Broecke <justb4@gmail.com>"
#
##
## ARGS
##
#ARG TIMEZONE="Europe/Amsterdam"
#ARG LOCALE="en_US.UTF-8"
#
#ARG ADD_DEB_PACKAGES=""
#ARG ADD_PIP_PACKAGES=""
#
## Tricky: must match installed GDAL version (2.1.2 on Stretch, 2.4.0 on Buster)
#ARG GDAL_PYTHON_BINDINGS_VERSION="2.4.0"
#
##
## ENV settings
##
#ENV TZ=${TIMEZONE} \
#   DEBIAN_FRONTEND="noninteractive" \
#   BUILD_DEPS="tzdata build-essential apt-utils libgdal-dev python3-pip python3-setuptools python3-dev" \
#   PYTHON_CORE_PACKAGES="locales python3-requests libgdal20 python3-gdal gdal-bin python3-tz python3-numpy python3-pandas python3-setuptools python3-lxml python3-psycopg2 python3-jinja2" \
#   PYTHON_EXTRA_DEB_PACKAGES="${ADD_PYTHON_DEB_PACKAGES}"  \
#   PYTHON_EXTRA_PIP_PACKAGES="${ADD_PYTHON_PIP_PACKAGES}"
#
## Add Source Code
#ADD . /stetl
#
## Set time right and configure timezone and locale
#RUN \
#	apt-get update \
#	&& apt-get --no-install-recommends install  -y \
#		${BUILD_DEPS} \
#	    ${PYTHON_CORE_PACKAGES} \
#	    ${PYTHON_EXTRA_DEB_PACKAGES} \
#	# Timezone
#	&& cp /usr/share/zoneinfo/${TZ} /etc/localtime\
#	&& dpkg-reconfigure tzdata \
#	# Locale
#	&& sed -i -e "s/# ${LOCALE} UTF-8/${LOCALE} UTF-8/" /etc/locale.gen \
#    && dpkg-reconfigure --frontend=noninteractive locales \
#    && update-locale LANG=${LOCALE} \
#    && pip3 install GDAL==${GDAL_PYTHON_BINDINGS_VERSION} ${PYTHON_EXTRA_PIP_PACKAGES} \
#	# Install and Remove build-related packages for smaller image size
#	&& cd /stetl \
#		&& python3 setup.py install  \
#		&& apt-get remove --purge ${BUILD_DEPS} -y \
#		&& apt autoremove -y  \
#        && rm -rf /var/lib/apt/lists/*
#
#ENV LANG="${LOCALE}" LANGUAGE="${LOCALE}"
