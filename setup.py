import logging
import os
from setuptools import setup, find_packages

# To publish: python setup.py sdist upload -r pypi

# Have to do this after importing setuptools, which monkey patches distutils.
# from distutils.extension import Extension

logging.basicConfig()
log = logging.getLogger()

# Parse the version from the stetl module.
version = ''
with open('stetl/version.py', 'r') as f:
    for line in f:
        if line.find("__version__") >= 0:
            version = line.split("=")[1].strip()
            version = version.strip('"')
            version = version.strip("'")
            continue

with open('VERSION.txt', 'w') as f:
    f.write(version)

# Get long description text from README.rst.
with open('README.md', 'r') as f:
    readme = f.read()

with open('CREDITS.txt', 'r') as f:
    credits = f.read()

with open('CHANGES.txt', 'r') as f:
    changes = f.read()

requirements_file = os.environ.get( 'REQUIREMENTS_FILE', 'requirements-main.txt' )

with open(requirements_file) as f:
    requirements = f.read().splitlines()

setup(
    name='Stetl',
    version=version,
    description="Transformation and conversion framework (ETL) mainly for geospatial data",
    license='GNU GPL v3',
    keywords='etl xsl gdal gis vector feature data gml xml',
    author='Just van den Broecke',
    author_email='justb4@gmail.com',
    maintainer='Just van den Broecke',
    maintainer_email='justb4@gmail.com',
    url='http://github.com/geopython/stetl',
    long_description=readme + "\n" + changes + "\n" + credits,
    long_description_content_type="text/markdown",
    packages=find_packages(exclude=['tests']),
    namespace_packages=['stetl'],
    include_package_data=True,
    package_data={'': ['*.cfg','*.xml','*.gml']},
    scripts=['bin/stetl'],
    install_requires=requirements,
    tests_require=['nose2'],
    test_suite='nose2.collector.collector',
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Environment :: Console',
        'Intended Audience :: Developers',
        'Intended Audience :: Science/Research',
        'License :: OSI Approved :: GNU General Public License v3 (GPLv3)',
        'Operating System :: OS Independent',
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        'Topic :: Scientific/Engineering :: GIS',
    ],
    zip_safe=True
)
