# testing: to be called by nosetests

import os

from stetl.etl import ETL
from tests.stetl_test_case import StetlTestCase


class ConfigTest(StetlTestCase):
    """Basic configuration tests"""

    def setUp(self):
        super(ConfigTest, self).setUp()


        # Initialize Stetl
        self.curr_dir = os.path.dirname(os.path.realpath(__file__))
        self.cfg_dict = {'config_file': os.path.join(self.curr_dir, 'configs/copy_in_out_file.cfg')}

    def tearDown(self):
        super(ConfigTest, self).tearDown()
        # Restore old enviroment
        try:
            del os.environ['stetl_out_file']
            del os.environ['stetl_in_file']
        except:
            pass

    def test_args_dict(self):
        args_dict = {'in_file': 'infile.txt', 'out_file': 'outfile.txt'}
        etl = ETL(self.cfg_dict, args_dict)

        # Test args substitution from args_dict
        self.assertEqual(etl.configdict.get('input_file', 'file_path'), 'infile.txt')
        self.assertEqual(etl.configdict.get('output_file', 'file_path'), 'outfile.txt')

    def test_args_dict_env_override(self):
        args_dict = {'in_file': 'infile.txt', 'out_file': 'outfile.txt'}

        # Override in OS env
        os.environ['stetl_in_file'] = 'env_infile.txt'

        etl = ETL(self.cfg_dict, args_dict)

        # Test args substitution from args_dict
        self.assertEqual(etl.configdict.get('input_file', 'file_path'), os.environ['stetl_in_file'])
        self.assertEqual(etl.configdict.get('output_file', 'file_path'), 'outfile.txt')

    def test_args_dict_env_all(self):
        """
        Substitute ALL args from OS env.
        :return:
        """

        # Set all args in in OS env
        os.environ['stetl_in_file'] = 'env_infile.txt'
        os.environ['stetl_out_file'] = 'env_outfile.txt'

        args_dict = None
        etl = ETL(self.cfg_dict, args_dict)

        # Test args substitution from args_dict
        self.assertEqual(etl.configdict.get('input_file', 'file_path'), os.environ['stetl_in_file'])
        self.assertEqual(etl.configdict.get('output_file', 'file_path'), os.environ['stetl_out_file'])
