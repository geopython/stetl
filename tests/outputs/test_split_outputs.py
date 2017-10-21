import os
import sys

from stetl.etl import ETL
from stetl.outputs.standardoutput import StandardOutput
from stetl.splitter import Splitter
from tests.stetl_test_case import StetlTestCase

class SplitterMultiOutputTest(StetlTestCase):
    """Unit tests for Splitter"""
    pass

    def setUp(self):
        super(SplitterMultiOutputTest, self).setUp()

        # Initialize Stetl
        curr_dir = os.path.dirname(os.path.realpath(__file__))
        cfg_dict = {'config_file': os.path.join(curr_dir, 'configs/splittermultioutput.cfg')}
        self.etl = ETL(cfg_dict)

    def test_instance(self):
        chain = StetlTestCase.get_chain(self.etl)

        splitter_comp = chain.first_comp.next
        self.assertTrue(isinstance(splitter_comp, Splitter))

        # The next is a list of multiple Outputs
        self.assertEqual(len(splitter_comp.next), 2)
        self.assertTrue(isinstance(splitter_comp.next[0], StandardOutput))
        self.assertTrue(isinstance(splitter_comp.next[1], StandardOutput))

    def test_execute(self):
        chain = StetlTestCase.get_chain(self.etl)
        chain.run()

        # Result should be merged lines from both files
        result = sys.stdout.getvalue().split('\n')

        # Strip empty lines
        result = [s for s in result if (s or len(s) > 0)]

        # Total should be twice of linecount non-empty lines in input file
        self.assertEqual(len(result), 36)
