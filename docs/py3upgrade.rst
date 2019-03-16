Upgrade to python 3
===================

Stetl development started in python 2. With `PEP 373
<https://legacy.python.org/dev/peps/pep-0373/>`_ the EOL of python 2.7 was annouced and python 2
will not be officialy supported after 2020. Stetl was therefore upgraded to python 3.

Python 3
--------
Work started early 2019 to upgrade ``stetl`` from python 2 to python 3. The last version of stetl
that supports python 2 is version 1.3. This version *might* receive quick fixes and updates, but
users are encouraged to upgrade to stetl version 2 and use python 3.

For the full discussion on the python 2 to python 3 migration: see the `conversation in pull
request #81 <https://github.com/geopython/stetl/pull/81>`_ on the github repository.

Important changes for developers
--------------------------------
Python 2 and 3 are very simular, but there are a couple of important changes that developers need
to keep in mind and are worth mentioning:

- stetl 2 supports python 3.4.2 and higher (so unfortunately no `f strings <https://www.python.org/dev/peps/pep-0498/>`_)
- python 3 uses unicode strings, meaning encoding/decoding is a bit different
- ``stringIO`` and ``cstringIO`` were moved around
- slight syntax change on calling ``next()`` for iterators
- update on ``import`` statements
- differences in ``urllib`` to make http-calls (although `issue 80 <https://github.com/geopython/stetl/issues/80>`_ might change it to the `requests` library).

Important changes for users
---------------------------

The specification of the tool chain uses a configuration file. You can use the inputs, filters, and
outputs that are provided by stetl, or write your own. If you use the stetl tools, you *must*
specify the ``stelt.`` prefix in the class declaration. For example before version 2 the input XML
file was specified as ::

    [input_xml_file]
    class = inputs.fileinput.XmlFileInput
    file_path = input/cities.xml

for version 2 this is changed to ::

    [input_xml_file]
    class = stetl.inputs.fileinput.XmlFileInput
    file_path = input/cities.xml

Note the extr ``stetl.`` part in the ``class`` specification.

