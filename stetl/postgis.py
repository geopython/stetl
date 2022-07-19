# PostGIS support wrapper.
#
# Author: Just van den Broecke
#
from .util import Util

log = Util.get_log("postgis")

try:
    import psycopg2
    import psycopg2.extensions
    import psycopg2.extras
    from psycopg2 import sql as pg2sql
except ImportError:
    log.error("cannot find package psycopg2 for Postgres client support, please install psycopg2 first!")
    # sys.exit(-1)


class PostGIS:
    def __init__(self, config):
        # Lees de configuratie
        self.config = config
        self.e = None

    def initialiseer(self, bestand):
        log.info('Connecting...')
        self.connect(True)

        log.info('executing sql script...')
        try:
            script = open(bestand, 'r').read()
            self.cursor.execute(script)
            self.connection.commit()
            log.info('script executed')
        except psycopg2.DatabaseError as e:
            log.warn("error '%s' from script '%s'" % (str(e), str(bestand)))

    def connect(self, initdb=False):
        try:
            conn_str = "dbname=%s user=%s host=%s port=%s" % (self.config['database'],
                                                              self.config['user'],
                                                              self.config.get('host', 'localhost'),
                                                              self.config.get('port', '5432'))
            log.info('Connecting to %s' % conn_str)
            conn_str += ' password=%s' % self.config['password']
            self.connection = psycopg2.connect(
                conn_str,
                keepalives=1,
                keepalives_idle=60,
                keepalives_interval=10,
                keepalives_count=5,
            )
            self.cursor = self.connection.cursor()

            self.set_schema()
            log.debug("Connected to database %s" % (self.config['database']))
        except Exception as e:
            log.error("Cannot connect to database '%s' e=%s" % (self.config['database'], str(e)))

    def disconnect(self):
        self.e = None
        try:
            self.connection.close()
        except Exception as e:
            self.e = e
            log.error("error %s in close" % (str(e)))

        return self.e

    def commit(self, close=True):
        self.e = None
        try:
            self.connection.commit()
            if close is True:
                self.connection.close()
        except Exception as e:
            self.e = e
            log.error("error %s in commit" % (str(e)))

        return self.e

    def create_schema(self):
        # Public schema: no further action required
        if self.config['schema'] != 'public':
            # A specific schema is required create it and set the search path
            self.execute('''DROP SCHEMA IF EXISTS %s CASCADE;''' % self.config['schema'])
            self.execute('''CREATE SCHEMA %s;''' % self.config['schema'])
            self.connection.commit()

    def set_schema(self):
        # Non-public schema set search path
        if self.config['schema'] != 'public':
            # Always set search path to our schema
            self.execute('SET search_path TO %s,public' % self.config['schema'])
            self.connection.commit()

    def log_action(self, action, bestand="n.v.t", bericht='geen', error=False):
        sql = "INSERT INTO stetl_log(actie, bestand, error, bericht) VALUES (%s, %s, %s, %s)"
        parameters = (action, bestand, error, bericht)
        self.tx_execute(sql, parameters)

    def log_meta(self, key, value):
        sql = "INSERT INTO stetl_info(sleutel, waarde) VALUES (%s, %s)"
        parameters = (key, value)
        self.tx_execute(sql, parameters)

    def make_bytea(self, blob):
        return psycopg2.Binary(blob)

    def get_column_names(self, table, schema='public'):
        self.cursor.execute(
            "select column_name from information_schema.columns where table_schema = '%s' and table_name='%s'" % (schema, table))
        column_names = [row[0] for row in self.cursor]
        return column_names

    def execute(self, sql, parameters=None):
        try:
            if parameters:
                self.cursor.execute(sql, parameters)
            else:
                self.cursor.execute(sql)

                # log.debug(self.cursor.statusmessage)
        except Exception as e:
            log.error("error %s in query: %s with params: %s" % (str(e), str(sql), str(parameters)))
            #            self.log_actie("uitvoeren_db", "n.v.t", "fout=%s" % str(e), True)
            return -1

        return self.cursor.rowcount

    def executemany(self, sql, parameters):
        try:
            self.cursor.executemany(sql, parameters)
            # log.debug(self.cursor.statusmessage)
        except Exception as e:
            log.exception("error '%s' in query: %s" % (str(e), str(sql)))
            return -1
        return self.cursor.rowcount

    def execute_batch(self, sql, parameters):
        try:
            psycopg2.extras.execute_batch(
                self.cursor,
                sql,
                parameters,
            )
            # log.debug(self.cursor.statusmessage)
        except Exception as e:
            log.exception("error '%s' in query: %s" % (str(e), str(sql)))
            return -1
        return self.cursor.rowcount

    def file_execute(self, sqlfile):
        self.e = None
        try:
            log.info("Executing SQL of file = %s ..." % sqlfile)
            self.connect()
            f = open(sqlfile, 'r')
            sql = f.read()
            self.execute(sql)
            self.connection.commit()
            f.close()
            log.info("SQL executed OK")
        except Exception as e:
            self.e = e
            self.log_action("file_execute", "n.v.t", "fout=%s" % str(e), True)
            log.warn("can't execute SQL script, error: %s" % (str(e)))

    def truncate_table(self, table):
        log.info("Truncating table: %s" % table)

        sqlfmt = {
            'table': pg2sql.Identifier(table),
        }

        query = pg2sql.SQL('TRUNCATE {table}').format(**sqlfmt)

        log.debug("query: %s" % query.as_string(context=self.cursor))

        self.cursor.execute(query)

    def tx_execute(self, sql, parameters=None):
        self.e = None
        try:
            self.connect()
            self.execute(sql, parameters)
            self.connection.commit()
            self.connection.close()

            # log.debug(self.cursor.statusmessage)
        except Exception as e:
            self.e = e
            log.error("error %s in transaction: %s with parms: %s" % (str(e), str(sql), str(parameters)))
            # Return a dummy "-1" row count in the same vein as self.execute()
            return -1

        # Make sure there is a cursor with a row count before returning it, otherwise "return early"
        if not hasattr(self, 'cursor'):
            return -1

        if not hasattr(self.cursor, 'rowcount'):
            return -1

        return self.cursor.rowcount
