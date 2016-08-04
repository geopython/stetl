import os
import sys

from stetl.etl import ETL
from stetl.packet import Packet
from stetl.inputs.fileinput import JsonFileInput
from tests.stetl_test_case import StetlTestCase

class JsonFileInputTest(StetlTestCase):
    """Unit tests for JsonFileInput"""
    pass

    def setUp(self):
        super(JsonFileInputTest, self).setUp()

        # Initialize Stetl
        curr_dir = os.path.dirname(os.path.realpath(__file__))
        cfg_dict = {'config_file': os.path.join(curr_dir, 'configs/jsonfileinput.cfg')}
        self.etl = ETL(cfg_dict)
    
    def test_class(self):
        chain = StetlTestCase.get_chain(self.etl)
        section = StetlTestCase.get_section(chain)
        class_name = self.etl.configdict.get(section, 'class')
        
        self.assertEqual('inputs.fileinput.JsonFileInput', class_name)
    
    def test_instance(self):
        chain = StetlTestCase.get_chain(self.etl)
        
        self.assertTrue(isinstance(chain.first_comp, JsonFileInput))
    
    def test_execute(self):
        chain = StetlTestCase.get_chain(self.etl)
        chain.first_comp.do_init()
        packet = Packet()
        packet.init()
        packet.component = chain.first_comp
        chain.first_comp.before_invoke(packet)
        packet = chain.first_comp.invoke(packet)
        
        self.assertIsNotNone(packet.data)
        self.assertIsInstance(packet.data, dict)
        self.assertTrue('menu' in packet.data)
        self.assertIsNotNone(packet.data['menu'])
        
        mydict = packet.data['menu']
        self.assertEqual(len(mydict), 3)
        self.assertTrue('id' in mydict)
        self.assertTrue('value' in mydict)
        self.assertTrue('popup' in mydict)
