import os
import re
from functools import partial

from lxml import etree
from psycopg2 import sql

from stetl.bagutil import BAGUtil
from stetl.outputs.bagoutput import BAGOutput, xmlns
from stetl.util import Util
from stetl.packet import FORMAT

log = Util.get_log('bagmutoutput')

xmlns.update({
    'Mutaties': (
        'http://www.kadaster.nl/schemas/lvbag/extract-deelbestand-mutaties-lvc/v20200601'
    ),
    'ml': (
        'http://www.kadaster.nl/schemas/mutatielevering-generiek/1.0'
    ),
    'mlm': (
        'http://www.kadaster.nl/schemas/lvbag/extract-deelbestand-mutaties-lvc/v20200601'
    ),
})


class BAGMutOutput(BAGOutput):
    """Process BAG 2.0 Extract mutation files"""

    def __init__(self, configdict, section, consumes=FORMAT.record):
        super().__init__(configdict, section, consumes=consumes)
        self.db = None

    def create_table(self, table):
        log.info("Creating table: %s" % table)

        enum_type = {
            'gebruiksdoelverblijfsobject': [
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
            'nummeraanduidingstatus': [
                'Naamgeving uitgegeven',
                'Naamgeving ingetrokken',
            ],
            'pandstatus': [
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
            'ligplaatsstatus': [
                'Plaats aangewezen',
                'Plaats ingetrokken',
            ],
            'verblijfsobjectstatus': [
                'Verblijfsobject gevormd',
                'Niet gerealiseerd verblijfsobject',
                'Verblijfsobject in gebruik (niet ingemeten)',
                'Verblijfsobject in gebruik',
                'Verbouwing verblijfsobject',
                'Verblijfsobject ingetrokken',
                'Verblijfsobject buiten gebruik',
                'Verblijfsobject ten onrechte opgevoerd',
            ],
            'woonplaatsstatus': [
                'Woonplaats aangewezen',
                'Woonplaats ingetrokken',
            ],
            'typeadresseerbaarobject': [
                'Verblijfsobject',
                'Standplaats',
                'Ligplaats',
            ],
            'openbareruimtetype': [
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

            'MutatieGroep': [
                'toevoeging',
                'wijziging',
            ],
            'MutatieToestand': [
                'was',
                'wordt',
            ],
        }

        table_enum = {
            'woonplaats': [
                'woonplaatsstatus',
            ],
            'openbareruimte': [
                'openbareruimtetype',
                'nummeraanduidingstatus',
            ],
            'nummeraanduiding': [
                'typeadresseerbaarobject',
                'nummeraanduidingstatus',
            ],
            'verblijfsobject': [
                'verblijfsobjectstatus',
            ],
            'ligplaats': [
                'ligplaatsstatus',
            ],
            'standplaats': [
                'ligplaatsstatus',
            ],
            'pand': [
                'pandstatus',
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

            'mutaties_woonplaats': [
                'MutatieGroep',
                'MutatieToestand',
            ],
            'mutaties_openbareruimte': [
                'MutatieGroep',
                'MutatieToestand',
            ],
            'mutaties_nummeraanduiding': [
                'MutatieGroep',
                'MutatieToestand',
            ],
            'mutaties_verblijfsobject': [
                'MutatieGroep',
                'MutatieToestand',
            ],
            'mutaties_ligplaats': [
                'MutatieGroep',
                'MutatieToestand',
            ],
            'mutaties_standplaats': [
                'MutatieGroep',
                'MutatieToestand',
            ],
            'mutaties_pand': [
                'MutatieGroep',
                'MutatieToestand',
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
                'type': 'varchar(16)',
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
                    'type': 'char(16)',
                    'null': False,
                },
                {
                    'include_group': 'voorkomen',
                },
                {
                    'name': 'nevenadresnummeraanduidingref',
                    'type': 'char(16)[]',
                    'null': True,
                },
            ],
            'mutatie': [
                {
                    'name': 'mutatiegroep',
                    'type': 'MutatieGroep',
                    'null': False,
                },
                {
                    'name': 'toestand',
                    'type': 'MutatieToestand',
                    'null': False,
                },
            ],
        }

        if not table.startswith("mutaties_"):
            raise Exception

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
                        'type': 'woonplaatsstatus',
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
                        'type': 'openbareruimtetype',
                        'null': False,
                    },
                    {
                        'name': 'status',
                        'type': 'nummeraanduidingstatus',
                        'null': False,
                    },
                    {
                        'include_group': 'common',
                    },
                    {
                        'name': 'woonplaatsref',
                        'type': 'char(4)',
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
                        'type': 'char(6)',
                        'null': True,
                    },
                    {
                        'name': 'typeadresseerbaarobject',
                        'type': 'typeadresseerbaarobject',
                        'null': False,
                    },
                    {
                        'name': 'status',
                        'type': 'nummeraanduidingstatus',
                        'null': False,
                    },
                    {
                        'include_group': 'common',
                    },
                    {
                        'name': 'woonplaatsref',
                        'type': 'char(4)',
                        'null': True,
                    },
                    {
                        'include_group': 'voorkomen',
                    },
                    {
                        'name': 'openbareruimteref',
                        'type': 'char(16)',
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
                        'type': 'verblijfsobjectstatus',
                        'null': False,
                    },
                    {
                        'include_group': 'common',
                    },
                    {
                        'name': 'pandref',
                        'type': 'char(16)[]',
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
                        'type': 'ligplaatsstatus',
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
                        'type': 'ligplaatsstatus',
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
                        'type': 'pandstatus',
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

            'mutaties_woonplaats': {
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
                        'type': 'woonplaatsstatus',
                        'null': False,
                    },
                    {
                        'include_group': 'common',
                    },
                    {
                        'include_group': 'voorkomen',
                    },
                    {
                        'include_group': 'mutatie',
                    },
                    {
                        'name': 'wkb_geometry',
                        'type': 'geometry(MultiPolygon,28992)',
                        'null': False,
                    },
                ],
                'primary_key': 'gid',
            },
            'mutaties_openbareruimte': {
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
                        'type': 'openbareruimtetype',
                        'null': False,
                    },
                    {
                        'name': 'status',
                        'type': 'nummeraanduidingstatus',
                        'null': False,
                    },
                    {
                        'include_group': 'common',
                    },
                    {
                        'include_group': 'voorkomen',
                    },
                    {
                        'name': 'woonplaatsref',
                        'type': 'char(4)',
                        'null': False,
                    },
                    {
                        'include_group': 'mutatie',
                    },
                    {
                        'name': 'verkortenaam',
                        'type': 'varchar(24)',
                        'null': True,
                    },
                ],
                'primary_key': 'gid',
            },
            'mutaties_nummeraanduiding': {
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
                        'type': 'char(6)',
                        'null': True,
                    },
                    {
                        'name': 'typeadresseerbaarobject',
                        'type': 'typeadresseerbaarobject',
                        'null': False,
                    },
                    {
                        'name': 'status',
                        'type': 'nummeraanduidingstatus',
                        'null': False,
                    },
                    {
                        'include_group': 'common',
                    },
                    {
                        'include_group': 'voorkomen',
                    },
                    {
                        'name': 'woonplaatsref',
                        'type': 'char(4)',
                        'null': True,
                    },
                    {
                        'include_group': 'mutatie',
                    },
                    {
                        'name': 'openbareruimteref',
                        'type': 'char(16)',
                        'null': False,
                    },
                ],
                'primary_key': 'gid',
            },
            'mutaties_verblijfsobject': {
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
                        'type': 'verblijfsobjectstatus',
                        'null': False,
                    },
                    {
                        'include_group': 'common',
                    },
                    {
                        'name': 'pandref',
                        'type': 'char(16)[]',
                        'null': False,
                    },
                    {
                        'include_group': 'adresseerbaarobject',
                    },
                    {
                        'include_group': 'mutatie',
                    },
                    {
                        'name': 'wkb_geometry',
                        'type': 'geometry(Point,28992)',
                        'null': False,
                    },
                ],
                'primary_key': 'gid',
            },
            'mutaties_ligplaats': {
                'columns': [
                    {
                        'include': 'gid',
                    },
                    {
                        'include': 'identificatie',
                    },
                    {
                        'name': 'status',
                        'type': 'ligplaatsstatus',
                        'null': False,
                    },
                    {
                        'include_group': 'common',
                    },
                    {
                        'include_group': 'adresseerbaarobject',
                    },
                    {
                        'include_group': 'mutatie',
                    },
                    {
                        'name': 'wkb_geometry',
                        'type': 'geometry(Polygon,28992)',
                        'null': False,
                    },
                ],
                'primary_key': 'gid',
            },
            'mutaties_standplaats': {
                'columns': [
                    {
                        'include': 'gid',
                    },
                    {
                        'include': 'identificatie',
                    },
                    {
                        'name': 'status',
                        'type': 'ligplaatsstatus',
                        'null': False,
                    },
                    {
                        'include_group': 'common',
                    },
                    {
                        'include_group': 'adresseerbaarobject',
                    },
                    {
                        'include_group': 'mutatie',
                    },
                    {
                        'name': 'wkb_geometry',
                        'type': 'geometry(Polygon,28992)',
                        'null': False,
                    },
                ],
                'primary_key': 'gid',
            },
            'mutaties_pand': {
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
                        'type': 'pandstatus',
                        'null': False,
                    },
                    {
                        'include_group': 'common',
                    },
                    {
                        'include_group': 'voorkomen',
                    },
                    {
                        'include_group': 'mutatie',
                    },
                    {
                        'name': 'wkb_geometry',
                        'type': 'geometry(Polygon,28992)',
                        'null': False,
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

        if table not in table_structure:
            raise Exception('Unsupported table: %s' % table)

        if table in table_enum:
            for name in table_enum[table]:
                if not self.enum_exists(name):
                    self.create_enum(name, enum_type[name])

        fields = set()

        def add_column(i_, column_):
            sqlstr_ = ''

            if 'include' in column_:
                sqlstr_ += add_column(
                    i_,
                    table_column[column_['include']],
                )
            elif 'include_group' in column_:
                for c in table_column_group[column_['include_group']]:
                    sqlstr_ += add_column(
                        i_,
                        c,
                    )
            else:
                if i_ > 0:
                    sqlstr_ += ', '

                sqlstr_ += '%(name)s %(type)s' % column_
                fields.add(column_["name"])

                if(
                    column_['null'] is False and  # noqa: W504
                    column_['type'] != 'serial'
                ):
                    sqlstr_ += ' NOT NULL'

                i_ += 1

            return sqlstr_

        sqlfmt = {
            'table': sql.Identifier(table),
        }

        sqlstr = r'CREATE TABLE {table} ('

        i = 0
        for column in table_structure[table]['columns']:
            sqlstr += add_column(i, column)

            i += 1

        if 'primary_key' in table_structure[table]:
            sqlstr += ', PRIMARY KEY ({primary_key})'

            key = 'primary_key'

            sqlfmt[key] = sql.Identifier(table_structure[table][key])

        sqlstr += r')'

        if not self.table_exists(table):

            log.debug("sqlstr: %s" % sqlstr)
            log.debug("sqlfmt: %s" % sqlfmt)

            query = sql.SQL(sqlstr).format(**sqlfmt)

            log.debug("query: %s" % query.as_string(context=self.db.cursor))

            self.db.execute(query)
            self.db.commit(close=False)

        return fields

    def insert_records(self, table, records):
        fields_from_creation = self.create_table(table)
        fields_from_creation.remove("gid")

        if self.truncate:
            self.truncate_table(table)

        if not records:
            log.warning("No records for '%s'" % table)
            return

        fields_from_record = set(records[0].keys())
        log.debug("fields: %s" % fields_from_creation)
        log.debug("fields: %s" % fields_from_record)

        fields_to_delete = tuple(fields_from_record - fields_from_creation)
        for record in records:
            for field in fields_to_delete:
                del record[field]

        fields = str(tuple(sorted(fields_from_creation))).replace("'", '"')
        values = ", ".join(f"%({field})s" for field in records[0])

        if "wkb_geometry" in fields_from_creation:
            values = values.replace("%(wkb_geometry)s", "ST_SetSRID(%(wkb_geometry)s::geometry, 28992)")

        query = f"INSERT INTO {table} {fields} VALUES ({values})"

        log.debug("query: %s" % query)

        result = self.db.execute_batch(
            query,
            records,
        )
        self.db.commit(close=False)

        log.debug("Inserted records for '%s': %d" % (table, result))

    def process_levering_xml(self, tree, root, xml_file):
        log.info("Processing: BAG Extract Mutatie Levering")

        table = 'nlx_bag_info'

        elements = root.xpath(
            (
                '.'
                '/xb:SelectieGegevens'
                '/selecties-extract:MUT-Extract'
                '/selecties-extract:StandTechnischeDatum'
            ),
            namespaces=xmlns,
        )

        if not elements:
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

        with open(xml_file) as f:
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

    def element_to_row(
        self,
        element,
        fields,
        object_type,
        object_element,
        mutation_type,
        mutation_verb,
    ):
        row = {
            field: None
            for field in fields
        }

        row = self.process_bag_object_element(
            object_type,
            object_element,
            element,
            row,
        )

        row["mutatiegroep"] = mutation_type
        row["toestand"] = mutation_verb

        return row

    def process_bag_object_xml(
        self,
        tree,
        root,
        status_type,
        object_type,
        *args,
    ):
        if args:
            raise Exception(f"Extra arguments not accepted for {type(self).__name__!r}.")

        object_element = {
            'LIG': 'Ligplaats',
            'NUM': 'Nummeraanduiding',
            'OPR': 'OpenbareRuimte',
            'PND': 'Pand',
            'STA': 'Standplaats',
            'VBO': 'Verblijfsobject',
            'WPL': 'Woonplaats',
        }
        mutations = (
            ("toevoeging", "wordt"),
            ("verwijdering", "was"),
            ("wijziging", "was"),
            ("wijziging", "wordt"),
        )

        elements = root.xpath(
            (
                '.'
                '/ml:mutatieBericht'
                '/ml:mutatieGroep'
                '/*'
                '/*'
                '/mlm:bagObject'
            ),
            namespaces=xmlns,
        )

        if not elements:
            log.warning('No bagObject elements found')
            return

        fields = [
            "begingeldigheid",
            "documentdatum",
            "documentnummer",
            "eindgeldigheid",
            "eindregistratie",
            "gebruiksdoel",
            "geconstateerd",
            "hoofdadresnummeraanduidingref",
            "huisletter",
            "huisnummer",
            "huisnummertoevoeging",
            "identificatie",
            "mutatiegroep",
            "naam",
            "nevenadresnummeraanduidingref",
            "nummeraanduidingref",
            "oorspronkelijkbouwjaar",
            "openbareruimteref",
            "oppervlakte",
            "pandref",
            "postcode",
            "status",
            "tijdstipeindregistratielv",
            "tijdstipinactief",
            "tijdstipinactieflv",
            "tijdstipnietbaglv",
            "tijdstipregistratie",
            "tijdstipregistratielv",
            "toestand",
            "type",
            "typeadresseerbaarobject",
            "verkortenaam",
            "voorkomenidentificatie",
            "wkb_geometry",
            "woonplaatsref",
        ]

        for key, obj in object_element.items():
            elements_filtered = [
                element
                for element in elements
                if element.getchildren()[0].tag.endswith(obj)
            ]

            records = []
            table = f"mutaties_{obj.lower()}"
            for mutation_type, mutation_verb in mutations:
                elements_filtered_twice = [
                    element
                    for element in elements_filtered
                    if element.getparent().tag.endswith(mutation_verb)
                    and element.getparent().getparent().tag.endswith(mutation_type)
                ]

                if mutation_type == "verwijdering" and elements_filtered_twice:
                    log.warning("Not implemented for 'verwijdering'")
                    raise NotImplementedError("'verwijdering'")

                if not elements_filtered_twice:
                    log.debug(
                        "Skipping table=%s object_type=%s mutation_type=%s mutation_verb=%s"
                        % (table, key, mutation_type, mutation_verb)
                    )
                    continue

                log.debug(
                    "Processing table=%s object_type=%s mutation_type=%s mutation_verb=%s"
                    % (table, key, mutation_type, mutation_verb)
                )
                to_row = partial(
                    self.element_to_row,
                    fields=fields,
                    object_type=key,
                    object_element=object_element,
                    mutation_type=mutation_type,
                    mutation_verb=mutation_verb,
                )
                records.extend(to_row(element) for element in elements_filtered_twice)

            self.insert_records(table, records)

    def process_mut_xml(self, tree, root, xml_file):
        log.info("Processing: BAG Mutaties")

        filename = os.path.basename(xml_file)

        match = re.search(
            r'^\d{4}(IO|)(MUT)\d{8}-\d{8}-\d{6}\.xml$',
            filename,
        )

        if not match:
            raise Exception('Failed to parse filename: %s' % filename)

        status_type, object_type = match.groups()

        log.debug("status_type: %s" % status_type)
        log.debug("object_type: %s" % object_type)

        if object_type != "MUT":
            raise Exception("Unsupported object type: %s" % object_type)

        if status_type == '':
            # Normal objects
            self.process_bag_object_xml(
                tree,
                root,
                status_type,
                object_type,
            )
        elif status_type == 'IO':
            # Under investigation (InOnderzoek)
            log.debug("InOnderzoek niet ondersteund")
        else:
            raise Exception("Unsupported status objects: %s (%s)" % (status_type, object_type))

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
        elif root.tag == '{%s}bagMutaties' % xmlns['Mutaties']:
            if xml_file.endswith("000001.xml"):
                log.warning("Skipping unsupported file: %s" % xml_file)
            else:
                self.process_mut_xml(tree, root, xml_file)
        else:
            log.warning("Skipping unsupported file: %s" % xml_file)

        BAGUtil.remove_temp_file(xml_file)
