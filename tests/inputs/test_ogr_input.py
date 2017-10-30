import os
import sys

from stetl.etl import ETL
from stetl.inputs.ogrinput import OgrInput
from tests.stetl_test_case import StetlTestCase

class OgrInputTest(StetlTestCase):
    """Unit tests for OgrInput"""
    pass

    def setUp(self):
        super(OgrInputTest, self).setUp()

        # Initialize Stetl
        curr_dir = os.path.dirname(os.path.realpath(__file__))
        cfg_dict = {'config_file': os.path.join(curr_dir, 'configs/ogrinput.cfg')}
        self.etl = ETL(cfg_dict)
    
    def test_class(self):
        chain = StetlTestCase.get_chain(self.etl)
        section = StetlTestCase.get_section(chain)
        class_name = self.etl.configdict.get(section, 'class')
        
        self.assertEqual('inputs.ogrinput.OgrInput', class_name)
    
    def test_instance(self):
        chain = StetlTestCase.get_chain(self.etl)
        
        self.assertTrue(isinstance(chain.first_comp, OgrInput))
    
    def test_execute(self):
        chain = StetlTestCase.get_chain(self.etl)
        chain.run()
        
        result = sys.stdout.getvalue().strip().split('\n')
        self.assertEqual(len(result), 3)
