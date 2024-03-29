API and Code
============

Below is the API documention for the the Stetl Python code.

Main Entry Points
-----------------

There are several entry points through which Stetl can be called.
The most common is to use the commandline script `bin/stetl`. This command should
be available after doing an install.

In some contexts like integrations
you may want to call Stetl via Python. The entries are then.

.. automodule:: stetl.main
   :members:

.. automodule:: stetl.etl
   :members:

Core Framework
--------------

The core framework is directly under the directory `src/stetl`.
Below are the main seven classes. Their interrelation is as follows:

One or more :class:`stetl.chain.Chain` objects are built from
a Stetl ETL configuration via the :class:`stetl.factory.Factory` class.
A :class:`stetl.chain.Chain` consists of a set of connected :class:`stetl.component.Component` objects.
A :class:`stetl.component.Component` is either an :class:`stetl.input.Input`, an :class:`stetl.output.Output`
or a :class:`stetl.filter.Filter`. Data and status flows as :class:`stetl.packet.Packet` objects
from an :class:`stetl.input.Input` via zero or more :class:`stetl.filter.Filter` objects to a final :class:`stetl.output.Output`.

As a trivial example: an :class:`stetl.input.Input` could be an XML file, a :class:`stetl.filter.Filter` could represent
an XSLT file and an :class:`stetl.output.Output` a PostGIS database. This is effected by specialized classes in
the subpackages inputs, filters, and outputs. New in 1.1.0: :class:`stetl.Splitter` to split data to multiple Outputs
and :class:`stetl.Merger` to combine multiple `Inputs`.

.. automodule:: stetl.factory
   :members:

.. automodule:: stetl.component
   :members:

.. automodule:: stetl.chain
   :members:

.. automodule:: stetl.packet
   :members:

.. automodule:: stetl.input
   :members:
   :show-inheritance:

.. automodule:: stetl.output
   :members:
   :show-inheritance:

.. automodule:: stetl.filter
   :members:
   :show-inheritance:

.. automodule:: stetl.splitter
   :members:
   :show-inheritance:

.. automodule:: stetl.merger
   :members:
   :show-inheritance:

Components: Inputs
------------------

.. automodule:: stetl.inputs.dbinput
   :members:
   :show-inheritance:

.. automodule:: stetl.inputs.fileinput
   :members:
   :show-inheritance:

.. automodule:: stetl.inputs.httpinput
   :members:
   :show-inheritance:

.. automodule:: stetl.inputs.ogrinput
   :members:
   :show-inheritance:

.. automodule:: stetl.inputs.deegreeinput
   :members:
   :show-inheritance:

Components: Filters
-------------------

.. automodule:: stetl.filters.xsltfilter
   :members:
   :show-inheritance:

.. automodule:: stetl.filters.xmlassembler
   :members:
   :show-inheritance:

.. automodule:: stetl.filters.xmlelementreader
   :members:
   :show-inheritance:

.. automodule:: stetl.filters.xmlvalidator
   :members:
   :show-inheritance:

.. automodule:: stetl.filters.sieve
   :members:
   :show-inheritance:

.. automodule:: stetl.filters.stringfilter
   :members:
   :show-inheritance:

.. automodule:: stetl.filters.templatingfilter
   :members:
   :show-inheritance:

.. automodule:: stetl.filters.gmlfeatureextractor
   :members:
   :show-inheritance:

.. automodule:: stetl.filters.gmlsplitter
   :members:
   :show-inheritance:

.. automodule:: stetl.filters.formatconverter
   :members:
   :show-inheritance:

.. automodule:: stetl.filters.execfilter
   :members:
   :show-inheritance:

.. automodule:: stetl.filters.nullfilter
   :members:
   :show-inheritance:

.. automodule:: stetl.filters.packetbuffer
   :members:
   :show-inheritance:

.. automodule:: stetl.filters.packetwriter
   :members:
   :show-inheritance:

.. automodule:: stetl.filters.regexfilter
   :members:
   :show-inheritance:

.. automodule:: stetl.filters.fileextractor
   :members:
   :show-inheritance:

.. automodule:: stetl.filters.vsifilter
   :members:
   :show-inheritance:

NB: `stetl.filters.zipfileextractor` is deprecated.
`ZipFileExtractor` is now part of module `stetl.filters.fileextractor`.

Components: Outputs
-------------------

.. automodule:: stetl.outputs.fileoutput
   :members:
   :show-inheritance:

.. automodule:: stetl.outputs.standardoutput
   :members:
   :show-inheritance:

.. automodule:: stetl.outputs.httpoutput
   :members:
   :show-inheritance:

.. automodule:: stetl.outputs.ogroutput
   :members:
   :show-inheritance:

.. automodule:: stetl.outputs.execoutput
   :members:
   :show-inheritance:

.. automodule:: stetl.outputs.dboutput
   :members:
   :show-inheritance:

.. automodule:: stetl.outputs.wfsoutput
   :members:
   :show-inheritance:

.. automodule:: stetl.outputs.deegreeoutput
   :members:
   :show-inheritance:






