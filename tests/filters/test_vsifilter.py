import mock
import os
import shutil
import sys

from stetl.etl import ETL
from tests.stetl_test_case import StetlTestCase

class VsiFilterTest(StetlTestCase):
    """Unit tests for VsiFilter"""

    def setUp(self):
        super(VsiFilterTest, self).setUp()

        # Initialize Stetl
        curr_dir = os.path.dirname(os.path.realpath(__file__))
        cfg_dict = {'config_file': os.path.join(curr_dir, 'configs/vsifiltertest.cfg')}
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
    def test_vsizipfilter(self, mock_call):
        chain = StetlTestCase.get_chain(self.etl, 1)
        chain.run()

        # Check command line
        args, kwargs = mock_call.call_args
        list = self.parse_command(args[0])

        # Check whether the vsizip filter has been applied to the input file
        self.assertTrue(list[-1].startswith('/vsizip/tests/data/bestuurlijkegrenzen.zip/'))

    @mock.patch('subprocess.call', autospec=True)
    def test_vsizipfilter_cleanup_input(self, mock_call):
        """
        This test checks whether Stetl won't show an error when it tries to clean up the input file,
        which it can't find. This is the full path to the file within the ZIP file prepended with
        /vsizip/.
        """

        chain = StetlTestCase.get_chain(self.etl, 2)
        chain.run()

        # Check command line
        args, kwargs = mock_call.call_args
        list = self.parse_command(args[0])

        # Check whether the vsizip filter has been applied to the input file
        self.assertTrue(list[-1].startswith('/vsizip/tests/data/bestuurlijkegrenzen.zip/'))
