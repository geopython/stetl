import os
import sys

from stetl.etl import ETL
from stetl.inputs.fileinput import LineStreamerFileInput
from stetl.merger import Merger
from tests.stetl_test_case import StetlTestCase

class MergerMultiInputTest(StetlTestCase):
    """Unit tests for Merger"""
    pass

    def setUp(self):
        super(MergerMultiInputTest, self).setUp()

        # Initialize Stetl
        curr_dir = os.path.dirname(os.path.realpath(__file__))
        cfg_dict = {'config_file': os.path.join(curr_dir, 'configs/mergermultiinput.cfg')}
        self.etl = ETL(cfg_dict)

    def test_instance(self):
        chain = StetlTestCase.get_chain(self.etl)

        merger_comp = chain.first_comp
        self.assertTrue(isinstance(merger_comp, Merger))
        self.assertEqual(len(merger_comp.children), 2)
        self.assertTrue(isinstance(merger_comp.children[0], LineStreamerFileInput))
        self.assertTrue(isinstance(merger_comp.children[1], LineStreamerFileInput))

        # Flag for End-of-Stream 2 subcomps
        self.assertEqual(merger_comp.end_count, 2)

    def test_execute(self):
        chain = StetlTestCase.get_chain(self.etl)
        chain.run()

        merger_comp = chain.first_comp
        
        # Flag for End-of-Stream 2 subcomps
        self.assertEqual(merger_comp.end_count, 0)

        # Result should be merged lines from both files
        result = sys.stdout.getvalue().split('\n')

        # Strip empty lines
        result = [s for s in result if (s or len(s) > 0)]

        # Total should be sum of linecount non-empty lines in input files
        self.assertEqual(len(result), 28)
