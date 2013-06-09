# -*- coding: utf-8 -*-
#
# PostGIS support wrapper.
#
# Author: Just van den Broecke
#
import sys
from util import Util

log = Util.get_log("postgis")

try:
    import psycopg2
    import psycopg2.extensions
except ImportError:
    log.error("cannot find packages psycopg2 for Postgres client support")
    sys.exit(-1)


class PostGIS:
    def __init__(self, config):
        # Lees de configuratie 
        self.config = config

    def initialiseer(self, bestand):
        log.info('Connecting...')
        self.connect(True)

        log.info('executing sql script...')
        try:
            script = open(bestand, 'r').read()
            self.cursor.execute(script)
            self.connection.commit()
            log.info('script executed')
        except psycopg2.DatabaseError, e:
            log.warn("error '%s' from script '%s'" % (str(e), str(bestand)))

    def connect(self, initdb=False):
        try:
            self.connection = psycopg2.connect(
                "dbname='%s' user='%s' host='%s' password='%s'" % (self.config['database'],
                                                                   self.config['user'],
                                                                   self.config['host'],
                                                                   self.config['password']))
            self.cursor = self.connection.cursor()

            self.set_schema()
            log.debug("connected to database %s" % (self.config['database']))
        except Exception, e:
            log.warn("cannot connect to database '%s'" % (self.config['database']))


    def commit(self):
        self.e = None
        try:
            self.connection.commit()
            self.connection.close()
        except (Exception), e:
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


    def execute(self, sql, parameters=None):
        try:
            if parameters:
                self.cursor.execute(sql, parameters)
            else:
                self.cursor.execute(sql)

                # log.debug(self.cursor.statusmessage)
        except (Exception), e:
            log.error("error %s in query: %s with params: %s" % (str(e), str(sql), str(parameters)))
            #            self.log_actie("uitvoeren_db", "n.v.t", "fout=%s" % str(e), True)
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
        except (Exception), e:
            self.e = e
            self.log_action("file_execute", "n.v.t", "fout=%s" % str(e), True)
            log.warn("can't execute SQL script, error: %s" % (str(e)))


    def tx_execute(self, sql, parameters=None):
        self.e = None
        try:
            self.connect()
            self.execute(sql, parameters)
            self.connection.commit()
            self.connection.close()

            # log.debug(self.cursor.statusmessage)
        except (Exception), e:
            self.e = e
            log.error("error %s in transaction: %s with parms: %s" % (str(e), str(sql), str(parameters)))

        return self.cursor.rowcount
