API and Code
============

Below is the API documention for the the Stetl Python code.

Main Entry Points
-----------------

There are two main entry points through which Stetl can be called.

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
the subpackages inputs, filters, and outputs.

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

.. automodule:: stetl.output
   :members:

.. automodule:: stetl.filter
   :members:








