Testing is done with Python unittest and run with 'nose2',
see http://nose2.readthedocs.io/en/latest/

To install and run with nose2:
pip install nose2

To execute nose2:
nose2 [options]

If you execute nose2 from another directory, it is best to specify the tests directory, otherwise it can discover potential tests in other directories as well.
For example to run nose2 from the parent directory (Stetl root), execute:
nose2 [options] tests
