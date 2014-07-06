# -*- coding: utf-8 -*-
#
# Input classes for ETL, databases.
#
# Author: Just van den Broecke
#
from stetl.component import Attr
from stetl.input import Input
from stetl.util import Util
from stetl.packet import FORMAT
from stetl.postgis import PostGIS

log = Util.get_log('dbinput')


class DbInput(Input):
    """
    Input from any database (abstract base class).
    """

    def __init__(self, configdict, section, produces):
        Input.__init__(self, configdict, section, produces=produces)

    def read(self, packet):
        return packet


class PostgresDbInput(Input):
    """
    Input by querying records from a Postgres database.
    Input is a query, like SELECT * from mytable.
    Output is zero or more records.

    produces=FORMAT.record
    """

    # Start attribute config meta
    cfg_database = Attr(str, True, None, "database name")

    cfg_host = Attr(str, False, 'localhost', "host name or host IP-address")

    cfg_user = Attr(str, False, 'postgres', "User name")

    cfg_password = Attr(str, False, 'postgres', "User password")

    cfg_schema = Attr(str, False, 'public', "Schema name")

    cfg_table = Attr(str, False, None, "Table name")

    cfg_table = Attr(str, False, None, "Column names to populate records with")

    cfg_read_once = Attr(bool, False, False, "Read once? i.e. only do query once and stop")

    # End attribute config meta

    def __init__(self, configdict, section):
        Input.__init__(self, configdict, section, produces=FORMAT.record)
        self.query = self.cfg.get('query')
        self.read_once = self.cfg.get_bool('read_once', False)
        self.column_names = self.cfg.get('column_names', None)
        self.db = None

    def init(self):
        # Connect only once to DB
        log.info('Init: connect to DB')
        self.db = PostGIS(self.cfg.get_dict())
        self.db.connect()

        # If no explicit column names given, get from DB meta info
        if self.column_names is None:
            self.column_names = self.db.get_column_names(self.cfg.get('table'), self.cfg.get('schema'))

    def exit(self):
        # Disconnect from DB when done
        log.info('Exit: disconnect from DB')

        self.db.disconnect()

    def do_query(self, query_str):

        self.db.execute(query_str)

        db_records = self.db.cursor.fetchall()
        log.info('read recs: %d' % len(db_records))

        # record is Python list of Python dict (multiple records)
        records = list()

        # Convert list of lists to list of dict using column_names
        for db_record in db_records:
            records.append(dict(zip(self.column_names, db_record)))

        return records

    def read(self, packet):
        packet.data = self.do_query(self.query)

        # No more records to process?
        if len(packet.data) == 0 or self.read_once is True:
            packet.set_end_of_stream()
            log.info('Nothing to do. All file_records done')
            return packet

        return packet
