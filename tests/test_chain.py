# testing: to be called by nosetests

import os

from stetl.etl import ETL
from stetl.chain import Chain
from tests.stetl_test_case import StetlTestCase

class ChainTest(StetlTestCase):
    """Basic chain tests"""

    def setUp(self):
        super(ChainTest, self).setUp()

        # Initialize Stetl
        curr_dir = os.path.dirname(os.path.realpath(__file__))
        cfg_dict = {'config_file': os.path.join(curr_dir, 'configs/copy_in_out.cfg')}
        self.etl = ETL(cfg_dict)
        
    def test_chain(self):
        chain = StetlTestCase.get_chain(self.etl, assemble=False)
        
        assert chain.first_comp is None
        assert chain.cur_comp is None

    def test_chain_assembly(self):
        chain = StetlTestCase.get_chain(self.etl, assemble=False)
        chain.assemble()
        
        assert chain.first_comp is not None
        assert chain.cur_comp is not None

        assert chain.first_comp.next is not None
        assert chain.cur_comp.next is None
        
        comp = chain.first_comp
        while comp.next is not None:
            comp = comp.next
            
        assert comp == chain.cur_comp
