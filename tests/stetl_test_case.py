import logging
import os
import sys
import unittest

from stetl.chain import Chain
from stetl.util import Util
from StringIO import StringIO

logging.basicConfig(stream=sys.stderr, level=logging.DEBUG)

class StetlTestCase(unittest.TestCase):
    """Base class for Stetl test cases"""

    def setUp(self):        
        # Replace logger method
        self._old_get_log = Util.get_log
        
        @staticmethod
        def get_log_new(name):
            log = logging.getLogger(name)
            log.setLevel(logging.WARN)
            return log
            
        Util.get_log = get_log_new
    
        # Disable info logging
        logging.disable(logging.WARN)
        
        # Replace stdout
        self._saved_stdout = sys.stdout
        sys.stdout = StringIO()
        
        # Replace work dir
        self._cwd = os.getcwd()
        os.chdir(os.path.join(os.path.dirname(os.path.realpath(__file__)), '..'))
        
    def tearDown(self):
        # Restore old enviroment
        sys.stdout = self._saved_stdout
        logging.disable(logging.NOTSET)
        Util.get_log = self._old_get_log
        os.chdir(self._cwd)

    @classmethod
    def get_chain(cls, etl, index=0, assemble=True):
    
        chains_str = etl.configdict.get('etl', 'chains')
        chain_strs = chains_str.split(',')        
        chain = Chain(chain_strs[index].strip(), etl.configdict)
        
        if assemble:
            chain.assemble()
        
        return chain
        
    @classmethod
    def get_section(cls, chain, index=0):
        return chain.chain_str.split('|')[index]
