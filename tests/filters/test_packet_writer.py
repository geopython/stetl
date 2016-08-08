import os

from stetl.etl import ETL
from stetl.filters.packetwriter import PacketWriter
from tests.stetl_test_case import StetlTestCase

class PacketWriterTest(StetlTestCase):
    """Unit tests for PacketWriter"""

    def setUp(self):
        super(PacketWriterTest, self).setUp()

        # Initialize Stetl
        curr_dir = os.path.dirname(os.path.realpath(__file__))
        cfg_dict = {'config_file': os.path.join(curr_dir, 'configs/packetwriter.cfg')}
        self.etl = ETL(cfg_dict)
    
    def test_class(self):
        chain = StetlTestCase.get_chain(self.etl)
        section = StetlTestCase.get_section(chain, 1)
        class_name = self.etl.configdict.get(section, 'class')
        
        self.assertEqual('filters.packetwriter.PacketWriter', class_name)
    
    def test_instance(self):
        chain = StetlTestCase.get_chain(self.etl)

        self.assertTrue(isinstance(chain.get_by_index(1), PacketWriter))
        
    def test_execute(self):
        chain = StetlTestCase.get_chain(self.etl)
        chain.run()

        # Check if temp file exists
        section = StetlTestCase.get_section(chain, 1)
        file_path = self.etl.configdict.get(section, 'file_path')
        self.assertTrue(os.path.exists(file_path))
        
        # Compare temp file to input file byte by byte
        section = StetlTestCase.get_section(chain)
        orig_file_path = self.etl.configdict.get(section, 'file_path')
        with open(file_path, 'rb') as f:
            file = f.read()
        with open(orig_file_path, 'rb') as f:
            orig_file = f.read()
        self.assertEqual(file, orig_file)
        
        # Remove temp file
        os.remove(file_path)
