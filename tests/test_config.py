# testing: to be called by nosetests

import os

from stetl.etl import ETL
from tests.stetl_test_case import StetlTestCase


class ConfigTest(StetlTestCase):
    """Basic configuration tests"""

    def setUp(self):
        super(ConfigTest, self).setUp()

        # Initialize Stetl
        curr_dir = os.path.dirname(os.path.realpath(__file__))
        cfg_dict = {'config_file': os.path.join(curr_dir, 'configs/copy_in_out.cfg')}
        self.etl = ETL(cfg_dict)

    def test_type(self):
        self.assertEqual(self.etl.configdict.get('etl', 'chains'), 'input_xml_file|output_std')

    def test_run(self):
        self.etl.run()
