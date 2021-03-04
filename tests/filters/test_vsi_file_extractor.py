import mock
import os

from stetl.etl import ETL
from stetl.filters.fileextractor import VsiFileExtractor
from tests.stetl_test_case import StetlTestCase

class VsiFileExtractorTest(StetlTestCase):
    """Unit tests for VsiFileExtractor plus deprecation"""

    def setUp(self):
        super(VsiFileExtractorTest, self).setUp()

        # Initialize Stetl
        self.curr_dir = os.path.dirname(os.path.realpath(__file__))
        cfg_dict = {'config_file': os.path.join(self.curr_dir, 'configs/vsifileextractor.cfg')}
        self.etl = ETL(cfg_dict)
    
    def test_class(self):
        chain = StetlTestCase.get_chain(self.etl)
        section = StetlTestCase.get_section(chain, 1)
        class_name = self.etl.configdict.get(section, 'class')
        self.assertEqual('stetl.filters.fileextractor.VsiFileExtractor', class_name)

    def test_instance(self):
        chain = StetlTestCase.get_chain(self.etl)

        self.assertTrue(isinstance(chain.first_comp.next, VsiFileExtractor))
        
    @mock.patch('stetl.filters.fileextractor.VsiFileExtractor.after_chain_invoke', autospec=True)
    def test_execute_gml(self, mock_after_chain_invoke):
        chain = StetlTestCase.get_chain(self.etl)
        chain.run()

        # ZIP file contains two GML files, both should be extracted; count is 4 because of final
        # call, so the VsiFileExtractor can indicate that no more files can be found.
        self.assertTrue(mock_after_chain_invoke.called)
        self.assertEqual(4, mock_after_chain_invoke.call_count)

        # Check if temp file exists
        section = StetlTestCase.get_section(chain, 1)
        file_path = self.etl.configdict.get(section, 'file_path')
        self.assertTrue(os.path.exists(file_path))
        os.remove(file_path)

    @mock.patch('stetl.filters.fileextractor.VsiFileExtractor.after_chain_invoke', autospec=True)
    def test_execute_xml(self, mock_after_chain_invoke):
        chain = StetlTestCase.get_chain(self.etl, index=1)
        chain.run()

        # ZIP file contains one XML file and is extracted; count is 2 because of final
        # call, so the VsiFileExtractor can indicate that no more files can be found.
        self.assertTrue(mock_after_chain_invoke.called)
        self.assertEqual(2, mock_after_chain_invoke.call_count)

        # Check if temp file exists
        section = StetlTestCase.get_section(chain, 1)
        file_path = self.etl.configdict.get(section, 'file_path')
        self.assertTrue(os.path.exists(file_path))
        os.remove(file_path)

    @mock.patch('stetl.filters.fileextractor.VsiFileExtractor.after_chain_invoke', autospec=True)
    def test_execute_all_xml(self, mock_after_chain_invoke):
        chain = StetlTestCase.get_chain(self.etl, index=2)
        chain.run()

        # ZIP file contains 18 XML files in various zipfiles and is extracted; count is 19 because of final
        # call, so the VsiFileExtractor can indicate that no more files can be found.
        self.assertTrue(mock_after_chain_invoke.called)
        self.assertEqual(19, mock_after_chain_invoke.call_count)

        # Check if temp file exists
        section = StetlTestCase.get_section(chain, 1)
        file_path = self.etl.configdict.get(section, 'file_path')
        self.assertTrue(os.path.exists(file_path))
        os.remove(file_path)

    @mock.patch('stetl.filters.fileextractor.VsiFileExtractor.after_chain_invoke', autospec=True)
    def test_execute_bag_zip(self, mock_after_chain_invoke):
        chain = StetlTestCase.get_chain(self.etl, index=3)
        chain.run()

        # ZIP file contains 2 valid BAG zip files (and 2 non-valid)
        # in various zipfiles and is extracted; count is 3 because of final
        # call, so the VsiFileExtractor can indicate that no more files can be found.
        self.assertTrue(mock_after_chain_invoke.called)
        self.assertEqual(3, mock_after_chain_invoke.call_count)

        # Check if temp file exists
        section = StetlTestCase.get_section(chain, 1)
        file_path = self.etl.configdict.get(section, 'file_path')
        self.assertTrue(os.path.exists(file_path))
        os.remove(file_path)
