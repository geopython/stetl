import os
import sys

from stetl.etl import ETL
from stetl.packet import Packet
from stetl.inputs.fileinput import LineStreamerFileInput
from tests.stetl_test_case import StetlTestCase

class LineStreamerFileInputTest(StetlTestCase):
    """Unit tests for LineStreamerFileInput"""
    pass

    def setUp(self):
        super(LineStreamerFileInputTest, self).setUp()

        # Initialize Stetl
        curr_dir = os.path.dirname(os.path.realpath(__file__))
        cfg_dict = {'config_file': os.path.join(curr_dir, 'configs/linestreamerfileinput.cfg')}
        self.etl = ETL(cfg_dict)
    
    def test_class(self):
        chain = StetlTestCase.get_chain(self.etl)
        section = StetlTestCase.get_section(chain)
        class_name = self.etl.configdict.get(section, 'class')
        
        self.assertEqual('inputs.fileinput.LineStreamerFileInput', class_name)
    
    def test_instance(self):
        chain = StetlTestCase.get_chain(self.etl)
        
        self.assertTrue(isinstance(chain.first_comp, LineStreamerFileInput))
    
    def test_execute(self):
        chain = StetlTestCase.get_chain(self.etl)
        chain.run()
        
        result = sys.stdout.getvalue().split('\n')
        
        # The total number of lines written to stdout is twice the number of lines in the text file,
        # because the print statement is used. This causes an extra linebreak to written. The number
        # to assert, is even one higher, because of the split statement above. The last "line" is an
        # empty string.
        self.assertEqual(len(result), 37)
