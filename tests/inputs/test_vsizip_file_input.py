import os
import sys

from stetl.etl import ETL
from stetl.inputs.fileinput import VsiZipFileInput
from tests.stetl_test_case import StetlTestCase

class VsiZipFileInputTest(StetlTestCase):
    """Unit tests for VsiZipFileInput"""

    def setUp(self):
        super(VsiZipFileInputTest, self).setUp()

        # Initialize Stetl
        curr_dir = os.path.dirname(os.path.realpath(__file__))
        cfg_dict = {'config_file': os.path.join(curr_dir, 'configs/vsizipfileinput.cfg')}
        self.etl = ETL(cfg_dict)
    
    def test_class(self):
        chain = StetlTestCase.get_chain(self.etl)
        section = StetlTestCase.get_section(chain)
        class_name = self.etl.configdict.get(section, 'class')
        
        self.assertEqual('stetl.inputs.fileinput.VsiZipFileInput', class_name)
    
    def test_instance(self):
        chain = StetlTestCase.get_chain(self.etl)
        
        self.assertTrue(isinstance(chain.first_comp, VsiZipFileInput))
    
    def test_execute(self):
        chain = StetlTestCase.get_chain(self.etl)
        chain.run()
        
        result = sys.stdout.getvalue().strip().split('\n')
        self.assertEqual(len(result), 40)
                                    
    def test_zip_name_filter(self):
        chain = StetlTestCase.get_chain(self.etl, 1)
        chain.run()
        
        result = sys.stdout.getvalue().strip().split('\n')
        self.assertEqual(len(result), 18)

    def test_xml_name_filter(self):
        chain = StetlTestCase.get_chain(self.etl, 2)
        chain.run()

        result = sys.stdout.getvalue().strip().split('\n')
        self.assertEqual(len(result), 18)

    def test_xml_re_name_filter(self):
        chain = StetlTestCase.get_chain(self.etl, 3)
        chain.run()

        result = sys.stdout.getvalue().strip().split('\n')
        self.assertEqual(len(result), 2)

    def test_xml_single_name__nested_filter(self):
        chain = StetlTestCase.get_chain(self.etl, 4)
        chain.run()

        result = sys.stdout.getvalue().strip().split('\n')
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0], '/vsizip/{tests/data/vsizipinput.zip}/Leveringsdocument-BAG-Extract.xml')

    def test_xml_single_name_nested_filter(self):
        chain = StetlTestCase.get_chain(self.etl, 5)
        chain.run()

        result = sys.stdout.getvalue().strip().split('\n')
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0], '/vsizip/{/vsizip/{tests/data/vsizipinput.zip}/9999WPL15092020.zip}/0221WPL15092020-000001.xml')

    def test_read_xml_from_vsi_path(self):
        chain = StetlTestCase.get_chain(self.etl, 6)
        chain.run()

        result = sys.stdout.getvalue()
        self.assertEqual(len(result), 25152)
        # self.assertEqual(result[0], 'xml stuff')
