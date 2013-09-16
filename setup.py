import logging
import sys
from setuptools import setup, find_packages

# Have to do this after importing setuptools, which monkey patches distutils.
from distutils.extension import Extension

logging.basicConfig()
log = logging.getLogger()

# Parse the version from the stetl module.
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

requirements = [
    'psycopg2',
    'lxml',
    'GDAL'
]

if sys.version_info < (2, 7):
    requirements.append('argparse')

setup(
    name='Stetl',
    version=version,
    description="Stetl provides transformation for spatial data",
    license='GNU GPL v3',
    keywords='etl xsl gdal gis vector feature data',
    author='Just van den Broecke',
    author_email='justb4@gmail.com',
    maintainer='Just van den Broecke',
    maintainer_email='justb4@gmail.com',
    url='http://github.com/justb4/stetl',
    long_description=readme + "\n" + changes + "\n" + credits,
    packages=find_packages(exclude=['tests']),
    namespace_packages=['stetl'],
    include_package_data=True,
    package_data={'': ['*.cfg','*.xml','*.gml']},
    scripts=['bin/stetl'],
    install_requires=requirements,
    tests_require=['nose'],
    test_suite='nose.collector',
    classifiers=[
        'Development Status :: 4 - Beta',
        'Environment :: Console',
        'Intended Audience :: Developers',
        'Intended Audience :: Science/Research',
        'License :: OSI Approved :: GNU General Public License v3 (GPLv3)',
        'Operating System :: OS Independent',
        'Programming Language :: Python :: 2',
        'Topic :: Scientific/Engineering :: GIS',
    ]
)
