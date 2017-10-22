import os
import sys

from stetl.etl import ETL
from stetl.inputs.fileinput import LineStreamerFileInput
from stetl.filters.nullfilter import NullFilter
from stetl.outputs.standardoutput import StandardOutput
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
        # Chain #1 - Simple Case
        chain = StetlTestCase.get_chain(self.etl)

        merger_comp = chain.first_comp
        self.assertTrue(isinstance(merger_comp, Merger))
        self.assertEqual(len(merger_comp.children), 2)
        self.assertTrue(isinstance(merger_comp.children[0][0], LineStreamerFileInput),
                        "Next is not LineStreamerFileInput")
        self.assertTrue(isinstance(merger_comp.children[1][0], LineStreamerFileInput),
                        "Next is not LineStreamerFileInput")
        self.assertTrue(isinstance(merger_comp.children[0][1], LineStreamerFileInput),
                        "Next is not LineStreamerFileInput")
        self.assertTrue(isinstance(merger_comp.children[1][1], LineStreamerFileInput),
                        "Next is not LineStreamerFileInput")
        self.assertTrue(isinstance(merger_comp.children[0][1].next, StandardOutput),
                        "Next is not StandardOutput")
        self.assertTrue(isinstance(merger_comp.children[1][1].next, StandardOutput),
                        "Next is not StandardOutput")

        # Flag for End-of-Stream 2 subcomps
        self.assertEqual(merger_comp.end_count, 2)

        # Chain #2 - SubChain Case
        chain = StetlTestCase.get_chain(self.etl, index=1)

        merger_comp = chain.first_comp
        children = merger_comp.children
        self.assertTrue(isinstance(merger_comp, Merger))
        self.assertEqual(len(merger_comp.children), 2, "Child count is not 2")
        self.assertTrue(isinstance(merger_comp.first(children[0]), LineStreamerFileInput),
                        "Next is not LineStreamerFileInput")
        self.assertTrue(isinstance(merger_comp.first(children[1]), LineStreamerFileInput),
                        "Next is not LineStreamerFileInput")
        self.assertTrue(isinstance(merger_comp.children[0][0].next, NullFilter),
                        "Next is not NullFilter")
        self.assertTrue(isinstance(merger_comp.first(children[1]).next, NullFilter),
                        "Next is not NullFilter")
        self.assertTrue(isinstance(merger_comp.last(children[1]).next, StandardOutput),
                        "Next is not StandardOutput")
        self.assertTrue(isinstance(merger_comp.children[1][1].next, StandardOutput),
                        "Next is not StandardOutput")

        # Flag for End-of-Stream 2 subcomps
        self.assertEqual(merger_comp.end_count, 2)

    def test_execute(self):
        run_count = 0
        for index in [0, 1]:
            chain = StetlTestCase.get_chain(self.etl, index=index)
            chain.run()

            merger_comp = chain.first_comp

            # Flag for End-of-Stream 2 subcomps
            self.assertEqual(merger_comp.end_count, 0)

            # Result should be merged lines from both files
            result = sys.stdout.getvalue().split('\n')

            # Strip empty lines
            result = [s for s in result if (s or len(s) > 0)]

            # Total should be sum of linecount non-empty lines in input files
            # each run increases line count hence multiply by run_count
            run_count += 1
            self.assertEqual(len(result), 28 * run_count)
