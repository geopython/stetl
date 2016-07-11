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
        
        self.assertIsNone(chain.first_comp)
        self.assertIsNone(chain.cur_comp)

    def test_chain_assembly(self):
        chain = StetlTestCase.get_chain(self.etl, assemble=False)
        chain.assemble()
        
        self.assertIsNotNone(chain.first_comp)
        self.assertIsNotNone(chain.cur_comp)

        self.assertIsNotNone(chain.first_comp.next)
        self.assertIsNone(chain.cur_comp.next)
        
        comp = chain.first_comp
        while comp.next is not None:
            comp = comp.next
            
        self.assertIs(comp, chain.cur_comp)
