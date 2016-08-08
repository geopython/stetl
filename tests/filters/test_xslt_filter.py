import os
import re
import sys

from stetl.etl import ETL
from stetl.filters.xsltfilter import XsltFilter
from stetl.filters.packetbuffer import PacketBuffer
from tests.stetl_test_case import StetlTestCase

class XsltFilterTest(StetlTestCase):
    """Unit tests for XsltFilter"""

    def setUp(self):
        super(XsltFilterTest, self).setUp()

        # Initialize Stetl
        curr_dir = os.path.dirname(os.path.realpath(__file__))
        cfg_dict = {'config_file': os.path.join(curr_dir, 'configs/xsltfilter.cfg')}
        self.etl = ETL(cfg_dict)
    
    def test_class(self):
        chain = StetlTestCase.get_chain(self.etl)
        section = StetlTestCase.get_section(chain, 1)
        class_name = self.etl.configdict.get(section, 'class')
        
        self.assertEqual('filters.xsltfilter.XsltFilter', class_name)
    
    def test_instance(self):
        chain = StetlTestCase.get_chain(self.etl)

        self.assertTrue(isinstance(chain.get_by_index(1), XsltFilter))
        
    def test_execute(self):
        chain = StetlTestCase.get_chain(self.etl)
        chain.run()

        buffer_filter = chain.get_by_class(PacketBuffer)
        packet_list = buffer_filter.packet_list
        self.assertEqual(len(packet_list), 1)

        # Inspect the result
        result = sys.stdout.getvalue().strip().split('\n')
        self.assertEqual(len(result), 6)
        
        pattern = r'<funcgeb id="[^"]+"/>'
        for i in range(2, 5):
            self.assertIsNotNone(re.match(pattern, result[i].strip()))
        self.assertTrue(result[1].strip().startswith('<dummy '))
        self.assertEqual(result[5].strip(), '</dummy>')
        