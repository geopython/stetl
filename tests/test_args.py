# testing: to be called by nosetests

import os

from stetl.etl import ETL
from tests.stetl_test_case import StetlTestCase
from stetl.main import parse_args


class ConfigTest(StetlTestCase):
    """Basic configuration tests"""

    def setUp(self):
        super(ConfigTest, self).setUp()


        # Initialize Stetl
        self.curr_dir = os.path.dirname(os.path.realpath(__file__))
        self.cfg_dict = {'config_file': os.path.join(self.curr_dir, 'configs/copy_in_out_file.cfg')}

    def clear_stetl_env(self):
        # Restore old enviroment
        try:
            del os.environ['stetl_out_file']
            del os.environ['stetl_in_file']
        except:
            pass

    def tearDown(self):
        super(ConfigTest, self).tearDown()
        self.clear_stetl_env()

    def test_config_args_file_single(self):
        """
        Test single -a argsfile option
        :return:
        """
        args_default = os.path.join(self.curr_dir, 'configs/copy_in_out_file_default.args')
        args_parsed = parse_args(['-a', args_default])

        # Test args substitution from args_dict
        config_args = args_parsed.config_args
        self.assertEqual(config_args['in_file'], 'default_infile.txt')
        self.assertEqual(config_args['out_file'], 'default_outfile.txt')

    def test_config_args_explicit_single(self):
        """
        Test single -a "arg1=x arg2=y" option
        :return:
        """
        args_default = os.path.join(self.curr_dir, 'configs/copy_in_out_file_default.args')
        args_parsed = parse_args(['-a', 'in_file=default_infile.txt out_file=default_outfile.txt'])

        # Test args substitution from args_dict
        config_args = args_parsed.config_args
        self.assertEqual(config_args['in_file'], 'default_infile.txt')
        self.assertEqual(config_args['out_file'], 'default_outfile.txt')

    def test_config_args_file_multi(self):
        """
        Test multiple: -a argsfile1 -a argsfile2 option with override
        :return:
        """
        args_default = os.path.join(self.curr_dir, 'configs/copy_in_out_file_default.args')
        args_my = os.path.join(self.curr_dir, 'configs/copy_in_out_file_my.args')
        args_parsed = parse_args(['-a', args_default, '-a', args_my])

        # Test args substitution from args_dict
        config_args = args_parsed.config_args
        self.assertEqual(config_args['in_file'], 'my_infile.txt')
        self.assertEqual(config_args['out_file'], 'default_outfile.txt')

    def test_config_args_file_explicit_multi(self):
        """
        Test multiple: -a argsfile1 -a arg=myarg option with override
        :return:
        """
        args_default = os.path.join(self.curr_dir, 'configs/copy_in_out_file_default.args')
        args_parsed = parse_args(['-a', args_default, '-a', 'in_file=my_infile.txt'])

        # Test args substitution from args_dict
        config_args = args_parsed.config_args
        self.assertEqual(config_args['in_file'], 'my_infile.txt')
        self.assertEqual(config_args['out_file'], 'default_outfile.txt')

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
