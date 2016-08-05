import os
import re
import sys

from stetl.etl import ETL
from stetl.filters.xmlelementreader import XmlElementReader
from tests.stetl_test_case import StetlTestCase

class XmlElementReaderTest(StetlTestCase):
    """Unit tests for XmlElementReader"""

    def setUp(self):
        super(XmlElementReaderTest, self).setUp()

        # Initialize Stetl
        curr_dir = os.path.dirname(os.path.realpath(__file__))
        cfg_dict = {'config_file': os.path.join(curr_dir, 'configs/xmlelementreader.cfg')}
        self.etl = ETL(cfg_dict)
    
    def test_class(self):
        chain = StetlTestCase.get_chain(self.etl)
        section = StetlTestCase.get_section(chain, 1)
        class_name = self.etl.configdict.get(section, 'class')
        
        self.assertEqual('filters.xmlelementreader.XmlElementReader', class_name)
    
    def test_instance(self):
        chain = StetlTestCase.get_chain(self.etl)

        self.assertTrue(isinstance(chain.first_comp.next, XmlElementReader))
        
    def check_execution_result(self, chain, result, with_namespace):        
        section = StetlTestCase.get_section(chain, 1)
        element_tags = self.etl.configdict.get(section, 'element_tags')
        pattern = "<Element %s%s " % ('{[^}]+}' if with_namespace else '', element_tags)
        for elem in result:
            self.assertIsNotNone(re.match(pattern, elem))
        
    def test_execute(self):
        chain = StetlTestCase.get_chain(self.etl)
        chain.run()

        # Check the number of elements
        result = sys.stdout.getvalue().strip().split('\n')
        self.assertEqual(len(result), 3)
        
        # Check the actual elements
        self.check_execution_result(chain, result, True)
        
    def test_strip_namespaces(self):
        chain = StetlTestCase.get_chain(self.etl, 1)
        chain.run()
        
        # Check the number of elements
        result = sys.stdout.getvalue().strip().split('\n')
        self.assertEqual(len(result), 3)
        
        # Check the actual elements
        self.check_execution_result(chain, result, False)
        
    def test_no_namespace(self):
        chain = StetlTestCase.get_chain(self.etl, 2)
        chain.run()
        
        # Check the number of elements
        result = sys.stdout.getvalue().strip().split('\n')
        self.assertEqual(len(result), 3)
        
        # Check the actual elements
        self.check_execution_result(chain, result, False)
