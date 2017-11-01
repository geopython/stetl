FROM debian:stretch-slim

LABEL maintainer "Just van den Broecke <justb4@gmail.com>"

# ARGS

ARG TIMEZONE="Europe/Amsterdam"
ENV TZ=${TIMEZONE}

ARG LOCALE="en_US.UTF-8"

ARG ADD_PYTHON_DEB_PACKAGES="python-requests"

# General ENV settings
ENV LC_ALL="${LOCALE}"
ENV LC_TYPE="${LOCALE}"
ENV LANG="${LOCALE}"
ENV LANGUAGE="${LOCALE}"
ENV DEBIAN_FRONTEND="noninteractive"
ENV BUILD_DEPS="tzdata locales"
ENV PYTHON_CORE_PACKAGES="python-setuptools python-lxml python-gdal python-psycopg2 python-jinja2 gdal-bin"
ENV PYTHON_TEST_PACKAGES="python-nose2 python-mock"
ENV PYTHON_EXTRA_PACKAGES="${ADD_PYTHON_DEB_PACKAGES}"

# Add Source Code
ADD . /stetl

# Set time right and configure timezone and locale
RUN \
	apt-get update \
	&& apt-get --no-install-recommends install  -y \
		${BUILD_DEPS} \
	    ${PYTHON_CORE_PACKAGES} \
	    ${PYTHON_TEST_PACKAGES} \
	    ${PYTHON_EXTRA_PACKAGES} \

	# Timezone
	# echo "${TZ}" > /etc/timezone && \
	&& cp /usr/share/zoneinfo/${TZ} /etc/localtime\
	&& dpkg-reconfigure tzdata \

	# Locale
	&& echo "LANG=${LANG}" >/etc/default/locale  \
	&& echo "${LANG} UTF-8" > /etc/locale.gen \
    && locale-gen\
    && dpkg-reconfigure locales \
    && /usr/sbin/update-locale LANG=${LANG} \

	# Install and Remove build-related packages for smaller image size
	&& cd /stetl \
		&& python setup.py install  \
		&& nose2 \
		&& apt-get purge ${PYTHON_TEST_PACKAGES} -y \
		&& apt autoremove -y  \
        && rm -rf /var/lib/apt/lists/* \
        
	&& echo "For ${TZ} date=`date`" \
	&& echo "locale=`locale`"

# Allow docker run
# docker run --rm -it geopython/stetl  stetl
# docker run --rm -it geopython/stetl  bash
