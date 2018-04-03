FROM debian:stretch-slim

LABEL maintainer="Just van den Broecke <justb4@gmail.com>"

#
# ARGS
#
ARG TIMEZONE="Europe/Amsterdam"
ARG LOCALE="en_US.UTF-8"

# ARG ADD_PYTHON_DEB_PACKAGES="python-scipy python-seaborn python-matplotlib"
ARG ADD_PYTHON_DEB_PACKAGES=""
# ARG ADD_PYTHON_PIP_PACKAGES="scikit-learn==0.18"
ARG ADD_PYTHON_PIP_PACKAGES=""

#
# ENV settings
#
ENV TZ=${TIMEZONE} \
   LC_ALL="${LOCALE}" \
   LC_TYPE="${LOCALE}" \
   LANG="${LOCALE}" \
   LANGUAGE="${LOCALE}" \
   DEBIAN_FRONTEND="noninteractive" \
   BUILD_DEPS="tzdata locales" \
   PYTHON_CORE_PACKAGES="cython python-requests python-tz python-numpy python-pandas python-setuptools python-pip python-lxml python-gdal python-psycopg2 python-jinja2 gdal-bin" \
   PYTHON_TEST_PACKAGES="python-nose2 python-mock" \
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
	    ${PYTHON_TEST_PACKAGES} \
	    ${PYTHON_EXTRA_DEB_PACKAGES} \

	# Timezone
	# echo "${TZ}" > /etc/timezone && \
	&& cp /usr/share/zoneinfo/${TZ} /etc/localtime\
	&& dpkg-reconfigure tzdata \

	# Locale
	&& echo "LANG=${LANG}" >/etc/default/locale  \
	&& echo "${LANG} UTF-8" > /etc/locale.gen \
    && locale-gen \
    && dpkg-reconfigure locales \
    && /usr/sbin/update-locale LANG=${LANG} \

    # Optional packages to install via Pip
	&& if [ "x${PYTHON_EXTRA_PIP_PACKAGES}" = "x" ] ;\
	    then \
	        echo "No extra Pip packages to install" ;\
	    else \
	        pip install ${PYTHON_EXTRA_PIP_PACKAGES} ;\
	    fi  \

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
