import mock
import os
import sys

from stetl.etl import ETL
from stetl.outputs.dboutput import PostgresDbOutput
from tests.stetl_test_case import StetlTestCase

class PostgresDbOutputTest(StetlTestCase):
    """Unit tests for PostgresDbOutput"""

    def setUp(self):
        super(PostgresDbOutputTest, self).setUp()

        # Initialize Stetl
        curr_dir = os.path.dirname(os.path.realpath(__file__))
        cfg_dict = {'config_file': os.path.join(curr_dir, 'configs/postgresdboutput.cfg')}
        self.etl = ETL(cfg_dict)
    
    def test_class(self):
        chain = StetlTestCase.get_chain(self.etl)
        section = StetlTestCase.get_section(chain, -1)
        class_name = self.etl.configdict.get(section, 'class')
        
        self.assertEqual('outputs.dboutput.PostgresDbOutput', class_name)
    
    def test_instance(self):
        chain = StetlTestCase.get_chain(self.etl)

        self.assertTrue(isinstance(chain.cur_comp, PostgresDbOutput))
    
    @mock.patch('stetl.postgis.PostGIS.tx_execute', autospec=True)
    def test_execute(self, mock_tx_execute):
        # Read content of input file
        chain = StetlTestCase.get_chain(self.etl)
        section = StetlTestCase.get_section(chain)
        fn = self.etl.configdict.get(section, 'file_path')
        with open(fn, 'r') as f:
            contents = f.read()

        self.etl.run()
        
        self.assertTrue(mock_tx_execute.called)
        self.assertEqual(1, mock_tx_execute.call_count)
        args, kwargs = mock_tx_execute.call_args
        self.assertEqual(contents, args[1])
        