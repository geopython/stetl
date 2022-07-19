import csv
import multiprocessing
import os
import pprint
import re
import zipfile

from lxml import etree
from osgeo import ogr, osr
from psycopg2 import sql

from stetl.bagutil import BAGUtil
from stetl.output import Output
from stetl.util import Util
from stetl.packet import FORMAT
from stetl.component import Config
from stetl.postgis import PostGIS

log = Util.get_log('bagoutput')

sr = osr.SpatialReference()
sr.ImportFromEPSG(28992)

xmlns = {
    'xsi': (
        'http://www.w3.org/2001/XMLSchema-instance'
    ),
    'xs': (
        'http://www.w3.org/2001/XMLSchema'
    ),

    'gml': (
        'http://www.opengis.net/gml/3.2'
    ),

    'xb': (
        'http://www.kadaster.nl/schemas/lvbag/extract-levering/v20200601'
    ),
    'selecties-extract': (
        'http://www.kadaster.nl/schemas/lvbag/extract-selecties/v20200601'
    ),

    'sl-bag-extract': (
        'http://www.kadaster.nl/schemas/lvbag/extract-deelbestand-lvc/v20200601'
    ),
    'sl': (
        'http://www.kadaster.nl/schemas/standlevering-generiek/1.0'
    ),

    'bagtypes': (
        'www.kadaster.nl/schemas/lvbag/gem-wpl-rel/bag-types/v20200601'
    ),
    'gwr-bestand': (
        'www.kadaster.nl/schemas/lvbag/gem-wpl-rel/gwr-deelbestand-lvc/v20200601'
    ),
    'gwr-product': (
        'www.kadaster.nl/schemas/lvbag/gem-wpl-rel/gwr-producten-lvc/v20200601'
    ),

    'DatatypenNEN3610': (
        'www.kadaster.nl/schemas/lvbag/imbag/datatypennen3610/v20200601'
    ),
    'Historie': (
        'www.kadaster.nl/schemas/lvbag/imbag/historie/v20200601'
    ),
    'KenmerkInOnderzoek': (
        'www.kadaster.nl/schemas/lvbag/imbag/kenmerkinonderzoek/v20200601'
    ),
    'nen5825': (
        'www.kadaster.nl/schemas/lvbag/imbag/nen5825/v20200601'
    ),
    'Objecten': (
        'www.kadaster.nl/schemas/lvbag/imbag/objecten/v20200601'
    ),
    'Objecten-ref': (
        'www.kadaster.nl/schemas/lvbag/imbag/objecten-ref/v20200601'
    ),
}


