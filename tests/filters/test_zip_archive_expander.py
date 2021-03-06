import mock
import os

from stetl.etl import ETL
from stetl.filters.archiveexpander import ZipArchiveExpander
from tests.stetl_test_case import StetlTestCase

class ZipArchiveExpanderTest(StetlTestCase):
    """Unit tests for ZipArchiveExpander plus deprecation"""

    def setUp(self):
        super(ZipArchiveExpanderTest, self).setUp()

        # Initialize Stetl
        self.curr_dir = os.path.dirname(os.path.realpath(__file__))
        cfg_dict = {'config_file': os.path.join(self.curr_dir, 'configs/ziparchiveexpander.cfg')}
        self.etl = ETL(cfg_dict)

    def test_class(self):
        chain = StetlTestCase.get_chain(self.etl)
        section = StetlTestCase.get_section(chain, 2)
        class_name = self.etl.configdict.get(section, 'class')
        self.assertEqual('stetl.filters.archiveexpander.ZipArchiveExpander', class_name)

    def test_instance(self):
        chain = StetlTestCase.get_chain(self.etl)

        self.assertTrue(isinstance(chain.first_comp.next.next, ZipArchiveExpander))

    @mock.patch('stetl.outputs.standardoutput.StandardOutput.after_chain_invoke', autospec=True)
    def test_execute_zip(self, mock_after_chain_invoke):
        chain = StetlTestCase.get_chain(self.etl)
        chain.run()

        # ZIP file contains two GML files, both should be extracted; count is 3 because of final
        # call, so the ZipArchiveExpander can indicate that no more files can be found.
        self.assertTrue(mock_after_chain_invoke.called)
        self.assertEqual(2, mock_after_chain_invoke.call_count)

        # Check if temp dir exists
        section = StetlTestCase.get_section(chain, 2)
        target_dir = self.etl.configdict.get(section, 'target_dir')
        self.assertTrue(os.path.exists(target_dir))
        file_objects = os.listdir(target_dir)

        # 3 XML files in archive
        self.assertEqual(3, len(file_objects))

        for file_object in file_objects:
            file_object_path = os.path.join(target_dir, file_object)
            self.assertTrue(file_object.startswith('0221LIG'))
            self.assertTrue(file_object.endswith('.xml'))

            self.assertTrue(os.path.exists(file_object_path))
            os.remove(file_object_path)

    @mock.patch('stetl.filters.fileextractor.VsiFileExtractor.after_chain_invoke', autospec=True)
    def test_execute_vsizip(self, mock_after_chain_invoke):
        chain = StetlTestCase.get_chain(self.etl, index=1)
        chain.run()

        # ZIP file contains one XML file and is extracted; count is 2 because of final
        # call, so the VsiFileExtractor can indicate that no more files can be found.
        self.assertTrue(mock_after_chain_invoke.called)
        self.assertEqual(2, mock_after_chain_invoke.call_count)

        # Check if temp file exists
        section = StetlTestCase.get_section(chain, 2)
        target_dir = self.etl.configdict.get(section, 'target_dir')
        self.assertTrue(os.path.exists(target_dir))
        file_objects = os.listdir(target_dir)

        # 2 XML files in archive
        self.assertEqual(2, len(file_objects))

        for file_object in file_objects:
            file_object_path = os.path.join(target_dir, file_object)
            self.assertTrue(file_object.startswith('0221WPL'))
            self.assertTrue(file_object.endswith('.xml'))

            self.assertTrue(os.path.exists(file_object_path))
            os.remove(file_object_path)

