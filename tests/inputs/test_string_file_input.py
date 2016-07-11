import os
import sys

from stetl.etl import ETL
from stetl.packet import Packet
from stetl.inputs.fileinput import StringFileInput
from tests.stetl_test_case import StetlTestCase

class StringFileInputTest(StetlTestCase):
    """Unit tests for StringFileInput"""

    def setUp(self):
        super(StringFileInputTest, self).setUp()

        # Initialize Stetl
        curr_dir = os.path.dirname(os.path.realpath(__file__))
        cfg_dict = {'config_file': os.path.join(curr_dir, 'configs/stringfileinput.cfg')}
        self.etl = ETL(cfg_dict)
    
    def test_class(self):
        chain = StetlTestCase.get_chain(self.etl)
        section = StetlTestCase.get_section(chain)
        class_name = self.etl.configdict.get(section, 'class')
        
        self.assertEqual('inputs.fileinput.StringFileInput', class_name)
    
    def test_instance(self):
        chain = StetlTestCase.get_chain(self.etl)
        
        self.assertTrue(isinstance(chain.first_comp, StringFileInput))
    
    def test_execute(self):
        # Read content of input file
        chain = StetlTestCase.get_chain(self.etl)
        section = StetlTestCase.get_section(chain)
        fn = self.etl.configdict.get(section, 'file_path')
        with open(fn, 'r') as f:
            contents = f.read()
    
        # Invoke first component of chain
        chain.first_comp.do_init()
        packet = Packet()
        packet.init()
        packet.component = chain.first_comp
        chain.first_comp.before_invoke(packet)
        packet = chain.first_comp.invoke(packet)
        
        self.assertEqual(packet.data, contents)
        
    def test_format_args(self):
        chain = StetlTestCase.get_chain(self.etl, 1)
        chain.first_comp.do_init()
        packet = Packet()
        packet.init()
        packet.component = chain.first_comp
        chain.first_comp.before_invoke(packet)
        packet = chain.first_comp.invoke(packet)

        self.assertEqual(packet.data, 'Hello NLExtract!')
