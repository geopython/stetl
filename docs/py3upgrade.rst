.. _py3upgrade:

Upgrade to Python 3
===================

Stetl development started in Python 2. With `PEP 373
<https://legacy.python.org/dev/peps/pep-0373/>`_ the EOL of python 2.7 was announced and python 2
will not be officialy supported after 2020. Stetl was therefore upgraded to Python 3.

Python 3
--------

Work started early 2019 to upgrade ``Stetl`` from Python 2 to Python 3. The last version of Stetl
that supports Python 2 is version 1.3. This version *might* receive quick fixes and updates, but
users are encouraged to upgrade to Stetl version 2 or higher and thus use Python 3.

For the full discussion on the Python 2 to Python 3 migration: see the `conversation in pull
request #81 <https://github.com/geopython/stetl/pull/81>`_ within the GitHub repository.

Important changes for developers
--------------------------------

Python 2 and 3 are very similar, but there are a couple of important changes that developers need
to keep in mind and are worth mentioning:

- Stetl 2 supports Python 3.4.2 and higher (so unfortunately no `f strings <https://www.python.org/dev/peps/pep-0498/>`_)
- Python 3 uses Unicode strings, meaning encoding/decoding is a bit different
- ``stringIO`` and ``cstringIO`` were moved around
- slight syntax change on calling ``next()`` for iterators
- update on ``import`` statements
- differences in ``urllib`` to make http-calls (although `issue 80 <https://github.com/geopython/stetl/issues/80>`_ might change it to the `requests` library).

Important changes for users
---------------------------

The specification of the Stetl tool chain uses a configuration file. You can use the Inputs, Filters, and
Outputs that are provided by Stetl, or write your own. If you use  Stetl Components in your configuration, you *must*
specify the ``stetl.`` package prefix in the class specification. For example before Stetl version 2 the input XML
file was specified as ::

    [input_xml_file]
    class = inputs.fileinput.XmlFileInput
    file_path = input/cities.xml

for Stetl version 2 this is changed to ::

    [input_xml_file]
    class = stetl.inputs.fileinput.XmlFileInput
    file_path = input/cities.xml

Note the extra ``stetl.`` part in the ``class`` specification.
