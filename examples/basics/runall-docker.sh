#!/bin/bash
#
# Shortcut to run all basic examples using the Stetl Docker image.
#


for DIR_NAME in `echo [0-9]*`; do
	pushd ${DIR_NAME}
	
	echo "==== running etl.sh for example ${DIR_NAME} ===="

	# Run with current dir mounted as work dir
	BASE_CMD="docker run --rm -v $(pwd):/work -w /work geopython/stetl:2.0 stetl -c etl.cfg"

	# Only exception is 6_cmdargs which has several
	# extended stetl -a commandlines
	if [ ${DIR_NAME} = "6_cmdargs" ]
	then
		echo "= Special case for ${DIR_NAME} - testing -a options ="
		${BASE_CMD} -a "in_xml=input/cities.xml in_xsl=cities2gml.xsl out_xml=output/gmlcities.gml"
		${BASE_CMD} -a etl.args
		${BASE_CMD} -a etl.args -a "in_xml=input/amsterdam.xml"
	else
		# regular
		${BASE_CMD}
	fi

	popd
done
