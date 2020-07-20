# Testing Stetl

Testing is done with Python unittest and run with 'nose2',
see http://nose2.readthedocs.io/en/latest/

## Unit Testing 

To install and run with nose2:

	pip install nose2

To execute nose2:

	nose2 [options]

Coverage plugin:

	pip install cov-core

Or install all dependencies at once (in root dir):

	pip3 install -r requirements-dev.txt 
		
Execution with coverage (from root dir):

	nose2 --with-coverage
	nose2 --with-coverage -coverage-report html

The test coverage is written to the dir htmlcov.

Mock objects: mock

	pip install mock

More information: http://www.voidspace.org.uk/python/mock/

When executing nose2, all directories are scanned for tests. See the nose2 documentation how this is done.
Regarding the coverage: if you specify the tests directory, only the coverage of the unit tests themselves is reported.
If you would like to see coverage for the source files as well, you need to execute nose2 from the Stetl root dir.

## Unit Testing within Docker Container

In root dir:

	docker build -t geopython/stetltest:latest -f Dockerfile.test .
	
Run `nose2` within Docker Image:

	docker run geopython/stetltest:latest

See also the [.travis.yml](../.travis.yml) file.
	