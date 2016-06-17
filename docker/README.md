# Stetl Docker

Docker image to run ETL tool Stetl. See http://stetl.org.
Public Docker images are available at: https://hub.docker.com/r/justb4/stetl/.

## Status

First version on June 17, 2016. Improvements welcome.

## Building

Use ./build.sh or

     docker build -t justb4/stetl:latest .

ARGs: optional --build-arg IMAGE_TIMEZONE="Europe/Amsterdam"

## Running

Mapping volumes (``docker -v``) can be handly to maintain all config and data on the Host, outside the Docker container. 
Note that full paths are required.

Example, running a basic Stetl example:

	cd test/1_copystd
	docker run -v `pwd`:`pwd` -w `pwd`  -t -i justb4/stetl:latest -c etl.cfg   

	or
	./etl.sh
	
Many Stetl configs require a connection to PostGIS. This can be effected with a linked container: ``--link postgis``, or
better using Docker networking.

## More

See https://github.com/Geonovum/smartemission/tree/master/etl for a real-world example using a single Stetl Docker image
for multiple Stetl configurations and linking with a PostGIS Docker container.  For example:
https://github.com/Geonovum/smartemission/blob/master/etl/last.sh
