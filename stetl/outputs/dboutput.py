# -*- coding: utf-8 -*-
#
# Output classes for ETL, databases.
#
# Author: Just van den Broecke
#
from stetl.output import Output
from stetl.util import Util
from stetl.packet import FORMAT
from stetl.postgis import PostGIS

log = Util.get_log('dboutput')


class DbOutput(Output):
    """
    Output to any database (abstract base class).
    """

    def __init__(self, configdict, section, consumes):
        Output.__init__(self, configdict, section, consumes)

    def write(self, packet):
        return packet

class PostgresDbOutput(DbOutput):
    """
    Output to PostgreSQL database.
    Input is an SQL string.
    Output by executing input SQL string.

    consumes=FORMAT.string
    """

    def __init__(self, configdict, section):
        DbOutput.__init__(self, configdict, section, consumes=FORMAT.string)

    def write(self, packet):
        if packet.data is None:
            return packet

        log.info('executing SQL')
        db = PostGIS(self.cfg.get_dict())
        rowcount = db.tx_execute(packet.data)
        log.info('executed SQL, rowcount=%d' % rowcount)
        return packet

class PostgresInsertOutput(PostgresDbOutput):
    """
    Output by inserting single record into Postgres database.
    Input is a record (Python dic structure) or a Python list of dicts (records).
    Creates an INSERT for Postgres to insert each single record.

    consumes=FORMAT.record
    """

    def __init__(self, configdict, section):
        DbOutput.__init__(self, configdict, section, consumes=FORMAT.record)
        self.query = None
        self.db = None
        self.key = self.cfg.get('key')

    def init(self):
        # Connect only once to DB
        log.info('Init: connect to DB')
        self.db = PostGIS(self.cfg.get_dict())
        self.db.connect()

    def exit(self):
        # Disconnect from DB when done
        log.info('Exit: disconnect from DB')
        self.db.disconnect()

    def write(self, packet):
        # Deal with empty or zero-length data structures (list or dict)
        if packet.data is None or len(packet.data) == 0:
            return packet

        # ASSERT: record data present

        # record is Python dict (single record) or list of Python dict (multiple records)
        record = packet.data

        # Generate INSERT query template once
        first_record = record
        if type(record) is list and len(record) > 0:
            first_record = record[0]

        if self.query is None:
            # We assume that all records do the same INSERT key/values
            # See http://grokbase.com/t/postgresql/psycopg/12735bvkmv/insert-into-with-a-dictionary-or-generally-with-a-variable-number-of-columns
            # e.g. INSERT INTO lml_files ("file_name", "file_data") VALUES (%s,%s)
            self.query = "INSERT INTO %s (%s) VALUES (%s)" % (self.cfg.get('table'), ",".join(['"%s"' % k for k in first_record]), ",".join(["%s",]*len(first_record.keys())))
            log.info('query is %s', self.query)

        # Check if record is single (dict) or array (list of dict)
        if type(record) is dict:
            # Do insert with values from the single record
            self.db.execute(self.query, record.values())
            self.db.commit(close=False)

            log.info('committed record key=%s' % record[self.key])

        elif type(record) is list:
                # Multiple records in list
                for rec in record:
                    # Do insert with values from the record
                    self.db.execute(self.query, rec.values())
                    self.db.commit(close=False)

                log.info('committed %d records' % len(record))

        return packet