class BAGOutput(Output):
    """
    Process BAG 2.0 Extract files
    """

    @Config(ptype=str, required=True, default=None)
    def database(self):
        """
        Database name
        """
        pass

    @Config(ptype=str, required=False, default=None)
    def user(self):
        """
        Dabase username
        """
        pass

    @Config(ptype=str, required=False, default=None)
    def password(self):
        """
        Database password
        """
        pass

    @Config(ptype=str, required=False, default=None)
    def host(self):
        """
        Database host
        """
        pass

    @Config(ptype=str, required=False, default='public')
    def schema(self):
        """
        Database schema
        """
        pass

    @Config(ptype=bool, required=False, default=False)
    def truncate(self):
        """
        Truncate database tables
        """
        pass

    @Config(ptype=bool, required=False, default=True)
    def process_inactief(self):
        """
        Process Inactief data
        """
        pass

    @Config(ptype=bool, required=False, default=True)
    def process_in_onderzoek(self):
        """
        Process InOnderzoek data
        """
        pass

    @Config(ptype=bool, required=False, default=True)
    def process_niet_bag(self):
        """
        Process NietBag data
        """
        pass

    @Config(ptype=bool, required=False, default=False)
    def process_lig(self):
        """
        Process LIG (Ligplaats) data
        """
        pass

    @Config(ptype=bool, required=False, default=False)
    def process_num(self):
        """
        Process NUM (Nummeraanduiding) data
        """
        pass

    @Config(ptype=bool, required=False, default=False)
    def process_opr(self):
        """
        Process OPR (OpenbareRuimte) data
        """
        pass

    @Config(ptype=bool, required=False, default=False)
    def process_pnd(self):
        """
        Process PND (Pand) data
        """
        pass

    @Config(ptype=bool, required=False, default=False)
    def process_sta(self):
        """
        Process STA (Standplaats) data
        """
        pass

    @Config(ptype=bool, required=False, default=False)
    def process_vbo(self):
        """
        Process VBO (Verblijfsobject) data
        """
        pass

    @Config(ptype=bool, required=False, default=False)
    def process_wpl(self):
        """
        Process WPL (Woonplaats) data
        """
        pass

    @Config(ptype=bool, required=False, default=False)
    def process_gwr(self):
        """
        Process GemeenteWoonplaatsRelatie data
        """
        pass

    @Config(ptype=bool, required=False, default=False)
    def process_levering(self):
        """
        Process Leveringsdocument data
        """
        pass

    @Config(ptype=str, required=False, default='/tmp')
    def temp_dir(self):
        """
        Path for temporary directory
        """
        pass

    @Config(ptype=int, required=False, default=(1024 * 1024 * 1024))
    def buffer_size(self):
        """
        Buffer size for read buffer during extraction
        """
        pass

    @Config(ptype=bool, required=False, default=False)
    def multiprocessing(self):
        """
        Process multiple files in parallel
        """
        pass

    @Config(ptype=int, required=False, default=(os.cpu_count() - 1))
    def workers(self):
        """
        Number of parallel processing workers
        """
        pass

    def __init__(self, configdict, section, consumes=FORMAT.record):
        Output.__init__(self, configdict, section, consumes=consumes)
        self.db = None

    def db_connect(self):
        log.info('Init: connect to DB')
        self.db = PostGIS(self.cfg.get_dict())
        self.db.connect()

    def db_disconnect(self):
        log.info('Exit: disconnect from DB')
        self.db.disconnect()

    def init(self):
        if not self.multiprocessing:
            self.db_connect()

    def exit(self):
        if not self.multiprocessing:
            self.db_disconnect()

    def update_record(self, table, record, identifiers):
        sqlstr = r'UPDATE {table} SET'
        sqlfmt = {
            'table': sql.Identifier(table),
        }
        param = []

        i = 0
        for key in record:
            if key in identifiers:
                continue

            if i > 0:
                sqlstr += ','

            column = 'col' + str(i)

            sqlstr += r' {' + column + r'} = %s'

            sqlfmt[column] = sql.Identifier(key)
            param.append(record[key])

            i += 1

        column = 'col' + str(i)

        sqlstr += r' WHERE '

        i = 0
        for key in identifiers:
            if i > 0:
                sqlstr += ' AND '

            column = 'con' + str(i)

            sqlstr += r'{' + column + r'} = %s'

            sqlfmt[column] = sql.Identifier(key)
            param.append(identifiers[key])

            i += 1

        log.debug("sqlstr: %s" % sqlstr)
        log.debug("sqlfmt: %s" % sqlfmt)

        query = sql.SQL(sqlstr).format(**sqlfmt)

        log.debug("query: %s" % query.as_string(context=self.db.cursor))
        log.debug("param: %s" % pprint.pformat(param))

        rowcount = self.db.execute(query, param)

        if rowcount == -1:
            raise Exception('Query failed: %s' % query)

    def insert_record(self, table, record):
        sqlstr = r'INSERT INTO {table} ('
        sqlfmt = {
            'table': sql.Identifier(table),
        }
        values = r') VALUES ('
        param = []

        i = 0
        for key in record:
            if i > 0:
                sqlstr += ', '
                values += ', '

            column = 'col' + str(i)

            sqlstr += r'{' + column + r'}'
            values += r'%s'

            sqlfmt[column] = sql.Identifier(key)
            param.append(record[key])

            i += 1

        sqlstr += values + r')'

        log.debug("sqlstr: %s" % sqlstr)
        log.debug("sqlfmt: %s" % sqlfmt)

        query = sql.SQL(sqlstr).format(**sqlfmt)

        log.debug("query: %s" % query.as_string(context=self.db.cursor))
        log.debug("param: %s" % pprint.pformat(param))

        rowcount = self.db.execute(query, param)

        if rowcount == -1:
            raise Exception('Query failed: %s' % query)

    def upsert_record(
        self,
        table,
        record,
        primary_key='gid',
        identifiers=None,
    ):
        update = False

        if identifiers is not None:
            sqlstr = r'SELECT {primary_key} FROM {table} WHERE '
            sqlfmt = {
                'primary_key': sql.Identifier(primary_key),
                'table': sql.Identifier(table),
            }
            param = []

            i = 0
            for key in identifiers:
                if i > 0:
                    sqlstr += ' AND '

                column = 'con' + str(i)

                sqlstr += r'{' + column + r'} = %s'

                sqlfmt[column] = sql.Identifier(key)
                param.append(identifiers[key])

                i += 1

            log.debug("sqlstr: %s" % sqlstr)
            log.debug("sqlfmt: %s" % sqlfmt)

            query = sql.SQL(sqlstr).format(**sqlfmt)

            log.debug("query: %s" % query.as_string(context=self.db.cursor))
            log.debug("param: %s" % pprint.pformat(param))

            rowcount = self.db.execute(query, param)

            log.debug("rowcount: %s" % rowcount)

            if rowcount == -1:
                raise Exception('Query failed: %s' % query)
            elif rowcount == 0:
                update = False
            elif rowcount == 1:
                update = True
            else:
                raise Exception(
                    '%d rows returned for query: %s' % (
                        rowcount,
                        query,
                    )
                )

        if update:
            self.update_record(table, record, identifiers)
        else:
            self.insert_record(table, record)

    def create_enum(self, name, values):
        log.info("Creating ENUM: %s" % name)

        sqlfmt = {
            'name': sql.Identifier(name.lower()),
        }

        sqlstr = r'CREATE TYPE {name} AS ENUM ('

        i = 0
        for value in values:
            if i > 0:
                sqlstr += ', '

            sqlstr += r'%s'

            i += 1

        sqlstr += ')'

        log.debug("sqlstr: %s" % sqlstr)
        log.debug("sqlfmt: %s" % sqlfmt)

        query = sql.SQL(sqlstr).format(**sqlfmt)

        log.debug("query: %s" % query.as_string(context=self.db.cursor))
        log.debug("param: %s" % pprint.pformat(values))

        self.db.cursor.execute(query, values)

    def enum_exists(self, name):
        query = """
            SELECT typname
              FROM pg_type
             WHERE LOWER(typname) = %(name)s
        """
        param = {
            'name': name.lower(),
        }

        log.debug("query: %s" % query)
        log.debug("param: %s" % pprint.pformat(param))

        self.db.cursor.execute(query, param)

        if self.db.cursor.rowcount == 0:
            return False
        else:
            return True

    def truncate_table(self, table):
        log.info("Truncating table: %s" % table)

        format = {
            'table': sql.Identifier(table),
        }

        query = sql.SQL('TRUNCATE {table}').format(**format)

        log.debug("query: %s" % query)

        self.db.cursor.execute(query)

    def create_table(self, table):
        log.info("Creating table: %s" % table)

        enum_type = {
            'GebruiksdoelType': [
                'woonfunctie',
                'bijeenkomstfunctie',
                'celfunctie',
                'gezondheidszorgfunctie',
                'industriefunctie',
                'kantoorfunctie',
                'logiesfunctie',
                'onderwijsfunctie',
                'sportfunctie',
                'winkelfunctie',
                'overige gebruiksfunctie',
            ],
            'StatusNaamgeving': [
                'Naamgeving uitgegeven',
                'Naamgeving ingetrokken',
            ],
            'StatusPand': [
                'Bouwvergunning verleend',
                'Niet gerealiseerd pand',
                'Bouw gestart',
                'Pand in gebruik (niet ingemeten)',
                'Pand in gebruik',
                'Verbouwing pand',
                'Sloopvergunning verleend',
                'Pand gesloopt',
                'Pand buiten gebruik',
                'Pand ten onrechte opgevoerd',
            ],
            'StatusPlaats': [
                'Plaats aangewezen',
                'Plaats ingetrokken',
            ],
            'StatusVerblijfsobject': [
                'Verblijfsobject gevormd',
                'Niet gerealiseerd verblijfsobject',
                'Verblijfsobject in gebruik (niet ingemeten)',
                'Verblijfsobject in gebruik',
                'Verbouwing verblijfsobject',
                'Verblijfsobject ingetrokken',
                'Verblijfsobject buiten gebruik',
                'Verblijfsobject ten onrechte opgevoerd',
            ],
            'StatusWoonplaats': [
                'Woonplaats aangewezen',
                'Woonplaats ingetrokken',
            ],
            'TypeAdresseerbaarObject': [
                'Verblijfsobject',
                'Standplaats',
                'Ligplaats',
            ],
            'TypeOpenbareRuimte': [
                'Weg',
                'Water',
                'Spoorbaan',
                'Terrein',
                'Kunstwerk',
                'Landschappelijk gebied',
                'Administratief gebied',
            ],

            'InOnderzoekLigplaats': [
                'geometrie',
                'status',
                'heeft als hoofdadres',
                'heeft als nevenadres',
            ],
            'InOnderzoekNummeraanduiding': [
                'huisnummer',
                'huisletter',
                'huisnummertoevoeging',
                'postcode',
                'type adresseerbaar object',
                'status',
                'ligt in',
                'ligt aan',
            ],
            'InOnderzoekOpenbareRuimte': [
                'naam',
                'type',
                'status',
                'ligt in',
            ],
            'InOnderzoekPand': [
                'geometrie',
                'oorspronkelijk bouwjaar',
                'status',
            ],
            'InOnderzoekStandplaats': [
                'geometrie',
                'status',
                'heeft als hoofdadres',
                'heeft als nevenadres',
            ],
            'InOnderzoekVerblijfsobject': [
                'geometrie',
                'gebruiksdoel',
                'oppervlakte',
                'status',
                'maakt deel uit van',
                'heeft als hoofdadres',
                'heeft als nevenadres',
            ],
            'InOnderzoekWoonplaats': [
                'naam',
                'geometrie',
                'status',
            ],
        }

        table_enum = {
            'woonplaats': [
                'StatusWoonplaats',
            ],
            'openbareruimte': [
                'TypeOpenbareRuimte',
                'StatusNaamgeving',
            ],
            'nummeraanduiding': [
                'TypeAdresseerbaarObject',
                'StatusNaamgeving',
            ],
            'verblijfsobject': [
                'StatusVerblijfsobject',
            ],
            'ligplaats': [
                'StatusPlaats',
            ],
            'standplaats': [
                'StatusPlaats',
            ],
            'pand': [
                'StatusPand',
            ],

            'inonderzoek_woonplaats': [
                'InOnderzoekWoonplaats',
            ],
            'inonderzoek_openbareruimte': [
                'InOnderzoekOpenbareRuimte',
            ],
            'inonderzoek_nummeraanduiding': [
                'InOnderzoekNummeraanduiding',
            ],
            'inonderzoek_verblijfsobject': [
                'InOnderzoekVerblijfsobject',
            ],
            'inonderzoek_ligplaats': [
                'InOnderzoekLigplaats',
            ],
            'inonderzoek_standplaats': [
                'InOnderzoekStandplaats',
            ],
            'inonderzoek_pand': [
                'InOnderzoekPand',
            ],
        }

        table_column = {
            'gid': {
                'name': 'gid',
                'type': 'serial',
                'null': False,
            },
            'identificatie': {
                'name': 'identificatie',
                'type': 'varchar',
                'null': False,
            },
            'naam': {
                'name': 'naam',
                'type': 'varchar(80)',
                'null': False,
            },

            'documentdatum': {
                'name': 'documentdatum',
                'type': 'date',
                'null': False,
            },
            'documentnummer': {
                'name': 'documentnummer',
                'type': 'varchar(40)',
                'null': False,
            },

            'voorkomenidentificatie': {
                'name': 'voorkomenidentificatie',
                'type': 'int',
                'null': False,
            },
            'begingeldigheid': {
                'name': 'begingeldigheid',
                'type': 'date',
                'null': False,
            },
            'eindgeldigheid': {
                'name': 'eindgeldigheid',
                'type': 'date',
                'null': True,
            },
            'tijdstipregistratie': {
                'name': 'tijdstipregistratie',
                'type': 'timestamp',
                'null': False,
            },
            'eindregistratie': {
                'name': 'eindregistratie',
                'type': 'timestamp',
                'null': True,
            },
            'tijdstipinactief': {
                'name': 'tijdstipinactief',
                'type': 'timestamp',
                'null': True,
            },
            'tijdstipregistratielv': {
                'name': 'tijdstipregistratielv',
                'type': 'timestamp',
                'null': False,
            },
            'tijdstipeindregistratielv': {
                'name': 'tijdstipeindregistratielv',
                'type': 'timestamp',
                'null': True,
            },
            'tijdstipinactieflv': {
                'name': 'tijdstipinactieflv',
                'type': 'timestamp',
                'null': True,
            },
            'tijdstipnietbaglv': {
                'name': 'tijdstipnietbaglv',
                'type': 'timestamp',
                'null': True,
            },
        }

        table_column_group = {
            'common': [
                {
                    'name': 'geconstateerd',
                    'type': 'bool',
                    'null': False,
                },
                {
                    'include': 'documentdatum',
                },
                {
                    'include': 'documentnummer',
                },
            ],
            'inonderzoek_common': [
                {
                    'name': 'inonderzoek',
                    'type': 'bool',
                    'null': False,
                },
                {
                    'include': 'documentdatum',
                },
                {
                    'include': 'documentnummer',
                },
            ],
            'voorkomen': [
                {
                    'include': 'voorkomenidentificatie',
                },
                {
                    'include': 'begingeldigheid',
                },
                {
                    'include': 'eindgeldigheid',
                },
                {
                    'include': 'tijdstipregistratie',
                },
                {
                    'include': 'eindregistratie',
                },
                {
                    'include': 'tijdstipinactief',
                },
                {
                    'include': 'tijdstipregistratielv',
                },
                {
                    'include': 'tijdstipeindregistratielv',
                },
                {
                    'include': 'tijdstipinactieflv',
                },
                {
                    'include': 'tijdstipnietbaglv',
                },
            ],
            'historieinonderzoek': [
                {
                    'include': 'tijdstipregistratie',
                },
                {
                    'include': 'eindregistratie',
                },
                {
                    'include': 'begingeldigheid',
                },
                {
                    'include': 'eindgeldigheid',
                },
                {
                    'include': 'tijdstipregistratielv',
                },
                {
                    'include': 'tijdstipeindregistratielv',
                },
            ],
            'adresseerbaarobject': [
                {
                    'name': 'hoofdadresnummeraanduidingref',
                    'type': 'varchar',
                    'null': False,
                },
                {
                    'include_group': 'voorkomen',
                },
                {
                    'name': 'nevenadresnummeraanduidingref',
                    'type': 'varchar[]',
                    'null': True,
                },
            ],
        }

        table_structure = {
            'woonplaats': {
                'columns': [
                    {
                        'include': 'gid',
                    },
                    {
                        'include': 'identificatie',
                    },
                    {
                        'include': 'naam',
                    },
                    {
                        'name': 'status',
                        'type': 'StatusWoonplaats',
                        'null': False,
                    },
                    {
                        'include_group': 'common',
                    },
                    {
                        'include_group': 'voorkomen',
                    },
                    {
                        'name': 'wkb_geometry',
                        'type': 'geometry(MultiPolygon,28992)',
                        'null': False,
                    },
                ],
                'primary_key': 'gid',
            },
            'openbareruimte': {
                'columns': [
                    {
                        'include': 'gid',
                    },
                    {
                        'include': 'identificatie',
                    },
                    {
                        'include': 'naam',
                    },
                    {
                        'name': 'type',
                        'type': 'TypeOpenbareRuimte',
                        'null': False,
                    },
                    {
                        'name': 'status',
                        'type': 'StatusNaamgeving',
                        'null': False,
                    },
                    {
                        'include_group': 'common',
                    },
                    {
                        'name': 'woonplaatsref',
                        'type': 'varchar',
                        'null': False,
                    },
                    {
                        'include_group': 'voorkomen',
                    },
                    {
                        'name': 'verkortenaam',
                        'type': 'varchar(24)',
                        'null': True,
                    },
                ],
                'primary_key': 'gid',
            },
            'nummeraanduiding': {
                'columns': [
                    {
                        'include': 'gid',
                    },
                    {
                        'include': 'identificatie',
                    },
                    {
                        'name': 'huisnummer',
                        'type': 'int',
                        'null': False,
                    },
                    {
                        'name': 'huisletter',
                        'type': 'varchar(1)',
                        'null': True,
                    },
                    {
                        'name': 'huisnummertoevoeging',
                        'type': 'varchar(4)',
                        'null': True,
                    },
                    {
                        'name': 'postcode',
                        'type': 'varchar(6)',
                        'null': True,
                    },
                    {
                        'name': 'typeadresseerbaarobject',
                        'type': 'TypeAdresseerbaarObject',
                        'null': False,
                    },
                    {
                        'name': 'status',
                        'type': 'StatusNaamgeving',
                        'null': False,
                    },
                    {
                        'include_group': 'common',
                    },
                    {
                        'name': 'woonplaatsref',
                        'type': 'varchar',
                        'null': True,
                    },
                    {
                        'include_group': 'voorkomen',
                    },
                    {
                        'name': 'openbareruimteref',
                        'type': 'varchar',
                        'null': False,
                    },
                ],
                'primary_key': 'gid',
            },
            'verblijfsobject': {
                'columns': [
                    {
                        'include': 'gid',
                    },
                    {
                        'include': 'identificatie',
                    },
                    {
                        'name': 'gebruiksdoel',
                        'type': 'varchar[]',
                        'null': False,
                    },
                    {
                        'name': 'oppervlakte',
                        'type': 'int',
                        'null': False,
                    },
                    {
                        'name': 'status',
                        'type': 'StatusVerblijfsobject',
                        'null': False,
                    },
                    {
                        'include_group': 'common',
                    },
                    {
                        'name': 'pandref',
                        'type': 'varchar[]',
                        'null': False,
                    },
                    {
                        'include_group': 'adresseerbaarobject',
                    },
                    {
                        'name': 'wkb_geometry',
                        'type': 'geometry(Point,28992)',
                        'null': False,
                    },
                ],
                'primary_key': 'gid',
            },
            'ligplaats': {
                'columns': [
                    {
                        'include': 'gid',
                    },
                    {
                        'include': 'identificatie',
                    },
                    {
                        'name': 'status',
                        'type': 'StatusPlaats',
                        'null': False,
                    },
                    {
                        'include_group': 'common',
                    },
                    {
                        'include_group': 'adresseerbaarobject',
                    },
                    {
                        'name': 'wkb_geometry',
                        'type': 'geometry(Polygon,28992)',
                        'null': False,
                    },
                ],
                'primary_key': 'gid',
            },
            'standplaats': {
                'columns': [
                    {
                        'include': 'gid',
                    },
                    {
                        'include': 'identificatie',
                    },
                    {
                        'name': 'status',
                        'type': 'StatusPlaats',
                        'null': False,
                    },
                    {
                        'include_group': 'common',
                    },
                    {
                        'include_group': 'adresseerbaarobject',
                    },
                    {
                        'name': 'wkb_geometry',
                        'type': 'geometry(Polygon,28992)',
                        'null': False,
                    },
                ],
                'primary_key': 'gid',
            },
            'pand': {
                'columns': [
                    {
                        'include': 'gid',
                    },
                    {
                        'include': 'identificatie',
                    },
                    {
                        'name': 'oorspronkelijkbouwjaar',
                        'type': 'int',
                        'null': False,
                    },
                    {
                        'name': 'status',
                        'type': 'StatusPand',
                        'null': False,
                    },
                    {
                        'include_group': 'common',
                    },
                    {
                        'include_group': 'voorkomen',
                    },
                    {
                        'name': 'wkb_geometry',
                        'type': 'geometry(Polygon,28992)',
                        'null': False,
                    },
                ],
                'primary_key': 'gid',
            },

            'inonderzoek_woonplaats': {
                'columns': [
                    {
                        'include': 'gid',
                    },
                    {
                        'name': 'kenmerk',
                        'type': 'InOnderzoekWoonplaats',
                        'null': False,
                    },
                    {
                        'include': 'identificatie',
                    },
                    {
                        'include_group': 'inonderzoek_common',
                    },
                    {
                        'include_group': 'historieinonderzoek',
                    },
                ],
                'primary_key': 'gid',
            },
            'inonderzoek_openbareruimte': {
                'columns': [
                    {
                        'include': 'gid',
                    },
                    {
                        'name': 'kenmerk',
                        'type': 'InOnderzoekOpenbareRuimte',
                        'null': False,
                    },
                    {
                        'include': 'identificatie',
                    },
                    {
                        'include_group': 'inonderzoek_common',
                    },
                    {
                        'include_group': 'historieinonderzoek',
                    },
                ],
                'primary_key': 'gid',
            },
            'inonderzoek_nummeraanduiding': {
                'columns': [
                    {
                        'include': 'gid',
                    },
                    {
                        'name': 'kenmerk',
                        'type': 'InOnderzoekNummeraanduiding',
                        'null': False,
                    },
                    {
                        'include': 'identificatie',
                    },
                    {
                        'include_group': 'inonderzoek_common',
                    },
                    {
                        'include_group': 'historieinonderzoek',
                    },
                ],
                'primary_key': 'gid',
            },
            'inonderzoek_verblijfsobject': {
                'columns': [
                    {
                        'include': 'gid',
                    },
                    {
                        'name': 'kenmerk',
                        'type': 'InOnderzoekVerblijfsobject',
                        'null': False,
                    },
                    {
                        'include': 'identificatie',
                    },
                    {
                        'include_group': 'inonderzoek_common',
                    },
                    {
                        'include_group': 'historieinonderzoek',
                    },
                ],
                'primary_key': 'gid',
            },
            'inonderzoek_ligplaats': {
                'columns': [
                    {
                        'include': 'gid',
                    },
                    {
                        'name': 'kenmerk',
                        'type': 'InOnderzoekLigplaats',
                        'null': False,
                    },
                    {
                        'include': 'identificatie',
                    },
                    {
                        'include_group': 'inonderzoek_common',
                    },
                    {
                        'include_group': 'historieinonderzoek',
                    },
                ],
                'primary_key': 'gid',
            },
            'inonderzoek_standplaats': {
                'columns': [
                    {
                        'include': 'gid',
                    },
                    {
                        'name': 'kenmerk',
                        'type': 'InOnderzoekStandplaats',
                        'null': False,
                    },
                    {
                        'include': 'identificatie',
                    },
                    {
                        'include_group': 'inonderzoek_common',
                    },
                    {
                        'include_group': 'historieinonderzoek',
                    },
                ],
                'primary_key': 'gid',
            },
            'inonderzoek_pand': {
                'columns': [
                    {
                        'include': 'gid',
                    },
                    {
                        'name': 'kenmerk',
                        'type': 'InOnderzoekPand',
                        'null': False,
                    },
                    {
                        'include': 'identificatie',
                    },
                    {
                        'include_group': 'inonderzoek_common',
                    },
                    {
                        'include_group': 'historieinonderzoek',
                    },
                ],
                'primary_key': 'gid',
            },
        }

        for prefix in [
            'inactief',
            'nietbag',
        ]:
            for suffix in [
                'woonplaats',
                'openbareruimte',
                'nummeraanduiding',
                'verblijfsobject',
                'ligplaats',
                'standplaats',
                'pand',
            ]:
                key = '%s_%s' % (prefix, suffix)

                table_structure[key] = table_structure[suffix]

                table_enum[key] = table_enum[suffix]

        sqlfmt = {
            'table': sql.Identifier(table),
        }

        if table not in table_structure:
            raise Exception('Unsupported table: %s' % table)

        if table in table_enum:
            for name in table_enum[table]:
                if not self.enum_exists(name):
                    self.create_enum(name, enum_type[name])

        sqlstr = r'CREATE TABLE {table} ('

        def add_column(i, column):
            sqlstr = ''

            if 'include' in column:
                sqlstr += add_column(
                    i,
                    table_column[column['include']],
                )
            elif 'include_group' in column:
                for c in table_column_group[column['include_group']]:
                    sqlstr += add_column(
                        i,
                        c,
                    )
            else:
                if i > 0:
                    sqlstr += ', '

                sqlstr += '%(name)s %(type)s' % column

                if(
                    column['null'] is False and  # noqa: W504
                    column['type'] != 'serial'
                ):
                    sqlstr += ' NOT NULL'

                i += 1

            return sqlstr

        i = 0
        for column in table_structure[table]['columns']:
            sqlstr += add_column(i, column)

            i += 1

        if 'primary_key' in table_structure[table]:
            sqlstr += ', PRIMARY KEY ({primary_key})'

            key = 'primary_key'

            sqlfmt[key] = sql.Identifier(table_structure[table][key])

        sqlstr += r')'

        log.debug("sqlstr: %s" % sqlstr)
        log.debug("sqlfmt: %s" % sqlfmt)

        query = sql.SQL(sqlstr).format(**sqlfmt)

        log.debug("query: %s" % query.as_string(context=self.db.cursor))

        self.db.execute(query)

    def table_exists(self, table):
        query = """
            SELECT tablename
              FROM pg_tables
             WHERE tablename = %(table)s
               AND schemaname = %(schema)s
        """
        param = {
            'table': table,
            'schema': self.schema,
        }

        log.debug("query: %s" % query)
        log.debug("param: %s" % pprint.pformat(param))

        self.db.cursor.execute(query, param)

        if self.db.cursor.rowcount == 0:
            return False
        else:
            return True

    def copy_from_csv(self, csv_file, table, fields, delimiter, null):
        if not self.table_exists(table):
            self.create_table(table)
        elif self.truncate:
            self.truncate_table(table)

        log.info("Copying records from CSV file: %s" % csv_file)

        sqlfmt = {
            'table': sql.Identifier(table),
        }

        sqlstr = r'COPY {table} ('

        i = 0
        for field in fields:
            if i > 0:
                sqlstr += ', '

            column = 'col' + str(i)

            sqlstr += r'{' + column + r'}'

            sqlfmt[column] = sql.Identifier(field)

            i += 1

        sqlstr += ') FROM STDIN WITH'
        sqlstr += ' DELIMITER {delimiter}'
        sqlstr += ' NULL {null}'
        sqlstr += ' CSV HEADER'

        sqlfmt['delimiter'] = sql.Literal(delimiter)
        sqlfmt['null'] = sql.Literal(null)

        log.debug("sqlstr: %s" % sqlstr)
        log.debug("sqlfmt: %s" % sqlfmt)

        query = sql.SQL(sqlstr).format(**sqlfmt)

        log.debug("query: %s" % query.as_string(context=self.db.cursor))

        with open(csv_file, 'r') as f:
            self.db.cursor.copy_expert(
                query,
                f,
            )

    def process_gml(self, gml, convert_to=None):
        geom = ogr.CreateGeometryFromGML(
            etree.tostring(
                gml,
            ).decode()
        )

        log.debug("Processing GML: %s" % geom.GetGeometryName())

        if geom.Is3D():
            log.debug("Geometry is 3D, flattening to 2D")

            geom.FlattenTo2D()

        if (
            convert_to is not None and  # noqa: W504
            convert_to == 'multipolygon'
        ):
            log.debug("Converting to MultiPolygon")

            geom = ogr.ForceToMultiPolygon(geom)
        elif (
            convert_to is not None and  # noqa: W504
            convert_to == 'point'
        ):
            log.debug("Converting to Point")

            geom = geom.Centroid()

        if not geom.GetSpatialReference():
            log.debug("Converting SRID to 28992")

            geom.AssignSpatialReference(sr)

        wkb = geom.ExportToWkb().hex().upper()

        return wkb

    def process_levering_xml(self, tree, root, xml_file):
        log.info("Processing: BAG Extract Levering")

        table = 'nlx_bag_info'

        elements = root.xpath(
            (
                '.'
                '/xb:SelectieGegevens'
                '/selecties-extract:LVC-Extract'
                '/selecties-extract:StandTechnischeDatum'
            ),
            namespaces=xmlns,
        )

        if len(elements) == 0:
            raise Exception("Failed to find StandTechnischeDatum element")

        extract_datum = elements[0].text

        record = {
            'sleutel': 'extract_datum',
            'waarde': extract_datum,
        }

        key = 'sleutel'

        self.upsert_record(
            table,
            record,
            identifiers={
                key: record[key],
            }
        )

        with open(xml_file, 'rt') as f:
            data = f.read()

        record = {
            'sleutel': 'levering_xml',
            'waarde': data,
        }

        self.upsert_record(
            table,
            record,
            identifiers={
                key: record[key],
            }
        )

        self.db.commit(close=False)

    def process_gwr_element(
        self,
        element,
        row,
        name,
        key,
        xpath,
        required=True,
    ):
        results = element.xpath(
            xpath,
            namespaces=xmlns,
        )

        if len(results) == 0 and required is True:
            raise Exception(
                'Failed to find %s elements' % name
            )
        elif len(results) != 0:
            row[key] = results[0].text

        return row

    def process_gwr_xml(self, tree, root, xml_file):
        log.info("Processing: Gemeente Woonplaats Relatie")

        table = 'gemeente_woonplaats'

        elements = root.xpath(
            (
                '.'
                '/gwr-bestand:Product'
                '/gwr-product:GemeenteWoonplaatsRelatieProduct'
                '/gwr-product:GemeenteWoonplaatsRelatie'
            ),
            namespaces=xmlns,
        )

        if len(elements) == 0:
            raise Exception(
                'Failed to find GemeenteWoonplaatsRelatie elements'
            )

        csv_file = os.path.join(self.temp_dir, 'gemeente_woonplaats.csv')

        fields = [
            'begingeldigheid',
            'eindgeldigheid',
            'woonplaatscode',
            'gemeentecode',
            'status',
        ]

        delimiter = r';'
        null = r'\N'

        log.info("Writing CSV file: %s" % csv_file)

        with open(csv_file, 'w', newline='') as f:
            writer = csv.DictWriter(
                f,
                fieldnames=fields,
                delimiter=delimiter,
                lineterminator='\n',
            )

            writer.writeheader()

            for element in elements:
                row = {
                    'begingeldigheid': '',
                    'eindgeldigheid': null,
                    'woonplaatscode': '',
                    'gemeentecode': '',
                }

                # begindatumTijdvakGeldigheid
                xpath = (
                    '.'
                    '/gwr-product:tijdvakgeldigheid'
                    '/bagtypes:begindatumTijdvakGeldigheid'
                )

                row = self.process_gwr_element(
                    element,
                    row,
                    'begindatumTijdvakGeldigheid',
                    'begingeldigheid',
                    xpath,
                )

                # einddatumTijdvakGeldigheid
                xpath = (
                    '.'
                    '/gwr-product:tijdvakgeldigheid'
                    '/bagtypes:einddatumTijdvakGeldigheid'
                )

                row = self.process_gwr_element(
                    element,
                    row,
                    'einddatumTijdvakGeldigheid',
                    'eindgeldigheid',
                    xpath,
                    required=False,
                )

                # gerelateerdeWoonplaats
                xpath = (
                    '.'
                    '/gwr-product:gerelateerdeWoonplaats'
                    '/gwr-product:identificatie'
                )

                row = self.process_gwr_element(
                    element,
                    row,
                    'gerelateerdeWoonplaats',
                    'woonplaatscode',
                    xpath,
                )

                # gerelateerdeGemeente
                xpath = (
                    '.'
                    '/gwr-product:gerelateerdeGemeente'
                    '/gwr-product:identificatie'
                )

                row = self.process_gwr_element(
                    element,
                    row,
                    'gerelateerdeGemeente',
                    'gemeentecode',
                    xpath,
                )

                # status
                xpath = (
                    '.'
                    '/gwr-product:status'
                )

                row = self.process_gwr_element(
                    element,
                    row,
                    'status',
                    'status',
                    xpath,
                )

                writer.writerow(row)

        self.copy_from_csv(csv_file, table, fields, delimiter, null)

        BAGUtil.remove_temp_file(csv_file)

        self.db.commit(close=False)

    def process_in_onderzoek_element(
        self,
        object_type,
        object_kenmerk_element,
        element,
        row,
        name,
        key=None,
        xpath=None,
        required=True,
    ):
        if key is None:
            key = name.lower()

        if xpath is None:
            xpath = (
                '.'
                '/KenmerkInOnderzoek:%s'
                '/KenmerkInOnderzoek:%s'
            ) % (
                object_kenmerk_element[object_type],
                name,
            )

        results = element.xpath(
            xpath,
            namespaces=xmlns,
        )

        if len(results) == 0 and required is True:
            raise Exception(
                'Failed to find %s elements' % name
            )
        elif len(results) != 0:
            row[key] = results[0].text

        return row

    def process_in_onderzoek_historie_element(
        self,
        object_type,
        object_kenmerk_element,
        element,
        row,
        name,
        key=None,
        xpath=None,
        required=True,
    ):
        if xpath is None:
            xpath = (
                '.'
                '/KenmerkInOnderzoek:%s'
                '/KenmerkInOnderzoek:historieInOnderzoek'
                '/Historie:HistorieInOnderzoek'
                '/Historie:%s'
            ) % (
                object_kenmerk_element[object_type],
                name,
            )

        return self.process_in_onderzoek_element(
            object_type,
            object_kenmerk_element,
            element,
            row,
            name,
            key,
            xpath,
            required,
        )

    def process_in_onderzoek_beschikbaarlv_element(
        self,
        object_type,
        object_kenmerk_element,
        element,
        row,
        name,
        key=None,
        xpath=None,
        required=True,
    ):
        if xpath is None:
            xpath = (
                '.'
                '/KenmerkInOnderzoek:%s'
                '/KenmerkInOnderzoek:historieInOnderzoek'
                '/Historie:HistorieInOnderzoek'
                '/Historie:BeschikbaarLVInOnderzoek'
                '/Historie:%s'
            ) % (
                object_kenmerk_element[object_type],
                name,
            )

        return self.process_in_onderzoek_element(
            object_type,
            object_kenmerk_element,
            element,
            row,
            name,
            key,
            xpath,
            required,
        )

    def process_in_onderzoek_xml(
        self,
        tree,
        root,
        status_type,
        object_type,
        csv_file,
        delimiter,
        null,
    ):
        object_kenmerk_element = {
            'LIG': 'KenmerkLigplaatsInOnderzoek',
            'NUM': 'KenmerkNummeraanduidingInOnderzoek',
            'OPR': 'KenmerkOpenbareruimteInOnderzoek',
            'PND': 'KenmerkPandInOnderzoek',
            'STA': 'KenmerkStandplaatsInOnderzoek',
            'VBO': 'KenmerkVerblijfsobjectInOnderzoek',
            'WPL': 'KenmerkWoonplaatsInOnderzoek',
        }

        object_identificatie_element = {
            'LIG': 'identificatieVanLigplaats',
            'NUM': 'identificatieVanNummeraanduiding',
            'OPR': 'identificatieVanOpenbareruimte',
            'PND': 'identificatieVanPand',
            'STA': 'identificatieVanStandplaats',
            'VBO': 'identificatieVanVerblijfsobject',
            'WPL': 'identificatieVanWoonplaats',
        }

        elements = root.xpath(
            (
                '.'
                '/sl:standBestand'
                '/sl:stand'
                '/sl-bag-extract:kenmerkInOnderzoek'
            ),
            namespaces=xmlns,
        )

        if len(elements) == 0:
            log.warning('No kenmerkInOnderzoek elements found')

            return

        fields = [
            'kenmerk',
            'identificatie',
            'inonderzoek',
            'documentdatum',
            'documentnummer',
            'tijdstipregistratie',
            'eindregistratie',
            'begingeldigheid',
            'eindgeldigheid',
            'tijdstipregistratielv',
            'tijdstipeindregistratielv',
        ]

        log.info("Writing CSV file: %s" % csv_file)

        with open(csv_file, 'w', newline='') as f:
            writer = csv.DictWriter(
                f,
                fieldnames=fields,
                delimiter=delimiter,
                lineterminator='\n',
            )

            writer.writeheader()

            for element in elements:
                row = {
                    'kenmerk': '',
                    'identificatie': '',
                    'inonderzoek': '',
                    'documentdatum': '',
                    'documentnummer': '',
                    'tijdstipregistratie': '',
                    'eindregistratie': null,
                    'begingeldigheid': '',
                    'eindgeldigheid': null,
                    'tijdstipregistratielv': '',
                    'tijdstipeindregistratielv': null,
                }

                # kenmerk
                row = self.process_in_onderzoek_element(
                    object_type,
                    object_kenmerk_element,
                    element,
                    row,
                    'kenmerk',
                )

                # identificatie
                row = self.process_in_onderzoek_element(
                    object_type,
                    object_kenmerk_element,
                    element,
                    row,
                    object_identificatie_element[object_type],
                    'identificatie',
                )

                # inOnderzoek
                row = self.process_in_onderzoek_element(
                    object_type,
                    object_kenmerk_element,
                    element,
                    row,
                    'inOnderzoek',
                )

                if row['inonderzoek'] == 'J':
                    row['inonderzoek'] = True
                else:
                    row['inonderzoek'] = False

                # documentdatum
                row = self.process_in_onderzoek_element(
                    object_type,
                    object_kenmerk_element,
                    element,
                    row,
                    'documentdatum',
                )

                # documentnummer
                row = self.process_in_onderzoek_element(
                    object_type,
                    object_kenmerk_element,
                    element,
                    row,
                    'documentnummer',
                )

                # tijdstipRegistratie
                row = self.process_in_onderzoek_historie_element(
                    object_type,
                    object_kenmerk_element,
                    element,
                    row,
                    'tijdstipRegistratie',
                )

                # eindRegistratie
                row = self.process_in_onderzoek_historie_element(
                    object_type,
                    object_kenmerk_element,
                    element,
                    row,
                    'eindRegistratie',
                    required=False,
                )

                # beginGeldigheid
                row = self.process_in_onderzoek_historie_element(
                    object_type,
                    object_kenmerk_element,
                    element,
                    row,
                    'beginGeldigheid',
                )

                # eindGeldigheid
                row = self.process_in_onderzoek_historie_element(
                    object_type,
                    object_kenmerk_element,
                    element,
                    row,
                    'eindGeldigheid',
                    required=False,
                )

                # tijdstipRegistratieLV
                row = self.process_in_onderzoek_beschikbaarlv_element(
                    object_type,
                    object_kenmerk_element,
                    element,
                    row,
                    'tijdstipRegistratieLV',
                )

                # tijdstipEindRegistratieLV
                row = self.process_in_onderzoek_beschikbaarlv_element(
                    object_type,
                    object_kenmerk_element,
                    element,
                    row,
                    'tijdstipEindRegistratieLV',
                    required=False,
                )

                writer.writerow(row)

        return fields

    def process_bag_object_subelement(
        self,
        object_type,
        object_element,
        element,
        row,
        name,
        key=None,
        xpath=None,
        required=True,
        gml=False,
        convert_to=None,
        array=False,
    ):
        if key is None:
            key = name.lower()

        if xpath is None:
            xpath = (
                '.'
                '/Objecten:%s'
                '/Objecten:%s'
            ) % (
                object_element[object_type],
                name,
            )

        results = element.xpath(
            xpath,
            namespaces=xmlns,
        )

        if len(results) == 0 and required is True:
            raise Exception(
                'Failed to find %s elements' % name
            )
        elif len(results) == 1 and array is False:
            if gml is True:
                row[key] = self.process_gml(
                    results[0],
                    convert_to,
                )
            else:
                row[key] = results[0].text
        elif len(results) >= 1 and array is True:
            value = '{'

            i = 0
            for result in results:
                if i > 0:
                    value += ','

                value += result.text

                i += 1

            value += '}'

            row[key] = value

        return row

    def process_bag_object_voorkomen_subelement(
        self,
        object_type,
        object_element,
        element,
        row,
        name,
        key=None,
        xpath=None,
        required=True,
        gml=False,
        convert_to=None,
        array=False,
    ):
        if xpath is None:
            xpath = (
                '.'
                '/Objecten:%s'
                '/Objecten:voorkomen'
                '/Historie:Voorkomen'
                '/Historie:%s'
            ) % (
                object_element[object_type],
                name,
            )

        return self.process_bag_object_subelement(
            object_type,
            object_element,
            element,
            row,
            name,
            key,
            xpath,
            required,
        )

    def process_bag_object_beschikbaarlv_subelement(
        self,
        object_type,
        object_element,
        element,
        row,
        name,
        key=None,
        xpath=None,
        required=True,
        gml=False,
        convert_to=None,
        array=False,
    ):
        if xpath is None:
            xpath = (
                '.'
                '/Objecten:%s'
                '/Objecten:voorkomen'
                '/Historie:Voorkomen'
                '/Historie:BeschikbaarLV'
                '/Historie:%s'
            ) % (
                object_element[object_type],
                name,
            )

        return self.process_bag_object_subelement(
            object_type,
            object_element,
            element,
            row,
            name,
            key,
            xpath,
            required,
        )

    def process_bag_object_element(
        self,
        object_type,
        object_element,
        element,
        row,
    ):
        # identificatie
        row = self.process_bag_object_subelement(
            object_type,
            object_element,
            element,
            row,
            'identificatie',
        )

        # naam
        if object_type in [
            'WPL',
            'OPR',
        ]:
            row = self.process_bag_object_subelement(
                object_type,
                object_element,
                element,
                row,
                'naam',
            )

        if object_type == 'OPR':
            # type
            row = self.process_bag_object_subelement(
                object_type,
                object_element,
                element,
                row,
                'type',
            )

        # huisnummer
        # huisletter
        # huisnummertoevoeging
        # postcode
        # typeAdresseerbaarObject
        if object_type == 'NUM':
            row = self.process_bag_object_subelement(
                object_type,
                object_element,
                element,
                row,
                'huisnummer',
            )

            row = self.process_bag_object_subelement(
                object_type,
                object_element,
                element,
                row,
                'huisletter',
                required=False,
            )

            row = self.process_bag_object_subelement(
                object_type,
                object_element,
                element,
                row,
                'huisnummertoevoeging',
                required=False,
            )

            row = self.process_bag_object_subelement(
                object_type,
                object_element,
                element,
                row,
                'postcode',
                required=False,
            )

            row = self.process_bag_object_subelement(
                object_type,
                object_element,
                element,
                row,
                'typeAdresseerbaarObject',
            )

        # geometrie
        if object_type == 'WPL':
            xpath = (
                '.'
                '/Objecten:%s'
                '/Objecten:geometrie'
                '/Objecten:vlak'
                '/*'
                ' | '
                '.'
                '/Objecten:%s'
                '/Objecten:geometrie'
                '/Objecten:multivlak'
                '/*'
            ) % (
                object_element[object_type],
                object_element[object_type],
            )

            row = self.process_bag_object_subelement(
                object_type,
                object_element,
                element,
                row,
                'geometrie',
                'wkb_geometry',
                xpath,
                gml=True,
                convert_to='multipolygon',
            )
        elif object_type == 'VBO':
            xpath = (
                '.'
                '/Objecten:%s'
                '/Objecten:geometrie'
                '/Objecten:punt'
                '/*'
                ' | '
                '.'
                '/Objecten:%s'
                '/Objecten:geometrie'
                '/Objecten:vlak'
                '/*'
            ) % (
                object_element[object_type],
                object_element[object_type],
            )

            row = self.process_bag_object_subelement(
                object_type,
                object_element,
                element,
                row,
                'geometrie',
                'wkb_geometry',
                xpath,
                gml=True,
                convert_to='point',
            )
        elif object_type in [
            'LIG',
            'STA',
            'PND',
        ]:
            xpath = (
                '.'
                '/Objecten:%s'
                '/Objecten:geometrie'
                '/*'
            ) % (
                object_element[object_type],
            )

            row = self.process_bag_object_subelement(
                object_type,
                object_element,
                element,
                row,
                'geometrie',
                'wkb_geometry',
                xpath,
                gml=True,
            )

        # gebruiksdoel
        # oppervlakte
        if object_type == 'VBO':
            row = self.process_bag_object_subelement(
                object_type,
                object_element,
                element,
                row,
                'gebruiksdoel',
                array=True,
            )

            row = self.process_bag_object_subelement(
                object_type,
                object_element,
                element,
                row,
                'oppervlakte',
            )

        # oorspronkelijkBouwjaar
        if object_type == 'PND':
            row = self.process_bag_object_subelement(
                object_type,
                object_element,
                element,
                row,
                'oorspronkelijkBouwjaar',
            )

        # status
        row = self.process_bag_object_subelement(
            object_type,
            object_element,
            element,
            row,
            'status',
        )

        # geconstateerd
        row = self.process_bag_object_subelement(
            object_type,
            object_element,
            element,
            row,
            'geconstateerd',
        )

        if row['geconstateerd'] == 'J':
            row['geconstateerd'] = True
        else:
            row['geconstateerd'] = False

        # documentdatum
        row = self.process_bag_object_subelement(
            object_type,
            object_element,
            element,
            row,
            'documentdatum',
        )

        # documentnummer
        row = self.process_bag_object_subelement(
            object_type,
            object_element,
            element,
            row,
            'documentnummer',
        )

        # ligtIn
        if object_type in [
            'OPR',
            'NUM',
        ]:
            if object_type == 'OPR':
                required = True
            elif object_type == 'NUM':
                required = False

            xpath = (
                '.'
                '/Objecten:%s'
                '/Objecten:ligtIn'
                '/Objecten-ref:WoonplaatsRef'
            ) % (
                object_element[object_type],
            )

            row = self.process_bag_object_subelement(
                object_type,
                object_element,
                element,
                row,
                'WoonplaatsRef',
                xpath=xpath,
                required=required
            )

        # maaktDeelUitVan
        if object_type == 'VBO':
            xpath = (
                '.'
                '/Objecten:%s'
                '/Objecten:maaktDeelUitVan'
                '/Objecten-ref:PandRef'
            ) % (
                object_element[object_type],
            )

            row = self.process_bag_object_subelement(
                object_type,
                object_element,
                element,
                row,
                'PandRef',
                xpath=xpath,
                array=True,
            )

        # heeftAlsHoofdadres
        # heeftAlsNevenadres
        if object_type in [
            'VBO',
            'LIG',
            'STA',
        ]:
            xpath = (
                '.'
                '/Objecten:%s'
                '/Objecten:heeftAlsHoofdadres'
                '/Objecten-ref:NummeraanduidingRef'
            ) % (
                object_element[object_type],
            )

            row = self.process_bag_object_subelement(
                object_type,
                object_element,
                element,
                row,
                'heeftAlsHoofdadres',
                'hoofdadresnummeraanduidingref',
                xpath=xpath,
            )

            xpath = (
                '.'
                '/Objecten:%s'
                '/Objecten:heeftAlsNevenadres'
                '/Objecten-ref:NummeraanduidingRef'
            ) % (
                object_element[object_type],
            )

            row = self.process_bag_object_subelement(
                object_type,
                object_element,
                element,
                row,
                'heeftAlsNevenadres',
                'nevenadresnummeraanduidingref',
                xpath=xpath,
                required=False,
                array=True,
            )

        # voorkomenidentificatie
        row = self.process_bag_object_voorkomen_subelement(
            object_type,
            object_element,
            element,
            row,
            'voorkomenidentificatie',
        )

        # beginGeldigheid
        row = self.process_bag_object_voorkomen_subelement(
            object_type,
            object_element,
            element,
            row,
            'beginGeldigheid',
        )

        # eindGeldigheid
        row = self.process_bag_object_voorkomen_subelement(
            object_type,
            object_element,
            element,
            row,
            'eindGeldigheid',
            required=False,
        )

        # tijdstipRegistratie
        row = self.process_bag_object_voorkomen_subelement(
            object_type,
            object_element,
            element,
            row,
            'tijdstipRegistratie',
        )

        # eindRegistratie
        row = self.process_bag_object_voorkomen_subelement(
            object_type,
            object_element,
            element,
            row,
            'eindRegistratie',
            required=False,
        )

        # tijdstipInactief
        row = self.process_bag_object_voorkomen_subelement(
            object_type,
            object_element,
            element,
            row,
            'tijdstipInactief',
            required=False,
        )

        # tijdstipRegistratieLV
        row = self.process_bag_object_beschikbaarlv_subelement(
            object_type,
            object_element,
            element,
            row,
            'tijdstipRegistratieLV',
        )

        # tijdstipEindRegistratieLV
        row = self.process_bag_object_beschikbaarlv_subelement(
            object_type,
            object_element,
            element,
            row,
            'tijdstipEindRegistratieLV',
            required=False,
        )

        # tijdstipInactiefLV
        row = self.process_bag_object_beschikbaarlv_subelement(
            object_type,
            object_element,
            element,
            row,
            'tijdstipInactiefLV',
            required=False,
        )

        # tijdstipNietBagLV
        row = self.process_bag_object_beschikbaarlv_subelement(
            object_type,
            object_element,
            element,
            row,
            'tijdstipNietBagLV',
            required=False,
        )

        # verkorteNaam
        if object_type == 'OPR':
            row = self.process_bag_object_subelement(
                object_type,
                object_element,
                element,
                row,
                'verkorteNaam',
                required=False,
            )

        # ligtAan
        if object_type == 'NUM':
            xpath = (
                '.'
                '/Objecten:%s'
                '/Objecten:ligtAan'
                '/Objecten-ref:OpenbareRuimteRef'
            ) % (
                object_element[object_type],
            )

            row = self.process_bag_object_subelement(
                object_type,
                object_element,
                element,
                row,
                'OpenbareRuimteRef',
                xpath=xpath,
            )

        return row

    def process_bag_object_xml(
        self,
        tree,
        root,
        status_type,
        object_type,
        csv_file,
        delimiter,
        null,
    ):
        object_element = {
            'LIG': 'Ligplaats',
            'NUM': 'Nummeraanduiding',
            'OPR': 'OpenbareRuimte',
            'PND': 'Pand',
            'STA': 'Standplaats',
            'VBO': 'Verblijfsobject',
            'WPL': 'Woonplaats',
        }

        elements = root.xpath(
            (
                '.'
                '/sl:standBestand'
                '/sl:stand'
                '/sl-bag-extract:bagObject'
            ),
            namespaces=xmlns,
        )

        if len(elements) == 0:
            log.warning('No bagObject elements found')

            return

        if object_type == 'WPL':
            fields = [
                'identificatie',
                'naam',
                'wkb_geometry',
                'status',
                'geconstateerd',
                'documentdatum',
                'documentnummer',
                'voorkomenidentificatie',
                'begingeldigheid',
                'eindgeldigheid',
                'tijdstipregistratie',
                'eindregistratie',
                'tijdstipinactief',
                'tijdstipregistratielv',
                'tijdstipeindregistratielv',
                'tijdstipinactieflv',
                'tijdstipnietbaglv',
            ]
        elif object_type == 'OPR':
            fields = [
                'identificatie',
                'naam',
                'type',
                'status',
                'geconstateerd',
                'documentdatum',
                'documentnummer',
                'woonplaatsref',
                'voorkomenidentificatie',
                'begingeldigheid',
                'eindgeldigheid',
                'tijdstipregistratie',
                'eindregistratie',
                'tijdstipinactief',
                'tijdstipregistratielv',
                'tijdstipeindregistratielv',
                'tijdstipinactieflv',
                'tijdstipnietbaglv',
                'verkortenaam',
            ]
        elif object_type == 'NUM':
            fields = [
                'identificatie',
                'huisnummer',
                'huisletter',
                'huisnummertoevoeging',
                'postcode',
                'typeadresseerbaarobject',
                'status',
                'geconstateerd',
                'documentdatum',
                'documentnummer',
                'woonplaatsref',
                'voorkomenidentificatie',
                'begingeldigheid',
                'eindgeldigheid',
                'tijdstipregistratie',
                'eindregistratie',
                'tijdstipinactief',
                'tijdstipregistratielv',
                'tijdstipeindregistratielv',
                'tijdstipinactieflv',
                'tijdstipnietbaglv',
                'openbareruimteref',
            ]
        elif object_type == 'VBO':
            fields = [
                'identificatie',
                'wkb_geometry',
                'gebruiksdoel',
                'oppervlakte',
                'status',
                'geconstateerd',
                'documentdatum',
                'documentnummer',
                'pandref',
                'hoofdadresnummeraanduidingref',
                'nevenadresnummeraanduidingref',
                'voorkomenidentificatie',
                'begingeldigheid',
                'eindgeldigheid',
                'tijdstipregistratie',
                'eindregistratie',
                'tijdstipinactief',
                'tijdstipregistratielv',
                'tijdstipeindregistratielv',
                'tijdstipinactieflv',
                'tijdstipnietbaglv',
            ]
        elif object_type == 'LIG':
            fields = [
                'identificatie',
                'status',
                'wkb_geometry',
                'geconstateerd',
                'documentdatum',
                'documentnummer',
                'hoofdadresnummeraanduidingref',
                'nevenadresnummeraanduidingref',
                'voorkomenidentificatie',
                'begingeldigheid',
                'eindgeldigheid',
                'tijdstipregistratie',
                'eindregistratie',
                'tijdstipinactief',
                'tijdstipregistratielv',
                'tijdstipeindregistratielv',
                'tijdstipinactieflv',
                'tijdstipnietbaglv',
            ]
        elif object_type == 'STA':
            fields = [
                'identificatie',
                'status',
                'wkb_geometry',
                'geconstateerd',
                'documentdatum',
                'documentnummer',
                'hoofdadresnummeraanduidingref',
                'nevenadresnummeraanduidingref',
                'voorkomenidentificatie',
                'begingeldigheid',
                'eindgeldigheid',
                'tijdstipregistratie',
                'eindregistratie',
                'tijdstipinactief',
                'tijdstipregistratielv',
                'tijdstipeindregistratielv',
                'tijdstipinactieflv',
                'tijdstipnietbaglv',
            ]
        elif object_type == 'PND':
            fields = [
                'identificatie',
                'wkb_geometry',
                'oorspronkelijkbouwjaar',
                'status',
                'geconstateerd',
                'documentdatum',
                'documentnummer',
                'voorkomenidentificatie',
                'begingeldigheid',
                'eindgeldigheid',
                'tijdstipregistratie',
                'eindregistratie',
                'tijdstipinactief',
                'tijdstipregistratielv',
                'tijdstipeindregistratielv',
                'tijdstipinactieflv',
                'tijdstipnietbaglv',
            ]

        log.info("Writing CSV file: %s" % csv_file)

        with open(csv_file, 'w', newline='') as f:
            writer = csv.DictWriter(
                f,
                fieldnames=fields,
                delimiter=delimiter,
                lineterminator='\n',
            )

            writer.writeheader()

            for element in elements:
                row = {
                    'identificatie': '',
                    'status': '',
                    'geconstateerd': '',
                    'documentdatum': '',
                    'documentnummer': '',
                    'voorkomenidentificatie': '',
                    'begingeldigheid': '',
                    'eindgeldigheid': null,
                    'tijdstipregistratie': '',
                    'eindregistratie': null,
                    'tijdstipinactief': null,
                    'tijdstipregistratielv': '',
                    'tijdstipeindregistratielv': null,
                    'tijdstipinactieflv': null,
                    'tijdstipnietbaglv': null,
                }

                if object_type == 'WPL':
                    row['naam'] = ''
                    row['wkb_geometry'] = ''
                elif object_type == 'OPR':
                    row['naam'] = ''
                    row['type'] = ''
                    row['woonplaatsref'] = ''
                    row['verkortenaam'] = null
                elif object_type == 'NUM':
                    row['huisnummer'] = ''
                    row['huisletter'] = null
                    row['huisnummertoevoeging'] = null
                    row['postcode'] = null
                    row['typeadresseerbaarobject'] = ''
                    row['woonplaatsref'] = null
                    row['openbareruimteref'] = ''
                elif object_type == 'VBO':
                    row['wkb_geometry'] = ''
                    row['gebruiksdoel'] = []
                    row['oppervlakte'] = ''
                    row['pandref'] = []
                    row['hoofdadresnummeraanduidingref'] = ''
                    row['nevenadresnummeraanduidingref'] = null
                elif object_type == 'LIG':
                    row['wkb_geometry'] = ''
                    row['hoofdadresnummeraanduidingref'] = ''
                    row['nevenadresnummeraanduidingref'] = null
                elif object_type == 'STA':
                    row['wkb_geometry'] = ''
                    row['hoofdadresnummeraanduidingref'] = ''
                    row['nevenadresnummeraanduidingref'] = null
                elif object_type == 'PND':
                    row['wkb_geometry'] = ''
                    row['oorspronkelijkbouwjaar'] = ''

                row = self.process_bag_object_element(
                    object_type,
                    object_element,
                    element,
                    row,
                )

                writer.writerow(row)

        return fields

    def process_stand_xml(self, tree, root, xml_file):
        log.info("Processing: BAG Stand")

        filename = os.path.basename(xml_file)

        match = re.search(
            r'^\d{4}(IA|IO|NB|)(LIG|NUM|OPR|PND|STA|VBO|WPL)\d{8}\-\d{6}\.xml$',
            filename,
        )

        if not match:
            raise Exception('Failed to parse filename: %s' % filename)

        (
            status_type,
            object_type,
        ) = match.groups()

        log.debug("status_type: %s" % status_type)
        log.debug("object_type: %s" % object_type)

        object_table = {
            'LIG': 'ligplaats',
            'NUM': 'nummeraanduiding',
            'OPR': 'openbareruimte',
            'PND': 'pand',
            'STA': 'standplaats',
            'VBO': 'verblijfsobject',
            'WPL': 'woonplaats',
        }

        if status_type == '':
            # Normal objects

            table = object_table[object_type]
        elif status_type == 'IA':
            # Inactive (Inactief)

            table = 'inactief_' + object_table[object_type]
        elif status_type == 'IO':
            # Under investigation (InOnderzoek)

            table = 'inonderzoek_' + object_table[object_type]
        elif status_type == 'NB':
            # Not BAG (NietBag)

            table = 'nietbag_' + object_table[object_type]
        else:
            raise Exception("Unsupported status objects: %s (%s)" % (status_type, object_type))

        csv_file = os.path.join(self.temp_dir, '%s.csv' % table)

        fields = []
        delimiter = r';'
        null = r'\N'

        if status_type == 'IO':
            fields = self.process_in_onderzoek_xml(
                tree,
                root,
                status_type,
                object_type,
                csv_file,
                delimiter,
                null,
            )
        else:
            fields = self.process_bag_object_xml(
                tree,
                root,
                status_type,
                object_type,
                csv_file,
                delimiter,
                null,
            )

        if fields is not None:
            self.copy_from_csv(csv_file, table, fields, delimiter, null)

            BAGUtil.remove_temp_file(csv_file)

            self.db.commit(close=False)

    def process_xml_file(self, xml_file):
        log.info("Processing XML file: %s" % xml_file)

        tree = etree.parse(xml_file)

        root = tree.getroot()

        log.debug("root: %s" % root.tag)

        if root.tag == '{%s}BAG-Extract-Levering' % xmlns['xb']:
            self.process_levering_xml(tree, root, xml_file)
        elif root.tag == '{%s}BAG-GWR-Deelbestand-LVC' % xmlns['gwr-bestand']:
            self.process_gwr_xml(tree, root, xml_file)
        elif root.tag == '{%s}bagStand' % xmlns['sl-bag-extract']:
            self.process_stand_xml(tree, root, xml_file)
        else:
            log.warning("Skipping unsupported file: %s" % xml_file)

        BAGUtil.remove_temp_file(xml_file)

    def process_zip_file(self, zip_file):
        extracted = BAGUtil.extract_zip_file(zip_file, self.temp_dir)

        BAGUtil.remove_temp_file(zip_file)

        for entry in extracted:
            if(
                os.path.isdir(entry) or                     # noqa: W504
                os.path.basename(entry).startswith('.') or  # noqa: W504
                not os.path.exists(entry)
            ):
                log.info("Not processing: %s" % entry)

                if os.path.isdir(entry) and os.path.exists(entry):
                    BAGUtil.remove_temp_dir(entry)
                elif os.path.exists(entry):
                    BAGUtil.remove_temp_file(entry)

                continue

            if entry.endswith('.xml'):
                self.process_xml_file(entry)
            elif entry.endswith('.zip'):
                self.process_zip_file(entry)
            else:
                log.warning("Skipping unsupported file: %s" % entry)

                BAGUtil.remove_temp_file(entry)

    def process_input_file(self, input_file):
        if self.multiprocessing:
            self.db_connect()

        if input_file.endswith('.xml'):
            self.process_xml_file(input_file)
        elif input_file.endswith('.zip'):
            zip_content = BAGUtil.zip_file_content(input_file)

            for entry in zip_content:
                if (
                    entry.startswith('.') or  # noqa: W504
                    entry.startswith('_')
                ):
                    continue

                if entry.endswith('.xml'):
                    xml_file = BAGUtil.extract_from_zip_file(
                        entry,
                        input_file,
                        self.temp_dir,
                    )

                    self.process_xml_file(xml_file)
                else:
                    log.warning("Ignoring entry: %s" % entry)
        else:
            log.warning("Skipping unsupported file: %s" % input_file)

        if self.multiprocessing:
            self.db_disconnect()

    def process_input_zip_file(self, packet):
        temp_file = os.path.join(self.temp_dir, packet.data['name'])

        log.info(
            "Extracting %s from %s to %s" % (
                packet.data['name'],
                packet.data['file_path'],
                temp_file,
            )
        )

        with zipfile.ZipFile(packet.data['file_path']) as z:
            with open(temp_file, 'wb') as f:
                with z.open(packet.data['name']) as zf:
                    while True:
                        buffer = zf.read(self.buffer_size)
                        if not buffer:
                            break
                        f.write(buffer)

        return temp_file

    def process_xml_file_packet(self, packet):
        temp_xml_file = self.process_input_zip_file(packet)

        self.process_xml_file(temp_xml_file)

        return packet

    def process_zip_file_packet(self, packet):
        temp_zip_file = self.process_input_zip_file(packet)

        self.process_zip_file(temp_zip_file)

        return packet

    def write(self, packet):
        if packet.data is None or len(packet.data) == 0:
            return packet

        if 'file_list' in packet.data:
            with multiprocessing.Pool(
                processes=self.workers,
                maxtasksperchild=1,
            ) as p:
                p.map(
                    self.process_input_file,
                    packet.data['file_list'],
                )

            return packet
        else:
            if (
                (
                    not self.process_inactief and  # noqa: W504
                    re.search(
                        r'^\d{4}Inactief\d{8}\.zip$',
                        packet.data['name']
                    )
                ) or  # noqa: W504
                (
                    not self.process_in_onderzoek and  # noqa: W504
                    re.search(
                        r'^\d{4}InOnderzoek\d{8}\.zip$',
                        packet.data['name']
                    )
                ) or  # noqa: W504
                (
                    not self.process_niet_bag and  # noqa: W504
                    re.search(
                        r'^\d{4}NietBag\d{8}\.zip$',
                        packet.data['name']
                    )
                ) or  # noqa: W504
                (
                    not self.process_lig and  # noqa: W504
                    re.search(
                        r'^\d{4}LIG\d{8}\.zip$',
                        packet.data['name']
                    )
                ) or  # noqa: W504
                (
                    not self.process_num and  # noqa: W504
                    re.search(
                        r'^\d{4}NUM\d{8}\.zip$',
                        packet.data['name']
                    )
                ) or  # noqa: W504
                (
                    not self.process_opr and  # noqa: W504
                    re.search(
                        r'^\d{4}OPR\d{8}\.zip$',
                        packet.data['name']
                    )
                ) or  # noqa: W504
                (
                    not self.process_pnd and  # noqa: W504
                    re.search(
                        r'^\d{4}PND\d{8}\.zip$',
                        packet.data['name']
                    )
                ) or  # noqa: W504
                (
                    not self.process_sta and  # noqa: W504
                    re.search(
                        r'^\d{4}STA\d{8}\.zip$',
                        packet.data['name']
                    )
                ) or  # noqa: W504
                (
                    not self.process_vbo and  # noqa: W504
                    re.search(
                        r'^\d{4}VBO\d{8}\.zip$',
                        packet.data['name']
                    )
                ) or  # noqa: W504
                (
                    not self.process_wpl and  # noqa: W504
                    re.search(
                        r'^\d{4}WPL\d{8}\.zip$',
                        packet.data['name']
                    )
                ) or  # noqa: W504
                (
                    not self.process_gwr and  # noqa: W504
                    re.search(
                        r'^GEM\-WPL\-RELATIE\-\d{8}\.zip$',
                        packet.data['name']
                    )
                ) or  # noqa: W504
                (
                    not self.process_levering and  # noqa: W504
                    re.search(
                        r'^Leveringsdocument\-BAG\-Extract\.xml$',
                        packet.data['name']
                    )
                )
            ):
                log.info("Skipping processing of: %s" % packet.data['name'])

                return packet

            if packet.data['name'].endswith('.xml'):
                return self.process_xml_file_packet(packet)
            elif packet.data['name'].endswith('.zip'):
                return self.process_zip_file_packet(packet)
            else:
                log.warning("Skipping unsupported file: %s" % packet.data['name'])

                return packet
