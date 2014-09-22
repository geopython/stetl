# -*- coding: utf-8 -*-
#
# Input classes for ETL, databases.
#
# Author: Just van den Broecke
#
from stetl.component import Config
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
    @Config(str, required=True, default=None)
    def database_name(self):
        """
        database name
        """
        pass

    @Config(str, required=False, default='localhost')
    def host(self):
        """
        host name or host IP-address
        """
        pass

    @Config(str, required=False, default='postgres')
    def user(self):
        """
        User name
        """
        pass

    @Config(str, required=False, default='postgres')
    def password(self):
        """
        User password
        """
        pass

    @Config(str, required=False, default='public')
    def schema(self):
        """
        Schema (postgres schema) name
        """
        pass

    @Config(str, required=False, default=None)
    def table(self):
        """
        Table name
        """
        pass

    @Config(str, required=False, default=None)
    def column_names(self):
        """
        Column names to populate records with
        """
        pass

    @Config(bool, required=False, default=False)
    def read_once(self):
        """
        Read once? i.e. only do query once and stop
        """
        pass


    @Config(str, required=False, default=None)
    def query(self):
        """
        The query (string) to fire.
        """
        pass
    # End attribute config meta

    def __init__(self, configdict, section):
        Input.__init__(self, configdict, section, produces=[FORMAT.record_array,FORMAT.record])
        self.db = None

    def init(self):
        # Connect only once to DB
        log.info('Init: connect to DB')
        self.db = PostGIS(self.cfg.get_dict())
        self.db.connect()

        # If no explicit column names given, get from DB meta info
        self.columns = self.column_names
        if self.column_names is None:
            self.columns = self.db.get_column_names(self.cfg.get('table'), self.cfg.get('schema'))

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
            records.append(dict(zip(self.columns, db_record)))

        return records

    def read(self, packet):
        packet.data = self.do_query(self.query)

        # No more records to process?
        if len(packet.data) == 0 or self.read_once is True:
            packet.set_end_of_stream()
            log.info('Nothing to do. All file_records done')
            return packet

        return packet
