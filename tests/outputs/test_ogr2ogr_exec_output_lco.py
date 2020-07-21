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
        cfg_dict = {'config_file': os.path.join(curr_dir, 'configs/ogr2ogrexecoutput_testlco_notalways.cfg')}
        self.etl = ETL(cfg_dict)

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
    def test_ogrexecoutput_lco_first(self, mock_call):
        chain = StetlTestCase.get_chain(self.etl)
        chain.run()

        # Check command line
        args, kwargs = mock_call.call_args
        list = self.parse_command(args[0])

        # Check whether layer creation options are absent
        self.assertFalse('-lco' in list)

    @mock.patch('subprocess.call', autospec=True)
    def test_ogrexecoutput_lco_always(self, mock_call):
        chain = StetlTestCase.get_chain(self.etl, 1)
        chain.run()

        # Check command line
        args, kwargs = mock_call.call_args
        list = self.parse_command(args[0])

        # Check layer creation options
        self.assertTrue('-lco' in list)
        lco_indices = [i for i, x in enumerate(list) if x == '-lco']
        self.assertEqual(len(lco_indices), 2)
        self.assertEqual(list[lco_indices[0] + 1], 'GEOMETRY_NAME=geomtest')
        self.assertEqual(list[lco_indices[1] + 1], 'PRECISION=NO')
