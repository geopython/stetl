import os
import sys

from stetl.etl import ETL
from stetl.outputs.standardoutput import StandardOutput
from tests.stetl_test_case import StetlTestCase

class StandardOutputTest(StetlTestCase):
    """Unit tests for StandardOutput"""

    def setUp(self):
        super(StandardOutputTest, self).setUp()

        # Initialize Stetl
        curr_dir = os.path.dirname(os.path.realpath(__file__))
        cfg_dict = {'config_file': os.path.join(curr_dir, 'configs/standardoutput.cfg')}
        self.etl = ETL(cfg_dict)
    
    def test_class(self):
        chain = StetlTestCase.get_chain(self.etl)
        section = StetlTestCase.get_section(chain, -1)
        class_name = self.etl.configdict.get(section, 'class')
        
        self.assertEqual('outputs.standardoutput.StandardOutput', class_name)
    
    def test_instance(self):
        chain = StetlTestCase.get_chain(self.etl)

        self.assertTrue(isinstance(chain.cur_comp, StandardOutput))
    
    def test_execute(self):
        # Read content of input file
        chain = StetlTestCase.get_chain(self.etl)
        section = StetlTestCase.get_section(chain)
        fn = self.etl.configdict.get(section, 'file_path')
        with open(fn, 'r') as f:
            contents = f.read()
        
        self.etl.run()
        
        self.assertGreater(sys.stdout.getvalue(), 0)
        # Assert includes last linebreak from stdout, due to print function
        self.assertEqual(sys.stdout.getvalue(), contents + '\n')
