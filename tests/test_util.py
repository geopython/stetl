# testing: to be called by nosetests

import os
from ast import literal_eval

from stetl.etl import ETL
from stetl.util import ConfigSection
from tests.stetl_test_case import StetlTestCase


class UtilTest(StetlTestCase):
    """Basic util tests"""

    def setUp(self):
        super(UtilTest, self).setUp()

    def test_configsection_to_string(self):
        cfg = {
            'name': 'Stetl',
            'password': 'something',
            'paswoord': 'iets',
            'token': 'abc123',
            'user': 'John',
            'username': 'Jane',
            'gebruiker': 'Jan',
            'ogrconn': 'PG:dbname=mydb host=myhost port=myport user=myuser password=mypassword active_schema=myschema',
            'ogrconn_singlequotes': 'PG:dbname=\'mydb\' host=\'myhost\' port=\'myport\' user=\'myuser\' password=\'mypassword\' active_schema=\'myschema\'',
            'ogrconn_doublequotes': 'PG:dbname="mydb" host="myhost" port="myport" user="myuser" password="mypassword" active_schema="myschema"',
            'ogrconn_crazypwd1': 'PG:dbname=\'mydb\' host=\'myhost\' port=\'myport\' user=\'myuser\' password=\'my\\\'crazy\\"password\' active_schema=\'myschema\'',
            'ogrconn_crazypwd2': 'PG:dbname="mydb" host="myhost" port="myport" user="myuser" password="my\\\'crazy\\"password" active_schema="myschema"',
            'ogrconn_dkk': '"PG:dbname=mydb host=myhost port=myport user=myuser password=mypassword active_schema=myschema"',
        }
        obj = literal_eval(ConfigSection(cfg).to_string())
        
        self.assertEqual('Stetl', obj['name'])
        self.assertEqual('<hidden>', obj['password'])
        self.assertEqual('<hidden>', obj['paswoord'])
        self.assertEqual('<hidden>', obj['token'])
        self.assertEqual('<hidden>', obj['user'])
        self.assertEqual('<hidden>', obj['username'])
        self.assertEqual('Jan', obj['gebruiker'])
        self.assertEqual('PG:dbname=mydb host=myhost port=myport user=<hidden> password=<hidden> active_schema=myschema', obj['ogrconn'])
        self.assertEqual('PG:dbname=\'mydb\' host=\'myhost\' port=\'myport\' user=\'<hidden>\' password=\'<hidden>\' active_schema=\'myschema\'', obj['ogrconn_singlequotes'])
        self.assertEqual('PG:dbname="mydb" host="myhost" port="myport" user="<hidden>" password="<hidden>" active_schema="myschema"', obj['ogrconn_doublequotes'])
        self.assertEqual('PG:dbname=\'mydb\' host=\'myhost\' port=\'myport\' user=\'<hidden>\' password=\'<hidden>\' active_schema=\'myschema\'', obj['ogrconn_crazypwd1'])
        self.assertEqual('PG:dbname="mydb" host="myhost" port="myport" user="<hidden>" password="<hidden>" active_schema="myschema"', obj['ogrconn_crazypwd2'])
        self.assertEqual('"PG:dbname=mydb host=myhost port=myport user=<hidden> password=<hidden> active_schema=myschema"', obj['ogrconn_dkk'])
