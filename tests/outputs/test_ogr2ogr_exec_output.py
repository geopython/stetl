import mock
import os
import shutil
import sys

from stetl.etl import ETL
from stetl.outputs.execoutput import Ogr2OgrExecOutput
from tests.stetl_test_case import StetlTestCase

class Ogr2OgrExecOutputTest(StetlTestCase):
    """Unit tests for Ogr2OgrExecOutput"""

    def setUp(self):
        super(Ogr2OgrExecOutputTest, self).setUp()

        # Initialize Stetl
        curr_dir = os.path.dirname(os.path.realpath(__file__))
        cfg_dict = {'config_file': os.path.join(curr_dir, 'configs/ogr2ogrexecoutput.cfg')}
        self.etl = ETL(cfg_dict)
    
    def test_class(self):
        chain = StetlTestCase.get_chain(self.etl)
        section = StetlTestCase.get_section(chain, -1)
        class_name = self.etl.configdict.get(section, 'class')
        
        self.assertEqual('outputs.execoutput.Ogr2OgrExecOutput', class_name)
    
    def test_instance(self):
        chain = StetlTestCase.get_chain(self.etl)

        self.assertTrue(isinstance(chain.cur_comp, Ogr2OgrExecOutput))
        
    def parse_command(self, command):
        """
        Parses the command line. With this regex the string is split at whitespace, except when
        whitespace is occurring between quotes. Because split keeps the capturing groups this way,
        every second item is removed from the list.
        """
        
        import re
        list = re.split(r"\s+(?=([^\"]*\"[^\"]*\")*[^\"]*$)", command)
        return list[0::2]
    
    @mock.patch('subprocess.call', autospec=True)
    def test_execute(self, mock_call):
        chain = StetlTestCase.get_chain(self.etl)
        chain.run()
        
        self.assertTrue(mock_call.called)
        self.assertEqual(1, mock_call.call_count)
        
        # Check command line
        args, kwargs = mock_call.call_args
        list = self.parse_command(args[0])
        self.assertEqual(len(list), 5)
        self.assertEqual(list[0], 'ogr2ogr')
        
        # Compare command line arguments with config
        section = StetlTestCase.get_section(chain, -1)
        file_path = self.etl.configdict.get(StetlTestCase.get_section(chain), 'file_path')
        
        # Certain options should not occur
        self.assertFalse('-spat' in list)
        self.assertFalse('-lco' in list)
        
        # Destination format
        self.assertTrue('-f' in list)
        f_idx = list.index('-f')
        dest_format = self.etl.configdict.get(section, 'dest_format')
        self.assertEqual(list[f_idx + 1], dest_format)
        
        # Destination datasource
        dest_data_source = self.etl.configdict.get(section, 'dest_data_source')
        self.assertEqual(list[f_idx + 2], dest_data_source)
        
        # Source datasource
        self.assertEqual(list[-1], file_path)
            
    @mock.patch('subprocess.call', autospec=True)
    def test_execute_lco(self, mock_call):
        chain = StetlTestCase.get_chain(self.etl, 1)
        chain.run()
        
        # Check command line
        args, kwargs = mock_call.call_args
        list = self.parse_command(args[0])
        self.assertEqual(len(list), 9)
        
        # Check layer creation options
        self.assertTrue('-lco' in list)
        lco_indices = [i for i, x in enumerate(list) if x == '-lco']
        self.assertEqual(len(lco_indices), 2)
        self.assertEqual(list[lco_indices[0] + 1], 'LAUNDER=YES')
        self.assertEqual(list[lco_indices[1] + 1], 'PRECISION=NO')
            
    @mock.patch('subprocess.call', autospec=True)
    def test_execute_extent(self, mock_call):
        chain = StetlTestCase.get_chain(self.etl, 2)
        chain.run()
        
        # Check command line
        args, kwargs = mock_call.call_args
        list = self.parse_command(args[0])
        self.assertEqual(len(list), 10)
        
        # Check spatial extent
        section = StetlTestCase.get_section(chain, -1)
        self.assertTrue('-spat' in list)
        spat_idx = list.index('-spat')
        spatial_extent = self.etl.configdict.get(section, 'spatial_extent')
        self.assertEqual(spatial_extent.split(), list[spat_idx + 1:spat_idx + 5])
            
    @mock.patch('subprocess.call', autospec=True)
    def test_execute_options(self, mock_call):
        chain = StetlTestCase.get_chain(self.etl, 3)
        chain.run()
        
        # Check command line
        args, kwargs = mock_call.call_args
        list = self.parse_command(args[0])
        self.assertEqual(len(list), 13)
        
        # Check spatial extent
        self.assertTrue('-append' in list)
        self.assertTrue('-gt' in list)
        self.assertTrue('--config' in list)
            
    @mock.patch('subprocess.call', autospec=True)
    def test_execute_gfs(self, mock_call):
        chain = StetlTestCase.get_chain(self.etl, 4)
        chain.run()
        
        # Check command line
        args, kwargs = mock_call.call_args
        list = self.parse_command(args[0])
        self.assertEqual(len(list), 5)
        
        # Check if GFS file exists, and clean it up
        file_path = self.etl.configdict.get(StetlTestCase.get_section(chain), 'file_path')
        file_ext = os.path.splitext(file_path) 
        gfs_path = file_ext[0] + '.gfs'
        self.assertTrue(os.path.exists(gfs_path))
        
        os.remove(gfs_path)
        self.assertFalse(os.path.exists(gfs_path))
        
    @mock.patch('subprocess.call', autospec=True)
    def test_execute_cleanup(self, mock_call):
        # Copy test file to temporary location, because it will be cleaned up
        orig_file_path = self.etl.configdict.get(StetlTestCase.get_section(StetlTestCase.get_chain(self.etl)), 'file_path')
        orig_file_ext = os.path.splitext(orig_file_path)
        temp_file_path = orig_file_ext[0] + "_temp" + orig_file_ext[1]
        shutil.copy(orig_file_path, temp_file_path)
        
        chain = StetlTestCase.get_chain(self.etl, 5)
        chain.run()
        
        # Check command line
        args, kwargs = mock_call.call_args
        list = self.parse_command(args[0])
        self.assertEqual(len(list), 5)
        
        # Check if temp file has been removed
        self.assertFalse(os.path.exists(temp_file_path))
        
    @mock.patch('subprocess.call', autospec=True)
    def test_execute_cleanup_gfs(self, mock_call):
        # Copy test file to temporary location, because it will be cleaned up
        orig_file_path = self.etl.configdict.get(StetlTestCase.get_section(StetlTestCase.get_chain(self.etl)), 'file_path')
        orig_file_ext = os.path.splitext(orig_file_path)
        temp_file_path = orig_file_ext[0] + "_temp" + orig_file_ext[1]
        shutil.copy(orig_file_path, temp_file_path)
        
        chain = StetlTestCase.get_chain(self.etl, 6)
        chain.run()
        
        # Check command line
        args, kwargs = mock_call.call_args
        list = self.parse_command(args[0])
        self.assertEqual(len(list), 5)
        
        # Check if temp file has been removed
        self.assertFalse(os.path.exists(temp_file_path))
        
        # Check if GFS file has already been removed
        gfs_path = orig_file_ext[0] + "_temp.gfs"
        self.assertFalse(os.path.exists(gfs_path))
        
    @mock.patch('subprocess.call', autospec=True)
    def test_execute_no_cleanup(self, mock_call):
        chain = StetlTestCase.get_chain(self.etl, 7)
        file_path = self.etl.configdict.get(StetlTestCase.get_section(chain), 'file_path')
        chain.run()
        
        # Check command line
        args, kwargs = mock_call.call_args
        list = self.parse_command(args[0])
        self.assertEqual(len(list), 5)
        
        # Check if input file still exists
        self.assertTrue(os.path.exists(file_path))
